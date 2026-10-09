"""Section 3.4: mitigation plan — candidate measures of 05A (NOT ACTIVATED until triggered), activated and verified by the user."""

from __future__ import annotations

import streamlit as st

from digcon.domain.enums import MitigationStatus, RuleEffect, label
from digcon.domain.models import ConfigBundle
from digcon.engine import EngineResult

from .. import state


def _short(text: str, limit: int = 90) -> str:
    """Cut at a word boundary, with an ellipsis, so expander titles never stop mid-word."""
    return text if len(text) <= limit else text[:limit].rsplit(" ", 1)[0].rstrip(",;:(") + "…"


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
        "The 50 catalogue measures start as **candidates (NOT ACTIVATED)** and count only once you activate them "
        "for a linked risk, rule or SEP finding.\n\n"
        "- Only **VERIFIED EFFECTIVE** reduces risk, and only once the residual risk is rated in the risk register (3.2). "
        "PROPOSED, PLANNED and IN IMPLEMENTATION reduce nothing.\n"
        "- To close a remediation, link the measure to the rule it remediates (e.g. SCR-01)."
    )
    in_register = set(state.store()["risks"])
    records = state.store()["mitigations"]
    remediating = sorted(r for r, rr in result.rules.items() if rr.fired and RuleEffect.REMEDIATION_REQUIRED in rr.effects)
    rule_options = sorted({*remediating, "HS08", "HS09", *(r for m in records.values() for r in m["linked_rule_ids"])})
    if remediating:
        st.markdown("**Rules waiting for a remediating measure:** " + " ".join(f"`{r}`" for r in remediating))

    views = {"register": "Register risks + activated", "all": "All 50 measures", "active": "Activated only"}
    state.seed("w.mit.view", "register" if in_register else "all")
    view = st.segmented_control("Show", list(views), key="w.mit.view", format_func=views.get, required=True)
    activated = {m for m, r in records.items() if r.get("activated")}
    shown = [
        s for s in cfg.mitigations.mitigations
        if view == "all" or (view == "active" and s.id in activated) or (view == "register" and (s.risk_id in in_register or s.id in activated))
    ]
    shown.sort(key=lambda s: s.id not in activated)  # activated measures first, catalogue order otherwise
    st.caption(f"{len(shown)} measures shown · {len(activated)} activated")
    if not shown:
        st.info("No measure matches this view. Add risks in the register (3.2) or show all 50 measures.",
                icon=":material/filter_alt_off:")

    for spec in shown:
        stored = records.get(spec.id) or {}
        k = f"w.mit.{spec.id}"
        on = bool(stored.get("activated"))
        status = label(MitigationStatus[stored.get("status", MitigationStatus.PROPOSED.value)])
        flag = f":blue-badge[Activated · {status}]" if on else ":gray-badge[Candidate]"
        with st.expander(f"{flag} {spec.id} · {spec.risk_id} · {spec.responsible_role} · {_short(spec.measure)}",
                         expanded=on):
            for col, (name, value) in zip(st.columns(4), (("Responsible", spec.responsible_role),
                                                          ("Decision effect", spec.decision_effect_text),
                                                          ("Timing", spec.timing_text),
                                                          ("Closure", spec.closure_criterion))):
                col.caption(name)
                col.markdown(value)
            c1, c2, c3 = st.columns([1, 1, 2])
            state.seed(f"{k}.on", stored.get("activated", False))
            state.seed(f"{k}.status", stored.get("status", MitigationStatus.PROPOSED.value))
            state.seed(f"{k}.owner", stored.get("owner") or "")
            state.seed(f"{k}.rules", [r for r in stored.get("linked_rule_ids", []) if r in rule_options])
            state.seed(f"{k}.refs", "\n".join(stored.get("evidence_refs", [])))
            with c1:
                st.toggle("Activated", key=f"{k}.on", on_change=_sync, args=(spec.id,))
            with c2:
                st.selectbox("Status", [s.value for s in MitigationStatus], key=f"{k}.status",
                             format_func=lambda c: label(MitigationStatus[c]), on_change=_sync, args=(spec.id,))
            with c3:
                st.text_input("Owner", key=f"{k}.owner", on_change=_sync, args=(spec.id,))
            st.pills("Remediates rule(s)", rule_options, selection_mode="multi", key=f"{k}.rules", wrap=True,
                     on_change=_sync, args=(spec.id,))
            st.text_area("Evidence of implementation or verification (one reference per line)", key=f"{k}.refs",
                         height=68, on_change=_sync, args=(spec.id,))
