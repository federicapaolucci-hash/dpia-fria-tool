import json
from datetime import datetime

import pandas as pd
import streamlit as st


# ---------------------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------------------

st.set_page_config(
    page_title="DPIA-based Fundamental Rights Assessment Tool",
    layout="wide"
)

st.title("DPIA-based Fundamental Rights Assessment Tool")
st.caption(
    "A DPIA-based workflow for identifying, reasoning about, and documenting "
    "fundamental-rights risks in AI and data-driven decision-making."
)


# ---------------------------------------------------------------------
# OPTIONS
# ---------------------------------------------------------------------

FILER_ROLES = [
    "Controller / data protection team",
    "Provider",
    "Deployer",
    "Joint assessment team",
    "Other"
]

CONTEXTS = [
    "Employment/HR",
    "Education",
    "Credit/insurance",
    "Welfare/public services",
    "Healthcare",
    "Justice/policing/migration",
    "Platforms/content",
    "Marketing/CRM",
    "Physical security/access",
    "Other"
]

ACTIONS = [
    "Scoring/ranking",
    "Classification",
    "Recommendation",
    "Exclusion/de-prioritisation",
    "Monitoring/surveillance",
    "Identity verification/biometrics",
    "Content moderation/ranking",
    "Risk prediction",
    "Content generation",
    "Other"
]

DATA_CATEGORIES = [
    "No personal data",
    "Common personal data",
    "Special categories of data",
    "Biometric data",
    "Inferred/profiling data",
    "Behavioural data",
    "Data from multiple sources",
    "Proxy variables",
    "Children's data"
]

DECISION_EFFECTS = [
    "No significant effect",
    "Support to human decision",
    "Legal or similarly significant effect",
    "Access/exclusion/priority in services or opportunities"
]

GROUPS = [
    "Workers/candidates",
    "Students",
    "Patients",
    "Welfare beneficiaries",
    "Consumers",
    "Children",
    "Migrants/asylum seekers",
    "Persons with disabilities",
    "Protected or vulnerable groups",
    "General public"
]

LEGAL_BASES = [
    "To be determined",
    "Consent",
    "Contract",
    "Legal obligation",
    "Public interest",
    "Legitimate interest",
    "Vital interests",
    "Not applicable / to be verified"
]

YES_NO_OPTIONS = [
    "Yes",
    "No",
    "Partly",
    "To be verified"
]


# ---------------------------------------------------------------------
# FUNDAMENTAL RIGHTS RISK CATALOGUE
# ---------------------------------------------------------------------

