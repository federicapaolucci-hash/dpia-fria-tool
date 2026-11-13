"""Step 4: recommended outcome (what to do next, registers, audit trail) and the final governance decision."""

from __future__ import annotations

import re

import pandas as pd
import streamlit as st

from digcon.domain.enums import Probability, label
from digcon.domain.models import ConfigBundle
from digcon.engine import EngineResult
from digcon.reporting import csv_tables, json_report, markdown

from .. import state
from digcon.domain.action_plan import title as finding_title
from ..labels import (
    MITIGATION_TITLE,
    NAV_LABELS,
    OUTCOME_TEXT,
    OUTCOME_TITLES,
    PHASE_TITLES,
    RECOMMENDATION_NOTE,
    REVIEW_TITLE,
    RISKS_TITLE,
    RULES_TITLE,
    workbook_text,
)
from ..style import OUTCOME_COLOUR, counters, outcome_banner, risk_matrix

GOVERNANCE_FIELDS = {
    "G01": "g01_decision",
    "G02": "g02_decision_maker",
    "G03": "g03_review_date",
    "G04": "g04_conditions",
    "G05": "g05_reasoning",
}


def _describe(cfg: ConfigBundle, ident: str) -> str:
    """ID plus what it names: the question, the catalogue measure or the right at risk."""
    for lookup, text in ((cfg.question, lambda x: x.text), (cfg.mitigation, lambda x: x.measure),
                         (cfg.risk, lambda x: x.right.split(";")[0])):
        try:
            return f"{ident} — {_short(text(lookup(ident)))}"
        except KeyError:
            continue
    return ident


def _short(text: str, limit: int = 80) -> str:
    return text if len(text) <= limit else text[:limit].rsplit(" ", 1)[0].rstrip(",;:(") + "…"


def _section_of(cfg: ConfigBundle, rule_id: str, ident: str | None) -> str:
    """Where the user acts on a finding: the question's section, the module of an element, measure or risk."""
    if ident:
        try:
            return PHASE_TITLES[cfg.question(ident).phase]
        except KeyError:
            pass
        if ident.startswith("MIT-"):
            return MITIGATION_TITLE
        if ident.startswith("RISK-"):
            return RISKS_TITLE
        if ident.startswith("HS"):
            return REVIEW_TITLE
    return REVIEW_TITLE if rule_id.startswith("HS") else RULES_TITLE


# What stands between the user and a better outcome, in precedence order (OUT-04 → OUT-02).
_NEXT = (
    ("evidence_gaps", "Evidence gaps", "violet", "Keep the outcome at O4 until resolved."),
    ("open_remediations", "Open remediations", "orange", "Keep the outcome at O3 until resolved."),
    ("open_conditions", "Conditions", "blue", "Remain attached to an O2 outcome."),
    ("pending_reviews", "Legal reviews pending", "gray", "Do not change the outcome by themselves."),
    ("verification_requests", "To be verified", "gray", "Do not change the outcome."),
)


def _open_plan(rule_id):
    from ..finding_navigation import open_finding
    open_finding(rule_id)


def _next_steps(cfg: ConfigBundle, result: EngineResult) -> None:
    with st.container(border=True):
        st.subheader("What to do next")
        if not any(getattr(result, attr) for attr, *_ in _NEXT):
            st.caption("Nothing open: no gap, remediation, condition, pending review or verification request.")
            return
        for attr, title, colour, effect in _NEXT:
            findings = getattr(result, attr)
            if not findings:
                continue
            st.markdown(f"**{title}** :{colour}-badge[{len(findings)}] :gray[{effect}]")
            for i, f in enumerate(findings):
                target = _section_of(cfg, f.rule_id, f.ids[0] if f.ids else None)
                text_col, go_col = st.columns([6, 1], vertical_alignment="center")
                items = " · ".join(_describe(cfg, x) for x in f.ids)
                text_col.markdown(f"**{finding_title(f.rule_id)}**")
                with text_col.expander("Technical finding details"):
                    st.write(f.message)
                    st.caption(f"{f.rule_id} · {items}")
                go_col.button("Work on this", key=f"next.{attr}.{i}", on_click=_open_plan,
                              args=(f.rule_id,), icon=":material/arrow_forward:", type="tertiary",
                              help=f"Open {NAV_LABELS[target]}")


def _risk_tab(cfg: ConfigBundle, result: EngineResult) -> None:
    if not result.risks:
        st.caption(f"No risk included yet ({RISKS_TITLE}).")
        return
    stored = state.store()["risks"]
    points = {
        r: (v.severity, Probability(stored[r]["probability"]) if stored[r].get("probability") else None,
            v.residual_severity,
            Probability(stored[r]["residual_probability"]) if v.residual and stored[r].get("residual_probability") else None)
        for r, v in result.risks.items()
    }
    st.markdown(risk_matrix(points, cfg.risks.calibration.matrix), unsafe_allow_html=True)
    st.caption("Solid chip: initial risk. Dashed chip: residual risk, shown only after a verified mitigation.")
    st.dataframe(
        pd.DataFrame(
            [
                {"Risk": r,
                 "Initial": label(v.initial) if v.initial else "—",
                 "Residual": label(v.residual) if v.residual else "— (not verified)",
                 "Severity": label(v.severity) if v.severity else "—",
                 "Right": cfg.risk(r).right.split(";")[0][:70],
                 "Reassess (SEP)": "Yes" if v.to_reassess else "—"}
                for r, v in result.risks.items()
            ]
        ),
        width="stretch",
        hide_index=True,
    )


