"""Section 6: hard stops (legal gate), reviewer checks and pending legal reviews."""

from __future__ import annotations

import streamlit as st

from digcon.domain.enums import ElementSource, RuleElementState
from digcon.domain.models import ConfigBundle
from digcon.engine import EngineResult

from .. import renderer, state


def render(cfg: ConfigBundle, result: EngineResult) -> None:
    recorded_gates = set(state.store()["human_gates"])

    st.markdown(
        "A hard stop is evaluated when an answer signals it, or when you open it by recording one of its elements. "
        "O5 requires **every element MET and the legal review recorded**. UNCERTAIN never counts as MET."
    )
    st.subheader("6.1 Hard stops (HS01–HS09)")
    for hs_id, hs in result.hard_stops.items():
        spec = cfg.rule(hs_id)
        if hs.state is RuleElementState.MET:
            icon, status = "🔴", "MET — confirmed"
        elif hs.opened:
            icon, status = "🟠", f"open · {hs.state.value}"
        else:
            icon, status = "⚪", "not opened"
        with st.expander(f"{icon} {hs_id} — {status}", expanded=hs.opened):
            st.caption(f"Elements: {spec.trigger_text}")
            st.caption(f"Remediability: {spec.remediability}")
            for el in spec.encoding.elements:
                renderer.element(el, hs.elements[el.id].value)
            if hs.opened or hs_id in recorded_gates:
                renderer.legal_gate(hs_id)
            if hs.awaiting_legal_review:
                st.warning("All elements MET: hard stop awaiting legal review.")

    st.subheader("6.2 Reviewer checks")
    st.caption(
        "Qualitative checks the engine does not infer from text (the slot a future API will fill). "
        "Not evaluated = 'to be verified': it does not block the outcome."
    )
    to_verify = {f.rule_id for f in result.verification_requests}
    for spec in cfg.rules.rules:
        manual = [e for e in spec.encoding.elements if e.source is ElementSource.MANUAL]
        if spec.family == "HS" or not manual:
            continue
        mark = " · to be verified" if spec.id in to_verify else ""
        with st.expander(f"{spec.id}{mark}"):
            st.caption(spec.trigger_text)
            for el in manual:
                renderer.element(el)

    st.subheader("6.3 Legal reviews")
    pending = [f.rule_id for f in result.pending_reviews if cfg.rule(f.rule_id).family != "HS"]
    done = [r for r in recorded_gates if cfg.rule(r).family != "HS" and r not in pending]
    if not pending and not done:
        st.success("No legal review pending outside the hard stops.")
    for rid in pending + done:
        st.markdown(f"**{rid}** — {cfg.rule(rid).flow_effect}")
        renderer.legal_gate(rid)