RISK_CATALOG = [
    {
        "id": "FR1",
        "risk": "Excessive or disproportionate data processing",
        "rights": [
            "Privacy",
            "Data protection",
            "Informational self-determination"
        ],
        "triggers": {
            "data_categories": [
                "Common personal data",
                "Special categories of data",
                "Biometric data",
                "Inferred/profiling data",
                "Behavioural data",
                "Data from multiple sources",
                "Children's data"
            ]
        },
        "mechanisms": [
            "Data minimisation failure",
            "Purpose creep",
            "Invisible inference",
            "Excessive retention",
            "Combination of datasets beyond reasonable expectations"
        ],
        "questions": [
            "Are all data strictly necessary for the stated purpose?",
            "Are inferred or derived data used?",
            "Is there a less intrusive alternative?",
            "Can the person exercise access, rectification, objection and restriction?"
        ],
        "safeguards": [
            "Data minimisation",
            "Purpose limitation",
            "Retention limits",
            "Clear information notice",
            "Effective data subject rights"
        ]
    },
    {
        "id": "FR2",
        "risk": "Direct, indirect or proxy discrimination",
        "rights": [
            "Equality",
            "Non-discrimination",
            "Equal access to opportunities"
        ],
        "triggers": {
            "contexts": [
                "Employment/HR",
                "Education",
                "Credit/insurance",
                "Welfare/public services",
                "Healthcare",
                "Justice/policing/migration"
            ],
            "actions": [
                "Scoring/ranking",
                "Classification",
                "Exclusion/de-prioritisation",
                "Risk prediction"
            ],
            "data_categories": [
                "Special categories of data",
                "Biometric data",
                "Proxy variables",
                "Inferred/profiling data"
            ]
        },
        "mechanisms": [
            "Historical bias",
            "Proxy variables",
            "Unequal error rates",
            "Under-representation of groups",
            "Disparate impact"
        ],
        "questions": [
            "Are protected attributes or proxy variables used?",
            "Has the system been tested across affected groups?",
            "Do historical data reproduce previous inequalities?",
            "Does impact vary by gender, age, ethnic origin, disability, territory or socio-economic status?"
        ],
        "safeguards": [
            "Bias testing",
            "Subgroup analysis",
            "Independent audit",
            "Control of proxy variables",
            "Effective human review"
        ]
    },
    {
        "id": "FR3",
        "risk": "Decision-making opacity and insufficient explanation",
        "rights": [
            "Transparency",
            "Effective remedy",
            "Defence rights",
            "Good administration"
        ],
        "triggers": {
            "actions": [
                "Scoring/ranking",
                "Classification",
                "Recommendation",
                "Risk prediction",
                "Exclusion/de-prioritisation"
            ],
            "decision_effects": [
                "Legal or similarly significant effect",
                "Access/exclusion/priority in services or opportunities"
            ]
        },
        "mechanisms": [
            "Opaque criteria",
            "Unexplained score",
            "Unclear role of automation",
            "Inability to understand the reason for the outcome"
        ],
        "questions": [
            "Does the person know that the system is used?",
            "Can the essential logic be explained in understandable terms?",
            "Can the person know the relevant criteria?",
            "Does the explanation enable concrete contestation?"
        ],
        "safeguards": [
            "Individual notice",
            "Understandable explanation",
            "Documentation of decision criteria",
            "Appeal channel",
            "Decision logging"
        ]
    },
    {
        "id": "FR4",
        "risk": "Ineffective or merely formal human oversight",
        "rights": [
            "Accountability",
            "Effective remedy",
            "Due process",
            "Good administration"
        ],
        "triggers": {
            "actions": [
                "Recommendation",
                "Scoring/ranking",
                "Risk prediction",
                "Exclusion/de-prioritisation"
            ],
            "decision_effects": [
                "Support to human decision",
                "Legal or similarly significant effect",
                "Access/exclusion/priority in services or opportunities"
            ]
        },
        "mechanisms": [
            "Automation bias",
            "Rubber-stamping",
            "Lack of authority to override",
            "Lack of time or competence for review"
        ],
        "questions": [
            "Can the human reviewer genuinely depart from the system output?",
            "Does the reviewer have time, competence and authority?",
            "Are automation bias and rubber-stamping prevented?",
            "Is the human review documented?"
        ],
        "safeguards": [
            "Reviewer training",
            "Override right",
            "Documented review",
            "Anti-automation-bias procedure",
            "Periodic control of confirmed decisions"
        ]
    },
    {
        "id": "FR5",
        "risk": "Exclusion from essential goods, services or opportunities",
        "rights": [
            "Access to services",
            "Substantive equality",
            "Dignity",
            "Effective remedy"
        ],
        "triggers": {
            "contexts": [
                "Employment/HR",
                "Education",
                "Credit/insurance",
                "Welfare/public services",
                "Healthcare",
                "Justice/policing/migration"
            ],
            "actions": [
                "Exclusion/de-prioritisation",
                "Scoring/ranking",
                "Classification"
            ],
            "decision_effects": [
                "Access/exclusion/priority in services or opportunities",
                "Legal or similarly significant effect"
            ]
        },
        "mechanisms": [
            "Denial of access",
            "De-prioritisation",
            "Loss of opportunity",
            "Irreversible or time-sensitive harm"
        ],
        "questions": [
            "Can the output restrict access to an essential service or opportunity?",
            "Is there a non-automated alternative channel?",
            "Can an error be corrected in due time?",
            "Is the harm reversible?"
        ],
        "safeguards": [
            "Alternative channel",
            "Urgent review",
            "Human fallback",
            "Outcome notification",
            "Remedy procedure"
        ]
    },
    {
        "id": "FR6",
        "risk": "Disproportionate surveillance and chilling effect",
        "rights": [
            "Privacy",
            "Personal liberty",
            "Freedom of expression",
            "Freedom of association",
            "Dignity"
        ],
        "triggers": {
            "actions": [
                "Monitoring/surveillance",
                "Identity verification/biometrics",
                "Content moderation/ranking"
            ],
            "data_categories": [
                "Biometric data",
                "Behavioural data",
                "Data from multiple sources",
                "Inferred/profiling data"
            ]
        },
        "mechanisms": [
            "Continuous observation",
            "Behavioural adaptation due to being monitored",
            "Excessive identification",
            "Function creep"
        ],
        "questions": [
            "Is monitoring continuous or systematic?",
            "May persons change behaviour because they feel observed?",
            "Is the measure strictly necessary?",
            "Are there temporal and functional limits?"
        ],
        "safeguards": [
            "Temporal limitation",
            "Purpose limitation",
            "Reduced data granularity",
            "Enhanced transparency",
            "Monitoring audit"
        ]
    },
    {
        "id": "FR7",
        "risk": "Dignity, autonomy and stigmatisation",
        "rights": [
            "Dignity",
            "Individual autonomy",
            "Reputation",
            "Free development of personality"
        ],
        "triggers": {
            "actions": [
                "Risk prediction",
                "Scoring/ranking",
                "Classification",
                "Monitoring/surveillance"
            ],
            "data_categories": [
                "Inferred/profiling data",
                "Behavioural data",
                "Biometric data"
            ]
        },
        "mechanisms": [
            "Reduction of the person to a score",
            "Stigmatising labels",
            "Predictive categorisation",
            "Loss of self-determination"
        ],
        "questions": [
            "Is the person reduced to a score, profile or category?",
            "Does the system assign reliability, risk, productivity or social value?",
            "Can the label generate stigma?",
            "Can the person correct or contest the classification?"
        ],
        "safeguards": [
            "Limit categories",
            "Avoid stigmatising labels",
            "Individual explanation",
            "Profile correction",
            "Qualified human review"
        ]
    },
    {
        "id": "FR8",
        "risk": "Freedom of expression, information and pluralism",
        "rights": [
            "Freedom of expression",
            "Freedom of information",
            "Pluralism",
            "Contestability"
        ],
        "triggers": {
            "contexts": [
                "Platforms/content"
            ],
            "actions": [
                "Content moderation/ranking",
                "Recommendation",
                "Exclusion/de-prioritisation",
                "Content generation"
            ]
        },
        "mechanisms": [
            "Over-removal",
            "Under-removal",
            "Opacity of ranking",
            "Distortion of visibility",
            "Chilling effect"
        ],
        "questions": [
            "Does the system remove, downrank or order content?",
            "Can it produce over-removal or under-removal?",
            "Does it affect the visibility of groups, opinions or information?",
            "Is there an effective and timely appeal?"
        ],
        "safeguards": [
            "Transparent ranking/moderation criteria",
            "User notice",
            "Appeal",
            "Audit of over-removal and under-removal",
            "Monitoring of systemic effects"
        ]
    },
    {
        "id": "FR9",
        "risk": "Accountability gap and unclear allocation of responsibilities",
        "rights": [
            "Accountability",
            "Effective remedy",
            "Effective protection of rights"
        ],
        "triggers": {
            "actions": [
                "Scoring/ranking",
                "Classification",
                "Recommendation",
                "Risk prediction",
                "Content generation",
                "Other"
            ]
        },
        "mechanisms": [
            "Unclear role allocation",
            "Responsibility shifting",
            "Lack of internal owner",
            "Fragmented provider-deployer-controller responsibilities"
        ],
        "questions": [
            "Is it clear who decides?",
            "Is it clear who controls?",
            "Is it clear who is responsible for error or harm?",
            "Are provider, deployer, controller, processor and internal owners distinguished?"
        ],
        "safeguards": [
            "Accountability matrix",
            "Internal owners",
            "Logging",
            "Audit trail",
            "Escalation procedure"
        ]
    },
    {
        "id": "FR10",
        "risk": "Ineffective remedy or impossibility of contestation",
        "rights": [
            "Effective remedy",
            "Due process",
            "Defence rights",
            "Good administration"
        ],
        "triggers": {
            "actions": [
                "Scoring/ranking",
                "Classification",
                "Exclusion/de-prioritisation",
                "Risk prediction",
                "Content moderation/ranking"
            ],
            "decision_effects": [
                "Legal or similarly significant effect",
                "Access/exclusion/priority in services or opportunities"
            ]
        },
        "mechanisms": [
            "No complaint channel",
            "Complaint without effect",
            "No human review",
            "No reasons given",
            "Excessive burden on affected person"
        ],
        "questions": [
            "Can the person contest the outcome?",
            "Is the complaint channel simple, accessible and timely?",
            "Can contestation concretely change the outcome?",
            "Are response deadlines defined?"
        ],
        "safeguards": [
            "Complaint mechanism",
            "Human channel",
            "Response deadlines",
            "Reasoned outcome",
            "Possibility of review"
        ]
    }
]


