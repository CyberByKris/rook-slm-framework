#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
import re
from typing import Any


CONFIDENCE_LEVELS = {"high", "medium", "low", "unsupported"}
GUARDRAIL_PROMPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "governance"
    / "ACCURACY_GUARDRAILS.md"
)

TIME_SENSITIVE_PATTERNS = [
    r"\bthis year\b",
    r"\blast year\b",
    r"\bas of \d{4}\b",
    r"\brecently\b",
    r"\blatest\b",
    r"\bapproaching the end of (?:the year|\d{4})\b",
]

@dataclass(frozen=True)
class SourceMetadata:
    title: str
    author_or_organization: str
    publication_date: str
    url_or_document_path: str
    accessed_date: str
    claim_supported: str
    confidence_level: str
    citation_verified: bool
    source_type: str = "external"


def load_accuracy_guardrail_text() -> str:
    return GUARDRAIL_PROMPT_PATH.read_text(encoding="utf-8").strip()


def build_fact_checking_instructions(current_date: date | None = None) -> str:
    today = current_date or date.today()
    return f"{load_accuracy_guardrail_text()}\n\nCurrent date for time-sensitive wording: {today.isoformat()}."


def get_unverified_claim_message() -> str:
    match = re.search(r'say:\s+"([^"]+)"', load_accuracy_guardrail_text(), re.I)
    if not match:
        raise ValueError("Canonical guardrail file is missing the unverified-claim message.")
    return match.group(1)


def normalize_source_metadata(raw_sources: list[dict[str, Any]]) -> list[SourceMetadata]:
    sources: list[SourceMetadata] = []
    for raw in raw_sources:
        confidence = str(raw.get("confidence_level") or raw.get("confidence") or "").lower()
        if confidence not in CONFIDENCE_LEVELS:
            confidence = "unsupported"
        sources.append(
            SourceMetadata(
                title=str(raw.get("title") or "").strip(),
                author_or_organization=str(
                    raw.get("author_or_organization") or raw.get("organization") or raw.get("author") or ""
                ).strip(),
                publication_date=str(raw.get("publication_date") or raw.get("date") or "").strip(),
                url_or_document_path=str(
                    raw.get("url_or_document_path") or raw.get("url") or raw.get("document_path") or ""
                ).strip(),
                accessed_date=str(raw.get("accessed_date") or "").strip(),
                claim_supported=str(raw.get("claim_supported") or "").strip(),
                confidence_level=confidence,
                citation_verified=_coerce_bool(raw.get("citation_verified", raw.get("verified", True))),
                source_type=str(raw.get("source_type") or "external").strip().lower(),
            )
        )
    return sources


def audit_final_output(
    draft: str,
    raw_sources: list[dict[str, Any]],
    current_date: date | None = None,
    unsupported_claim_decisions: dict[str, str] | None = None,
) -> dict[str, Any]:
    today = current_date or date.today()
    sources = normalize_source_metadata(raw_sources)
    source_audits = [_audit_source(source) for source in sources]
    factual_claims = _extract_factual_claims(draft)
    unsupported_claims = _find_unsupported_claims(factual_claims, sources)
    overclaiming = _find_overclaiming(draft, sources)
    time_sensitive_language = _find_time_sensitive_language(draft, today)
    weak_citations = _find_weak_citations(source_audits, sources)
    unsupported_claims_report = _build_unsupported_claims_report(
        unsupported_claims,
        unsupported_claim_decisions or {},
    )
    needs_fallback = bool(factual_claims and not sources)

    return {
        "ok": not (
            unsupported_claims
            or overclaiming
            or time_sensitive_language
            or weak_citations
            or any(item["issues"] for item in source_audits)
        ),
        "current_date": today.isoformat(),
        "source_metadata": [asdict(source) for source in sources],
        "citation_audit": source_audits,
        "unsupported_claims": unsupported_claims,
        "unsupported_claims_report": unsupported_claims_report,
        "overclaiming": overclaiming,
        "time_sensitive_language": time_sensitive_language,
        "weak_citations": weak_citations,
        "fallback_response": get_unverified_claim_message() if needs_fallback else "",
        "source_note": (
            "Source grounding: This draft used verified sources where cited. Claims "
            "without adequate support were either removed or qualified."
        ),
    }


def _coerce_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() not in {"0", "false", "no", "unverified"}
    return bool(value)


