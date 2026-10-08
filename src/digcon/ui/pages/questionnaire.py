from __future__ import annotations

import streamlit as st

from digcon.domain.enums import Phase
from digcon.domain.models import ConfigBundle
from digcon.engine import EngineResult

from .. import renderer, state
from ..labels import subsection


def routing_box(result: EngineResult) -> None:
    """What the routing currently opens, and what is missing to open the add-ons."""
    answers = state.store()["answers"]
    role = result.role
    high_risk = result.high_risk
    lines = [f"High risk (FOLLOW): **{high_risk or 'not answered'}** · Role (C05): **{role or 'not answered'}**"]
    if result.routing_suspended:
        lines.append("⚠️ C03 = YES: add-ons suspended until the HS07 legal gate excludes the prohibition (section 6).")
    else:
        if result.provider_module:
            lines.append("✅ Article 9 provider add-on open (5A).")
        elif role in ("PROVIDER", "JOINT"):
            lines.append("Article 9 add-on (5A): needs **HIGH RISK = YES**.")
        if result.deployer_module:
            lines.append("✅ Article 27 deployer add-on open (5B).")
        elif role in ("DEPLOYER", "JOINT"):
            if high_risk != "YES":
                lines.append("Article 27 add-on (5B): needs **HIGH RISK = YES**, then **D00 = YES** in section 5B.")
            elif (answers.get("D00") or {}).get("state") != "YES":
                lines.append("Article 27 add-on (5B): answer **D00 = YES** (first question of section 5B) to open D01–D10.")
        if high_risk == "NO":
            lines.append("Not high-risk: the AI Act add-ons stay closed; the fundamental-rights assessment continues on the core.")
    st.info("\n\n".join(lines), icon="🧭")


def render(cfg: ConfigBundle, result: EngineResult, phase: Phase) -> None:
    visible = set(result.visible_questions)
    if phase in (Phase.PROVIDER, Phase.DEPLOYER):
        routing_box(result)
        if phase is Phase.PROVIDER and not result.provider_module:
            return
        if phase is Phase.DEPLOYER and "D00" not in visible:
            return

    current = None
    for q in cfg.questions.questions:
        if q.phase is not phase or q.id not in visible:
            continue
        if q.subsection != current:
            current = q.subsection
            st.subheader(subsection(current))
        renderer.question(cfg, q)

    if phase in (Phase.INTRO, Phase.WHAT):
        st.divider()
        routing_box(result)
