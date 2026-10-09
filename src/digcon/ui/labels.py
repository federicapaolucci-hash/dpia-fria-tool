"""Interface texts that the workbook does not provide. Enum labels come from digcon.domain.enums.label."""

from __future__ import annotations

from digcon.domain.enums import Outcome, Phase

APP_TITLE = "DPIA-based Fundamental Rights Assessment Tool"
APP_CAPTION = (
    "A DPIA-based workflow for identifying fundamental-rights risks, "
    "with role-specific AI Act add-ons for providers and deployers."
)
FOOTER = "DIGCON — FIS-funded project, Baffi Centre, Bocconi University · All rights reserved"
DISCLAIMER = (
    "**Research prototype** — for academic and sandbox testing purposes only. "
    "Do not enter personal data, confidential DPIAs, trade secrets or sensitive organisational information."
)

METHODOLOGY = """
This tool is a **research prototype** developed for the DIGCON Fundamental Rights Assessment Sandbox.

It uses the **DPIA as the common methodological backbone**. The assessment runs in four steps:

1. **Core assessment**, common to providers and deployers (INTRO → WHAT → HOW → WHY);
2. **role-specific add-ons**, opened by the scoping answers;
3. **transversal modules**: stakeholder engagement, risk register, rules and scrutiny, mitigation plan, hard stop gate;
4. **recommended outcome** (O1–O5), then the **final governance decision**.

**Article 9 and Article 27 AI Act remain distinct obligations** and open only after scoping:

- the **Article 9 provider add-on** opens when the system is high-risk and the role is Provider or Joint;
- the **Article 27 deployer add-on** opens when the system is high-risk, the role is Deployer or Joint and Article 27 applies.

Answers feed a deterministic decision engine (DIGCON T17). **Unknown, not applicable and not owned are never treated as "No"**:
they produce an evidence gap or a verification request. Risks are calibrated from scale, scope, reversibility and probability;
residual risk is recorded only after a mitigation has been verified effective.

**The engine does not decide whether a measure is proportionate.** Proportionality checks return a structured status;
normative balancing is referred to human legal review. A **hard stop (O5)** requires every constituent element to be
established and confirmed by a legal reviewer — high risk alone never produces O5.

The recommended outcome (O1–O5) is **not the final governance decision**, which is recorded separately by the responsible body.
"""

# The four steps of 00_MAPPA_FLUSSO: common core, add-ons opened after scoping, transversal modules, convergence.
STEP_CORE = "Step 1 — Core assessment"
STEP_ADDONS = "Step 2 — Role-specific add-ons"
STEP_ANALYSIS = "Step 3 — Risk analysis and safeguards"
STEP_OUTCOME = "Step 4 — Outcome and governance"
STEP_TEXT = {
    STEP_CORE: "The common path for providers and deployers: INTRO → WHAT → HOW → WHY. No add-on replaces these questions.",
    STEP_ADDONS: "Opened only after scoping: Article 9 for providers, Article 27 (FRIA) for deployers, both for joint roles. "
                 "Not high-risk: the add-ons stay closed and the assessment continues on the core.",
    STEP_ANALYSIS: "Transversal modules fed by steps 1 and 2: stakeholder engagement, risk register, rules and scrutiny, "
                   "mitigation plan and the hard stop gate.",
    STEP_OUTCOME: "The recommended outcome (O1–O5) converges from everything above. The final governance decision is "
                  "recorded separately by the responsible body.",
}

PHASE_TITLES = {
    Phase.INTRO: "1.1 Introduction and scoping",
    Phase.WHAT: "1.2 What — purpose, scope and system context",
    Phase.HOW: "1.3 How — decision-making, oversight, contestability",
    Phase.WHY: "1.4 Why — legal basis, data, proportionality",
    Phase.PROVIDER: "2.1 Provider add-on — Article 9 AI Act",
    Phase.DEPLOYER: "2.2 Deployer add-on — Article 27 AI Act (FRIA)",
}

SUBSECTIONS = {"Scoping e ruoli": "Scoping and roles"}

