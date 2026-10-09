"""Section 2.0: routing after scoping (00_MAPPA_FLUSSO §2) — which add-ons the core answers open."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from digcon.domain.models import ConfigBundle
from digcon.engine import EngineResult

from .questionnaire import routing_box

# 00_MAPPA_FLUSSO, "Routing dopo lo scoping".
ROUTES = [
    ("High-risk = NO", "Closes the AI Act high-risk add-ons; the fundamental-rights assessment continues on the core"),
    ("High-risk = YES + Provider", "Core + Provider add-on (Article 9)"),
    ("High-risk = YES + Deployer + Article 27 applicable", "Core + Deployer add-on (Article 27 FRIA)"),
    ("High-risk = YES + Joint", "Core + Provider add-on (Article 9) + Deployer add-on (Article 27 FRIA)"),
]


def _active_route(result: EngineResult) -> int | None:
    if result.high_risk == "NO":
        return 0
    if result.high_risk != "YES" or result.routing_suspended:
        return None
    return {"PROVIDER": 1, "DEPLOYER": 2, "JOINT": 3}.get(result.role or "")


def render(cfg: ConfigBundle, result: EngineResult) -> None:
    st.markdown(
        "The core (step 1) is always completed. The add-ons open **only after scoping**, from the classification "
        "(HIGH RISK, section 1.2) and the role (C05, section 1.1). Joint is not a third logic: it opens both add-ons "
        "on the same risk register."
    )
    routing_box(result)
    active = _active_route(result)
    st.dataframe(
        pd.DataFrame(
            [
                {"Current": "yes" if i == active else "", "Condition": cond, "Path": path}
                for i, (cond, path) in enumerate(ROUTES)
            ]
        ),
        width="stretch",
        hide_index=True,
    )
    if active is None and not result.routing_suspended:
        st.caption("No route yet: answer HIGH RISK (1.2) and the role C05 (1.1). UNKNOWN opens nothing and is an evidence gap.")