# ---------------------------------------------------------------------
# FUNCTIONS
# ---------------------------------------------------------------------

def has_intersection(values, triggers):
    return bool(set(values).intersection(set(triggers)))


def is_provider_role(inputs):
    return (
        "Provider" in inputs["filer_role"]
        or "Joint assessment team" in inputs["filer_role"]
    )


def is_deployer_role(inputs):
    return (
        "Deployer" in inputs["filer_role"]
        or "Joint assessment team" in inputs["filer_role"]
    )


def activate_fundamental_rights_risks(inputs):
    activated = []

    for item in RISK_CATALOG:
        matched = []
        triggers = item["triggers"]

        if "contexts" in triggers and has_intersection(inputs["contexts"], triggers["contexts"]):
            matched.append("deployment context")

        if "actions" in triggers and has_intersection(inputs["actions"], triggers["actions"]):
            matched.append("system action")

        if "data_categories" in triggers and has_intersection(inputs["data_categories"], triggers["data_categories"]):
            matched.append("data category")

        if "decision_effects" in triggers and inputs["decision_effect"] in triggers["decision_effects"]:
            matched.append("effect on persons or opportunities")

        if matched:
            activated.append({
                "ID": item["id"],
                "Fundamental rights risk": item["risk"],
                "Rights involved": "; ".join(item["rights"]),
                "Legal mechanisms of harm": "; ".join(item["mechanisms"]),
                "Triggered by": ", ".join(matched),
                "Questions for legal analysis": " | ".join(item["questions"]),
                "Safeguards to test": " | ".join(item["safeguards"])
            })

    return activated


