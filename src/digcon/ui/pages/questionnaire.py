from __future__ import annotations

import streamlit as st

from digcon.domain.enums import Phase
from digcon.domain.models import ConfigBundle
from digcon.engine import EngineResult

from .. import renderer
from ..labels import subsection


def render(cfg: ConfigBundle, result: EngineResult, phase: Phase) -> None:
    visible = set(result.visible_questions)
    if phase is Phase.PROVIDER and not result.provider_module:
        st.info(_closed_reason(result, "Provider", "PROVIDER / JOINT"))
        return
    if phase is Phase.DEPLOYER and not any(q in visible for q in ("D00", "D01")):
        st.info(_closed_reason(result, "Deployer", "DEPLOYER / JOINT"))
        return
    if phase is Phase.DEPLOYER and not result.deployer_module:
        st.info("Article 27 add-on (D01–D10) opens when D00 = YES.")

    current = None
    for q in cfg.questions.questions:
        if q.phase is not phase or q.id not in visible:
            continue
        if q.subsection != current:
            current = q.subsection
            st.subheader(subsection(current))
        renderer.question(cfg, q)


def _closed_reason(result: EngineResult, who: str, roles: str) -> str:
    if result.routing_suspended:
        return f"{who} add-on suspended: C03 = YES routes to the HS07 legal gate first (see section 6)."
    return (
        f"{who} add-on not active. It opens when HIGH RISK (FOLLOW) = YES and role (C05) is {roles}. "
        f"Current: high-risk = {result.high_risk or '—'}, role = {result.role or '—'}."
    )
