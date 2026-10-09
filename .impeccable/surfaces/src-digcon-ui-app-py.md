---
version: 1
slug: "src-digcon-ui-app-py"
primary_target: "src/digcon/ui/app.py"
related_targets: ["streamlit_app.py"]
---

# Surface: DIGCON assessment app (whole Streamlit app)

Mode: Operate. Audience: sandbox participants (compliance, DPO, legal) filling in a long assessment alone, at a desktop, over several sittings.

Task: reach a defensible recommended outcome (O1–O5), see what blocks it and what to do next, never lose work. Product truths to keep visible: every finding points to its rule and source question; UNKNOWN / N/A / NOT OWNED are never "no"; recommendation and governance decision stay separate.

Constraints: Streamlit only (theme in .streamlit/config.toml first, CSS only where theming cannot reach); engine, config, copy (title, credits, disclaimer), section numbering, four steps, JSON save format and widget keys stay. No Bocconi/Baffi marks. Light theme only. No external font or asset hosts.

Open decisions (not to invent): browser leave-page warning (JS component), Markdown report export (missing; separate from redesign).

## Direction contract

THESIS: The category standard for GRC/privacy assessment platforms, executed at OneTrust's craft level: a navy navigation rail, a light working canvas, white cards, segmented answer controls and a results page that leads with what to do next. It refuses the default Streamlit page of stacked widgets and tables, and refuses any pass/fail verdict styling.

OWN-WORLD: Navy rail (#0F1B33) with light text and step groups; canvas #F4F6FA; white cards with 1px #DDE3EC borders and 8px radius, no shadows beyond a faint 1px lift; primary blue #1F5EDB; system UI sans throughout; IDs as small grey code chips; outcome levels O1 green, O2 blue, O3 orange, O4 violet, O5 red as tinted badges; risk levels on one sequential orange ramp; unresolved answers carry their own badge, never colour alone.

STORY: The participant always knows which step they are in, how much is left, whether their work is saved, and on the results page exactly which gaps, remediations and conditions stand between them and a better outcome, each one a click away from the question that causes it.

FIRST VIEWPORT: Left rail: product name and step index (1.0–4.2) with per-section status badges, current outcome badge with three counters, and a save block (saved / unsaved changes + download). Main canvas: compact header (title, caption, disclaimer callout, methodology popover), step breadcrumb, section title, then question rows in a single column: question text with ID chip, segmented answer control directly beneath, unresolved badge when it applies.

FORM: Category standard (canon), chosen by the user over the roll; reference product OneTrust. Seed key 8992e1ac.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
