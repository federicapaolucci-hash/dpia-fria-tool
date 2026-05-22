import streamlit as st

st.set_page_config(
    page_title="DPIA+ FRIA Tool",
    layout="wide"
)

st.title("DPIA+ / FRIA Legal Risk Selection Tool")

st.write(
    "Prototype for integrating DPIA, Article 9 AI Act and Article 27 AI Act."
)

project_name = st.text_input(
    "Project name",
    "Recruitment AI Pilot"
)

context = st.selectbox(
    "Context",
    [
        "Employment/HR",
        "Education",
        "Credit/insurance",
        "Welfare/public services",
        "Healthcare",
        "Justice/policing/migration",
        "Platforms/content",
        "Other"
    ]
)

action = st.selectbox(
    "System action",
    [
        "Scoring/ranking",
        "Classification",
        "Recommendation",
        "Exclusion/de-prioritisation",
        "Monitoring/surveillance",
        "Risk prediction",
        "Other"
    ]
)

if st.button("Generate preliminary assessment"):

    risks = []

    if context == "Employment/HR":
        risks.extend([
            "Non-discrimination",
            "Access to work",
            "Privacy and data protection",
            "Contestability",
            "Human oversight"
        ])

    if action == "Monitoring/surveillance":
        risks.extend([
            "Privacy",
            "Chilling effect",
            "Autonomy",
            "Proportionality"
        ])

    st.subheader("Preliminary risks")

    for r in sorted(set(risks)):
        st.write("-", r)

    if not risks:
        st.info("Manual assessment required.")