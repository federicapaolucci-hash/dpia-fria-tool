"""Section 0: start a new assessment or resume a saved one."""

from __future__ import annotations

import streamlit as st

from digcon.domain.models import ConfigBundle
from digcon.engine import EngineResult

from .. import state


def _sync_id() -> None:
    value = (st.session_state.get("w.meta.id") or "").strip()
    if value:
        state.store()["assessment_id"] = value


def save_button(where: str) -> None:
    st.download_button(
        "Save progress (download JSON)",
        state.to_json(),
        file_name=f"{state.store()['assessment_id']}.json",
        mime="application/json",
        key=f"save.{where}",
        help="Keep this file: upload it in section 0 to resume the assessment later.",
    )


def render(cfg: ConfigBundle, result: EngineResult) -> None:
    st.markdown(
        "Work through the sections in the left menu, in order. Your answers stay in this browser session: "
        "**save progress as a JSON file** to resume later. Nothing is stored on a server."
    )
    col_new, col_resume = st.columns(2)
    with col_new:
        st.subheader("New assessment")
        state.seed("w.meta.id", state.store()["assessment_id"])
        st.text_input("Assessment name / ID", key="w.meta.id", on_change=_sync_id)
        if st.button("Clear and start a new assessment"):
            state.replace(state.empty_store(cfg))
            st.rerun()
    with col_resume:
        st.subheader("Resume an assessment")
        upload = st.file_uploader("Saved assessment (JSON)", type=["json"], label_visibility="collapsed")
        if upload is not None and st.button("Load this assessment"):
            try:
                state.replace(state.parse_upload(upload.getvalue()))
                st.success("Assessment loaded.")
                st.rerun()
            except ValueError as exc:
                st.error(f"Not a valid assessment file: {exc}")
    st.divider()
    save_button("start")
