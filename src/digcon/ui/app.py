"""Streamlit app: header, step-by-step navigation (00_MAPPA_FLUSSO), live engine result.

Step 1 is the common core, step 2 the add-ons opened by the scoping answers, step 3 the
transversal modules, step 4 the recommended outcome and the governance decision. The
left menu lists every section of every step as a button, with its status.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import streamlit as st

from digcon.config import default_config
from digcon.domain.enums import Outcome, Phase
from digcon.engine import EngineResult, InvalidAssessment, RunContext, run_engine

from . import state
from .labels import (
    APP_CAPTION,
    APP_TITLE,
    DISCLAIMER,
    FOOTER,
    GOVERNANCE_TITLE,
    METHODOLOGY,
    MITIGATION_TITLE,
    NAV_LABELS,
    OUTCOME_TITLES,
    PHASE_TITLES,
    RESULT_TITLE,
    REVIEW_TITLE,
    RISKS_TITLE,
    ROUTING_TITLE,
    RULES_TITLE,
    SEP_TITLE,
    START_TITLE,
    STEP_ADDONS,
    STEP_ANALYSIS,
    STEP_CORE,
    STEP_OUTCOME,
    STEP_TEXT,
)
from .pages import mitigation, questionnaire, result, review, risks, routing, sep, start

NAV = "nav"
OUTCOME_COLOUR = {Outcome.O1: "green", Outcome.O2: "blue", Outcome.O3: "orange", Outcome.O4: "orange", Outcome.O5: "red"}

SIDEBAR_WIDTH = 368  # px: section labels and their status on one line
SIDEBAR_CSS = """
<style>
section[data-testid="stSidebar"] .stButton button {
    justify-content: flex-start; text-align: left; padding: 0.4rem 0.8rem; min-height: 2.4rem;
}
section[data-testid="stSidebar"] .stButton button > div { justify-content: flex-start; }
section[data-testid="stSidebar"] .stButton button p { font-size: 0.98rem; }
.digcon-step { font-size: 0.78rem; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase;
               opacity: 0.65; margin: 1.1rem 0 0.35rem 0; }
