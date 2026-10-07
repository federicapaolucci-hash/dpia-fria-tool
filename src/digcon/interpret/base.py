"""Contract between the deterministic engine and a future text interpreter (API).

The interpreter may only fill the same slots a person fills by hand: element
states of MANUAL rule elements, with evidence references. It never chooses an
outcome, never creates rules and never invents enum values (06_API).
"""

from __future__ import annotations

from typing import Protocol

from digcon.domain.models import AssessmentState, ElementEvaluation, RuleElementSpec


class Interpreter(Protocol):
    def evaluate(self, state: AssessmentState, elements: list[RuleElementSpec]) -> list[ElementEvaluation]:
        """Return element-level evaluations with evidence_refs; omit elements it cannot assess."""
        ...
