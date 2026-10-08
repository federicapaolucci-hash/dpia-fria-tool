"""The 44 fixtures of 07_TEST_FIXTURES plus the engine invariants of the workbook."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from digcon.config import default_config
from digcon.domain.enums import Outcome, RuleElementState
from digcon.domain.models import AuditEvent
from digcon.engine import InvalidAssessment, RunContext, run_engine
from digcon.engine.calibration import severity
from engine_support import CTX, build_state, load_yaml, run

FIXTURE_FILES = ["outcome.yaml", "hard_stops.yaml", "calibration.yaml", "proportionality.yaml", "process.yaml"]
ALL_FIXTURES = [f for name in FIXTURE_FILES for f in load_yaml(name)]
ENGINE_FIXTURES = [f for f in ALL_FIXTURES if "special" not in f]


def test_all_44_workbook_fixtures_are_translated():
    ids = [f["id"] for f in ALL_FIXTURES]
    assert len(ids) == len(set(ids)) == 44


@pytest.mark.parametrize("fx", ENGINE_FIXTURES, ids=lambda f: f["id"])
def test_workbook_fixture(fx):
    r = run(fx.get("patch"))
    exp = fx["expect"]
    if "outcome" in exp:
        assert r.outcome.value == exp["outcome"], _explain(r)
    if "not_outcome" in exp:
        assert r.outcome.value != exp["not_outcome"], _explain(r)
    for hs, state in exp.get("hs", {}).items():
        assert r.hard_stops[hs].state.value == state, r.hard_stops[hs]
    if "hs_opened" in exp:
        assert sorted(h for h, v in r.hard_stops.items() if v.opened) == sorted(exp["hs_opened"])
    for rid, status in exp.get("prop", {}).items():
        assert r.prop_statuses.get(rid) is not None and r.prop_statuses[rid].value == status, r.rules[rid]
    for rid, effects in exp.get("prop_effects", {}).items():
        assert {e.value for e in r.rules[rid].effects} >= set(effects), r.rules[rid]
    for rid, levels in exp.get("risk", {}).items():
        rr = r.risks[rid]
        for stage, level in levels.items():
            got = getattr(rr, stage)
            assert (got.value if got else None) == level, (rid, stage, rr)
    for mid, status in exp.get("mitigation_status", {}).items():
        assert build_state(fx["patch"]).mitigations[mid].status.value == status
    for flag, value in exp.get("flags", {}).items():
        assert {f.value: v for f, v in r.flags.items()}[flag] is value
    if "sep_status" in exp:
        assert r.sep_status is not None and r.sep_status.value == exp["sep_status"]
    for rid in exp.get("fired", []):
        assert r.rules[rid].fired, rid
    if "reassess" in exp:
        assert sorted(k for k, v in r.risks.items() if v.to_reassess) == exp["reassess"]
    if "routing_suspended" in exp:
        assert r.routing_suspended is exp["routing_suspended"]
    assert r.closed, r.audit_defects


def _explain(r) -> str:
    return (
        f"{r.outcome.value} via {r.outcome_rule}; gaps={[(f.rule_id, f.ids) for f in r.evidence_gaps]} "
        f"remediations={[f.rule_id for f in r.open_remediations]} conditions={[f.ids for f in r.open_conditions]}"
    )


# --- AUD-T01 / AUD-T02 ------------------------------------------------------------


def test_aud_t01_incomplete_event_is_not_a_closure():
    event = run().audit_trail[-1].model_dump()
    with pytest.raises(ValidationError):
        AuditEvent.model_validate({**event, "workbook_version": ""})
    stripped = AuditEvent.model_validate({**event, "evidence_refs": []})
    assert "rule event without evidence_refs" in stripped.audit_defects()


def test_aud_t02_same_state_same_result():
    a = run({"answers": {"C46": "NO"}})
    b = run({"answers": {"C46": "NO"}})
    assert a.model_dump() == b.model_dump()
    other = run({"answers": {"C46": "NO"}}, RunContext(run_id="RUN-OTHER", timestamp=datetime(2027, 1, 1, tzinfo=timezone.utc)))
    strip = {"run_id", "timestamp", "audit_trail"}
    assert a.model_dump(exclude=strip) == other.model_dump(exclude=strip)
    assert [e.engine_output for e in a.audit_trail] == [e.engine_output for e in other.audit_trail]


def test_every_applied_rule_has_a_complete_audit_event():
    r = run({"answers": {"C46": "NO", "C20": "UNKNOWN"}, "elements": {"PROP-03.E1": "MET"}})
    applied = {rid for rid, rr in r.rules.items() if rr.applied and not rid.startswith("OUT")}
    events = {e.rule_id: e for e in r.audit_trail if e.rule_id}
    assert applied <= set(events)
    for e in r.audit_trail:
        assert e.workbook_version == "T17-REV2" and e.evidence_refs, e
    assert r.audit_trail[-1].module.value == "OUTCOME" and r.audit_trail[-1].engine_output.startswith(r.outcome.value)


# --- invariants -----------------------------------------------------------------------


def test_baseline_is_o1():
    r = run()
    assert r.outcome is Outcome.O1 and r.evidence_gaps == [] and r.open_remediations == []


@pytest.mark.parametrize("state", ["UNKNOWN", "N_A", "NOT_OWNED"])
def test_unresolved_is_never_no(state):
    # C46 = NO is a HIGH red flag + remediation; an unresolved C46 must not behave like NO.
    r = run({"answers": {"C46": state}})
    assert not r.rules["SCR-01"].fired
    assert not r.hard_stops["HS05"].opened
    assert r.outcome is not Outcome.O5


def test_n_a_is_a_verification_request_not_a_gap():
    r = run({"answers": {"C15": "N_A"}})
    assert r.outcome is Outcome.O1
    assert any("C15" in f.ids for f in r.verification_requests)


def test_unknown_and_missing_are_material_gaps():
    assert run({"answers": {"C21": "NOT_OWNED"}}).outcome is Outcome.O4
    assert run({"remove_answers": ["C21"]}).outcome is Outcome.O4


def test_high_risk_alone_is_not_o5():
    r = run({"risks": {"RISK-21": {"scale": "VERY_HIGH", "scope": "SYSTEMIC", "reversibility": "IRREVERSIBLE", "probability": "VERY_LIKELY"}}})
    assert r.risks["RISK-21"].initial.value == "VERY_HIGH"
    assert r.outcome is not Outcome.O5


def test_uncertain_element_never_counts_as_met():
    r = run({"elements": {"HS05.E1": "MET", "HS05.E2": "MET", "HS05.E3": "UNCERTAIN"}, "human_gates": {"HS05": "COMPLETED"}})
    assert r.hard_stops["HS05"].state is RuleElementState.UNCERTAIN
    assert r.outcome is Outcome.O4


def test_hard_stop_without_completed_legal_gate_is_not_o5():
    r = run({"elements": {"HS01.E1": "MET", "HS01.E2": "MET", "HS01.E3": "MET"}})
    assert r.hard_stops["HS01"].awaiting_legal_review
    assert r.outcome is Outcome.O4
    assert any(f.rule_id == "HS01" and "awaiting legal review" in f.message for f in r.pending_reviews)


def test_hs08_mitigation_element_needs_a_verified_mitigation():
    r = run({"elements": {"HS08.E1": "MET", "HS08.E2": "MET", "HS08.E3": "MET"}, "human_gates": {"HS08": "COMPLETED"}})
    assert r.hard_stops["HS08"].elements["HS08.E2"] is RuleElementState.UNCERTAIN
    assert r.outcome is not Outcome.O5
    assert any("AS-018" in w for w in r.warnings)


def test_mitigation_cannot_clear_a_met_hard_stop():
    r = run(
        {
            "answers": {"C03": "YES"},
            "elements": {"HS07.E1": "MET"},
            "human_gates": {"HS07": "COMPLETED"},
            "mitigations": {"MIT-009": {"activated": True, "status": "VERIFIED_EFFECTIVE", "linked_rule_ids": ["HS07"], "evidence_refs": ["doc:x"]}},
        }
    )
    assert r.outcome is Outcome.O5


def test_no_prop_rule_produces_o5_or_opens_hs_by_itself():
    r = run({"elements": {f"PROP-0{i}.E1": "MET" for i in (2, 3, 4, 5, 6)} | {"PROP-07.E1": "MET"}})
    assert r.outcome is not Outcome.O5
    assert not any(h.opened for h in r.hard_stops.values())


def test_proposed_mitigation_does_not_reduce_residual_risk():
    r = run(
        {
            "risks": {"RISK-21": {"scale": "HIGH", "scope": "WIDE", "reversibility": "PARTLY_REVERSIBLE", "probability": "LIKELY",
                                  "residual_scale": "LOW", "residual_scope": "LIMITED", "residual_reversibility": "REVERSIBLE", "residual_probability": "RARE"}},
            "mitigations": {"MIT-038": {"activated": True, "status": "PROPOSED"}},
        }
    )
    assert r.risks["RISK-21"].residual is None
    assert any("residual dimensions ignored" in w for w in r.warnings)


def test_verified_mitigation_does_not_bypass_other_conditions():  # MIT-T02 negative control
    r = run({"answers": {"C20": "UNKNOWN"}, "mitigations": {"MIT-009": {"activated": True, "status": "VERIFIED_EFFECTIVE", "evidence_refs": ["doc:x"]}}})
    assert r.outcome is Outcome.O4


def test_red_flag_opens_hs_then_remediation_then_condition():
    # C46 = NO: HS05 screening opens (AS-017) -> must be evaluated -> O4 until it is.
    r = run({"answers": {"C46": "NO"}})
    assert r.hard_stops["HS05"].opened and r.outcome is Outcome.O4
    # Lawyer excludes HS05: SCR-01 remediation stays open -> O3.
    hs05_excluded = {
        "answers": {"C46": "NO"},
        "elements": {"HS05.E1": "MET", "HS05.E2": "NOT_MET", "HS05.E3": "NOT_MET"},
        "human_gates": {"HS05": "COMPLETED"},
    }
    r = run(hs05_excluded)
    assert r.hard_stops["HS05"].state is RuleElementState.NOT_MET and r.outcome is Outcome.O3
    # A linked, verified mitigation closes the remediation; MIT-002 is a continuous condition -> O2.
    linked = {"MIT-002": {"activated": True, "status": "VERIFIED_EFFECTIVE", "linked_rule_ids": ["SCR-01"], "evidence_refs": ["doc:x"]}}
    r = run({**hs05_excluded, "mitigations": linked})
    assert not r.open_remediations
    assert r.outcome is Outcome.O2


def test_unevaluated_reviewer_checks_do_not_block():
    state = build_state()
    state.elements = {}
    r = run_engine(default_config(), state, CTX)
    assert r.outcome is Outcome.O1
    assert {f.rule_id for f in r.verification_requests} >= {"QUAL-01", "PROP-05", "REM-01"}


def test_pending_non_hs_legal_review_is_a_warning_only():
    r = run({"answers": {"C35": "YES"}})  # SCR-03: human gate REQUIRED
    assert r.rules["SCR-03"].fired
    assert any(f.rule_id == "SCR-03" for f in r.pending_reviews)
    assert r.outcome is Outcome.O1


# --- routing --------------------------------------------------------------------------


def _routing(patch):
    r = run(patch)
    return r.provider_module, r.deployer_module, set(r.visible_questions)


def test_routing_not_high_risk_is_core_only():
    provider, deployer, visible = _routing({})
    assert (provider, deployer) == (False, False)
    assert not any(q.startswith(("P", "D")) for q in visible)


def test_routing_provider():
    provider, deployer, visible = _routing({"answers": {"FOLLOW": "YES", "C05": "PROVIDER"}})
    assert (provider, deployer) == (True, False)
    assert {f"P{i:02d}" for i in range(1, 11)} <= visible and "D00" not in visible


def test_routing_deployer_needs_article_27():
    _, deployer, visible = _routing({"answers": {"FOLLOW": "YES"}})
    assert not deployer and "D00" in visible and "D01" not in visible
    _, deployer, visible = _routing({"answers": {"FOLLOW": "YES", "D00": "YES"}})
    assert deployer and {f"D{i:02d}" for i in range(0, 11)} <= visible


def test_routing_joint_opens_both_add_ons():
    provider, deployer, _ = _routing({"answers": {"FOLLOW": "YES", "C05": "JOINT", "D00": "YES"}})
    assert provider and deployer


def test_routing_unknown_role_or_classification_opens_nothing():
    for patch in ({"FOLLOW": "UNKNOWN", "C05": "PROVIDER"}, {"FOLLOW": "YES", "C05": "UNKNOWN"}):
        r = run({"answers": patch})
        assert not r.provider_module and not r.deployer_module
        assert r.outcome is Outcome.O4


def test_c03_yes_suspends_routing_until_hs07_not_met():
    r = run({"answers": {"FOLLOW": "YES", "C05": "JOINT", "D00": "YES", "C03": "YES"}})
    assert r.routing_suspended and not r.provider_module and not r.deployer_module
    assert r.hard_stops["HS07"].opened and r.outcome is Outcome.O4
    r = run(
        {
            "answers": {"FOLLOW": "YES", "C05": "JOINT", "D00": "YES", "C03": "YES"},
            "elements": {"HS07.E1": "NOT_MET"},
            "human_gates": {"HS07": "COMPLETED"},
        }
    )
    assert not r.routing_suspended and r.provider_module and r.deployer_module


def test_hidden_questions_are_not_gaps():
    r = run({"answers": {"FOLLOW": "YES", "C05": "PROVIDER"}})  # P01–P10 visible, unanswered
    assert r.outcome is Outcome.O4
    assert all(q.startswith("P") for f in r.evidence_gaps if f.rule_id == "EG-01" for q in f.ids)


# --- calibration and input validation ------------------------------------------------


def test_severity_is_the_max_dimension():
    from digcon.domain.enums import Reversibility, Scale, Scope, Severity

    assert severity(Scale.LOW, Scope.SYSTEMIC, Reversibility.REVERSIBLE) is Severity.VERY_HIGH
    assert severity(Scale.MEDIUM, Scope.LIMITED, Reversibility.PARTLY_REVERSIBLE) is Severity.MEDIUM


def test_missing_dimension_gives_no_level():
    r = run({"risks": {"RISK-21": {"scale": "HIGH", "scope": "WIDE", "reversibility": "IRREVERSIBLE"}}})
    assert r.risks["RISK-21"].initial is None


@pytest.mark.parametrize(
    "patch",
    [
        {"answers": {"C46": "PARTLY"}},
        {"answers": {"C38": ["SCORING_RANKING", "MIND_READING"]}},
        {"answers": {"C05": "REGULATOR"}},
        {"answers": {"C03": "N_A"}},  # C03 offers YES / NO / UNKNOWN only
        {"elements": {"HS02.E1": "MET"}},  # bound to C14, not settable
        {"mitigations": {"MIT-999": {"activated": True}}},
    ],
)
def test_out_of_enum_input_is_rejected(patch):
    with pytest.raises((InvalidAssessment, ValidationError)):
        run(patch)


# --- one complete assessment per role ------------------------------------------------

PROVIDER_ANSWERS = {
    "FOLLOW": "YES", "P01": "YES", "P02": "NO", "P03": "YES", "P04": "YES", "P05": "NO",
    "P06": "YES", "P07": "YES", "P08": "YES", "P09": "YES", "P10": "YES",
}
DEPLOYER_ANSWERS = {
    "FOLLOW": "YES", "D00": "YES",
    "D01": "Recruiters use the ranking as one input when shortlisting, as per instructions v2.1",
    "D02": "12-month pilot, daily use during open recruitment campaigns",
    "D03": ["WORKERS_CANDIDATES", "PERSONS_WITH_DISABILITIES"],
    "D04": ["RISK-21"],
    "D05": "Recruiter reviews every ranked list; override logged; escalation to HR lead",
    "D06": "Complaint channel via HR mailbox, review within 10 days, owner: HR lead",
    "D07": "NO", "D08": "NO", "D09": "DPIA-2026-04 sections 2-5", "D10": "NOT_REQUIRED",
}
FRIA_CHECKS = {"FRIA-27A.E1": "NOT_MET", "FRIA-27D.E1": "NOT_MET", "FRIA-27E.E1": "NOT_MET", "FRIA-27F.E1": "NOT_MET"}


@pytest.mark.parametrize(
    ("role", "answers", "elements", "provider", "deployer"),
    [
        ("PROVIDER", PROVIDER_ANSWERS, {}, True, False),
        ("DEPLOYER", DEPLOYER_ANSWERS, FRIA_CHECKS, False, True),
        ("JOINT", PROVIDER_ANSWERS | DEPLOYER_ANSWERS, FRIA_CHECKS, True, True),
    ],
)
def test_complete_assessment_per_role(role, answers, elements, provider, deployer):
    r = run({"answers": {**answers, "C05": role}, "elements": elements, "human_gates": {"RMS-9I": "COMPLETED"}})
    assert (r.provider_module, r.deployer_module) == (provider, deployer)
    assert r.evidence_gaps == [], r.evidence_gaps
    assert r.outcome is Outcome.O1
    assert r.closed