</style>
"""


@st.cache_resource
def _config():
    return default_config()


def _phase_page(phase: Phase):
    return lambda cfg, res: questionnaire.render(cfg, res, phase)


def _steps() -> dict[str, list[tuple[str, object]]]:
    """Step -> [(section title, render function)], in protocol order."""
    return {
        STEP_CORE: [(START_TITLE, start.render)]
        + [(PHASE_TITLES[p], _phase_page(p)) for p in (Phase.INTRO, Phase.WHAT, Phase.HOW, Phase.WHY)],
        STEP_ADDONS: [
            (ROUTING_TITLE, routing.render),
            (PHASE_TITLES[Phase.PROVIDER], _phase_page(Phase.PROVIDER)),
            (PHASE_TITLES[Phase.DEPLOYER], _phase_page(Phase.DEPLOYER)),
        ],
        STEP_ANALYSIS: [
            (SEP_TITLE, sep.render),
            (RISKS_TITLE, risks.render),
            (RULES_TITLE, review.render_rules),
            (MITIGATION_TITLE, mitigation.render),
            (REVIEW_TITLE, review.render_hard_stops),
        ],
        STEP_OUTCOME: [(RESULT_TITLE, result.render), (GOVERNANCE_TITLE, result.render_governance)],
    }


def step_of(title: str) -> str:
    return next(step for step, items in _steps().items() if title in [t for t, _ in items])


def _go(title: str) -> None:
    st.session_state[NAV] = title


def _progress(cfg, res: EngineResult | None) -> tuple[dict[str, str], dict[str, tuple[int, int]]]:
    """Per-section status mark (markdown) and per-step (answered, visible) question counts."""
    if res is None:
        return {}, {}
    answers = state.store()["answers"]
    visible = set(res.visible_questions)
    marks: dict[str, str] = {}
    counts: dict[str, tuple[int, int]] = {STEP_CORE: (0, 0), STEP_ADDONS: (0, 0)}
    for phase in Phase:
        ids = [q.id for q in cfg.questions.questions if q.phase is phase and q.id in visible]
        title = PHASE_TITLES[phase]
        locked = (phase is Phase.PROVIDER and not res.provider_module) or (phase is Phase.DEPLOYER and not ids)
        if locked:
            marks[title] = ":gray[closed]"
            continue
        done = sum(1 for q in ids if q in answers)
        marks[title] = ":green[complete]" if done == len(ids) else f":gray[{done} / {len(ids)}]"
        step = STEP_CORE if phase in (Phase.INTRO, Phase.WHAT, Phase.HOW, Phase.WHY) else STEP_ADDONS
        a, v = counts[step]
        counts[step] = (a + done, v + len(ids))
    opened = sum(1 for h in res.hard_stops.values() if h.opened)
    if opened:
        marks[REVIEW_TITLE] = f":orange[{opened} open]"
    if res.verification_requests:
        marks[RULES_TITLE] = f":gray[{len(res.verification_requests)} to verify]"
    marks[RESULT_TITLE] = f":{OUTCOME_COLOUR[res.outcome]}[**{res.outcome.value}**]"
    return {k: v for k, v in marks.items() if v}, counts


def _menu(steps: dict[str, list], res: EngineResult | None, marks: dict[str, str], counts) -> None:
    current = st.session_state[NAV]
    with st.sidebar:
        if res is not None:
            colour = OUTCOME_COLOUR[res.outcome]
            st.markdown(f"#### :{colour}[{OUTCOME_TITLES[res.outcome]}]")
            c1, c2, c3 = st.columns(3)
            c1.metric("Gaps", len(res.evidence_gaps))
            c2.metric("Remediations", len(res.open_remediations))
            c3.metric("To verify", len(res.verification_requests))
        for n, (step, items) in enumerate(steps.items(), 1):
            st.markdown(f'<div class="digcon-step">Step {n} · {step.split(" — ", 1)[1]}</div>', unsafe_allow_html=True)
            answered, total = counts.get(step, (0, 0))
            if total:
                st.progress(answered / total, text=f"{answered} of {total} questions answered")
            for title, _ in items:
                label = NAV_LABELS[title] + (f"  {marks[title]}" if title in marks else "")
                st.button(
                    label,
                    key=f"nav.{title}",
                    on_click=_go,
                    args=(title,),
                    type="primary" if title == current else "secondary",
                    width="stretch",
                )
        st.divider()
        st.caption("Light / dark theme: menu at the top right → Settings.")


def _pager(titles: list[str], current: str) -> None:
    i = titles.index(current)
    st.divider()
    prev_col, _, next_col = st.columns([2, 3, 2])
    if i > 0:
        prev_col.button(f"← {NAV_LABELS[titles[i - 1]]}", on_click=_go, args=(titles[i - 1],), key="nav.prev", width="stretch")
    if i < len(titles) - 1:
        next_col.button(
            f"{NAV_LABELS[titles[i + 1]]} →", on_click=_go, args=(titles[i + 1],), key="nav.next", type="primary", width="stretch"
        )


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, layout="wide", initial_sidebar_state=SIDEBAR_WIDTH)
    st.markdown(SIDEBAR_CSS, unsafe_allow_html=True)
    st.title(APP_TITLE)
    st.caption(APP_CAPTION)
    st.markdown(DISCLAIMER)

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
        st.error(
            "The outcome cannot be calculated: this assessment contains values that are not allowed answers ("
            + "; ".join(exc.errors)
            + "). Load a different saved file or start a new assessment in section 1.0."
        )

    steps = _steps()
    sections = {title: render for items in steps.values() for title, render in items}
    titles = list(sections)
    if st.session_state.get(NAV) not in titles:
        st.session_state[NAV] = titles[0]
    marks, counts = _progress(cfg, res)
    _menu(steps, res, marks, counts)
    current = st.session_state[NAV]
    step = step_of(current)

    with st.expander("Methodological logic", expanded=False):
        st.markdown(METHODOLOGY)

    st.caption(f"Step {list(steps).index(step) + 1} of {len(steps)} · {step.split(' — ', 1)[1]}")
    st.header(current)
    if current == steps[step][0][0]:
        st.markdown(STEP_TEXT[step])
    if res is not None or current == START_TITLE:
        sections[current](cfg, res)
    if current in (RESULT_TITLE, GOVERNANCE_TITLE):
        start.save_button(current[:3])
    _pager(titles, current)
    st.caption(FOOTER)