def compute_red_flags(inputs, risks):
    flags = []
    risk_ids = {risk["ID"] for risk in risks}

    significant_decision = inputs["decision_effect"] in [
        "Legal or similarly significant effect",
        "Access/exclusion/priority in services or opportunities"
    ]

    sensitive_data = {
        "Special categories of data",
        "Biometric data",
        "Children's data"
    }

    if not inputs["purpose"].strip():
        flags.append(("BLOCKING", "Purpose is missing or insufficiently specified."))

    if inputs["legal_basis"] in ["To be determined", "Not applicable / to be verified"]:
        flags.append(("BLOCKING", "Legal basis is not clearly identified."))

    if set(inputs["data_categories"]).intersection(sensitive_data) and inputs["data_necessary"] != "Yes":
        flags.append((
            "HIGH",
            "Sensitive, biometric or children's data are used without a strict necessity justification."
        ))

    if inputs["alternatives_assessed"] in ["No", "To be verified"]:
        flags.append((
            "HIGH",
            "Less intrusive alternatives have not been sufficiently assessed."
        ))

    if significant_decision and inputs["contestability"] != "Yes":
        flags.append((
            "BLOCKING",
            "Affected persons cannot effectively contest a significant outcome."
        ))

    if significant_decision and inputs["remedy_effectiveness"] in ["No", "To be verified"]:
        flags.append((
            "HIGH",
            "The remedy is not shown to be capable of changing the outcome."
        ))

    if significant_decision and inputs["human_oversight"] in ["Absent", "Merely formal", "To be verified"]:
        flags.append((
            "HIGH",
            "Human oversight is absent, merely formal or insufficiently demonstrated in a significant decision-making context."
        ))

    if not inputs["accountability_owner"].strip():
        flags.append((
            "HIGH",
            "Internal accountability owner is missing."
        ))

    if "FR2" in risk_ids and inputs["bias_control"] in ["No", "To be verified"]:
        flags.append((
            "HIGH",
            "Discrimination risk is present, but bias/proxy-control safeguards are not sufficiently demonstrated."
        ))

    if "FR10" in risk_ids and inputs["remedy_effectiveness"] != "Yes":
        flags.append((
            "HIGH",
            "A remedy risk is present, but remedy effectiveness is not demonstrated."
        ))

    if "FR5" in risk_ids and inputs["fallback_channel"] in ["No", "To be verified"]:
        flags.append((
            "HIGH",
            "Potential exclusion from services or opportunities is present without a reliable fallback channel."
        ))

    if is_provider_role(inputs):
        if "FR2" in risk_ids and inputs["subgroup_testing"] != "Yes":
            flags.append((
                "HIGH",
                "Provider-side add-on: discrimination risk without subgroup testing."
            ))

        if inputs["residual_risk_defined"] != "Yes":
            flags.append((
                "MEDIUM",
                "Provider-side add-on: residual risk is not clearly defined and documented."
            ))

        if inputs["misuse_assessed"] in ["No", "To be verified"]:
            flags.append((
                "MEDIUM",
                "Provider-side add-on: reasonably foreseeable misuse is not sufficiently assessed."
            ))

    if is_deployer_role(inputs):
        if inputs["affected_categories_described"] != "Yes":
            flags.append((
                "HIGH",
                "Deployer-side add-on: affected persons and groups are not sufficiently described in the deployment context."
            ))

        if inputs["monitoring"] != "Yes":
            flags.append((
                "MEDIUM",
                "Deployer-side add-on: post-deployment monitoring is not clearly established."
            ))

    return flags


