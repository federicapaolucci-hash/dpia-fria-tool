"""The assessment lives in one store in st.session_state, in AssessmentState JSON shape.

Widgets have keys ``w.<...>``; they are seeded from the store when missing and write back
through callbacks. Streamlit drops the state of widgets that are not rendered (hidden
questions, other add-ons): the store keeps the answers anyway.
"""

from __future__ import annotations

import json
from typing import Any

import streamlit as st

from digcon.domain.models import AssessmentState, ConfigBundle

STORE = "assessment"
WIDGET_PREFIX = "w."


def empty_store(cfg: ConfigBundle) -> dict[str, Any]:
    return AssessmentState(assessment_id="new-assessment", workbook_version=cfg.version).model_dump(mode="json")


def store() -> dict[str, Any]:
    return st.session_state[STORE]


def init(cfg: ConfigBundle) -> None:
    if STORE not in st.session_state:
        st.session_state[STORE] = empty_store(cfg)


def assessment() -> AssessmentState:
    return AssessmentState.model_validate(store())


def seed(key: str, default: Any) -> None:
    """Give a widget its value from the store the first time it is rendered."""
    if key not in st.session_state:
        st.session_state[key] = default


def replace(data: dict[str, Any]) -> None:
    """Load a whole assessment (resume from JSON) and reset every widget."""
    st.session_state[STORE] = AssessmentState.model_validate(data).model_dump(mode="json")
    for key in [k for k in st.session_state if str(k).startswith(WIDGET_PREFIX)]:
        del st.session_state[key]


def to_json() -> str:
    return json.dumps(assessment().model_dump(mode="json"), ensure_ascii=False, indent=2)


def parse_upload(raw: bytes) -> dict[str, Any]:
    data = json.loads(raw.decode("utf-8"))
    return AssessmentState.model_validate(data).model_dump(mode="json")


def set_or_remove(section: str, key: str, value: dict[str, Any] | None) -> None:
    bucket = store()[section]
    if value is None:
        bucket.pop(key, None)
    else:
        bucket[key] = value
