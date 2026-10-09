from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from digcon.domain.enums import (
    UNRESOLVED_STATES,
    AnswerState,
    MitigationStatus,
    PropStatus,
    RiskLevel,
    Scale,
    SepEffect,
    Severity,
    label,
    parse,
)
from digcon.domain.models import (
    AllOf,
    Answer,
    AnswerIs,
    AssessmentState,
    AuditEvent,
    ElementUnresolved,
    HumanGateRecord,
    NotOf,
    RiskMatch,
    RuleEncoding,
)


# --- enums ------------------------------------------------------------------


@pytest.mark.parametrize(
    ("enum", "text", "member"),
    [
        (PropStatus, "NOT DEMONSTRATED", PropStatus.NOT_DEMONSTRATED),
        (PropStatus, "NOT_DEMONSTRATED", PropStatus.NOT_DEMONSTRATED),
        (MitigationStatus, "IMPLEMENTED — UNVERIFIED", MitigationStatus.IMPLEMENTED_UNVERIFIED),
        (SepEffect, "NEW ISSUE", SepEffect.NEW_ISSUE),
        (RiskLevel, "VERY LOW", RiskLevel.VERY_LOW),
        (AnswerState, "N/A", AnswerState.N_A),
    ],
)
def test_parse_accepts_code_and_workbook_label(enum, text, member):
    assert parse(enum, text) is member
    assert parse(enum, label(member)) is member


@pytest.mark.parametrize(
    ("enum", "text"),
    [
        (AnswerState, "To be verified"),
        (AnswerState, "yes"),
        (PropStatus, "PROPORTIONATE"),
        (MitigationStatus, "DONE"),
        (RiskLevel, "MEDIUM"),
    ],
)
def test_parse_rejects_values_outside_the_enum(enum, text):
    with pytest.raises(ValueError):
        parse(enum, text)


def test_enums_with_same_value_are_distinct():
    assert Scale.LOW != Severity.LOW
    assert Scale.LOW != "LOW"
    assert len({Scale.HIGH, Severity.HIGH, RiskLevel.HIGH}) == 3


def test_unresolved_states_never_include_no():
    assert AnswerState.NO not in UNRESOLVED_STATES
    assert UNRESOLVED_STATES == {AnswerState.UNKNOWN, AnswerState.N_A, AnswerState.NOT_OWNED}


# --- runtime models -----------------------------------------------------------


def test_answer_needs_state_or_value():
    with pytest.raises(ValidationError):
        Answer(question_id="C10")
    with pytest.raises(ValidationError):
        Answer(question_id="C10", value="   ")
    assert Answer(question_id="C10", value="Screening of job applicants").value


def test_unresolved_answer_cannot_carry_a_value():
    with pytest.raises(ValidationError):
        Answer(question_id="C10", state="UNKNOWN", value="something")
    assert Answer(question_id="C10", state="NOT_OWNED").state is AnswerState.NOT_OWNED


def test_answer_rejects_out_of_enum_state_and_bad_id():
    with pytest.raises(ValidationError):
        Answer(question_id="C46", state="To be verified")
    with pytest.raises(ValidationError):
        Answer(question_id="X99", state="YES")


def test_assessment_state_keys_must_match_ids():
    with pytest.raises(ValidationError):
        AssessmentState(
            assessment_id="a1",
            workbook_version="T17-v1.0.1",
            answers={"C46": Answer(question_id="C47", state="YES")},
        )


def test_completed_human_gate_needs_a_recorded_decision():
    with pytest.raises(ValidationError):
        HumanGateRecord(rule_id="HS07", gate="COMPLETED")
    rec = HumanGateRecord(rule_id="HS07", gate="COMPLETED", decision="Not prohibited", decided_by="Legal")
    assert rec.gate.value == "COMPLETED"


def _event(**overrides):
    base = dict(
        event_id="e1",
        assessment_id="a1",
        run_id="r1",
        workbook_version="T17-v1.0.1",
        timestamp=datetime(2026, 10, 7, tzinfo=timezone.utc),
        module="RULE",
        rule_id="SCR-01",
        evidence_refs=["C46"],
    )
    base.update(overrides)
    return AuditEvent(**base)


def test_audit_event_without_workbook_version_is_rejected():  # AUD-T01
    with pytest.raises(ValidationError):
        _event(workbook_version="")
    with pytest.raises(ValidationError):
        _event(timestamp=datetime(2026, 10, 7))  # naive timestamps are rejected


def test_rule_event_without_evidence_refs_is_an_audit_defect():  # AUD-T01
    assert _event().audit_defects() == []
    assert "rule event without evidence_refs" in _event(evidence_refs=[]).audit_defects()


def test_audit_event_rejects_unknown_module():
    with pytest.raises(ValidationError):
        _event(module="ENGINE")


# --- condition language ---------------------------------------------------------


def test_condition_union_picks_the_right_node():
    cond = AllOf.model_validate(
        {
            "all": [
                {"q": "FOLLOW", "is": ["YES"]},
                {"not": {"q": "C03", "is": ["YES"]}},
                {"element": "PROP-03.E1", "unresolved": True},
                {"risk": "ANY", "initial_at_least": "HIGH", "residual_missing": True},
            ]
        }
    )
    assert [type(c) for c in cond.all] == [AnswerIs, NotOf, ElementUnresolved, RiskMatch]


def test_condition_rejects_unknown_keys():
    with pytest.raises(ValidationError):
        AllOf.model_validate({"all": [{"q": "C46", "equals": "NO"}]})


def test_rule_encoding_shape():
    with pytest.raises(ValidationError):
        RuleEncoding(kind="STRUCTURED")  # no cases
    with pytest.raises(ValidationError):
        RuleEncoding(kind="SYSTEM", cases=[{"when": {"q": "C46", "is": ["NO"]}}])
    with pytest.raises(ValidationError):
        RuleEncoding(kind="STRUCTURED", cases=[{"when": {"q": "C46", "is": ["NO"]}}], gap={"q": "C46", "unresolved": True})
