"""Reject an assessment state that does not fit the config. Nothing is coerced."""

from __future__ import annotations

from digcon.domain.enums import AnswerKind, NotificationStatus, PropStatus, RiskLevel, Role
from digcon.domain.models import RISK_ID_RE, AssessmentState, ConfigBundle, QuestionSpec


class InvalidAssessment(ValueError):
    def __init__(self, errors: list[str]) -> None:
        super().__init__("; ".join(errors))
        self.errors = errors


def _codes(cfg: ConfigBundle, q: QuestionSpec) -> set[str]:
    if q.kind is AnswerKind.ROLE:
        return {r.value for r in Role if r is not Role.UNKNOWN}
    if q.kind is AnswerKind.RISK_RATING:
        return {r.value for r in RiskLevel}
    if q.kind is AnswerKind.NOTIFICATION:
        return {n.value for n in NotificationStatus}
    if q.kind in (AnswerKind.SINGLE, AnswerKind.MULTI):
        return {o.code for os_ in cfg.questions.option_sets if os_.id == q.option_set for o in os_.options}
    return set()


def check_state(cfg: ConfigBundle, state: AssessmentState) -> list[str]:
    errors: list[str] = []
    if state.workbook_version != cfg.version:
        errors.append(f"assessment is for {state.workbook_version}, config is {cfg.version}")
    questions = {q.id: q for q in cfg.questions.questions}
    elements = {e.id: e for r in cfg.rules.rules for e in r.encoding.elements}
    rules = {r.id for r in cfg.rules.rules}
    risks = {r.id for r in cfg.risks.risks}
    mitigations = {m.id for m in cfg.mitigations.mitigations}

    for qid, ans in state.answers.items():
        q = questions.get(qid)
        if q is None:
            errors.append(f"{qid}: unknown question")
            continue
        if ans.state is not None and ans.state not in q.states:
            errors.append(f"{qid}: state {ans.state.value} not offered (allowed {[s.value for s in q.states]})")
        if q.kind is AnswerKind.STATE:
            if ans.state is None:
                errors.append(f"{qid}: closed question needs a state")
            if ans.value is not None:
                errors.append(f"{qid}: closed question takes no value (use detail)")
            continue
        if ans.value is None:
            continue
        if q.kind is AnswerKind.MULTI:
            if not isinstance(ans.value, list):
                errors.append(f"{qid}: expects a list of options")
            else:
                bad = sorted(set(ans.value) - _codes(cfg, q))
                if bad:
                    errors.append(f"{qid}: unknown options {bad}")
        elif q.kind in (AnswerKind.SINGLE, AnswerKind.ROLE, AnswerKind.RISK_RATING, AnswerKind.NOTIFICATION):
            if not isinstance(ans.value, str) or ans.value not in _codes(cfg, q):
                errors.append(f"{qid}: {ans.value!r} is not one of {sorted(_codes(cfg, q))}")
        elif q.kind is AnswerKind.RISK_ROWS:
            values = ans.value if isinstance(ans.value, list) else None
            if values is not None and any(not RISK_ID_RE.match(v) or v not in risks for v in values):
                errors.append(f"{qid}: risk rows must be existing RISK-* ids")
        elif not isinstance(ans.value, str):
            errors.append(f"{qid}: expects text")

    for eid, ev in state.elements.items():
        spec = elements.get(eid)
        if spec is None:
            errors.append(f"{eid}: unknown rule element")
            continue
        if spec.source.value == "ANSWER":
            errors.append(f"{eid}: is read from {spec.binding.q}, it cannot be set by hand")
        want_prop = spec.state_enum == "PropStatus"
        if want_prop != isinstance(ev.state, PropStatus):
            errors.append(f"{eid}: expects a {spec.state_enum}")

    for rid in state.human_gates:
        if rid not in rules:
            errors.append(f"{rid}: human gate for an unknown rule")
    for rid in state.risks:
        if rid not in risks:
            errors.append(f"{rid}: unknown risk")
    for mid, rec in state.mitigations.items():
        if mid not in mitigations:
            errors.append(f"{mid}: unknown mitigation")
        errors += [f"{mid}: linked risk {r} unknown" for r in rec.linked_risk_ids if r not in risks]
        errors += [f"{mid}: linked rule {r} unknown" for r in rec.linked_rule_ids if r not in rules]
    errors += [f"SEP09: risk {r} unknown" for r in state.sep.effect_risk_ids if r not in risks]
    return errors
