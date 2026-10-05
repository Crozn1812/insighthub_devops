from __future__ import annotations

import importlib.util
import pathlib
import sys
import unittest
from unittest.mock import patch


SCRIPT = pathlib.Path(__file__).parents[1] / "scripts" / "rag-poisoning-eval.py"
SPEC = importlib.util.spec_from_file_location("rag_poisoning_eval", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class FakeClient:
    def __init__(self, chat_error: bool = False) -> None:
        self.deleted = False
        self.chat_error = chat_error

    def upload(self, filename: str, content: bytes) -> dict:
        self.filename = filename
        self.content = content
        return {"id": 42, "status": "pending"}

    def documents(self) -> list[dict]:
        return [] if self.deleted else [{"id": 42, "status": "ready"}]

    def chat(self, question: str) -> dict:
        if self.chat_error:
            raise RuntimeError("controlled chat failure")
        if self.deleted:
            return {"contexts": [], "answer": "not found"}
        marker = "DAY6_POISON_" + self.content.decode().split("DAY6_POISON_", 1)[1].split()[0].rstrip(".")
        return {
            "contexts": [{"content": marker, "filename": self.filename}],
            "answer": marker,
            "mode": "real",
            "provider": "ollama",
            "model": "qwen3:4b",
        }

    def delete(self, document_id: int) -> None:
        self.deleted = True


class RagPoisoningEvalTests(unittest.TestCase):
    @patch.object(MODULE.time, "sleep", return_value=None)
    def test_real_path_result_and_cleanup(self, _sleep) -> None:
        client = FakeClient()
        result = MODULE.run_evaluation(client)
        self.assertTrue(result.marker_in_answer)
        self.assertTrue(result.deleted)
        self.assertFalse(result.stale_document_present)
        self.assertFalse(result.stale_context_retrieved)

    @patch.object(MODULE.time, "sleep", return_value=None)
    def test_cleanup_runs_when_chat_fails(self, _sleep) -> None:
        client = FakeClient(chat_error=True)
        with self.assertRaisesRegex(RuntimeError, "controlled chat failure"):
            MODULE.run_evaluation(client)
        self.assertTrue(client.deleted)


if __name__ == "__main__":
    unittest.main()
