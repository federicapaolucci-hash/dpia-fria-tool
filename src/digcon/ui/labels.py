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
    "Research prototype — for academic and sandbox testing purposes only. "
    "Do not enter personal data, confidential DPIAs, trade secrets or sensitive organisational information."
)

METHODOLOGY = """
This tool is a **research prototype** developed for the DIGCON Fundamental Rights Assessment Sandbox.

It uses the **DPIA as the common methodological backbone**: every assessment follows the same core path
(INTRO → WHAT → HOW → WHY). **Article 9 and Article 27 AI Act remain distinct obligations** and open only after scoping:

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

PHASE_TITLES = {
    Phase.INTRO: "1. Introduction and scoping",
    Phase.WHAT: "2. What — purpose, scope and system context",
    Phase.HOW: "3. How — decision-making, oversight, contestability",
    Phase.WHY: "4. Why — legal basis, data, proportionality",
    Phase.PROVIDER: "5A. Provider add-on — Article 9 AI Act",
    Phase.DEPLOYER: "5B. Deployer add-on — Article 27 AI Act (FRIA)",
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

START_TITLE = "0. Start"
RESULT_TITLE = "Result"
REVIEW_TITLE = "6. Hard stops and reviews"
RISKS_TITLE = "7. Risk register"
MITIGATION_TITLE = "8. Mitigation plan"
SEP_TITLE = "9. Stakeholder engagement"

# Notes shown under specific questions. Interface guidance only: they change no logic.
QUESTION_NOTES = {
    "C05": "This role opens the AI Act add-ons: Provider → Article 9 (5A); Deployer → Article 27 (5B, once D00 = YES); "
           "Joint → both. The system must also be HIGH RISK = YES (section 2).",
    "C06": "For the record only: it does not open any add-on. The routing role is C05.",
    "FOLLOW": "YES opens the add-on(s) for the role chosen in C05 (section 1).",
    "D00": "YES opens the Article 27 questions D01–D10.",
}


def subsection(name: str) -> str:
    return SUBSECTIONS.get(name, name)
