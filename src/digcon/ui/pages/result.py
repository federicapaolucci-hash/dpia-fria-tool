"""Step 4: recommended outcome (metrics, findings, registers, audit trail) and the final governance decision."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from digcon.domain.enums import Outcome, label
from digcon.domain.models import ConfigBundle
from digcon.engine import EngineResult

from .. import state
from ..labels import MITIGATION_TITLE, OUTCOME_TEXT, OUTCOME_TITLES, RISKS_TITLE

GOVERNANCE_FIELDS = {
    "G01": "g01_decision",
    "G02": "g02_decision_maker",
    "G03": "g03_review_date",
    "G04": "g04_conditions",
    "G05": "g05_reasoning",
}
_COLOUR = {Outcome.O1: "green", Outcome.O2: "blue", Outcome.O3: "orange", Outcome.O4: "orange", Outcome.O5: "red"}


def _describe(cfg: ConfigBundle, ident: str) -> str:
    try:
        return f"{ident} — {cfg.question(ident).text[:80]}"
    except KeyError:
        return ident


def findings_table(cfg: ConfigBundle, findings) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"Rule": f.rule_id, "Issue": f.message, "Items": "; ".join(_describe(cfg, i) for i in f.ids)}
            for f in findings
        ]
    )


def _section(title: str, cfg: ConfigBundle, findings, empty: str) -> None:
    st.subheader(title)
    if findings:
        table = findings_table(cfg, findings)
        if table["Issue"].nunique() == 1:  # one shared message: say it once, above the table
            st.caption(table["Issue"].iloc[0])
            table = table.drop(columns="Issue")
        st.dataframe(table, width="stretch", hide_index=True)
    else:
        st.caption(empty)


def _sync_governance() -> None:
    gov = {attr: (st.session_state.get(f"w.gov.{gid}") or "").strip() or None for gid, attr in GOVERNANCE_FIELDS.items()}
    state.store()["governance"] = gov


def render(cfg: ConfigBundle, result: EngineResult) -> None:
    opened = [h for h, v in result.hard_stops.items() if v.opened]
    cols = [*st.columns(3), *st.columns(3)]
    cols[0].metric("Recommended outcome", result.outcome.value)
    cols[1].metric("Evidence gaps", len(result.evidence_gaps))
    cols[2].metric("Open remediations", len(result.open_remediations))
    cols[3].metric("Conditions", len(result.open_conditions))
    cols[4].metric("Hard stops open", len(opened))
    cols[5].metric("Legal reviews pending", len(result.pending_reviews))

    with st.container(border=True):
        st.markdown(f"### :{_COLOUR[result.outcome]}[{OUTCOME_TITLES[result.outcome]}]")
        st.markdown(OUTCOME_TEXT[result.outcome])
    st.caption(
        f"Rule {result.outcome_rule} · precedence O5 → O4 → O3 → O2 → O1 · workbook {result.workbook_version}. "
        "This is the recommended outcome, not the final governance decision."
    )

    _section("Evidence gaps (O4 until resolved)", cfg, result.evidence_gaps, "No material evidence gap.")
    _section("Open remediations (O3 until resolved)", cfg, result.open_remediations, "No open remediation.")
    _section("Conditions (O2)", cfg, result.open_conditions, "No remaining condition.")
    _section("Legal reviews pending", cfg, result.pending_reviews, "No legal review pending.")
    _section("To be verified (does not change the outcome)", cfg, result.verification_requests, "Nothing left to verify.")

    st.subheader("Hard stops")
    st.dataframe(
        pd.DataFrame(
            [
                {"HS": h, "Opened": v.opened, "State": v.state.value, "Legal gate": v.gate.value,
                 "Elements": ", ".join(f"{k.split('.')[1]}={s.value}" for k, s in v.elements.items())}
                for h, v in result.hard_stops.items()
            ]
        ),
        width="stretch",
        hide_index=True,
    )

    st.subheader("Proportionality checks")
    if result.prop_statuses:
        st.dataframe(
            pd.DataFrame(
                [
                    {"Rule": r, "Status": label(s), "Action": ", ".join(label(e) for e in result.rules[r].effects)}
                    for r, s in result.prop_statuses.items()
                ]
            ),
            width="stretch",
            hide_index=True,
        )
        st.caption("The engine never concludes 'proportionate' or 'disproportionate': normative balancing stays with legal review.")
    else:
        st.caption("No proportionality check applicable yet.")

    st.subheader("Fundamental rights risk register")
    if result.risks:
        st.dataframe(
            pd.DataFrame(
                [
                    {"Risk": r, "Right": cfg.risk(r).right.split(";")[0][:70],
                     "Severity": label(v.severity) if v.severity else "—",
                     "Initial": label(v.initial) if v.initial else "—",
                     "Residual": label(v.residual) if v.residual else "— (not verified)",
                     "Reassess (SEP)": v.to_reassess}
                    for r, v in result.risks.items()
                ]
            ),
            width="stretch",
            hide_index=True,
        )
    else:
        st.caption(f"No risk in the case register yet ({RISKS_TITLE}).")

    activated = [m for m in state.assessment().mitigations.values() if m.activated]
    st.subheader("Mitigation plan (activated measures)")
    if activated:
        st.dataframe(
            pd.DataFrame(
                [
                    {"Mitigation": m.mitigation_id, "Risk": cfg.mitigation(m.mitigation_id).risk_id,
                     "Measure": cfg.mitigation(m.mitigation_id).measure[:80], "Status": label(m.status),
                     "Decision effect": cfg.mitigation(m.mitigation_id).decision_effect_text,
                     "Remediates": ", ".join(m.linked_rule_ids), "Owner": m.owner or "TO ASSIGN"}
                    for m in activated
                ]
            ),
            width="stretch",
            hide_index=True,
        )
    else:
        st.caption(f"No measure activated ({MITIGATION_TITLE}).")

    if result.warnings:
        st.subheader("Warnings")
        for w in result.warnings:
            st.warning(w)

    with st.expander(f"Audit trail ({len(result.audit_trail)} events)"):
        if result.audit_defects:
            st.error("Audit defects: " + "; ".join(result.audit_defects))
        st.dataframe(
            pd.DataFrame(
                [
                    {"Event": e.event_id, "Module": e.module.value, "Rule": e.rule_id or "", "Output": e.engine_output or "",
                     "Inputs": ", ".join(e.input_ids), "Evidence": ", ".join(e.evidence_refs),
                     "Human gate": e.human_gate.value if e.human_gate else "", "Parent": e.parent_event_id or ""}
                    for e in result.audit_trail
                ]
            ),
            width="stretch",
            hide_index=True,
        )


def render_governance(cfg: ConfigBundle, result: EngineResult) -> None:
    st.markdown(
        f"Recommended outcome: **{OUTCOME_TITLES[result.outcome]}** (rule {result.outcome_rule}). "
        "The final decision is distinct from it: it is recorded by the responsible person or body, "
        "and the engine never fills these fields (SYS-03)."
    )
    gov = state.store()["governance"]
    for g in cfg.questions.governance_fields:
        key = f"w.gov.{g.id}"
        state.seed(key, gov.get(GOVERNANCE_FIELDS[g.id]) or "")
        st.text_input(f"{g.field} `{g.id}`", key=key, help=g.purpose, on_change=_sync_governance)
    st.caption("To reassess later, save progress below and load the file in section 1.0 when the review date or a trigger arrives.")