def _audit_source(source: SourceMetadata) -> dict[str, Any]:
    issues: list[str] = []
    if not source.title:
        issues.append("missing title")
    if not source.author_or_organization:
        issues.append("missing author_or_organization")
    if not source.publication_date:
        issues.append("missing publication_date")
    if not source.url_or_document_path:
        issues.append("missing url_or_document_path")
    if not source.accessed_date:
        issues.append("missing accessed_date")
    if not source.claim_supported:
        issues.append("missing claim_supported")
    if source.confidence_level == "unsupported":
        issues.append("unsupported confidence_level")
    if source.confidence_level == "low":
        issues.append("low confidence_level")
    if not source.citation_verified:
        issues.append("unverified citation")
    if source.url_or_document_path and not _source_locator_is_plausible(source.url_or_document_path):
        issues.append("source locator is not a URL and local document path was not found")
    return {"source": source.title or source.url_or_document_path, "issues": issues}


def _source_locator_is_plausible(locator: str) -> bool:
    if re.match(r"^https?://[^\s]+$", locator):
        return True
    return Path(locator).expanduser().exists()


def _extract_factual_claims(draft: str) -> list[str]:
    claims: list[str] = []
    for sentence in re.split(r"(?<=[.!?])\s+", draft.strip()):
        cleaned = sentence.strip()
        if not cleaned or cleaned.endswith("?"):
            continue
        if re.search(r"\b(I think|I believe|maybe|perhaps|opinion)\b", cleaned, re.I):
            continue
        if re.search(r"\b(is|are|was|were|has|have|announced|reported|shows|uses|deployed|will)\b", cleaned, re.I):
            claims.append(cleaned)
    return claims


def _find_unsupported_claims(claims: list[str], sources: list[SourceMetadata]) -> list[str]:
    if not claims:
        return []
    supported_fragments = [
        source.claim_supported.lower()
        for source in sources
        if source.claim_supported and source.confidence_level != "unsupported"
    ]
    if any(source.source_type == "general_background" for source in sources):
        return []

    unsupported: list[str] = []
    for claim in claims:
        normalized = claim.lower()
        if not any(_claim_matches_source(normalized, fragment) for fragment in supported_fragments):
            unsupported.append(claim)
    return unsupported


def _build_unsupported_claims_report(
    unsupported_claims: list[str],
    decisions: dict[str, str],
) -> dict[str, list[str]]:
    report = {
        "removed": [],
        "qualified": [],
        "left_unsupported": [],
    }
    for claim in unsupported_claims:
        decision = decisions.get(claim, "left_unsupported")
        if decision not in report:
            decision = "left_unsupported"
        report[decision].append(claim)
    return report


def _find_weak_citations(
    source_audits: list[dict[str, Any]],
    sources: list[SourceMetadata],
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    by_name = {source.title or source.url_or_document_path: source for source in sources}
    for audit in source_audits:
        source = by_name.get(str(audit["source"]))
        issues = list(audit["issues"])
        if source and source.confidence_level in {"low", "unsupported"}:
            issue = f"{source.confidence_level} confidence citation"
            if issue not in issues:
                issues.append(issue)
        if issues:
            findings.append({"source": audit["source"], "issues": issues})
    return findings


def _claim_matches_source(claim: str, source_claim: str) -> bool:
    if not source_claim:
        return False
    if source_claim in claim or claim in source_claim:
        return True
    claim_terms = set(re.findall(r"[a-z0-9]{4,}", claim))
    source_terms = set(re.findall(r"[a-z0-9]{4,}", source_claim))
    if not claim_terms:
        return False
    return len(claim_terms & source_terms) / len(claim_terms) >= 0.75


def _find_overclaiming(draft: str, sources: list[SourceMetadata]) -> list[dict[str, str]]:
    lowered_draft = draft.lower()
    source_text = " ".join(source.claim_supported.lower() for source in sources)
    findings: list[dict[str, str]] = []
    for weak, strong in _load_overclaiming_pairs():
        if weak in source_text and strong in lowered_draft:
            findings.append({"source_language": weak, "draft_language": strong})
    return findings


def _load_overclaiming_pairs() -> list[tuple[str, str]]:
    text = load_accuracy_guardrail_text()
    return [
        (weak.lower(), strong.lower())
        for weak, strong in re.findall(r'"([^"]+)"\s+into\s+"([^"]+)"', text)
    ]


def _find_time_sensitive_language(draft: str, today: date) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for pattern in TIME_SENSITIVE_PATTERNS:
        for match in re.finditer(pattern, draft, re.I):
            text = match.group(0)
            issue = "verify against current date before final output"
            if re.search(r"approaching the end of (?:the year|" + str(today.year) + r")", text, re.I):
                issue = f"not supported by current date {today.isoformat()}"
            findings.append({"text": text, "issue": issue})
    return findings


__all__ = [
    "SourceMetadata",
    "audit_final_output",
    "build_fact_checking_instructions",
    "get_unverified_claim_message",
    "load_accuracy_guardrail_text",
    "normalize_source_metadata",
]
