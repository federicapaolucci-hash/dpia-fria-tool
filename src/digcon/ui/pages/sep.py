"""Section 3.1: stakeholder engagement process (04A). Evidence and process only: no direct outcome."""

from __future__ import annotations

import streamlit as st

from digcon.domain.enums import SepDecision, SepEffect, SepVulnerability, label
from digcon.domain.models import ConfigBundle
from digcon.engine import EngineResult

from .. import state

ENUM_FIELDS = {
    "SEP00": ("decision", [m.value for m in SepDecision], SepDecision),
    "SEP03": ("vulnerability", [m.value for m in SepVulnerability], SepVulnerability),
    "SEP09": ("effect", [m.value for m in SepEffect], SepEffect),
    "SEP10": ("new_risk", ["YES", "NO"], None),
    "SEP11": ("new_mitigation", ["YES", "NO"], None),
}


def _sync(cfg: ConfigBundle) -> None:
    ss = st.session_state
    data: dict = {"texts": {}, "evidence_refs": [], "effect_risk_ids": list(ss.get("w.sep.risks") or [])}
    for fid, (attr, _, _) in ENUM_FIELDS.items():
        v = ss.get(f"w.sep.{fid}")
        if v is not None:
            data[attr] = v
    for f in cfg.sep.fields:
        if f.id not in ENUM_FIELDS:
            t = (ss.get(f"w.sep.{f.id}") or "").strip()
            if t:
                data["texts"][f.id] = t
    data["evidence_refs"] = [r.strip() for r in (ss.get("w.sep.refs") or "").splitlines() if r.strip()]
    state.store()["sep"] = data


def render(cfg: ConfigBundle, result: EngineResult) -> None:
    st.markdown(
        "SEP is a transversal, conditional process. A previous consultation (C55) is evidence, not a gate. "
        "Stakeholder evidence changes a risk only through an explicit link; consultation alone never lowers risk."
    )
    if result.sep_status:
        st.markdown(f"SEP status: **{label(result.sep_status)}**")
    sep = state.store()["sep"]
    for f in cfg.sep.fields:
        key = f"w.sep.{f.id}"
        title = f"{f.question} `{f.id}`"
        if f.id in ENUM_FIELDS:
            attr, options, enum = ENUM_FIELDS[f.id]
            state.seed(key, sep.get(attr))
            st.selectbox(title, options, key=key, placeholder="—", help=f.activation,
                         format_func=lambda c, e=enum: label(e[c]) if e else c, on_change=_sync, args=(cfg,))
            if f.id == "SEP09":
                state.seed("w.sep.risks", sep.get("effect_risk_ids", []))
                st.multiselect("Risks affected by the stakeholder evidence", [r.id for r in cfg.risks.risks],
                               key="w.sep.risks", on_change=_sync, args=(cfg,))
        else:
            state.seed(key, sep.get("texts", {}).get(f.id, ""))
            st.text_area(title, key=key, height=68, help=f.activation, on_change=_sync, args=(cfg,))
    state.seed("w.sep.refs", "\n".join(sep.get("evidence_refs", [])))
    st.text_area("Evidence references (one per line)", key="w.sep.refs", height=68, on_change=_sync, args=(cfg,))
