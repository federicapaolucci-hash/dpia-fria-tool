"""No-op interpreter: every MANUAL element stays as the person left it."""

from __future__ import annotations

from digcon.domain.models import AssessmentState, ElementEvaluation, RuleElementSpec


class StubInterpreter:
    def evaluate(self, state: AssessmentState, elements: list[RuleElementSpec]) -> list[ElementEvaluation]:
        return []
