"""Opt-in local incident proxy; forwards real model requests without logging bodies."""

import asyncio
import os

import httpx
from fastapi import FastAPI, Request, Response

app = FastAPI()
UPSTREAM = os.environ.get("FAULT_PROXY_UPSTREAM", "http://insighthub-native-litellm:4000")
DELAY = float(os.environ.get("FAULT_PROXY_DELAY_SECONDS", "0"))
ERROR = os.environ.get("FAULT_PROXY_FORCE_ERROR", "false").lower() == "true"
if not 0 <= DELAY <= 45:
    raise ValueError("Incident delay must be bounded to 45 seconds")


@app.get("/healthz")
def health():
    return {"status": "ok", "incident_proxy": True}


@app.api_route("/v1/{path:path}", methods=["GET", "POST"])
async def forward(path: str, request: Request):
    if ERROR:
        return Response('{"error":{"message":"Controlled local provider incident"}}',
                        status_code=503, media_type="application/json")
    if DELAY:
        await asyncio.sleep(DELAY)
    headers = {name: value for name, value in request.headers.items()
               if name.lower() in {"authorization", "content-type"}}
    try:
        async with httpx.AsyncClient(timeout=90) as client:
            result = await client.request(request.method, UPSTREAM + "/v1/" + path,
                                          content=await request.body(), headers=headers,
                                          params=request.query_params)
        return Response(result.content, status_code=result.status_code,
                        media_type=result.headers.get("content-type", "application/json"))
    except httpx.HTTPError:
        return Response('{"error":{"message":"Local provider transport unavailable"}}',
                        status_code=502, media_type="application/json")
