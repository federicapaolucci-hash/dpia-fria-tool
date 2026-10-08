"""Section 8: mitigation plan — candidate measures of 05A, activated and verified by the user."""

from __future__ import annotations

import streamlit as st

from digcon.domain.enums import MitigationStatus, RuleEffect, label
from digcon.domain.models import ConfigBundle
from digcon.engine import EngineResult

from .. import state


def _sync(mid: str) -> None:
    ss = st.session_state
    k = f"w.mit.{mid}"
    activated = ss.get(f"{k}.on", False)
    status = ss.get(f"{k}.status") or MitigationStatus.PROPOSED.value
    owner = (ss.get(f"{k}.owner") or "").strip()
    rules = ss.get(f"{k}.rules") or []
    refs = [r.strip() for r in (ss.get(f"{k}.refs") or "").splitlines() if r.strip()]
    if not activated and status == MitigationStatus.PROPOSED.value and not owner and not rules and not refs:
        state.set_or_remove("mitigations", mid, None)
        return
    data = {"mitigation_id": mid, "activated": activated, "status": status, "linked_rule_ids": list(rules), "evidence_refs": refs}
    if owner:
        data["owner"] = owner
    state.set_or_remove("mitigations", mid, data)


def render(cfg: ConfigBundle, result: EngineResult) -> None:
    st.markdown(
        "The 50 measures of the plan are **candidates**: they count only once **activated**. "
        "PROPOSED / PLANNED / IN IMPLEMENTATION never reduce risk; only VERIFIED EFFECTIVE does, after reassessment. "
        "Link a measure to the rule it remediates (e.g. SCR-01) to close that remediation."
    )
    in_register = set(state.store()["risks"])
    show_all = st.toggle("Show measures for all risks", value=not in_register, key="w.mit.show_all")
    remediating = sorted(r for r, rr in result.rules.items() if rr.fired and RuleEffect.REMEDIATION_REQUIRED in rr.effects)
    rule_options = sorted({*remediating, "HS08", "HS09", *(r for m in state.store()["mitigations"].values() for r in m["linked_rule_ids"])})
    if remediating:
        st.info("Rules requiring remediation now: " + ", ".join(remediating))

    for spec in cfg.mitigations.mitigations:
        if not show_all and spec.risk_id not in in_register:
            continue
        stored = state.store()["mitigations"].get(spec.id) or {}
        k = f"w.mit.{spec.id}"
        flag = "✅" if stored.get("activated") else "▫️"
        with st.expander(f"{flag} {spec.id} · {spec.risk_id} · {spec.measure[:90]}", expanded=bool(stored.get("activated"))):
            st.caption(
                f"Decision effect: {spec.decision_effect_text} · Timing: {spec.timing_text} · "
                f"Closure: {spec.closure_criterion}"
            )
            c1, c2, c3 = st.columns([1, 1, 2])
            state.seed(f"{k}.on", stored.get("activated", False))
            state.seed(f"{k}.status", stored.get("status", MitigationStatus.PROPOSED.value))
            state.seed(f"{k}.owner", stored.get("owner") or "")
            state.seed(f"{k}.rules", [r for r in stored.get("linked_rule_ids", []) if r in rule_options])
            state.seed(f"{k}.refs", "\n".join(stored.get("evidence_refs", [])))
            with c1:
                st.checkbox("Activated", key=f"{k}.on", on_change=_sync, args=(spec.id,))
            with c2:
                st.selectbox("Status", [s.value for s in MitigationStatus], key=f"{k}.status",
                             format_func=lambda c: label(MitigationStatus[c]), on_change=_sync, args=(spec.id,))
            with c3:
                st.text_input("Owner", key=f"{k}.owner", on_change=_sync, args=(spec.id,))
            st.multiselect("Remediates rule(s)", rule_options, key=f"{k}.rules", on_change=_sync, args=(spec.id,))
            st.text_area("Implementation / verification evidence (one reference per line)", key=f"{k}.refs",
                         height=68, on_change=_sync, args=(spec.id,))
