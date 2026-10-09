"""Section 1.0: start a new assessment or resume a saved one."""

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
        help="Keep this file: upload it in section 1.0 to resume the assessment later.",
    )


def render(cfg: ConfigBundle, result: EngineResult) -> None:
    st.markdown(
        "Work through the four steps in the left menu, in order: first the **core**, then the **add-ons** the "
        "scoping opens, then the **transversal modules**, then the **outcome**.\n\n"
        "Answers are kept only in this browser session and are **lost if you reload or close the page**. "
        "Save progress as a JSON file to resume later: no copy is kept for you."
    )
    col_new, col_resume = st.columns(2)
    with col_new:
        st.subheader("New assessment")
        state.seed("w.meta.id", state.store()["assessment_id"])
        st.text_input("Assessment name", key="w.meta.id", on_change=_sync_id,
                      help="Used as the file name when you save progress.")
        if st.button("Discard answers and start over",
                     help="Removes every answer in this session. Save progress first if you may need them."):
            state.replace(state.empty_store(cfg))
            st.rerun()
    with col_resume:
        st.subheader("Resume an assessment")
        upload = st.file_uploader("Saved assessment (JSON)", type=["json"], label_visibility="collapsed")
        if upload is not None and st.button("Load this assessment", help="Replaces the answers in this session."):
            try:
                state.replace(state.parse_upload(upload.getvalue()))
                st.rerun()
            except ValueError as exc:
                st.error("This file could not be loaded. Choose a JSON file saved from this tool with "
                         "“Save progress”, unchanged.")
                with st.expander("Technical details"):
                    st.code(str(exc), language=None)
    st.divider()
    save_button("start")