def render(cfg: ConfigBundle, result: EngineResult) -> None:
    from digcon.domain.review_progress import stop_progress
    opened = [h for h, v in result.hard_stops.items() if stop_progress(v)[1]]
    st.markdown(outcome_banner(result.outcome, OUTCOME_TITLES[result.outcome], OUTCOME_TEXT[result.outcome]),
                unsafe_allow_html=True)
    st.markdown(f":material/info: **{RECOMMENDATION_NOTE}**")
    with st.expander("Technical decision details"):
        st.caption(f"Rule {result.outcome_rule} · precedence O5 → O4 → O3 → O2 → O1 · logic version {result.workbook_version}.")
    st.markdown(counters([
        ("Evidence gaps", len(result.evidence_gaps)),
        ("Open remediations", len(result.open_remediations)),
        ("Conditions", len(result.open_conditions)),
        ("Stop checks needing attention", len(opened)),
        ("Legal reviews pending", len(result.pending_reviews)),
    ]), unsafe_allow_html=True)

    for w in result.warnings:
        st.warning(w)

    _next_steps(cfg, result)

    tab_risk, tab_hs, tab_prop, tab_mit, tab_audit = st.tabs(
        ["Fundamental rights risks", "Stop conditions", "Proportionality", "Safeguards and mitigation", "Audit trail"]
    )
    with tab_risk:
        _risk_tab(cfg, result)
    with tab_hs:
        st.dataframe(
            pd.DataFrame(
                [
                    {"HS": h, "Opened": v.opened, "State": v.state.value, "Legal review": v.gate.value,
                     "Elements": ", ".join(f"{k.split('.')[1]}={s.value}" for k, s in v.elements.items())}
                    for h, v in result.hard_stops.items()
                ]
            ),
            width="stretch",
            hide_index=True,
        )
    with tab_prop:
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
            st.caption("The tool never concludes 'proportionate' or 'disproportionate': normative balancing stays with legal review.")
        else:
            st.caption("No proportionality check applicable yet.")
    with tab_mit:
        activated = [m for m in state.assessment().mitigations.values() if m.activated]
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
    with tab_audit:
        if result.audit_defects:
            st.error("Audit defects: " + "; ".join(result.audit_defects))
        with st.expander(f"Audit trail ({len(result.audit_trail)} events)", expanded=True):
            st.dataframe(
                pd.DataFrame(
                    [
                        {"Event": e.event_id, "Module": e.module.value, "Rule": e.rule_id or "", "Output": e.engine_output or "",
                         "Inputs": ", ".join(e.input_ids), "Evidence": ", ".join(e.evidence_refs),
                         "Human review": e.human_gate.value if e.human_gate else "", "Parent": e.parent_event_id or ""}
                        for e in result.audit_trail
                    ]
                ),
                width="stretch",
                hide_index=True,
            )
    downloads(cfg, result, "result")


def downloads(cfg: ConfigBundle, result: EngineResult, where: str) -> None:
    """The report of this run: Markdown to read, JSON with the full audit trail, CSV tables."""
    current = state.assessment()
    name = re.sub(r"[^A-Za-z0-9._-]+", "-", current.assessment_id).strip("-") or "assessment"
    with st.container(border=True):
        st.subheader("Download the report")
        st.caption("The outcome, what to do next, every answer, the registers, the governance decision and the "
                   "audit trail of this run. The JSON report can also be loaded in section 1.0 to resume.")
        with st.container(horizontal=True, gap="small"):
            st.download_button("Report (Markdown)", markdown.build(cfg, current, result),
                               file_name=f"{name}-report.md", mime="text/markdown", key=f"report.md.{where}",
                               icon=":material/description:", type="primary")
            st.download_button("Report (JSON)", json_report.dumps(current, result),
                               file_name=f"{name}-report.json", mime="application/json", key=f"report.json.{where}",
                               icon=":material/data_object:")
            with st.popover("Tables (CSV)", icon=":material/table_view:"):
                for label_, data, file_ in (
                    ("Fundamental rights risks", csv_tables.risk_register(cfg, current, result), "risk-register"),
                    ("Safeguards and mitigation", csv_tables.mitigation_plan(cfg, current), "mitigation-plan"),
                    ("Audit trail", csv_tables.audit_trail(result), "audit-trail"),
                ):
                    st.download_button(label_, data, file_name=f"{name}-{file_}.csv", mime="text/csv",
                                       key=f"report.csv.{file_}.{where}", icon=":material/download:", width="stretch")


def _sync_governance() -> None:
    gov = {attr: (st.session_state.get(f"w.gov.{gid}") or "").strip() or None for gid, attr in GOVERNANCE_FIELDS.items()}
    state.store()["governance"] = gov


def render_governance(cfg: ConfigBundle, result: EngineResult) -> None:
    st.markdown(
        f"Recommended outcome: :{OUTCOME_COLOUR[result.outcome]}-badge[{OUTCOME_TITLES[result.outcome]}] "
        f"(rule {result.outcome_rule})."
    )
    st.markdown(
        "The recommended outcome is a recommendation of the tool. The final decision is the organisation's: it is "
        "recorded by the responsible person or body, and the tool never fills these fields (SYS-03)."
    )
    gov = state.store()["governance"]
    with st.container(border=True):
        for g in cfg.questions.governance_fields:
            key = f"w.gov.{g.id}"
            state.seed(key, gov.get(GOVERNANCE_FIELDS[g.id]) or "")
            st.text_input(f"{g.field} `{g.id}`", key=key, help=workbook_text(g.id, "purpose", g.purpose),
                          on_change=_sync_governance)
    st.caption("To reassess later, save progress (left menu) and load the file in section 1.0 when the review date or a trigger arrives.")
    downloads(cfg, result, "governance")
