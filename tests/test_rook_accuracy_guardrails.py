from __future__ import annotations

from datetime import date
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from rook_accuracy_guardrails import (
    audit_final_output,
    build_fact_checking_instructions,
    load_accuracy_guardrail_text,
)
import seed_rook_guardrails


class RookAccuracyGuardrailsTests(unittest.TestCase):
    def test_guardrail_text_loads_from_single_prompt_file(self) -> None:
        text = load_accuracy_guardrail_text()
        prompt = build_fact_checking_instructions(date(2026, 6, 29))

        self.assertIn("# Rook SLM Accuracy Guardrails", text)
        self.assertIn("Fabricated or unverifiable references.", text)
        self.assertEqual(seed_rook_guardrails.GUARDRAILS.count(text), 1)
        self.assertEqual(prompt.count("Rook SLM must prioritize accuracy over fluency."), 1)

    def test_fabricated_or_unverified_citation_is_flagged(self) -> None:
        audit = audit_final_output(
            "The Acme Rook study proved the control works.",
            [
                {
                    "title": "Acme Rook Study",
                    "author_or_organization": "Acme Labs",
                    "publication_date": "2026-06-29",
                    "url_or_document_path": "/definitely/not/a/real/source.pdf",
                    "accessed_date": "2026-06-29",
                    "claim_supported": "The Acme Rook study proved the control works.",
                    "confidence_level": "high",
                    "citation_verified": False,
                }
            ],
            current_date=date(2026, 6, 29),
        )

        self.assertFalse(audit["ok"])
        self.assertTrue(any("unverified citation" in item["issues"] for item in audit["weak_citations"]))
        self.assertTrue(
            any(
                "source locator is not a URL and local document path was not found" in item["issues"]
                for item in audit["weak_citations"]
            )
        )

    def test_unsupported_claim_gets_fallback_response(self) -> None:
        audit = audit_final_output(
            "IBM announced Eagle in 2023.",
            [],
            current_date=date(2026, 6, 29),
        )

        self.assertFalse(audit["ok"])
        self.assertEqual(audit["unsupported_claims"], ["IBM announced Eagle in 2023."])
        self.assertEqual(audit["unsupported_claims_report"]["left_unsupported"], ["IBM announced Eagle in 2023."])
        self.assertEqual(audit["fallback_response"], "I do not have a verified source for that claim.")

    def test_stale_date_language_is_flagged(self) -> None:
        audit = audit_final_output(
            "As we are approaching the end of 2026, the latest guidance is changing.",
            [
                {
                    "title": "General background",
                    "author_or_organization": "Rook SLM",
                    "publication_date": "2026-06-29",
                    "url_or_document_path": "https://example.com/source",
                    "accessed_date": "2026-06-29",
                    "claim_supported": "General time wording check.",
                    "confidence_level": "high",
                    "source_type": "general_background",
                }
            ],
            current_date=date(2026, 6, 29),
        )

        self.assertFalse(audit["ok"])
        self.assertTrue(
            any(item["text"] == "approaching the end of 2026" for item in audit["time_sensitive_language"])
        )
        self.assertTrue(any(item["text"] == "latest" for item in audit["time_sensitive_language"]))

    def test_overclaiming_language_is_flagged(self) -> None:
        audit = audit_final_output(
            "The capability is deployed across production.",
            [
                {
                    "title": "Pilot note",
                    "author_or_organization": "Rook SLM",
                    "publication_date": "2026-06-29",
                    "url_or_document_path": "https://example.com/pilot",
                    "accessed_date": "2026-06-29",
                    "claim_supported": "The capability is in pilot.",
                    "confidence_level": "medium",
                }
            ],
            current_date=date(2026, 6, 29),
        )

        self.assertFalse(audit["ok"])
        self.assertIn({"source_language": "pilot", "draft_language": "deployed"}, audit["overclaiming"])


if __name__ == "__main__":
    unittest.main()
