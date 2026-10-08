"""Streamlit app: header, session sidebar, numbered sections, live engine result."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import streamlit as st

from digcon.config import default_config
from digcon.domain.enums import Phase
from digcon.engine import InvalidAssessment, RunContext, run_engine

from . import state
from .labels import APP_CAPTION, APP_TITLE, CREDITS, DISCLAIMER, METHODOLOGY, OUTCOME_TITLES, PHASE_TITLES
from .pages import mitigation, questionnaire, result, review, risks, sep


@st.cache_resource
def _config():
    return default_config()


def _sync_id() -> None:
    value = (st.session_state.get("w.meta.id") or "").strip()
    if value:
        state.store()["assessment_id"] = value


def _sidebar(cfg, res) -> None:
    with st.sidebar:
        st.header("Session")
        state.seed("w.meta.id", state.store()["assessment_id"])
        st.text_input("Assessment ID", key="w.meta.id", on_change=_sync_id)
        st.download_button(
            "Download assessment (JSON, to resume later)",
            state.to_json(),
            file_name=f"{state.store()['assessment_id']}_state.json",
            mime="application/json",
            width="stretch",
        )
        upload = st.file_uploader("Resume an assessment", type=["json"])
        if upload is not None and st.button("Load this assessment", width="stretch"):
            try:
                state.replace(state.parse_upload(upload.getvalue()))
                st.rerun()
            except ValueError as exc:
                st.error(f"Not a valid assessment file: {exc}")
        if st.button("Start a new assessment", width="stretch"):
            state.replace(state.empty_store(cfg))
            st.rerun()

        st.divider()
        st.header("Live status")
        if res is not None:
            st.markdown(f"**{OUTCOME_TITLES[res.outcome]}**")
            st.caption(
                f"High-risk: {res.high_risk or '—'} · Role: {res.role or '—'}\n\n"
                f"Article 9 add-on: {'open' if res.provider_module else 'closed'} · "
                f"Article 27 add-on: {'open' if res.deployer_module else 'closed'}"
                + ("\n\n⚠️ Routing suspended: C03 = YES (HS07 legal gate)" if res.routing_suspended else "")
            )
            st.caption(
                f"{len(res.evidence_gaps)} evidence gap(s) · {len(res.open_remediations)} remediation(s) · "
                f"{len(res.verification_requests)} to verify"
            )
        st.caption(f"Decision engine: workbook {cfg.version}")


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    st.title(APP_TITLE)
    st.caption(APP_CAPTION)
    st.markdown(CREDITS)
    st.info(DISCLAIMER)

    cfg = _config()
    state.init(cfg)
    try:
        res = run_engine(
            cfg,
            state.assessment(),
            RunContext(run_id=uuid.uuid4().hex[:12], timestamp=datetime.now(timezone.utc)),
        )
    except InvalidAssessment as exc:
        res = None
        st.error("The assessment contains values outside the allowed answers: " + "; ".join(exc.errors))

    _sidebar(cfg, res)
    with st.expander("Methodological logic", expanded=False):
        st.markdown(METHODOLOGY)
    if res is None:
        return

    titles = [
        *PHASE_TITLES.values(),
        "6. Hard stops and reviews",
        "7. Risk register",
        "8. Mitigation plan",
        "9. Stakeholder engagement",
        "Result",
    ]
    tabs = st.tabs(titles)
    for tab, phase in zip(tabs, Phase):
        with tab:
            st.header(PHASE_TITLES[phase])
            questionnaire.render(cfg, res, phase)
    pages = [review, risks, mitigation, sep, result]
    for tab, title, page in zip(tabs[len(Phase):], titles[len(Phase):], pages):
        with tab:
            st.header(title if page is not result else "Assessment result")
            page.render(cfg, res)
