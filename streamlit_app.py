import json
from datetime import datetime

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="DPIA+ FRIA Legal Risk Selection Tool",
    layout="wide"
)


# ---------------------------------------------------------------------
# 1. CATALOGHI DI BASE
# ---------------------------------------------------------------------

CONTEXTS = [
    "Lavoro/HR",
    "Istruzione",
    "Credito/assicurazioni",
    "Welfare/servizi pubblici",
    "Sanità",
    "Giustizia/polizia/migrazione",
    "Piattaforme/contenuti",
    "Marketing/CRM",
    "Sicurezza fisica/accessi",
    "Altro"
]

ACTIONS = [
    "Scoring/ranking",
    "Classificazione",
    "Raccomandazione",
    "Esclusione/de-prioritizzazione",
    "Monitoraggio/sorveglianza",
    "Verifica identità/biometria",
    "Moderazione/ordinamento contenuti",
    "Predizione rischio/affidabilità",
    "Generazione contenuti",
    "Altro"
]

DATA_CATEGORIES = [
    "Nessun dato personale",
    "Dati personali comuni",
    "Dati particolari art. 9 GDPR",
    "Dati biometrici",
    "Dati inferiti/profilazione",
    "Dati comportamentali",
    "Dati da fonti multiple",
    "Proxy variables",
    "Dati di minori"
]

GROUPS = [
    "Lavoratori/candidati",
    "Studenti",
    "Pazienti",
    "Beneficiari welfare",
    "Consumatori",
    "Minori",
    "Migranti/richiedenti asilo",
    "Persone con disabilità",
    "Gruppi protetti o vulnerabili",
    "Pubblico generale"
]

LEGAL_BASES = [
    "Da definire",
    "Consenso",
    "Contratto",
    "Obbligo legale",
    "Interesse pubblico",
    "Interesse legittimo",
    "Tutela interessi vitali",
    "Non applicabile / da verificare"
]

DECISION_EFFECTS = [
    "Nessun effetto significativo",
    "Supporto a decisione umana",
    "Effetti giuridici o similmente significativi",
    "Esclusione/accesso/priorità in servizi o opportunità"
]


# ---------------------------------------------------------------------
# 2. CATALOGO RISCHI GIURIDICI
# ---------------------------------------------------------------------

