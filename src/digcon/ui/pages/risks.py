"""Section 7: case risk register — four dimensions per risk, calibrated by the engine."""

from __future__ import annotations

import streamlit as st

from digcon.domain.enums import Probability, Reversibility, Scale, Scope, label
from digcon.domain.models import ConfigBundle
from digcon.engine import EngineResult

from .. import state

DIMENSIONS = (("scale", Scale), ("scope", Scope), ("reversibility", Reversibility), ("probability", Probability))


def _sync(rid: str) -> None:
    ss = st.session_state
    if not ss.get(f"w.risk.{rid}.include"):
        state.set_or_remove("risks", rid, None)
        return
    data = {"risk_id": rid}
    for prefix in ("", "residual_"):
        for dim, _ in DIMENSIONS:
            v = ss.get(f"w.risk.{rid}.{prefix}{dim}")
            if v is not None:
                data[f"{prefix}{dim}"] = v
    refs = [r.strip() for r in (ss.get(f"w.risk.{rid}.refs") or "").splitlines() if r.strip()]
    if refs:
        data["evidence_refs"] = refs
    state.set_or_remove("risks", rid, data)


def _dims(rid: str, prefix: str, stored: dict) -> None:
    cols = st.columns(4)
    for col, (dim, enum) in zip(cols, DIMENSIONS):
        key = f"w.risk.{rid}.{prefix}{dim}"
        state.seed(key, stored.get(f"{prefix}{dim}"))
        with col:
            st.selectbox(dim.capitalize(), [m.value for m in enum], key=key, placeholder="—",
                         format_func=lambda c, e=enum: label(e[c]), on_change=_sync, args=(rid,))


def render(cfg: ConfigBundle, result: EngineResult) -> None:
    st.markdown(
        "Select the risks relevant to this case and rate them. Severity = MAX(scale, scope, reversibility); "
        "level = severity × probability. **Residual** dimensions count only after a linked mitigation is "
        "VERIFIED EFFECTIVE (section 8); before that the residual risk stays empty."
    )
    for spec in cfg.risks.risks:
        stored = state.store()["risks"].get(spec.id) or {}
        rr = result.risks.get(spec.id)
        level = f" · initial {label(rr.initial) if rr and rr.initial else '—'} · residual {label(rr.residual) if rr and rr.residual else '—'}" if rr else ""
        title = f"{spec.id}{' (' + spec.label + ')' if spec.label else ''} — {spec.right.split(';')[0][:90]}{level}"
        with st.expander(title, expanded=bool(stored)):
            key = f"w.risk.{spec.id}.include"
            state.seed(key, bool(stored))
            st.checkbox("Include in the case risk register", key=key, on_change=_sync, args=(spec.id,))
            if rr and rr.to_reassess:
                st.warning("Stakeholder evidence modified or contradicted this risk (SEP09): reassess it.")
            with st.popover("Harm scenarios and safeguards to verify"):
                for h in spec.harm_scenarios:
                    st.markdown(f"- {h}")
                st.caption(spec.safeguards_to_verify)
            if not st.session_state[key]:
                continue
            st.markdown("**Initial**")
            _dims(spec.id, "", stored)
            st.markdown("**Residual (after verified mitigation)**")
            _dims(spec.id, "residual_", stored)
            state.seed(f"w.risk.{spec.id}.refs", "\n".join(stored.get("evidence_refs", [])))
            st.text_area("Evidence references (one per line)", key=f"w.risk.{spec.id}.refs", height=68,
                         on_change=_sync, args=(spec.id,))