def compute_scrutiny_level(inputs, flags, risks):
    score = 0

    high_contexts = {
        "Employment/HR",
        "Education",
        "Credit/insurance",
        "Welfare/public services",
        "Healthcare"
    }

    very_high_contexts = {
        "Justice/policing/migration"
    }

    vulnerable_groups = {
        "Children",
        "Migrants/asylum seekers",
        "Persons with disabilities",
        "Protected or vulnerable groups",
        "Welfare beneficiaries",
        "Patients"
    }

    sensitive_data = {
        "Special categories of data",
        "Biometric data",
        "Children's data"
    }

    if set(inputs["contexts"]).intersection(high_contexts):
        score += 2

    if set(inputs["contexts"]).intersection(very_high_contexts):
        score += 3

    if set(inputs["groups"]).intersection(vulnerable_groups):
        score += 3

    if set(inputs["data_categories"]).intersection(sensitive_data):
        score += 3

    if inputs["decision_effect"] in [
        "Legal or similarly significant effect",
        "Access/exclusion/priority in services or opportunities"
    ]:
        score += 3

    if len(risks) >= 5:
        score += 2

    if any(level == "BLOCKING" for level, _ in flags):
        score += 4

    if score >= 9:
        return "Very high"

    if score >= 6:
        return "High"

    if score >= 3:
        return "Medium"

    return "Low"


def compute_outcome(flags, scrutiny_level):
    levels = [level for level, _ in flags]

    if "BLOCKING" in levels:
        return "NO-GO / redesign required before deployment"

    if "HIGH" in levels:
        return "CONDITIONAL GO with mandatory safeguards and escalation"

    if scrutiny_level in ["High", "Very high"]:
        return "CONDITIONAL GO / enhanced human-rights review"

    if "MEDIUM" in levels:
        return "GO with documented review and monitoring"

    return "GO"


