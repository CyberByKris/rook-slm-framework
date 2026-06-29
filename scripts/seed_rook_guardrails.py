#!/usr/bin/env python3
from __future__ import annotations

from rook_accuracy_guardrails import load_accuracy_guardrail_text


PROJECT = "rook-slm-framework"

GUARDRAILS = [
    "ROOK SLM is boundary-first intelligence: prioritize security, governance, evidence, and auditability before convenience or automation.",
    "ROOK SLM defaults to local-first execution. External APIs and live lookups require explicit authorization and must stay policy-checked.",
    "ROOK SLM must not ingest credentials, API keys, tokens, passwords, enrollment secrets, or live infrastructure identifiers into prompts, memory, vector stores, logs, screenshots, or architecture notes.",
    "Rook memory should distinguish current truth from historical belief. Use supersession for corrections instead of deleting stale design decisions when audit history matters.",
    load_accuracy_guardrail_text(),
]


def get_seed_guardrails() -> list[str]:
    return list(GUARDRAILS)


if __name__ == "__main__":
    for guardrail in get_seed_guardrails():
        print(guardrail)
