# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Primary users are participants in the DIGCON Fundamental Rights Assessment Sandbox: teams at organisations that provide or deploy AI systems (compliance, DPO, legal), assessing one of their own systems. They usually fill in the assessment on their own at a desktop, often across several sittings, saving and reloading the assessment as JSON between sessions.

The DIGCON research team (the supervising professor plus the provider-side and deployer-side leads) owns the methodology and judges whether the tool applies it correctly. They are reviewers of the tool, not its main day-to-day users.

## Product Purpose

The tool runs a DPIA-based fundamental-rights assessment of an AI system, with role-specific EU AI Act add-ons for providers (Art. 9) and deployers (Art. 27). It applies the T17 decision engine deterministically. Users answer a structured questionnaire, and the engine routes them, calibrates the risks, tracks mitigations and evidence, checks the hard-stop conditions and recommends one of five outcomes, O1 (can proceed) to O5 (cannot proceed). Every outcome comes with an audit trail and downloadable Markdown and JSON reports.

The assessment succeeds when a participant reaches a defensible recommended outcome. That means seeing exactly which evidence is missing, which mitigations are still open and which rules fired, and being able to hand the report to whoever makes the governance decision.

## Positioning

- The tool reaches its result through traceable rules, not a score or an LLM opinion. Each recommendation traces back to specific rule IDs in a versioned specification (the T17 workbook).
- Uncertainty is kept visible rather than resolved. "Unknown", "not applicable" and "not owned" are never treated as "no". They produce evidence gaps or verification requests.
- The tool only recommends an outcome. It never declares a system proportionate or disproportionate, and the final governance decision is recorded separately by a person.

## Operating Context

- A self-paced, step-by-step flow:
  1. Core assessment (Start, INTRO, WHAT, HOW, WHY).
  2. Role add-ons, which open according to the scoping answers.
  3. Cross-cutting modules: stakeholder engagement (SEP), risk register, rules and scrutiny, mitigation plan, hard-stop gate.
  4. Outcome: recommended outcome, then the governance decision.
- Sessions are resumed by downloading and re-uploading the assessment JSON. There is no account and no database.
- Results leave the tool as Markdown, JSON and CSV exports, which then feed an organisation's own DPIA, FRIA and governance documents.
- It runs as a Streamlit app, probably published from the public `main` branch on Streamlit Community Cloud. Development happens on `rewrite/t17-engine`.

## Capabilities and Constraints

- **Stack:** Python with Streamlit, Pydantic v2 and PyYAML. Questions, rules, risks, mitigations and SEP fields are data in `config/`, generated from the frozen workbook (`T17-v1.0.1`). The UI is rendered from `questions.yaml`.
- **The engine is pure and deterministic.** Outcome precedence is O5 → O4 → O3 → O2 → O1. O5 can only come from hard stops whose constituent elements are fully MET. Only mitigations marked "verified effective" lower residual risk.
- **Every closed question offers Unknown, N/A and Not owned** wherever its answer model allows them.
- **Out of scope for now:** LLM/API interpretation (there is only a stub slot in `interpret/`), a database, a human-gate workflow (it is a manually filled field), and batch runs.
- **Delivery deadline:** 12 October 2026, with the same look as the current app. After that delivery the visual design may be fully redesigned. Copy, credits and disclaimer stay.
- **Language:** code, identifiers and UI text are in English.
- **The repo is public.** Nothing from the private specification folder goes into it.

## Brand Commitments

- **Title:** "DPIA-based Fundamental Rights Assessment Tool".
- **Credits:** "DIGCON — FIS-funded project, Baffi Centre, Bocconi University · All rights reserved".
- **Disclaimer:** "Research prototype — for academic and sandbox testing purposes only. Do not enter personal data, confidential DPIAs, trade secrets or sensitive organisational information." It must stay prominent.
- **Voice:** precise, legal-methodological and non-promotional. Never imply that the tool gives a legal conclusion.
- **Institutional branding:** no binding Bocconi or Baffi brand guidelines or logos have been given. Do not add institutional marks without confirmation.

## Evidence on Hand

- UI copy, labels, methodology text, credits and disclaimer are in `src/digcon/ui/labels.py`.
- The engine configuration is in `config/`. It holds 74 questions, 79 rules, 11 risks, 50 mitigation templates and 15 SEP fields.
- `tests/fixtures/` holds the 46 workbook test fixtures, which are concrete example assessment states.
- **Not available:** no real user testimonials, adoption figures, case studies or pilot results. Do not fabricate any.

## Product Principles

1. **Traceability over persuasion.** Every on-screen judgement must point back to the rule, input or evidence that produced it.
2. **Never collapse uncertainty.** Unknown, missing and not-owned answers stay visibly distinct from "no", and they stay visible all the way to the outcome.
3. **Recommend, don't decide.** Keep the engine's recommendation clearly separate from the human governance decision.
4. **Support long, interrupted work.** Users fill in a long questionnaire on their own, so progress, open items and the way to resume must always be obvious.
5. **Research-grade honesty.** The tool presents itself as a sandbox prototype, never as a compliance certification.
