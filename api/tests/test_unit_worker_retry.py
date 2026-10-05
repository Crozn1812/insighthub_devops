"""Transient ingestion failures retry; invalid content and exhausted jobs do not."""

import asyncio
import unittest
from unittest.mock import patch

from arq import Retry

from app.core.errors import TransientProviderError
from app.worker import WorkerSettings, ingest_document


class WorkerRetryTests(unittest.TestCase):
    def test_three_exponential_delays(self):
        for attempt, delay in ((1, 1), (2, 2), (3, 4)):
            with self.subTest(attempt=attempt), \
                    patch("app.worker.run_document", side_effect=TransientProviderError()):
                with self.assertRaises(Retry) as error:
                    asyncio.run(ingest_document({"job_try": attempt}, 42))
                self.assertEqual(error.exception.defer_score, delay * 1000)
        self.assertEqual(WorkerSettings.max_tries, 4)

    def test_final_attempt_disables_retry(self):
        with patch("app.worker.run_document", return_value="failed") as process:
            self.assertEqual(asyncio.run(ingest_document({"job_try": 4}, 42)), "failed")
        process.assert_called_once_with(42, False)

    def test_non_transient_failure_is_not_retried(self):
        with patch("app.worker.run_document", return_value="failed"):
            self.assertEqual(asyncio.run(ingest_document({"job_try": 1}, 42)), "failed")

    def test_success_keeps_document_identity(self):
        with patch("app.worker.run_document", return_value="ready") as process:
            self.assertEqual(asyncio.run(ingest_document({"job_try": 2}, 42)), "ready")
        process.assert_called_once_with(42, True)
