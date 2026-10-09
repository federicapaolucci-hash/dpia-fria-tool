"""Section 3.2: case risk register — RSEL-01 selection from the catalogue, four dimensions per risk, calibrated by the engine."""

from __future__ import annotations

import streamlit as st

from digcon.domain.enums import Probability, Reversibility, RuleEffect, Scale, Scope, label
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


def suggestions(cfg: ConfigBundle, result: EngineResult) -> dict[str, list[str]]:
    """RSEL-01 (AS-032): risks whose source questions (sheet 04) were read by a rule that identified a harm.

    A suggestion only: the selection stays human and never goes outside the 11-risk catalogue.
    """
    triggers = {
        rid: set(rr.input_ids)
        for rid, rr in result.rules.items()
        if rr.fired and RuleEffect.RISK_INPUT in rr.effects and rid != "RSEL-01"
    }
    d04 = (state.store()["answers"].get("D04") or {}).get("value") or []
    out: dict[str, list[str]] = {}
    for spec in cfg.risks.risks:
        sources = set(spec.core_questions + spec.provider_questions + spec.deployer_questions)
        why = [f"{rid} ({', '.join(sorted(qs & sources))})" for rid, qs in triggers.items() if qs & sources]
        if spec.id in d04:
            why.insert(0, "selected in D04")
        if why:
            out[spec.id] = why
    return out


def render(cfg: ConfigBundle, result: EngineResult) -> None:
    st.markdown(
        "Include the risks relevant to this case **from the DIGCON catalogue** and rate them; new risks cannot be "
        "added (RSEL-01). Severity = MAX(scale, scope, reversibility); level = severity × probability.\n\n"
        "Rate the **residual** dimensions only once a linked measure is VERIFIED EFFECTIVE (3.4). "
        "Until then the residual risk stays empty."
    )
    suggested = suggestions(cfg, result)
    rsel = result.rules.get("RSEL-01")
    in_register = set(state.store()["risks"])
    if rsel is not None and rsel.gap:
        st.warning("Your answers identify a harm (RSEL-01), but no risk in the register is rated yet, so this is an "
                   "evidence gap. Include at least one risk below and rate its four initial dimensions.")
    missing = {r: why for r, why in suggested.items() if r not in in_register}
    if missing:
        with st.container(border=True):
            st.markdown(
                "**Suggested by RSEL-01** (not yet in the register)\n\n"
                + "\n".join(f"- **{r}** — from {'; '.join(why)}" for r, why in missing.items())
            )
    for spec in cfg.risks.risks:
        stored = state.store()["risks"].get(spec.id) or {}
        rr = result.risks.get(spec.id)
        level = f" · initial {label(rr.initial) if rr and rr.initial else '—'} · residual {label(rr.residual) if rr and rr.residual else '—'}" if rr else ""
        hint = " · suggested" if spec.id in suggested and spec.id not in in_register else ""
        title = f"{spec.id}{' (' + spec.label + ')' if spec.label else ''} — {spec.right.split(';')[0][:90]}{level}{hint}"
        with st.expander(title, expanded=bool(stored)):
            key = f"w.risk.{spec.id}.include"
            state.seed(key, bool(stored))
            st.checkbox("Include in the case risk register", key=key, on_change=_sync, args=(spec.id,))
            if rr and rr.to_reassess:
                st.warning("Stakeholder evidence modified or contradicted this risk (SEP09): review its ratings below.")
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
