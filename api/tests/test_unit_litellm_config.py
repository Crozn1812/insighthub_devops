import unittest

from app.core.config import Settings


class LiteLLMConfigurationTests(unittest.TestCase):
    def test_gateway_key_alias_is_private_and_usable(self):
        settings = Settings(_env_file=None, rag_mode="real", llm_provider="openai",
                            embedding_provider="ollama", openai_base_url="http://gateway:4000/v1",
                            openai_chat_model="qwen3:4b", litellm_api_key="synthetic-gateway-credential")
        self.assertEqual(settings.openai_api_key, settings.litellm_api_key)
        self.assertNotIn("synthetic-gateway-credential", repr(settings))

    def test_explicit_openai_key_is_preserved(self):
        settings = Settings(_env_file=None, rag_mode="real", llm_provider="openai",
                            embedding_provider="ollama", openai_base_url="http://gateway:4000/v1",
                            openai_chat_model="qwen3:4b", openai_api_key="synthetic-explicit",
                            litellm_api_key="synthetic-other")
        self.assertEqual(settings.openai_api_key, "synthetic-explicit")
