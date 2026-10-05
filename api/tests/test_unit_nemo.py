"""Native rail integration must distinguish policy blocks from service failure."""

import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import httpx
from fastapi import HTTPException

from app.security.nemo import nemo_allowed


class NemoIntegrationTests(unittest.TestCase):
    def settings(self, enabled=True):
        return SimpleNamespace(nemo_guardrails_url="http://guard:8082" if enabled else "",
                               nemo_guardrails_key="synthetic-test-identity")

    def test_disabled_fixture_does_not_contact_service(self):
        with patch("app.security.nemo.get_settings", return_value=self.settings(False)), \
                patch("app.security.nemo.httpx.Client") as client:
            self.assertTrue(nemo_allowed("Explain queues", "input"))
            client.assert_not_called()

    def test_native_allow_and_block_are_preserved(self):
        for allowed in (True, False):
            response = MagicMock()
            response.json.return_value = {"allowed": allowed}
            with patch("app.security.nemo.get_settings", return_value=self.settings()), \
                    patch("app.security.nemo.httpx.Client") as client:
                client.return_value.__enter__.return_value.post.return_value = response
                self.assertEqual(nemo_allowed("synthetic content", "context"), allowed)

    def test_unavailable_service_returns_503(self):
        with patch("app.security.nemo.get_settings", return_value=self.settings()), \
                patch("app.security.nemo.httpx.Client", side_effect=httpx.ConnectError("offline")):
            with self.assertRaises(HTTPException) as error:
                nemo_allowed("Explain queues", "input")
        self.assertEqual(error.exception.status_code, 503)

    def test_malformed_verdict_fails_closed(self):
        response = MagicMock()
        response.json.return_value = {"allowed": "true"}
        with patch("app.security.nemo.get_settings", return_value=self.settings()), \
                patch("app.security.nemo.httpx.Client") as client:
            client.return_value.__enter__.return_value.post.return_value = response
            with self.assertRaises(HTTPException) as error:
                nemo_allowed("Explain queues", "output")
        self.assertEqual(error.exception.status_code, 503)
