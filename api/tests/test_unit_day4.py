import unittest
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException

from support import configured
from app.main import day4_controlled_error
from app.services.llm import generate
from app.services.queue import get_queue_depth


class Day4ChaosTests(unittest.TestCase):
    def test_controlled_error_is_disabled_by_default(self):
        with configured(day4_chaos_force_error=False):
            with self.assertRaises(HTTPException) as raised:
                day4_controlled_error()
        self.assertEqual(raised.exception.status_code, 404)

    def test_controlled_error_is_explicit_and_sanitized(self):
        with configured(day4_chaos_force_error=True):
            with self.assertRaises(HTTPException) as raised:
                day4_controlled_error()
        self.assertEqual(raised.exception.status_code, 503)
        self.assertNotIn("secret", str(raised.exception.detail).lower())

    def test_fixture_delay_is_zero_by_default_and_bounded_when_enabled(self):
        contexts = [{"source": "fixture.txt", "chunk_text": "known context"}]
        with configured(day4_chaos_llm_delay_seconds=0), patch(
            "app.services.llm.time.sleep"
        ) as sleep:
            generate("question", contexts)
            sleep.assert_not_called()
        with configured(day4_chaos_llm_delay_seconds=2.5), patch(
            "app.services.llm.time.sleep"
        ) as sleep:
            generate("question", contexts)
            sleep.assert_called_once_with(2.5)


class QueueDepthTests(unittest.IsolatedAsyncioTestCase):
    async def test_queue_depth_uses_real_configured_redis_sorted_set(self):
        pool = AsyncMock()
        pool.zcard.return_value = 7
        with configured(ingestion_queue="insighthub:test"), patch(
            "app.services.queue.create_pool", new=AsyncMock(return_value=pool)
        ):
            self.assertEqual(await get_queue_depth(), 7)
        pool.zcard.assert_awaited_once_with("insighthub:test")
        pool.aclose.assert_awaited_once()
