"""Streamlit app: header, left menu with the protocol sections, live engine result."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import streamlit as st

from digcon.config import default_config
from digcon.domain.enums import Phase
from digcon.engine import InvalidAssessment, RunContext, run_engine

from . import state
from .labels import (
    APP_CAPTION,
    APP_TITLE,
    DISCLAIMER,
    FOOTER,
    METHODOLOGY,
    MITIGATION_TITLE,
    OUTCOME_TITLES,
    PHASE_TITLES,
    RESULT_TITLE,
    REVIEW_TITLE,
    RISKS_TITLE,
    SEP_TITLE,
    START_TITLE,
)
from .pages import mitigation, questionnaire, result, review, risks, sep, start

NAV = "nav"


@st.cache_resource
def _config():
    return default_config()


def _sections():
    """(title, render function) in protocol order."""
    items = [(START_TITLE, start.render)]
    for phase in Phase:
        items.append((PHASE_TITLES[phase], lambda cfg, res, p=phase: questionnaire.render(cfg, res, p)))
    items += [
        (REVIEW_TITLE, review.render),
        (RISKS_TITLE, risks.render),
        (MITIGATION_TITLE, mitigation.render),
        (SEP_TITLE, sep.render),
        (RESULT_TITLE, result.render),
    ]
    return items


def _go(title: str) -> None:
    st.session_state[NAV] = title


def _menu(titles: list[str], res) -> str:
    with st.sidebar:
        st.radio("Assessment protocol", titles, key=NAV)
        st.divider()
        if res is not None:
            st.markdown(f"**{OUTCOME_TITLES[res.outcome]}**")
            st.caption(
                f"{len(res.evidence_gaps)} evidence gap(s) · {len(res.open_remediations)} remediation(s) · "
                f"{len(res.verification_requests)} to verify"
            )
            st.caption(
                f"Article 9 add-on: {'open' if res.provider_module else 'closed'} · "
                f"Article 27 add-on: {'open' if res.deployer_module else 'closed'}"
            )
        st.caption("Light / dark theme: ⋮ menu (top right) → Settings.")
    return st.session_state[NAV]


def _pager(titles: list[str], current: str) -> None:
    i = titles.index(current)
    st.divider()
    prev_col, _, next_col = st.columns([1, 3, 1])
    if i > 0:
        prev_col.button(f"← {titles[i - 1]}", on_click=_go, args=(titles[i - 1],), key="nav.prev")
    if i < len(titles) - 1:
        next_col.button(f"{titles[i + 1]} →", on_click=_go, args=(titles[i + 1],), key="nav.next")


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    st.title(APP_TITLE)
    st.caption(APP_CAPTION)
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

    sections = _sections()
    titles = [t for t, _ in sections]
    if st.session_state.get(NAV) not in titles:
        st.session_state[NAV] = titles[0]
    current = _menu(titles, res)

    with st.expander("Methodological logic", expanded=False):
        st.markdown(METHODOLOGY)

    st.header("Assessment result" if current == RESULT_TITLE else current)
    if res is not None or current == START_TITLE:
        dict(sections)[current](cfg, res)
    if current == RESULT_TITLE:
        start.save_button("result")
    _pager(titles, current)
    st.caption(FOOTER)
