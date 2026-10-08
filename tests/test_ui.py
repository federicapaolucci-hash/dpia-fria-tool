"""The Streamlit app, driven through its widgets (streamlit.testing.AppTest)."""

import json
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from digcon.domain.models import AssessmentState
from digcon.ui import state as ui_state
from engine_support import build_state

TIMEOUT = 60
APP = str(Path(__file__).resolve().parents[1] / "streamlit_app.py")


def app(patch=None) -> AppTest:
    at = AppTest.from_file(APP, default_timeout=TIMEOUT)
    if patch is not None:
        at.session_state[ui_state.STORE] = build_state(patch).model_dump(mode="json")
    return at.run()


def outcome(at: AppTest) -> str:
    return next(m.value for m in at.metric if m.label == "Recommended outcome")


def no_errors(at: AppTest) -> None:
    assert not at.exception, [e.message for e in at.exception]
    assert not at.error, [e.value for e in at.error]


def test_empty_app_renders_with_header_and_disclaimer():
    at = app()
    no_errors(at)
    assert at.title[0].value == "DPIA-based Fundamental Rights Assessment Tool"
    assert "Research prototype" in at.info[0].value
    assert outcome(at) == "O4"  # nothing answered yet: evidence gaps


def test_baseline_assessment_shows_o1():
    at = app({})
    no_errors(at)
    assert outcome(at) == "O1"


def test_widget_answer_updates_outcome_and_opens_hard_stop():
    at = app({})
    at.radio(key="w.C46").set_value("NO").run()
    no_errors(at)
    assert at.session_state[ui_state.STORE]["answers"]["C46"]["state"] == "NO"
    assert outcome(at) == "O4"  # HS05 opened by the signal, not evaluated yet
    # The lawyer excludes HS05 from the UI.
    at.selectbox(key="w.HS05.E1").set_value("MET").run()
    at.selectbox(key="w.HS05.E2").set_value("NOT_MET").run()
    at.checkbox(key="w.gate.HS05").check().run()
    at.text_input(key="w.gate.HS05.decision").input("Oversight can be introduced").run()
    at.text_input(key="w.gate.HS05.by").input("F. Paolucci").run()
    no_errors(at)
    assert outcome(at) == "O3"  # SCR-01 remediation still open


def test_unknown_status_on_text_question_is_a_gap_not_a_no():
    at = app({})
    at.selectbox(key="w.C11.status").set_value("UNKNOWN").run()
    no_errors(at)
    assert at.session_state[ui_state.STORE]["answers"]["C11"]["state"] == "UNKNOWN"
    assert outcome(at) == "O4"


def test_hidden_answers_survive_in_the_store():
    at = app({"answers": {"FOLLOW": "YES", "C05": "PROVIDER", "P01": "YES"}})
    at.radio(key="w.FOLLOW").set_value("NO").run()  # provider add-on closes
    at.radio(key="w.FOLLOW").set_value("YES").run()  # and reopens
    no_errors(at)
    assert at.session_state[ui_state.STORE]["answers"]["P01"]["state"] == "YES"
    assert at.radio(key="w.P01").value == "YES"


@pytest.mark.parametrize(
    ("role", "extra"),
    [
        ("PROVIDER", {}),
        ("DEPLOYER", {"D00": "YES"}),
        ("JOINT", {"D00": "YES"}),
    ],
)
def test_complete_assessment_per_role_from_the_ui(role, extra):
    """Acceptance check: one full assessment per role reaches an outcome with an audit trail."""
    at = app({"answers": {"FOLLOW": "YES", **extra}})
    at.selectbox(key="w.C05").set_value(role).run()
    if role in ("PROVIDER", "JOINT"):
        for q, v in {"P01": "YES", "P02": "NO", "P03": "YES", "P04": "YES", "P05": "NO",
                     "P06": "YES", "P07": "YES", "P08": "YES", "P09": "YES", "P10": "YES"}.items():
            at.radio(key=f"w.{q}").set_value(v).run()
        at.checkbox(key="w.gate.RMS-9I").check().run()
        at.text_input(key="w.gate.RMS-9I.decision").input("Residual risk acceptable").run()
        at.text_input(key="w.gate.RMS-9I.by").input("Provider governance board").run()
    if role in ("DEPLOYER", "JOINT"):
        texts = {
            "D01": "Recruiters use the ranking when shortlisting",
            "D02": "12-month pilot, daily use",
            "D05": "Every list reviewed by a recruiter",
            "D06": "Complaint channel, HR lead owner",
            "D09": "DPIA-2026-04",
        }
        for q, v in texts.items():
            at.text_area(key=f"w.{q}.value").input(v).run()
        at.multiselect(key="w.D03.value").set_value(["WORKERS_CANDIDATES"]).run()
        at.multiselect(key="w.D04.value").set_value(["RISK-21"]).run()
        at.radio(key="w.D07").set_value("NO").run()
        at.radio(key="w.D08").set_value("NO").run()
        at.selectbox(key="w.D10").set_value("NOT_REQUIRED").run()
        for el in ("FRIA-27A.E1", "FRIA-27D.E1", "FRIA-27E.E1", "FRIA-27F.E1"):
            at.selectbox(key=f"w.{el}").set_value("NOT_MET").run()
    no_errors(at)
    assert outcome(at) == "O1"
    audit = [e for e in at.expander if e.label.startswith("Audit trail")]
    assert audit and "(0 events)" not in audit[0].label


def test_state_json_roundtrip():
    at = app({"answers": {"C46": "NO"}})
    exported = json.loads(ui_state.AssessmentState.model_validate(at.session_state[ui_state.STORE]).model_dump_json())
    again = AssessmentState.model_validate(exported)
    assert again.answers["C46"].state.value == "NO"
    assert ui_state.parse_upload(json.dumps(exported).encode("utf-8")) == again.model_dump(mode="json")