OUTCOME_TITLES = {
    Outcome.O1: "O1 — Proceed",
    Outcome.O2: "O2 — Proceed with conditions",
    Outcome.O3: "O3 — Revision required",
    Outcome.O4: "O4 — Assessment incomplete (evidence gap)",
    Outcome.O5: "O5 — Not proceedable under current conditions",
}
OUTCOME_TEXT = {
    Outcome.O1: "No hard stop, material evidence gap, unresolved remediation or restrictive condition. Ordinary monitoring and review may remain.",
    Outcome.O2: "Only explicit pilot / deployment / continuous conditions remain. Proceed with those conditions.",
    Outcome.O3: "At least one required remediation is still open, failed or not verified. Revise before proceeding.",
    Outcome.O4: "Material information needed for a required conclusion is missing or unknown. Complete the assessment.",
    Outcome.O5: "At least one hard stop (HS01–HS09) is fully established and confirmed by legal review. A mitigation plan cannot override it.",
}

ANSWERED = "ANSWERED"

START_TITLE = "1.0 Start — new or saved assessment"
ROUTING_TITLE = "2.0 Routing after scoping"
SEP_TITLE = "3.1 Stakeholder engagement (SEP)"
RISKS_TITLE = "3.2 Risk register"
RULES_TITLE = "3.3 Rules and scrutiny"
MITIGATION_TITLE = "3.4 Mitigation plan"
REVIEW_TITLE = "3.5 Hard stop gate"
RESULT_TITLE = "4.1 Recommended outcome"
GOVERNANCE_TITLE = "4.2 Final governance decision"

# Notes shown under specific questions. Interface guidance only: they change no logic.
QUESTION_NOTES = {
    "C05": "Once the system is high-risk (HIGH RISK = YES, section 1.2), this role opens the step 2 add-ons: "
           "Provider → Article 9 (2.1); Deployer → Article 27 (2.2, after D00 = YES); Joint → both.",
    "C06": "For the record only: it does not open any add-on. The routing role is C05.",
    "FOLLOW": "YES opens the step 2 add-on(s) for the role chosen in C05 (section 1.1).",
    "D00": "YES opens the Article 27 questions D01–D10.",
    "C43": "Effectiveness evidence only: VERIFIED EFFECTIVE does not lower any risk by itself. Residual risk is recalculated "
           "in the risk register (3.2), after a linked mitigation is verified.",
    "C48": "Effectiveness evidence only: VERIFIED EFFECTIVE does not lower any risk by itself. Residual risk is recalculated "
           "in the risk register (3.2), after a linked mitigation is verified.",
    "C34": "Imported from a prior DPIA or impact assessment: it does not override the DIGCON calibration. N/A if none applies.",
    "C35": "Imported evidence, not the DIGCON residual-risk calculation. N/A if no prior assessment applies.",
    "D04": "Select concrete risks from the DIGCON catalogue (RSEL-01). Rate them in the risk register (3.2).",
}


def subsection(name: str) -> str:
    return SUBSECTIONS.get(name, name)


# Short names of the sections in the left menu.
NAV_LABELS = {
    START_TITLE: "1.0  Start",
    PHASE_TITLES[Phase.INTRO]: "1.1  Introduction and scoping",
    PHASE_TITLES[Phase.WHAT]: "1.2  What",
    PHASE_TITLES[Phase.HOW]: "1.3  How",
    PHASE_TITLES[Phase.WHY]: "1.4  Why",
    ROUTING_TITLE: "2.0  Routing",
    PHASE_TITLES[Phase.PROVIDER]: "2.1  Provider · Article 9",
    PHASE_TITLES[Phase.DEPLOYER]: "2.2  Deployer · Article 27 FRIA",
    SEP_TITLE: "3.1  Stakeholder engagement",
    RISKS_TITLE: "3.2  Risk register",
    RULES_TITLE: "3.3  Rules and scrutiny",
    MITIGATION_TITLE: "3.4  Mitigation plan",
    REVIEW_TITLE: "3.5  Hard stop gate",
    RESULT_TITLE: "4.1  Recommended outcome",
    GOVERNANCE_TITLE: "4.2  Governance decision",
}
