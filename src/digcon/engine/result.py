"""What one engine run returns. Immutable, JSON-serialisable."""

from __future__ import annotations

from pydantic import AwareDatetime, BaseModel, ConfigDict

from digcon.domain.enums import (
    EngineFlag,
    HumanGate,
    Outcome,
    PropStatus,
    RiskLevel,
    RuleEffect,
    RuleElementState,
    SepDecision,
    Severity,
)
from digcon.domain.models import AuditEvent


class _Result(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class RunContext(_Result):
    """Identifiers and clock come from outside: the engine never reads them itself."""

    run_id: str
    timestamp: AwareDatetime


class RuleResult(_Result):
    rule_id: str
    fired: bool
    case: int | None = None  # 1-based index of the matched case
    effects: list[RuleEffect] = []
    status: PropStatus | None = None
    gap: bool = False
    gap_effects: list[RuleEffect] = []
    review: bool = False
    human_gate: HumanGate = HumanGate.NO
    input_ids: list[str] = []
    evidence_refs: list[str] = []
    linked_risk_ids: list[str] = []
    linked_mitigation_ids: list[str] = []

    @property
    def applied(self) -> bool:
        return self.fired or self.gap or self.review


class HardStopResult(_Result):
    hs_id: str
    opened: bool
    state: RuleElementState
    elements: dict[str, RuleElementState]
    gate: HumanGate
    awaiting_legal_review: bool  # all elements MET, gate not completed (AS-006 / AS-029)


class RiskResult(_Result):
    risk_id: str
    severity: Severity | None
    initial: RiskLevel | None
    residual_severity: Severity | None
    residual: RiskLevel | None  # empty until a verified reassessment (never 0, never assumed)
    to_reassess: bool  # stakeholder evidence modified / contradicted it (SEP-03)


class Finding(_Result):
    """One line of the report: a gap, a verification request, an open action, a pending review."""

    rule_id: str
    message: str
    ids: list[str] = []


class EngineResult(_Result):
    assessment_id: str
    run_id: str
    workbook_version: str
    timestamp: AwareDatetime
    outcome: Outcome
    outcome_rule: str
    high_risk: str | None
    role: str | None
    routing_suspended: bool
    provider_module: bool
    deployer_module: bool
    visible_questions: list[str]
    flags: dict[EngineFlag, bool]
    rules: dict[str, RuleResult]
    hard_stops: dict[str, HardStopResult]
    prop_statuses: dict[str, PropStatus]
    risks: dict[str, RiskResult]
    sep_status: SepDecision | None
    evidence_gaps: list[Finding]
    verification_requests: list[Finding]
    open_remediations: list[Finding]
    open_conditions: list[Finding]
    pending_reviews: list[Finding]
    warnings: list[str]
    audit_trail: list[AuditEvent]
    audit_defects: list[str]

    @property
    def closed(self) -> bool:
        """A run with audit defects is not a reproducible closure (AUD-T01)."""
        return not self.audit_defects