RISK_CATALOG = [
    {
        "id": "R1",
        "name": "Trattamento eccedente o non proporzionato di dati",
        "rights": ["privacy", "protezione dei dati", "autonomia informativa"],
        "triggers": {
            "data_categories": [
                "Dati personali comuni",
                "Dati particolari art. 9 GDPR",
                "Dati biometrici",
                "Dati inferiti/profilazione",
                "Dati comportamentali",
                "Dati da fonti multiple",
                "Dati di minori"
            ],
            "actions": [
                "Scoring/ranking",
                "Classificazione",
                "Monitoraggio/sorveglianza",
                "Predizione rischio/affidabilità"
            ]
        },
        "baseline": "medio",
        "questions": [
            "Tutti i dati trattati sono necessari rispetto alla finalità dichiarata?",
            "Sono trattati dati inferiti o derivati non immediatamente visibili alla persona?",
            "Esistono alternative meno intrusive?",
            "La persona può esercitare accesso, rettifica, opposizione o limitazione?"
        ],
        "measures": [
            "minimizzazione dei dati",
            "limitazione della finalità",
            "limiti di conservazione",
            "informativa comprensibile",
            "diritti dell'interessato effettivi"
        ]
    },
    {
        "id": "R2",
        "name": "Discriminazione diretta, indiretta o tramite proxy",
        "rights": ["uguaglianza", "non discriminazione", "pari accesso a opportunità"],
        "triggers": {
            "contexts": [
                "Lavoro/HR",
                "Istruzione",
                "Credito/assicurazioni",
                "Welfare/servizi pubblici",
                "Sanità",
                "Giustizia/polizia/migrazione"
            ],
            "actions": [
                "Scoring/ranking",
                "Classificazione",
                "Esclusione/de-prioritizzazione",
                "Predizione rischio/affidabilità"
            ],
            "data_categories": [
                "Dati particolari art. 9 GDPR",
                "Dati biometrici",
                "Proxy variables",
                "Dati inferiti/profilazione"
            ]
        },
        "baseline": "alto",
        "questions": [
            "Sono presenti variabili protette o variabili proxy?",
            "Il modello è stato testato per sottogruppi?",
            "I dati storici incorporano disuguaglianze pregresse?",
            "L'impatto varia per genere, età, origine, disabilità, territorio o status socio-economico?"
        ],
        "measures": [
            "bias testing",
            "analisi per sottogruppi",
            "audit indipendente",
            "rimozione o controllo delle proxy variables",
            "revisione umana effettiva"
        ]
    },
    {
        "id": "R3",
        "name": "Opacità decisionale e spiegazione insufficiente",
        "rights": ["trasparenza", "rimedio effettivo", "diritto di difesa", "buona amministrazione"],
        "triggers": {
            "actions": [
                "Scoring/ranking",
                "Classificazione",
                "Raccomandazione",
                "Predizione rischio/affidabilità",
                "Esclusione/de-prioritizzazione"
            ],
            "decision_effects": [
                "Effetti giuridici o similmente significativi",
                "Esclusione/accesso/priorità in servizi o opportunità"
            ]
        },
        "baseline": "alto",
        "questions": [
            "La persona sa che il sistema è usato?",
            "La logica essenziale della decisione è spiegabile in linguaggio comprensibile?",
            "La persona può conoscere i criteri rilevanti?",
            "La spiegazione consente una contestazione concreta?"
        ],
        "measures": [
            "notice individuale",
            "spiegazione comprensibile",
            "documentazione dei criteri decisionali",
            "canale di contestazione",
            "logging della decisione"
        ]
    },
    {
        "id": "R4",
        "name": "Human oversight ineffettivo o meramente formale",
        "rights": ["accountability", "rimedio effettivo", "due process", "buona amministrazione"],
        "triggers": {
            "actions": [
                "Raccomandazione",
                "Scoring/ranking",
                "Predizione rischio/affidabilità",
                "Esclusione/de-prioritizzazione"
            ],
            "decision_effects": [
                "Supporto a decisione umana",
                "Effetti giuridici o similmente significativi",
                "Esclusione/accesso/priorità in servizi o opportunità"
            ]
        },
        "baseline": "alto",
        "questions": [
            "L'umano può realmente discostarsi dall'output del sistema?",
            "Il revisore ha tempo, competenza e autorità per modificare l'esito?",
            "Sono prevenuti automation bias e rubber-stamping?",
            "La revisione umana è documentata?"
        ],
        "measures": [
            "formazione dei revisori",
            "diritto di override",
            "documentazione della revisione",
            "procedure anti-automation bias",
            "controllo periodico delle decisioni confermate"
        ]
    },
    {
        "id": "R5",
        "name": "Esclusione da beni, servizi o opportunità essenziali",
        "rights": ["accesso ai servizi", "uguaglianza sostanziale", "dignità", "rimedio effettivo"],
        "triggers": {
            "contexts": [
                "Lavoro/HR",
                "Istruzione",
                "Credito/assicurazioni",
                "Welfare/servizi pubblici",
                "Sanità",
                "Giustizia/polizia/migrazione"
            ],
            "actions": [
                "Esclusione/de-prioritizzazione",
                "Scoring/ranking",
                "Classificazione"
            ],
            "decision_effects": [
                "Esclusione/accesso/priorità in servizi o opportunità",
                "Effetti giuridici o similmente significativi"
            ]
        },
        "baseline": "alto",
        "questions": [
            "L'esito può impedire o limitare accesso a un servizio essenziale?",
            "Esiste un canale alternativo non automatizzato?",
            "L'errore è correggibile in tempo utile?",
            "Il danno è reversibile?"
        ],
        "measures": [
            "canale alternativo",
            "revisione urgente",
            "fallback umano",
            "notifica dell'esito",
            "procedura di rimedio"
        ]
    },
    {
        "id": "R6",
        "name": "Sorveglianza sproporzionata e chilling effect",
        "rights": ["privacy", "libertà personale", "libertà di espressione", "libertà di associazione", "dignità"],
        "triggers": {
            "actions": [
                "Monitoraggio/sorveglianza",
                "Verifica identità/biometria",
                "Moderazione/ordinamento contenuti"
            ],
            "data_categories": [
                "Dati biometrici",
                "Dati comportamentali",
                "Dati da fonti multiple",
                "Dati inferiti/profilazione"
            ]
        },
        "baseline": "alto",
        "questions": [
            "Il monitoraggio è continuo o sistematico?",
            "Le persone possono modificare il proprio comportamento per timore di osservazione?",
            "La misura è strettamente necessaria?",
            "Sono presenti limiti temporali e funzionali?"
        ],
        "measures": [
            "limitazione temporale",
            "limitazione della finalità",
            "riduzione granularità dati",
            "informativa rafforzata",
            "audit sul monitoraggio"
        ]
    },
    {
        "id": "R7",
        "name": "Dignità, autonomia e stigmatizzazione",
        "rights": ["dignità", "autonomia individuale", "reputazione", "libero sviluppo della persona"],
        "triggers": {
            "actions": [
                "Predizione rischio/affidabilità",
                "Scoring/ranking",
                "Classificazione",
                "Monitoraggio/sorveglianza"
            ],
            "contexts": [
                "Lavoro/HR",
                "Istruzione",
                "Sanità",
                "Welfare/servizi pubblici",
                "Giustizia/polizia/migrazione"
            ],
            "data_categories": [
                "Dati inferiti/profilazione",
                "Dati comportamentali",
                "Dati biometrici"
            ]
        },
        "baseline": "alto",
        "questions": [
            "La persona viene ridotta a punteggio, profilo o categoria?",
            "Il sistema attribuisce affidabilità, rischio, produttività o valore sociale?",
            "L'etichetta prodotta può generare stigma?",
            "La persona può correggere o contestare la classificazione?"
        ],
        "measures": [
            "limitazione delle categorie",
            "divieto di etichette stigmatizzanti",
            "spiegazione individuale",
            "rettifica del profilo",
            "revisione umana qualificata"
        ]
    },
    {
        "id": "R8",
        "name": "Libertà di espressione, informazione e pluralismo",
        "rights": ["libertà di espressione", "libertà di informazione", "pluralismo", "contestabilità"],
        "triggers": {
            "contexts": [
                "Piattaforme/contenuti"
            ],
            "actions": [
                "Moderazione/ordinamento contenuti",
                "Raccomandazione",
                "Esclusione/de-prioritizzazione",
                "Generazione contenuti"
            ]
        },
        "baseline": "alto",
        "questions": [
            "Il sistema rimuove, de-prioritizza o ordina contenuti?",
            "Può produrre over-removal o under-removal?",
            "Incide sulla visibilità di gruppi, opinioni o informazioni?",
            "Esiste un reclamo effettivo e tempestivo?"
        ],
        "measures": [
            "criteri di ranking/moderazione trasparenti",
            "notice agli utenti",
            "appeal",
            "audit su over-removal e under-removal",
            "monitoraggio degli effetti sistemici"
        ]
    },
    {
        "id": "R9",
        "name": "Accountability gap e allocazione incerta delle responsabilità",
        "rights": ["accountability", "rimedio effettivo", "effettività della tutela"],
        "triggers": {
            "actions": [
                "Scoring/ranking",
                "Classificazione",
                "Raccomandazione",
                "Predizione rischio/affidabilità",
                "Generazione contenuti",
                "Altro"
            ],
            "decision_effects": [
                "Supporto a decisione umana",
                "Effetti giuridici o similmente significativi",
                "Esclusione/accesso/priorità in servizi o opportunità"
            ]
        },
        "baseline": "medio",
        "questions": [
            "È chiaro chi decide?",
            "È chiaro chi controlla?",
            "È chiaro chi risponde in caso di errore o danno?",
            "Provider, deployer, controller, processor e responsabili interni sono distinti?"
        ],
        "measures": [
            "accountability matrix",
            "nomina responsabili interni",
            "logging",
            "audit trail",
            "procedure di escalation"
        ]
    },
    {
        "id": "R10",
        "name": "Rimedio ineffettivo o impossibilità di contestazione",
        "rights": ["rimedio effettivo", "due process", "diritto di difesa", "buona amministrazione"],
        "triggers": {
            "actions": [
                "Scoring/ranking",
                "Classificazione",
                "Esclusione/de-prioritizzazione",
                "Predizione rischio/affidabilità",
                "Moderazione/ordinamento contenuti"
            ],
            "decision_effects": [
                "Effetti giuridici o similmente significativi",
                "Esclusione/accesso/priorità in servizi o opportunità"
            ]
        },
        "baseline": "alto",
        "questions": [
            "La persona può contestare l'esito?",
            "Il reclamo è semplice, accessibile e tempestivo?",
            "La contestazione può modificare concretamente l'esito?",
            "Sono previsti tempi certi di risposta?"
        ],
        "measures": [
            "complaint mechanism",
            "canale umano",
            "tempi di risposta",
            "motivazione dell'esito",
            "possibilità di revisione"
        ]
    }
]


