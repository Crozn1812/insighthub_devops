import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from support import configured, real_config
from app.core.errors import DocumentConflict
from app.services.chunking import chunk_text, effective_embedding_budget, estimate_embedding_tokens
from app.services.embeddings import embed
from app.services.ingestion import _pipeline_id, extract_text
from app.services.payloads import prepare_retry


def local_model(**extra):
    return real_config(embedding_provider="ollama", embedding_model="mxbai-embed-large", **extra)


class SafeChunkTests(unittest.TestCase):
    def test_short_text_and_other_provider_keep_legacy_behavior(self):
        with local_model():
            self.assertEqual(chunk_text("short   ordinary text"), ["short ordinary text"])
        with configured():
            self.assertEqual(chunk_text("word " * 650)[0], " ".join(["word"] * 600))

    def test_long_unicode_and_dense_word_are_bounded_nonempty_deterministic(self):
        for text in (" ".join(f"Tài liệu tiếng Việt số{i} có dấu." for i in range(100)),
                     "".join(chr(0x4E00 + i) + "🙂" for i in range(600)),
                     "".join(f"{i:04x}" for i in range(600))):
            with local_model():
                chunks = chunk_text(text)
                self.assertGreater(len(chunks), 1)
                self.assertEqual(chunks, chunk_text(text))
                self.assertTrue(all(c and estimate_embedding_tokens(c) <= 400 for c in chunks))
                normalized = " ".join(text.split())
                covered = chunks[0]
                for c in chunks[1:]:
                    shared = max((i for i in range(min(len(covered), len(c)) + 1)
                                  if covered.endswith(c[:i])), default=0)
                    # Whitespace normalization may omit a boundary space only.
                    covered += c[shared:]
                self.assertEqual(covered.replace(" ", ""), normalized.replace(" ", ""))

    def test_overlap_and_logical_target(self):
        text = "abcdefghij" * 200
        with local_model() as settings:
            chunks = chunk_text(text)
            self.assertEqual(effective_embedding_budget(settings), 400)
            self.assertEqual(chunks[0][-100:], chunks[1][:100])
        with local_model(chunk_size=200, chunk_overlap=40) as settings:
            self.assertEqual(effective_embedding_budget(settings), 200)
            self.assertTrue(all(estimate_embedding_tokens(c) <= 200 for c in chunk_text(text)))

    def test_txt_md_and_compatibility_unicode(self):
        for extension in (".txt", ".md"):
            with local_model():
                chunks = chunk_text(extract_text("synthetic" + extension, ("ﷺ Việt Nam " * 100).encode()))
                self.assertTrue(all(estimate_embedding_tokens(c) <= 400 for c in chunks))
        with local_model():
            self.assertEqual(chunk_text(" \n\t "), [])

    def test_pdf_extraction_uses_same_bounded_stage(self):
        reader = MagicMock()
        reader.is_encrypted = False
        page = MagicMock()
        page.extract_text.return_value = "Synthetic PDF operations guide. " * 100
        reader.pages = [page]
        with local_model(), patch("pypdf.PdfReader", return_value=reader):
            chunks = chunk_text(extract_text("ordinary.pdf", b"synthetic PDF fixture"))
            self.assertGreater(len(chunks), 1)
            self.assertTrue(all(estimate_embedding_tokens(c) <= 400 for c in chunks))

    def test_embedding_contract_unchanged(self):
        with local_model() as settings, patch("app.services.embeddings.post_json") as post:
            post.return_value = {"embeddings": [[1.0] * 1024]}
            vectors = embed(["bounded synthetic text"])
            self.assertEqual(settings.embedding_dim, 1024)
            self.assertEqual(len(vectors[0]), 1024)
            self.assertIs(post.call_args.kwargs["payload"]["truncate"], False)
            self.assertEqual(post.call_args.kwargs["payload"]["model"], "mxbai-embed-large")

    def test_failed_legacy_retry_migrates_only_verified_payload(self):
        with tempfile.TemporaryDirectory() as folder, local_model(payload_dir=folder):
            payload = b"synthetic retained input"
            Path(folder, "123.payload").write_bytes(payload)
            legacy = _pipeline_id(legacy=True)
            current = _pipeline_id()
            self.assertNotEqual(current, legacy)
            connection = MagicMock()
            connection.execute.return_value.fetchone.return_value = (
                "ordinary.txt", "failed", hashlib.sha256(payload).hexdigest(), legacy)
            with patch("app.services.payloads.get_conn") as context:
                context.return_value.__enter__.return_value = connection
                self.assertEqual(prepare_retry(123), "ordinary.txt")
                self.assertEqual(connection.execute.call_args.args[1], (current, 123))
                connection.execute.return_value.fetchone.return_value = (
                    "ordinary.txt", "failed", hashlib.sha256(payload).hexdigest(), "unrelated-pipeline")
                with self.assertRaises(DocumentConflict):
                    prepare_retry(123)
                connection.execute.return_value.fetchone.return_value = (
                    "ordinary.txt", "failed", hashlib.sha256(payload).hexdigest(), legacy)
                Path(folder, "123.payload").write_bytes(b"changed input")
                with self.assertRaises(DocumentConflict):
                    prepare_retry(123)
