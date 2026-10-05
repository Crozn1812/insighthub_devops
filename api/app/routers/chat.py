"""RAG executes in FastAPI's threadpool; usage preserves its provenance."""

import time
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from app.core.metrics import (
    llm_call_latency,
    llm_estimated_cost_usd_total,
    llm_tokens_total,
    rag_query_latency,
)
from app.services.llm import SYSTEM_PROMPT, generate
from app.services.retrieval import retrieve
from app.security.nemo import nemo_allowed
from app.core.config import get_settings
from app.core.metrics import guardrail_decisions_total
from app.security.guardrails import (
    REFUSAL,
    filter_contexts,
    inspect_request,
    normalize_source_citations,
    protect_output,
    sanitize_context_sources,
)

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    question: str = Field(min_length=1, max_length=2000)
    top_k: int | None = Field(default=None, ge=1, le=20)


class TokenUsage(BaseModel):
    input_tokens: int | None = None
    output_tokens: int | None = None
    source: Literal["provider", "unavailable"]


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]
    contexts: list[dict]
    latency_ms: int
    mode: Literal["fixture", "real"]
    provider: str
    model: str
    usage: TokenUsage


@router.post("", response_model=ChatResponse)
def chat(req: ChatRequest):
    start = time.perf_counter()
    decision = inspect_request(req.question)
    guardrail_decisions_total.labels(
        "request", "allow" if decision.allowed else "block", decision.category
    ).inc()
    if not decision.allowed or not nemo_allowed(req.question, "input"):
        settings = get_settings()
        return ChatResponse(
            answer=REFUSAL, sources=[], contexts=[],
            latency_ms=int((time.perf_counter() - start) * 1000),
            mode=settings.rag_mode, provider=settings.llm_provider,
            model=settings.resolved_chat_model,
            usage=TokenUsage(input_tokens=None, output_tokens=None, source="unavailable"),
        )
    with rag_query_latency.time():
        contexts = retrieve(req.question, top_k=req.top_k)
        if not contexts:
            raise HTTPException(
                404, "Chưa có tài liệu nào sẵn sàng. Hãy upload tài liệu trước."
            )
        retrieved_contexts = contexts
        contexts, filtered = filter_contexts(contexts)
        nemo_contexts = [context for context in contexts
                         if nemo_allowed(str(context.get("chunk_text", "")), "context")]
        filtered = filtered or len(nemo_contexts) != len(contexts)
        contexts = nemo_contexts
        response_contexts = contexts
        if filtered:
            safe_keys = {(context.get("id"), context["source"]) for context in contexts}
            response_contexts = contexts + [
                {"source": context["source"], "chunk_text": "[FILTERED_BY_GUARDRAIL]"}
                for context in retrieved_contexts
                if (context.get("id"), context["source"]) not in safe_keys
            ]
        if not contexts:
            settings = get_settings()
            result = {"answer": REFUSAL, "sources": [], "mode": settings.rag_mode,
                      "provider": settings.llm_provider, "model": settings.resolved_chat_model,
                      "usage": {"input_tokens": None, "output_tokens": None, "source": "unavailable"}}
        else:
            generation_contexts = sanitize_context_sources(contexts)
            with llm_call_latency.time():
                result = generate(req.question, generation_contexts)
            result["answer"], _ = protect_output(result["answer"], (SYSTEM_PROMPT,))
            if result["answer"] != REFUSAL and not nemo_allowed(result["answer"], "output"):
                result["answer"] = REFUSAL
            if result["answer"] == REFUSAL:
                result["sources"] = []
            else:
                result["answer"], result["sources"] = normalize_source_citations(
                    result["answer"], generation_contexts
                )
        response_contexts = sanitize_context_sources(response_contexts)
    for direction in ("input", "output"):
        value = result["usage"].get(f"{direction}_tokens")
        if value is not None:
            llm_tokens_total.labels(result["provider"], direction).inc(value)
    if result["mode"] == "fixture":
        # Fixture mode has no external provider call and therefore zero provider cost.
        llm_estimated_cost_usd_total.labels(result["provider"], "fixture").inc(0)
    return ChatResponse(
        **result,
        contexts=response_contexts,
        latency_ms=int((time.perf_counter() - start) * 1000),
    )