# ---------------------------------------------------------------------
# 3. FUNZIONI DI VALUTAZIONE
# ---------------------------------------------------------------------

def list_intersection(a, b):
    return sorted(list(set(a).intersection(set(b))))


def activate_risks(inputs):
    activated = []

    for risk in RISK_CATALOG:
        matched = []

        for trigger_key, trigger_values in risk["triggers"].items():
            input_values = inputs.get(trigger_key, [])
            hits = list_intersection(trigger_values, input_values)
            matched.extend(hits)

        if matched:
            activated.append({
                "id": risk["id"],
                "name": risk["name"],
                "rights": risk["rights"],
                "baseline": risk["baseline"],
                "trigger_match": sorted(list(set(matched))),
                "questions": risk["questions"],
                "measures": risk["measures"]
            })

    return activated


def compute_red_flags(inputs, activated_risks):
    flags = []
    risk_ids = {r["id"] for r in activated_risks}

    sensitive_data = {
        "Dati particolari art. 9 GDPR",
        "Dati biometrici",
        "Dati di minori"
    }.intersection(set(inputs["data_categories"]))

    if not inputs["purpose"].strip():
        flags.append({
            "severity": "blocking",
            "label": "Finalità non descritta",
            "explanation": "La finalità deve essere specifica, esplicita e sufficientemente determinata."
        })

    if inputs["legal_basis"] in ["Da definire", "Non applicabile / da verificare"]:
        flags.append({
            "severity": "blocking",
            "label": "Base giuridica non definita",
            "explanation": "La DPIA+ non può concludersi positivamente senza una base giuridica chiara."
        })

    if sensitive_data and inputs["data_strictly_necessary"] != "Sì":
        flags.append({
            "severity": "high",
            "label": "Dati sensibili o vulnerabili senza necessità stringente",
            "explanation": "Dati particolari, biometrici o di minori richiedono una giustificazione rafforzata."
        })

    if inputs["alternatives_assessed"] == "No":
        flags.append({
            "severity": "high",
            "label": "Alternative meno intrusive non valutate",
            "explanation": "La necessità non è dimostrata se non sono state considerate alternative meno invasive."
        })

    if inputs["decision_effect"] in [
        "Effetti giuridici o similmente significativi",
        "Esclusione/accesso/priorità in servizi o opportunità"
    ] and inputs["contestability"] != "Sì":
        flags.append({
            "severity": "blocking",
            "label": "Decisione significativa senza contestabilità effettiva",
            "explanation": "Una decisione con effetti significativi richiede un rimedio effettivo e accessibile."
        })

    if inputs["decision_effect"] in [
        "Effetti giuridici o similmente significativi",
        "Esclusione/accesso/priorità in servizi o opportunità"
    ] and inputs["human_oversight"] in ["Assente", "Solo formale"]:
        flags.append({
            "severity": "high",
            "label": "Human oversight assente o meramente formale",
            "explanation": "Il controllo umano deve poter comprendere, contestare e modificare l'output del sistema."
        })

    if "R2" in risk_ids and inputs["subgroup_testing"] != "Sì":
        flags.append({
            "severity": "high",
            "label": "Rischio discriminatorio senza test per sottogruppi",
            "explanation": "Il rischio di discriminazione non può essere mitigato senza verifiche su gruppi potenzialmente colpiti."
        })

    if inputs["monitoring"] != "Sì":
        flags.append({
            "severity": "medium",
            "label": "Monitoraggio post-deployment insufficiente",
            "explanation": "Il risk management deve proseguire dopo il deployment, specialmente nei casi ad alto rischio."
        })

    if not inputs["accountability_owner"].strip():
        flags.append({
            "severity": "high",
            "label": "Responsabilità non allocata",
            "explanation": "Serve un owner interno responsabile dell'assessment, delle misure e del riesame."
        })

    return flags


