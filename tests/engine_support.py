"""Build AssessmentState objects from the YAML fixtures (baseline + patch)."""

from __future__ import annotations

import copy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from digcon.config import default_config
from digcon.domain.enums import AnswerState
from digcon.domain.models import AssessmentState
from digcon.engine import RunContext, run_engine
from tools.export_workbook import StrictLoader

FIXTURES = Path(__file__).resolve().parent / "fixtures"
CTX = RunContext(run_id="RUN-TEST", timestamp=datetime(2026, 10, 12, 9, 0, tzinfo=timezone.utc))
_STATES = set(AnswerState.__members__)


def load_yaml(name: str) -> Any:
    with open(FIXTURES / name, encoding="utf-8") as fh:
        return yaml.load(fh, Loader=StrictLoader)


def _answer(qid: str, raw: Any) -> dict[str, Any]:
    if isinstance(raw, dict):
        return {"question_id": qid, **raw}
    if isinstance(raw, str) and raw in _STATES:
        return {"question_id": qid, "state": raw}
    return {"question_id": qid, "value": raw}


def _gate(rid: str, raw: Any) -> dict[str, Any]:
    if raw == "COMPLETED":
        return {"rule_id": rid, "gate": "COMPLETED", "decision": "Fixture legal determination", "decided_by": "Legal reviewer"}
    return {"rule_id": rid, **raw}


def build_state(patch: dict[str, Any] | None = None) -> AssessmentState:
    base = load_yaml("baseline.yaml")
    data = copy.deepcopy(base)
    patch = patch or {}
    for qid in patch.get("remove_answers", []):
        data["answers"].pop(qid)
    data["answers"].update(patch.get("answers", {}))
    data["elements"] = {**data.get("elements", {}), **patch.get("elements", {})}
    data["risks"] = {**data.get("risks", {}), **patch.get("risks", {})}
    return AssessmentState.model_validate(
        {
            "assessment_id": data["assessment_id"],
            "workbook_version": data["workbook_version"],
            "answers": {q: _answer(q, v) for q, v in data["answers"].items()},
            "elements": {e: {"element_id": e, "state": s} for e, s in data["elements"].items()},
            "human_gates": {r: _gate(r, g) for r, g in patch.get("human_gates", {}).items()},
            "risks": {r: {"risk_id": r, **v} for r, v in data["risks"].items()},
            "mitigations": {m: {"mitigation_id": m, **v} for m, v in patch.get("mitigations", {}).items()},
            "sep": patch.get("sep", {}),
        }
    )


def run(patch: dict[str, Any] | None = None, ctx: RunContext = CTX):
    return run_engine(default_config(), build_state(patch), ctx)
