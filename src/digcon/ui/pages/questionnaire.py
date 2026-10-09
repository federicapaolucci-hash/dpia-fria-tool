from __future__ import annotations

import streamlit as st

from digcon.domain.enums import Phase
from digcon.domain.models import ConfigBundle
from digcon.engine import EngineResult

from .. import renderer, state
from ..labels import PHASE_TITLES, REVIEW_TITLE, subsection

PROVIDER = PHASE_TITLES[Phase.PROVIDER].split(" ", 1)[0]
DEPLOYER = PHASE_TITLES[Phase.DEPLOYER].split(" ", 1)[0]


def routing_box(result: EngineResult) -> None:
    """What the routing currently opens, and what is missing to open the add-ons."""
    answers = state.store()["answers"]
    role = result.role
    high_risk = result.high_risk
    lines = [f"High risk (FOLLOW): **{high_risk or 'not answered'}** · Role (C05): **{role or 'not answered'}**"]
    if result.routing_suspended:
        lines.append(f"**Add-ons suspended.** C03 = YES: they stay closed until the HS07 legal gate excludes the prohibition ({REVIEW_TITLE}).")
    else:
        if result.provider_module:
            lines.append(f"**Article 9 provider add-on: open** ({PROVIDER}).")
        elif role in ("PROVIDER", "JOINT"):
            lines.append(f"Article 9 add-on ({PROVIDER}): needs **HIGH RISK = YES**.")
        if result.deployer_module:
            lines.append(f"**Article 27 deployer add-on: open** ({DEPLOYER}).")
        elif role in ("DEPLOYER", "JOINT"):
            if high_risk != "YES":
                lines.append(f"Article 27 add-on ({DEPLOYER}): needs **HIGH RISK = YES**, then **D00 = YES** in section {DEPLOYER}.")
            elif (answers.get("D00") or {}).get("state") != "YES":
                lines.append(f"Article 27 add-on ({DEPLOYER}): answer **D00 = YES** (first question of section {DEPLOYER}) to open D01–D10.")
        if high_risk == "NO":
            lines.append("Not high-risk: the AI Act add-ons stay closed; the fundamental-rights assessment continues on the core.")
    with st.container(border=True):
        st.markdown("**Routing**")
        st.markdown("\n\n".join(lines))


def render(cfg: ConfigBundle, result: EngineResult, phase: Phase) -> None:
    visible = set(result.visible_questions)
    if phase in (Phase.PROVIDER, Phase.DEPLOYER):
        routing_box(result)
        if phase is Phase.PROVIDER and not result.provider_module:
            return
        if phase is Phase.DEPLOYER and "D00" not in visible:
            return

    shown = [q for q in cfg.questions.questions if q.phase is phase and q.id in visible]
    answered = sum(1 for q in shown if q.id in state.store()["answers"])
    st.progress(answered / len(shown) if shown else 0.0, text=f"{answered} of {len(shown)} questions answered")
    st.caption("UNKNOWN, N/A and NOT OWNED are answers too: never treated as NO.")
    groups: dict[str, list] = {}
    for q in shown:
        groups.setdefault(q.subsection, []).append(q)
    for name, questions in groups.items():
        with st.container(border=True):
            st.subheader(subsection(name))
            for q in questions:
                renderer.question(cfg, q)

    if phase in (Phase.INTRO, Phase.WHAT):
        st.divider()
        routing_box(result)