def compute_scrutiny_level(inputs, flags):
    level = 1

    high_contexts = {
        "Lavoro/HR",
        "Istruzione",
        "Credito/assicurazioni",
        "Welfare/servizi pubblici",
        "Sanità"
    }

    very_high_contexts = {
        "Giustizia/polizia/migrazione"
    }

    vulnerable_groups = {
        "Minori",
        "Migranti/richiedenti asilo",
        "Persone con disabilità",
        "Gruppi protetti o vulnerabili",
        "Beneficiari welfare",
        "Pazienti"
    }

    sensitive_data = {
        "Dati particolari art. 9 GDPR",
        "Dati biometrici",
        "Dati di minori"
    }

    if high_contexts.intersection(set(inputs["contexts"])):
        level = max(level, 3)

    if very_high_contexts.intersection(set(inputs["contexts"])):
        level = max(level, 4)

    if vulnerable_groups.intersection(set(inputs["groups"])):
        level = max(level, 4)

    if sensitive_data.intersection(set(inputs["data_categories"])):
        level = max(level, 4)

    if inputs["decision_effect"] in [
        "Effetti giuridici o similmente significativi",
        "Esclusione/accesso/priorità in servizi o opportunità"
    ]:
        level = max(level, 3)

    if any(flag["severity"] == "blocking" for flag in flags):
        level = max(level, 4)

    mapping = {
        1: "basso",
        2: "medio",
        3: "alto",
        4: "molto alto"
    }

    return mapping[level]