def build_report(inputs, risks, flags, scrutiny_level, outcome):
    is_provider = is_provider_role(inputs)
    is_deployer = is_deployer_role(inputs)

    report = []

    report.append("# DPIA-based Fundamental Rights Assessment Report")
    report.append("")
    report.append(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("")

    report.append("## 1. Assessment scope")
    report.append(f"- Project name: {inputs['project_name']}")
    report.append(f"- Organisation: {inputs['organisation']}")
    report.append(f"- Who is completing the assessment: {', '.join(inputs['filer_role'])}")
    report.append(f"- Accountability owner: {inputs['accountability_owner']}")
    report.append("")

    report.append("## 2. DPIA baseline")
    report.append(f"- Purpose: {inputs['purpose']}")
    report.append(f"- Legal basis: {inputs['legal_basis']}")
    report.append(f"- Data categories: {', '.join(inputs['data_categories'])}")
    report.append(f"- Data strictly necessary: {inputs['data_necessary']}")
    report.append("")

    report.append("## 3. Decision-making context")
    report.append(f"- Deployment context: {', '.join(inputs['contexts'])}")
    report.append(f"- System action: {', '.join(inputs['actions'])}")
    report.append(f"- Effect on persons, groups or opportunities: {inputs['decision_effect']}")
    report.append(f"- Affected persons or groups: {', '.join(inputs['groups'])}")
    report.append("")

    report.append("## 4. Necessity and proportionality")
    report.append(f"- Less intrusive alternatives assessed: {inputs['alternatives_assessed']}")
    report.append(f"- Necessity reasoning: {inputs['necessity_reasoning']}")
    report.append(f"- Proportionality reasoning: {inputs['proportionality_reasoning']}")
    report.append("")

    report.append("## 5. Fundamental rights safeguards")
    report.append(f"- Human oversight: {inputs['human_oversight']}")
    report.append(f"- Contestability: {inputs['contestability']}")
    report.append(f"- Remedy effectiveness: {inputs['remedy_effectiveness']}")
    report.append(f"- Fallback channel: {inputs['fallback_channel']}")
    report.append(f"- Bias/proxy-control safeguards: {inputs['bias_control']}")
    report.append(f"- Affected groups consulted: {inputs['affected_groups_consulted']}")
    report.append(f"- Governance notes: {inputs['governance_notes']}")
    report.append("")

    if is_provider:
        report.append("## 6A. Provider-side add-on")
        report.append(f"- Reasonably foreseeable misuse assessed: {inputs['misuse_assessed']}")
        report.append(f"- Subgroup testing: {inputs['subgroup_testing']}")
        report.append(f"- Residual risk defined and documented: {inputs['residual_risk_defined']}")
        report.append("")

    if is_deployer:
        report.append("## 6B. Deployer-side add-on")
        report.append(f"- Expected frequency of use: {inputs['deployment_frequency']}")
        report.append(f"- Affected categories described: {inputs['affected_categories_described']}")
        report.append(f"- Post-deployment monitoring: {inputs['monitoring']}")
        report.append("")

    report.append("## 7. Fundamental rights risks selected")

    if not risks:
        report.append("No risk automatically activated. Manual legal review is required.")
        report.append("")
    else:
        for risk in risks:
            report.append(f"### {risk['ID']} - {risk['Fundamental rights risk']}")
            report.append(f"- Rights involved: {risk['Rights involved']}")
            report.append(f"- Legal mechanisms of harm: {risk['Legal mechanisms of harm']}")
            report.append(f"- Triggered by: {risk['Triggered by']}")
            report.append(f"- Questions for legal analysis: {risk['Questions for legal analysis']}")
            report.append(f"- Safeguards to test: {risk['Safeguards to test']}")
            report.append("")

    report.append("## 8. Red flags")
    if not flags:
        report.append("No red flags detected.")
    else:
        for level, message in flags:
            report.append(f"- [{level}] {message}")
    report.append("")

    report.append("## 9. Scrutiny and recommended outcome")
    report.append(f"- Scrutiny level: {scrutiny_level}")
    report.append(f"- Recommended outcome: {outcome}")
    report.append("")

    report.append("## Methodological note")
    report.append(
        "This tool does not automate constitutional judgment. "
        "It automates the procedural conditions for better fundamental-rights reasoning: "
        "completeness, consistency, traceability, contestability and accountability. "
        "Provider-side and deployer-side regulatory modules are opened only when relevant to the role of the filer."
    )

    return "\n".join(report)


# ---------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------

with st.expander("Methodological logic", expanded=False):
    st.markdown(
        """
        This tool uses the **DPIA as the procedural baseline** and adds a deeper
        **fundamental-rights risk selection layer**.

        The assessment is structured around:
        - the decision-making context;
        - the persons and groups affected;
        - the legal mechanisms through which harm may occur;
        - necessity and proportionality;
        - safeguards, remedies and contestability.

        **Provider-side questions** are shown only when the filer is a provider
        or a joint assessment team.

        **Deployer-side questions** are shown only when the filer is a deployer
        or a joint assessment team.
        """
    )

with st.form("assessment_form"):
    st.header("1. Assessment scope")

    col1, col2 = st.columns(2)

    with col1:
        project_name = st.text_input("Project name", "Recruitment AI Pilot")
        organisation = st.text_input("Organisation", "Example organisation")
        filer_role = st.multiselect(
            "Who is completing this assessment?",
            FILER_ROLES,
            default=["Controller / data protection team"]
        )

    with col2:
        accountability_owner = st.text_input(
            "Accountability owner",
            "DPO / AI Governance Officer"
        )
        legal_basis = st.selectbox("Legal basis", LEGAL_BASES)
        data_necessary = st.selectbox(
            "Are data strictly necessary for the stated purpose?",
            YES_NO_OPTIONS
        )

    st.header("2. DPIA baseline")

    purpose = st.text_area(
        "Purpose of the processing / AI use",
        "",
        placeholder="Describe the specific purpose, context and expected outcome."
    )

    data_categories = st.multiselect(
        "Data categories",
        DATA_CATEGORIES,
        default=["Common personal data"]
    )

    st.header("3. Decision-making context")

    col3, col4 = st.columns(2)

    with col3:
        contexts = st.multiselect(
            "Deployment context",
            CONTEXTS,
            default=["Employment/HR"]
        )

        actions = st.multiselect(
            "System action",
            ACTIONS,
            default=["Scoring/ranking"]
        )

    with col4:
        decision_effect = st.selectbox(
            "Effect on persons, groups or opportunities",
            DECISION_EFFECTS
        )

        groups = st.multiselect(
            "Affected persons or groups",
            GROUPS,
            default=["Workers/candidates"]
        )

    st.header("4. Necessity and proportionality")

    col5, col6 = st.columns(2)

    with col5:
        alternatives_assessed = st.selectbox(
            "Have less intrusive alternatives been assessed?",
            YES_NO_OPTIONS
        )

        necessity_reasoning = st.text_area(
            "Necessity reasoning",
            "",
            placeholder=(
                "Why is this system, these data and this form of automation necessary? "
                "Could the same purpose be achieved with a less intrusive measure?"
            )
        )

    with col6:
        proportionality_reasoning = st.text_area(
            "Proportionality reasoning",
            "",
            placeholder=(
                "Which concrete benefits justify the risks? "
                "Who benefits, who bears the risk, and is the residual risk acceptable?"
            )
        )

    st.header("5. Fundamental rights safeguards and contestability")

    col7, col8 = st.columns(2)

    with col7:
        human_oversight = st.selectbox(
            "Is there meaningful human oversight?",
            ["Effective", "Merely formal", "Absent", "Not applicable", "To be verified"]
        )

        contestability = st.selectbox(
            "Can affected persons contest the outcome?",
            YES_NO_OPTIONS
        )

        remedy_effectiveness = st.selectbox(
            "Is the remedy capable of changing the outcome?",
            YES_NO_OPTIONS
        )

    with col8:
        fallback_channel = st.selectbox(
            "Is there a reliable non-automated or alternative channel where needed?",
            YES_NO_OPTIONS
        )

        bias_control = st.selectbox(
            "Are bias and proxy-discrimination safeguards demonstrated?",
            YES_NO_OPTIONS
        )

        affected_groups_consulted = st.selectbox(
            "Have affected groups or representatives been consulted?",
            ["Yes", "No", "Partly", "Not applicable", "To be verified"]
        )

    governance_notes = st.text_area(
        "Governance and accountability notes",
        "",
        placeholder=(
            "Who decides, who controls, who responds, who updates the assessment, "
            "and who is accountable for residual risk?"
        )
    )

    show_provider_module = (
        "Provider" in filer_role
        or "Joint assessment team" in filer_role
    )

    show_deployer_module = (
        "Deployer" in filer_role
        or "Joint assessment team" in filer_role
    )

    if show_provider_module:
        st.header("6A. Provider-side add-on")
        st.caption(
            "Opened because the filer includes a provider role. "
            "This section supports provider-side risk-management reasoning."
        )

        col9, col10 = st.columns(2)

        with col9:
            misuse_assessed = st.selectbox(
                "Has reasonably foreseeable misuse been assessed?",
                YES_NO_OPTIONS
            )

            subgroup_testing = st.selectbox(
                "Has testing been planned for affected subgroups?",
                ["Yes", "No", "Partly", "Not applicable", "To be verified"]
            )

        with col10:
            residual_risk_defined = st.selectbox(
                "Has residual risk been defined and documented?",
                YES_NO_OPTIONS
            )
    else:
        misuse_assessed = "Not applicable"
        subgroup_testing = "Not applicable"
        residual_risk_defined = "Not applicable"

    if show_deployer_module:
        st.header("6B. Deployer-side add-on")
        st.caption(
            "Opened because the filer includes a deployer role. "
            "This section supports context-specific deployment and FRIA reasoning."
        )

        col11, col12 = st.columns(2)

        with col11:
            deployment_frequency = st.selectbox(
                "Expected frequency of use",
                ["One-off", "Occasional", "Regular", "Continuous", "To be verified"]
            )

            affected_categories_described = st.selectbox(
                "Are categories of affected persons and groups described?",
                YES_NO_OPTIONS
            )

        with col12:
            monitoring = st.selectbox(
                "Is post-deployment monitoring planned?",
                YES_NO_OPTIONS
            )
    else:
        deployment_frequency = "Not applicable"
        affected_categories_described = "Not applicable"
        monitoring = "Not applicable"

    submitted = st.form_submit_button("Generate fundamental rights assessment")


if submitted:
    inputs = {
        "project_name": project_name,
        "organisation": organisation,
        "filer_role": filer_role,
        "accountability_owner": accountability_owner,
        "legal_basis": legal_basis,
        "data_necessary": data_necessary,
        "purpose": purpose,
        "data_categories": data_categories,
        "contexts": contexts,
        "actions": actions,
        "decision_effect": decision_effect,
        "groups": groups,
        "alternatives_assessed": alternatives_assessed,
        "necessity_reasoning": necessity_reasoning,
        "proportionality_reasoning": proportionality_reasoning,
        "human_oversight": human_oversight,
        "contestability": contestability,
        "remedy_effectiveness": remedy_effectiveness,
        "fallback_channel": fallback_channel,
        "bias_control": bias_control,
        "affected_groups_consulted": affected_groups_consulted,
        "governance_notes": governance_notes,
        "misuse_assessed": misuse_assessed,
        "subgroup_testing": subgroup_testing,
        "residual_risk_defined": residual_risk_defined,
        "deployment_frequency": deployment_frequency,
        "affected_categories_described": affected_categories_described,
        "monitoring": monitoring
    }

    risks = activate_fundamental_rights_risks(inputs)
    flags = compute_red_flags(inputs, risks)
    scrutiny_level = compute_scrutiny_level(inputs, flags, risks)
    outcome = compute_outcome(flags, scrutiny_level)
    report = build_report(inputs, risks, flags, scrutiny_level, outcome)

    st.session_state["last_assessment"] = {
        "inputs": inputs,
        "risks": risks,
        "flags": flags,
        "scrutiny_level": scrutiny_level,
        "outcome": outcome,
        "report": report
    }


# ---------------------------------------------------------------------
# OUTPUT
# ---------------------------------------------------------------------

if "last_assessment" in st.session_state:
    result = st.session_state["last_assessment"]

    st.divider()
    st.header("Assessment result")

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.metric("Fundamental-rights risks selected", len(result["risks"]))

    with col_b:
        st.metric("Red flags", len(result["flags"]))

    with col_c:
        st.metric("Scrutiny level", result["scrutiny_level"])

    st.subheader("Recommended outcome")
    st.markdown(f"**{result['outcome']}**")

    st.subheader("Red flags")

    if not result["flags"]:
        st.success("No red flags detected.")
    else:
        for level, message in result["flags"]:
            if level == "BLOCKING":
                st.error(f"{level}: {message}")
            elif level == "HIGH":
                st.warning(f"{level}: {message}")
            else:
                st.info(f"{level}: {message}")

    st.subheader("Fundamental rights risk register")

    if result["risks"]:
        df = pd.DataFrame(result["risks"])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No risk automatically activated. Manual legal review is required.")

    st.subheader("Download report")

    safe_file_name = (
        result["inputs"]["project_name"]
        .lower()
        .replace(" ", "_")
        .replace("/", "_")
    )

    st.download_button(
        "Download Markdown report",
        result["report"],
        file_name=f"{safe_file_name}_fundamental_rights_assessment.md",
        mime="text/markdown"
    )

    st.download_button(
        "Download JSON assessment",
        json.dumps(result, ensure_ascii=False, indent=2),
        file_name=f"{safe_file_name}_assessment.json",
        mime="application/json"
    )