import unittest
from unittest.mock import patch

from support import real_config
from app.core.errors import ProviderError
from app.services.llm import generate


class GatewayOutputTests(unittest.TestCase):
    def test_native_gateway_schema_extracts_only_answer(self):
        with real_config(llm_structured_output=True):
            with patch("app.services.llm.post_json", return_value={
                "choices": [{"message": {"content": '{"answer":"Redis queues jobs."}'}}],
                "usage": {"prompt_tokens": 12, "completion_tokens": 9},
            }) as request:
                result = generate("Explain Redis.", [{"source": "manual.md", "chunk_text": "Redis queues jobs."}])
                self.assertEqual(result["answer"], "Redis queues jobs.")
                self.assertEqual(request.call_args.kwargs["payload"]["response_format"]["type"], "json_schema")

    def test_truncated_gateway_schema_is_rejected_without_body(self):
        with real_config(llm_structured_output=True):
            with patch("app.services.llm.post_json", return_value={
                "choices": [{"message": {"content": '{"answer":"synthetic private data'}}],
            }):
                with self.assertRaises(ProviderError) as caught:
                    generate("Explain Redis.", [{"source": "manual.md", "chunk_text": "Redis queues jobs."}])
                self.assertNotIn("synthetic private", str(caught.exception))