def recommend_outcome(scrutiny_level, flags):
    if any(flag["severity"] == "blocking" for flag in flags):
        return "NO-GO temporaneo / redesign obbligatorio"

    if any(flag["severity"] == "high" for flag in flags):
        return "CONDITIONAL GO con misure obbligatorie ed escalation"

    if scrutiny_level in ["alto", "molto alto"]:
        return "CONDITIONAL GO / enhanced review"

    return "GO con monitoraggio periodico"


def build_risk_dataframe(activated_risks):
    rows = []

    for risk in activated_risks:
        rows.append({
            "ID": risk["id"],
            "Rischio": risk["name"],
            "Diritti coinvolti": ", ".join(risk["rights"]),
            "Trigger rilevati": ", ".join(risk["trigger_match"]),
            "Baseline": risk["baseline"],
            "Domande obbligatorie": " | ".join(risk["questions"]),
            "Misure minime": " | ".join(risk["measures"])
        })

    return pd.DataFrame(rows)


def build_markdown_report(inputs, activated_risks, flags, scrutiny_level, outcome):
    lines = []

    lines.append("# DPIA+ / FRIA Legal Risk Selection Report")
    lines.append("")
    lines.append(f"**Data generazione:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    lines.append("## 1. Identificazione del progetto")
    lines.append(f"- **Nome progetto:** {inputs['project_name']}")
    lines.append(f"- **Organizzazione:** {inputs['organization']}")
    lines.append(f"- **Owner accountability:** {inputs['accountability_owner']}")
    lines.append("")

    lines.append("## 2. DPIA core")
    lines.append(f"- **Finalità:** {inputs['purpose']}")
    lines.append(f"- **Base giuridica:** {inputs['legal_basis']}")
    lines.append(f"- **Categorie di dati:** {', '.join(inputs['data_categories'])}")
    lines.append(f"- **Dati strettamente necessari:** {inputs['data_strictly_necessary']}")
    lines.append("")

    lines.append("## 3. AI system / decision-making layer")
    lines.append(f"- **Contesto d'uso:** {', '.join(inputs['contexts'])}")
    lines.append(f"- **Azione del sistema:** {', '.join(inputs['actions'])}")
    lines.append(f"- **Effetto della decisione:** {inputs['decision_effect']}")
    lines.append(f"- **Gruppi coinvolti:** {', '.join(inputs['groups'])}")
    lines.append("")

    lines.append("## 4. Necessità")
    lines.append(f"- **Alternative meno intrusive valutate:** {inputs['alternatives_assessed']}")
    lines.append(f"- **Motivazione di necessità:** {inputs['necessity_reasoning']}")
    lines.append("")

    lines.append("## 5. Proporzionalità")
    lines.append(f"- **Motivazione di proporzionalità:** {inputs['proportionality_reasoning']}")
    lines.append(f"- **Contestabilità:** {inputs['contestability']}")
    lines.append(f"- **Human oversight:** {inputs['human_oversight']}")
    lines.append("")

    lines.append("## 6. Art. 9 AI Act — Risk management")
    lines.append(f"- **Test per sottogruppi:** {inputs['subgroup_testing']}")
    lines.append(f"- **Monitoraggio post-deployment:** {inputs['monitoring']}")
    lines.append(f"- **Reasonably foreseeable misuse considerato:** {inputs['misuse_assessed']}")
    lines.append("")

    lines.append("## 7. Art. 27 AI Act — FRIA deployment layer")
    lines.append(f"- **Complaint mechanism:** {inputs['contestability']}")
    lines.append(f"- **Categorie di persone/gruppi colpiti:** {', '.join(inputs['groups'])}")
    lines.append(f"- **Governance interna:** {inputs['governance_notes']}")
    lines.append("")

    lines.append("## 8. Rischi fondamentali attivati")
    if not activated_risks:
        lines.append("Nessun rischio attivato automaticamente. Verificare manualmente.")
    else:
        for risk in activated_risks:
            lines.append(f"### {risk['id']} — {risk['name']}")
            lines.append(f"- **Diritti coinvolti:** {', '.join(risk['rights'])}")
            lines.append(f"- **Trigger:** {', '.join(risk['trigger_match'])}")
            lines.append(f"- **Baseline:** {risk['baseline']}")
            lines.append("- **Domande obbligatorie:**")
            for q in risk["questions"]:
                lines.append(f"  - {q}")
            lines.append("- **Misure minime:**")
            for m in risk["measures"]:
                lines.append(f"  - {m}")
            lines.append("")

    lines.append("## 9. Red flags")
    if not flags:
        lines.append("Nessuna red flag automatica rilevata.")
    else:
        for flag in flags:
            lines.append(f"- **[{flag['severity'].upper()}] {flag['label']}**: {flag['explanation']}")
    lines.append("")

    lines.append("## 10. Esito")
    lines.append(f"- **Livello di scrutinio:** {scrutiny_level}")
    lines.append(f"- **Esito raccomandato:** {outcome}")
    lines.append("")
    lines.append("## 11. Nota metodologica")
    lines.append(
        "Questo report non sostituisce la valutazione giuridica umana. "
        "Il tool automatizza la selezione preliminare dei rischi, la tracciabilità "
        "del ragionamento e l'individuazione delle red flags."
    )

    return "\n".join(lines)


# ---------------------------------------------------------------------
# 4. STATO SESSIONE
# ---------------------------------------------------------------------

if "last_result" not in st.session_state:
    st.session_state.last_result = None


# ---------------------------------------------------------------------
# 5. INTERFACCIA
# ---------------------------------------------------------------------

st.title("DPIA+ / FRIA Legal Risk Selection Tool")
st.caption(
    "Prototipo Streamlit per integrare DPIA, art. 9 AI Act e art. 27 AI Act "
    "attraverso un legal risk selection layer."
)

with st.expander("Logica del tool", expanded=False):
    st.markdown(
        """
        Il tool usa la DPIA come base procedurale e aggiunge tre livelli:

        1. **Legal risk selection**: seleziona i rischi fondamentali sulla base di contesto, dati, azione del sistema e tipo di decisione.
        2. **Art. 9 AI Act**: introduce risk management, testing, rischio residuo e monitoraggio.
        3. **Art. 27 AI Act**: introduce contesto di deployment, gruppi colpiti, human oversight, governance e reclami.

        Il tool non decide la conformità finale. Guida l'analista e produce un report tracciabile.
        """
    )

st.divider()

with st.form("dpia_fria_form"):
    st.subheader("1. Identificazione")

    col1, col2 = st.columns(2)

    with col1:
        project_name = st.text_input("Nome progetto / sistema", value="Recruitment AI Pilot")
        organization = st.text_input("Organizzazione", value="Example Organization")
        accountability_owner = st.text_input("Owner accountability", value="DPO / AI Governance Officer")

    with col2:
        legal_basis = st.selectbox("Base giuridica", LEGAL_BASES, index=0)
        decision_effect = st.selectbox("Effetto della decisione", DECISION_EFFECTS, index=1)
        data_strictly_necessary = st.selectbox(
            "I dati sono strettamente necessari?",
            ["Sì", "No", "Parziale", "Da verificare"],
            index=3
        )

    st.subheader("2. DPIA core")

    purpose = st.text_area(
        "Finalità del trattamento / uso del sistema",
        value="",
        height=90,
        placeholder="Descrivere finalità specifica, contesto e risultato atteso."
    )

    data_categories = st.multiselect(
        "Categorie di dati",
        DATA_CATEGORIES,
        default=["Dati personali comuni"]
    )

    st.subheader("3. AI system e contesto d'uso")

    col3, col4 = st.columns(2)

    with col3:
        contexts = st.multiselect(
            "Contesto d'uso",
            CONTEXTS,
            default=["Lavoro/HR"]
        )

        actions = st.multiselect(
            "Azione del sistema",
            ACTIONS,
            default=["Scoring/ranking"]
        )

    with col4:
        groups = st.multiselect(
            "Persone o gruppi potenzialmente coinvolti",
            GROUPS,
            default=["Lavoratori/candidati"]
        )

        misuse_assessed = st.selectbox(
            "Reasonably foreseeable misuse valutato?",
            ["Sì", "No", "Parziale", "Da verificare"],
            index=3
        )

    st.subheader("4. Necessità e proporzionalità")

    col5, col6 = st.columns(2)

    with col5:
        alternatives_assessed = st.selectbox(
            "Sono state valutate alternative meno intrusive?",
            ["Sì", "No", "Parziale", "Da verificare"],
            index=3
        )

        necessity_reasoning = st.text_area(
            "Motivazione di necessità",
            value="",
            height=100,
            placeholder="Perché è necessario usare questo sistema, questi dati e questa forma di automazione?"
        )

    with col6:
        proportionality_reasoning = st.text_area(
            "Motivazione di proporzionalità",
            value="",
            height=100,
            placeholder="Quali benefici concreti giustificano i rischi? Chi beneficia e chi sopporta il rischio?"
        )

    st.subheader("5. Art. 9 / Art. 27 operational layer")

    col7, col8 = st.columns(2)

    with col7:
        subgroup_testing = st.selectbox(
            "Sono stati previsti test per sottogruppi?",
            ["Sì", "No", "Parziale", "Non applicabile", "Da verificare"],
            index=4
        )

        monitoring = st.selectbox(
            "È previsto monitoraggio post-deployment?",
            ["Sì", "No", "Parziale", "Da verificare"],
            index=3
        )

    with col8:
        human_oversight = st.selectbox(
            "Human oversight",
            ["Effettivo", "Solo formale", "Assente", "Non applicabile", "Da verificare"],
            index=4
        )

        contestability = st.selectbox(
            "Complaint / contestability mechanism",
            ["Sì", "No", "Parziale", "Da verificare"],
            index=3
        )

    governance_notes = st.text_area(
        "Note su governance interna, ruoli e responsabilità",
        value="",
        height=80,
        placeholder="Indicare chi decide, chi controlla, chi risponde e chi aggiorna l'assessment."
    )

    submitted = st.form_submit_button("Genera risk register e report")


if submitted:
    inputs = {
        "project_name": project_name,
        "organization": organization,
        "accountability_owner": accountability_owner,
        "legal_basis": legal_basis,
        "decision_effect": decision_effect,
        "decision_effects": [decision_effect],
        "data_strictly_necessary": data_strictly_necessary,
        "purpose": purpose,
        "data_categories": data_categories,
        "contexts": contexts,
        "actions": actions,
        "groups": groups,
        "misuse_assessed": misuse_assessed,
        "alternatives_assessed": alternatives_assessed,
        "necessity_reasoning": necessity_reasoning,
        "proportionality_reasoning": proportionality_reasoning,
        "subgroup_testing": subgroup_testing,
        "monitoring": monitoring,
        "human_oversight": human_oversight,
        "contestability": contestability,
        "governance_notes": governance_notes
    }

    activated_risks = activate_risks(inputs)
    flags = compute_red_flags(inputs, activated_risks)
    scrutiny_level = compute_scrutiny_level(inputs, flags)
    outcome = recommend_outcome(scrutiny_level, flags)
    risk_df = build_risk_dataframe(activated_risks)
    report_md = build_markdown_report(
        inputs,
        activated_risks,
        flags,
        scrutiny_level,
        outcome
    )

    st.session_state.last_result = {
        "inputs": inputs,
        "activated_risks": activated_risks,
        "flags": flags,
        "scrutiny_level": scrutiny_level,
        "outcome": outcome,
        "risk_df": risk_df,
        "report_md": report_md
    }


# ---------------------------------------------------------------------
# 6. OUTPUT
# ---------------------------------------------------------------------

if st.session_state.last_result:
    result = st.session_state.last_result

    st.divider()
    st.subheader("Risultato assessment")

    metric1, metric2, metric3 = st.columns(3)

    with metric1:
        st.metric("Rischi attivati", len(result["activated_risks"]))

    with metric2:
        st.metric("Livello scrutinio", result["scrutiny_level"])

    with metric3:
        st.metric("Red flags", len(result["flags"]))

    st.markdown(f"### Esito raccomandato: **{result['outcome']}**")

    st.subheader("Red flags")

    if not result["flags"]:
        st.success("Nessuna red flag automatica rilevata.")
    else:
        for flag in result["flags"]:
            message = f"**{flag['label']}** — {flag['explanation']}"

            if flag["severity"] == "blocking":
                st.error(message)
            elif flag["severity"] == "high":
                st.warning(message)
            else:
                st.info(message)

    st.subheader("Risk register")

    if result["risk_df"].empty:
        st.info("Nessun rischio attivato automaticamente. Verificare manualmente.")
    else:
        st.dataframe(result["risk_df"], use_container_width=True)

    st.subheader("Download")

    file_base = result["inputs"]["project_name"].lower().replace(" ", "_").replace("/", "_")

    st.download_button(
        label="Scarica report Markdown",
        data=result["report_md"],
        file_name=f"{file_base}_dpia_fria_report.md",
        mime="text/markdown"
    )

    json_payload = {
        "inputs": result["inputs"],
        "activated_risks": result["activated_risks"],
        "flags": result["flags"],
        "scrutiny_level": result["scrutiny_level"],
        "outcome": result["outcome"],
        "generated_at": datetime.now().isoformat()
    }

    st.download_button(
        label="Scarica assessment JSON",
        data=json.dumps(json_payload, ensure_ascii=False, indent=2),
        file_name=f"{file_base}_assessment.json",
        mime="application/json"
    )
else:
    st.info("Compila il form e clicca su 'Genera risk register e report'.")