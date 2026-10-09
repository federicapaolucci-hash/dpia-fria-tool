---
name: DIGCON Fundamental Rights Assessment
description: A navy-rail assessment workspace that records the work, flags what is uncertain and recommends an outcome it can trace to its rules.
colors:
  primary: "#1F5EDB"
  selection: "#CFE0FF"
  canvas: "#F4F6FA"
  surface: "#FFFFFF"
  ink: "#18202F"
  ink-muted: "#3A4456"
  slate: "#5B6576"
  border: "#D5DCE6"
  hairline: "#E4E9F0"
  table-border: "#E1E6EE"
  code-ground: "#EEF1F6"
  code-ink: "#4A5568"
  rail: "#0F1B33"
  rail-raised: "#1A2945"
  rail-card: "#16243F"
  rail-hover: "#1F3052"
  rail-active: "#24406F"
  rail-border: "#2A3B5C"
  rail-button-border: "#3A5383"
  rail-ink: "#E3E8F1"
  rail-nav-ink: "#D7DEEA"
  rail-muted: "#9AA7BD"
  rail-accent: "#4C8DFF"
  rail-focus: "#7FAEFF"
  outcome-o1: "#1F7A4D"
  outcome-o1-tint: "#E8F4EE"
  outcome-o1-ink: "#14532D"
  outcome-o2-tint: "#E8EFFC"
  outcome-o2-ink: "#173F95"
  outcome-o3: "#B45309"
  outcome-o3-tint: "#FDF0E1"
  outcome-o3-ink: "#7C3A06"
  outcome-o4: "#6D3FC4"
  outcome-o4-tint: "#F1EBFB"
  outcome-o4-ink: "#4B2A8C"
  outcome-o5: "#B42318"
  outcome-o5-tint: "#FCEBEA"
  outcome-o5-ink: "#7F1D16"
  risk-very-low: "#FFF7EC"
  risk-low: "#FEE7C8"
  risk-moderate: "#FBC98E"
  risk-high: "#F08A3E"
  risk-very-high: "#B5480F"
  risk-ink-light: "#5A3A12"
  risk-ink-moderate: "#4A2A06"
  risk-ink-high: "#3B1A02"
typography:
  app-title:
    fontFamily: "'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, 'Helvetica Neue', Arial, sans-serif"
    fontSize: "1.15rem"
    fontWeight: 700
    letterSpacing: "-0.01em"
  headline:
    fontFamily: "'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, 'Helvetica Neue', Arial, sans-serif"
    fontSize: "1.6rem"
    fontWeight: 650
    letterSpacing: "-0.01em"
  outcome-title:
    fontFamily: "'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, 'Helvetica Neue', Arial, sans-serif"
    fontSize: "1.45rem"
    fontWeight: 650
  title:
    fontFamily: "'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, 'Helvetica Neue', Arial, sans-serif"
    fontSize: "1.12rem"
    fontWeight: 600
    letterSpacing: "-0.01em"
  question:
    fontFamily: "'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, 'Helvetica Neue', Arial, sans-serif"
    fontSize: "0.98rem"
    fontWeight: 600
    lineHeight: 1.4
  body:
    fontFamily: "'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, 'Helvetica Neue', Arial, sans-serif"
    fontSize: "15px"
    fontWeight: 400
  count:
    fontFamily: "'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, 'Helvetica Neue', Arial, sans-serif"
    fontSize: "1.35rem"
    fontWeight: 650
    fontFeature: "tnum"
  caption:
    fontFamily: "'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, 'Helvetica Neue', Arial, sans-serif"
    fontSize: "0.86rem"
    fontWeight: 400
  rail-group:
    fontFamily: "'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, 'Helvetica Neue', Arial, sans-serif"
    fontSize: "0.72rem"
    fontWeight: 650
    letterSpacing: "0.07em"
  id-code:
    fontFamily: "Consolas, 'SFMono-Regular', Menlo, monospace"
    fontSize: "0.75rem"
    fontWeight: 500
rounded:
  chip: "4px"
  button: "6px"
  cell: "6px"
  card: "8px"
spacing:
  matrix-gap: "4px"
  counter-gap: "0.5rem"
  question-rule-top: "0.9rem"
  question-rule-bottom: "0.7rem"
  canvas-top: "1.2rem"
  canvas-bottom: "3rem"
  canvas-max: "1180px"
  rail-width: "368px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.surface}"
    rounded: "{rounded.button}"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.button}"
  button-tertiary:
    textColor: "{colors.ink}"
  segment-selected:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.surface}"
    rounded: "{rounded.button}"
  segment-unselected:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.button}"
  rail-nav-item:
    backgroundColor: "{colors.rail}"
    textColor: "{colors.rail-nav-ink}"
    padding: "0.3rem 0.75rem"
    height: "2.15rem"
  rail-nav-item-hover:
    backgroundColor: "{colors.rail-hover}"
    textColor: "{colors.surface}"
  rail-nav-item-active:
    backgroundColor: "{colors.rail-active}"
    textColor: "{colors.surface}"
  rail-status-card:
    backgroundColor: "{colors.rail-card}"
    textColor: "{colors.rail-ink}"
    rounded: "{rounded.card}"
  card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.card}"
  outcome-banner-o1:
    backgroundColor: "{colors.outcome-o1-tint}"
    textColor: "{colors.outcome-o1-ink}"
    rounded: "{rounded.card}"
    padding: "1.1rem 1.25rem"
  outcome-banner-o2:
    backgroundColor: "{colors.outcome-o2-tint}"
    textColor: "{colors.outcome-o2-ink}"
    rounded: "{rounded.card}"
    padding: "1.1rem 1.25rem"
  outcome-banner-o3:
    backgroundColor: "{colors.outcome-o3-tint}"
    textColor: "{colors.outcome-o3-ink}"
    rounded: "{rounded.card}"
    padding: "1.1rem 1.25rem"
  outcome-banner-o4:
    backgroundColor: "{colors.outcome-o4-tint}"
    textColor: "{colors.outcome-o4-ink}"
    rounded: "{rounded.card}"
    padding: "1.1rem 1.25rem"
  outcome-banner-o5:
    backgroundColor: "{colors.outcome-o5-tint}"
    textColor: "{colors.outcome-o5-ink}"
    rounded: "{rounded.card}"
    padding: "1.1rem 1.25rem"
  counter:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink-muted}"
    rounded: "{rounded.card}"
    padding: "0.55rem 0.8rem"
  counter-zero:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.slate}"
    rounded: "{rounded.card}"
    padding: "0.55rem 0.8rem"
  matrix-cell:
    rounded: "{rounded.cell}"
    padding: "0.45rem"
    height: "3.4rem"
  matrix-chip-initial:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.chip}"
    padding: "0.05rem 0.4rem"
  id-chip:
    backgroundColor: "{colors.code-ground}"
    textColor: "{colors.code-ink}"
    typography: "{typography.id-code}"
---

# Design System: DIGCON Fundamental Rights Assessment

## Overview

**Creative North Star: "The Case File Workbench"**

The app is a working surface for one long, careful job: filling in a fundamental-rights assessment over several sittings and reaching a recommended outcome that can be traced to its rules. It follows the category standard for governance, risk and privacy assessment platforms. A dark navy rail holds orientation (where am I, how much is left, is my work saved, what is the outcome now). A light, cool canvas holds the work, and white bordered cards group it. Nothing on the canvas performs; every surface either asks a question, states a status or points to the next action.

Density is high but ordered. Questions run in a single column, each a bold line with its ID in a small grey code chip, the answer control directly beneath, and a hairline rule to the next. Colour carries meaning, not decoration: one blue for action and selection, five outcome hues for the five recommendation levels, one sequential orange ramp for risk intensity, and violet for answers that are still unresolved. The system rejects the default Streamlit page of stacked widgets and raw tables, and it rejects pass/fail verdict styling: no outcome is ever presented as a green tick or a red cross alone.

**Key Characteristics:**
- Navy rail plus light canvas: orientation on the left, work on the right.
- White cards with a 1px cool-grey border and 8px corners, flat, no shadow.
- One action blue; every selected answer fills with it.
- Outcomes O1 to O5 each own a hue and show as tinted banners and badges with a text label.
- Risk intensity on a single light-to-dark orange ramp.
- Unresolved answers (Unknown, Not owned, N/A) always carry a labelled badge, never colour alone.
- IDs (questions, rules, measures, risks) stay visible as small monospace chips.

## Colors

A cool, institutional palette: navy and slate neutrals, one saturated working blue, and semantic hues that only appear where they mean something.

### Primary
- **Assessment Blue** (#1F5EDB): primary buttons (the forward pager button, "Load this assessment"), the selected segment in every answer control, selected pills, links, progress bars on the canvas and the 2px focus outline. It is also the O2 outcome hue.
- **Selection Wash** (#CFE0FF): text selection only.

### Secondary
- **Rail Navy** (#0F1B33): the sidebar ground. It is the only dark surface in the app.
- **Rail Raised** (#1A2945), **Rail Card** (#16243F), **Rail Hover** (#1F3052), **Rail Active** (#24406F): the rail's tonal steps, from the status card behind the outcome and save block, to hovered and current navigation items.
- **Rail Accent** (#4C8DFF) and **Rail Focus** (#7FAEFF): the rail's progress bars and its focus outline; the canvas blue is too dark to read on navy.
- **Rail Ink** (#E3E8F1), **Rail Nav Ink** (#D7DEEA), **Rail Muted** (#9AA7BD), **Rail Border** (#2A3B5C), **Rail Button Border** (#3A5383): text, secondary text, dividers and the outlined save button in the rail.

### Tertiary
Outcome hues. Each recommendation level owns one hue, used for its badge in the rail and nav, and as a tint-plus-ink pair for the outcome banner.
- **O1 Proceed Green** (#1F7A4D), banner tint #E8F4EE with ink #14532D.
- **O2 Conditions Blue** (Assessment Blue), banner tint #E8EFFC with ink #173F95.
- **O3 Revision Orange** (#B45309), banner tint #FDF0E1 with ink #7C3A06. Also the "Unsaved changes" and "open hard stop" signal.
- **O4 Evidence Violet** (#6D3FC4), banner tint #F1EBFB with ink #4B2A8C. Also the colour of the Unknown and Not owned badges, because those are what produce evidence gaps.
- **O5 Stop Red** (#B42318), banner tint #FCEBEA with ink #7F1D16. Only a fully MET hard stop ever shows red.

Risk ramp, light to dark, for matrix cells: **Very Low** (#FFF7EC), **Low** (#FEE7C8), **Moderate** (#FBC98E), **High** (#F08A3E), **Very High** (#B5480F). Text on the first two uses #5A3A12, on Moderate #4A2A06, on High #3B1A02, on Very High white.

### Neutral
- **Canvas** (#F4F6FA): the main background behind all cards.
- **Surface White** (#FFFFFF): cards, counters, inputs, secondary buttons, matrix chips.
- **Ink** (#18202F): body text and headings.
- **Ink Muted** (#3A4456): counter labels.
- **Slate** (#5B6576): captions, zero counters, matrix headers, the grey badge hue.
- **Border** (#D5DCE6): card, input and counter borders.
- **Hairline** (#E4E9F0): the rule between question rows.
- **Table Border** (#E1E6EE) and **Code Ground** (#EEF1F6): dataframe borders, table header ground and the ID chip ground; **Code Ink** (#4A5568) for ID text.

### Named Rules
**The One Hue Per Outcome Rule.** O1 green, O2 blue, O3 orange, O4 violet, O5 red, always with the outcome code and its title in text. An outcome is a recommendation level, never a pass/fail verdict, so it is never shown as colour alone.

**The Single Ramp Rule.** Risk intensity uses only the orange ramp, light to dark. Do not mix outcome hues into risk cells or use red for "very high".

**The Violet Means Unresolved Rule.** Violet marks material that is missing or unknown (O4, Unknown, Not owned). It is never used for decoration.

## Typography

**Display Font:** Segoe UI (with -apple-system, BlinkMacSystemFont, Roboto, Helvetica Neue, Arial)
**Body Font:** Segoe UI (same stack)
**Label/Mono Font:** Consolas (with SFMono-Regular, Menlo, monospace)

**Character:** A single plain system sans, as the shipped build uses it. This follows the project constraint of no external font or asset hosts. It is the current state, not a doctrine: a self-hosted face would be a system change, not a violation. Monospace is reserved for identifiers.

### Hierarchy
- **Headline** (650, 1.6rem, -0.01em): the section heading ("4.1 Recommended outcome"). It is the largest text on the canvas and leads every page.
- **Outcome Title** (650, 1.45rem): the line inside the outcome banner.
- **App Title** (700, 1.15rem, -0.01em): the product title in the header. It is deliberately quiet, so the section heading leads.
- **Title** (600, 1.12rem, -0.01em): card and subsection headings ("What to do next", "Human oversight").
- **Question** (600, 0.98rem, line-height 1.4): question text above each answer control.
- **Body** (400, 15px base): running text, capped at 78ch (outcome text at 80ch).
- **Count** (650, 1.35rem, tabular numerals): the figure in each open-item counter. Metrics, tables and counts all use tabular numerals.
- **Caption** (400, about 0.86rem, Slate): rule references, precedence lines, the header caption and the disclaimer.
- **Rail Group** (650, 0.72rem, 0.07em tracking, uppercase, Rail Muted): the step group headings in the navigation rail only.
- **ID Code** (500, 0.75rem, monospace): question, rule, measure and risk IDs.

### Named Rules
**The Section Leads Rule.** The section heading is the largest type on the page; the app title stays a quiet line above it.

**The IDs Stay Visible Rule.** Every question, finding and measure shows its ID in monospace beside its text, because every judgement must point back to a rule or input.

## Layout

The layout is a fixed two-zone shell. A 368px navy rail on the left holds the brand line (DIGCON plus subtitle), a status card (current outcome badge, three open-item counts, save state and the save button), then the four steps. Each step has a group heading, a progress bar where it has questions, and one full-width nav item per section with its status badge on the same line. The canvas is a single centred column, max 1180px wide, with 1.2rem top and 3rem bottom padding. It opens with a compact header: the title with its caption, a "Methodology" popover aligned right, and a bordered disclaimer card. The section heading and content follow, then a pager (previous on the left in a secondary button, next on the right in a primary button), a divider and the credits caption.

Question rows run single column inside white cards grouped by subsection. Rows are separated by a hairline rule with 0.9rem above and 0.7rem below. The results page stacks the outcome banner, a precedence caption, a row of five counters (auto-fit grid, min 150px, 0.5rem gap), the "What to do next" card, then tabs for the registers. On narrow screens the rail collapses behind its toggle, the header stacks, counters reflow into two columns, the pager buttons stack full width, and the risk matrix (min 560px) and tables scroll horizontally inside their wrappers.

## Elevation & Depth

The system is flat. Depth comes from tonal layering: navy rail against light canvas, white cards against the cool canvas, and on the rail, slightly lighter navy cards and nav states. The build adds no custom shadows. Borders (1px #D5DCE6) separate surfaces, and the hairline rule separates rows inside them.

### Named Rules
**The Flat Card Rule.** Cards are separated from the canvas by their white ground and a 1px border, never by a drop shadow.

## Shapes

Corners are gently rounded and step down with size: 8px for cards, the outcome banner, counters and the rail status card; 6px for buttons, segmented controls and risk matrix cells; 4px for chips inside the matrix. Pills (multi-select options) are fully rounded, as Streamlit draws them. Matrix cells sit on a 4px gap so the ramp reads as a grid of tiles. A dashed border is reserved for residual-risk chips, which separates them from the solid initial-risk chips.

## Components

### Buttons
Plain and functional, sized to the column they fill.
- **Shape:** gently rounded (6px).
- **Primary:** Assessment Blue fill, white text. Used for the forward pager button and single confirming actions. Icons (Material Symbols) sit at the leading edge, or trailing for "next".
- **Secondary:** white fill, 1px border, ink text. Used for the back pager, "Methodology" and "Discard answers".
- **Tertiary:** text only, with a leading arrow. Used for "Open 1.3" links from each finding to the section that causes it.
- **Focus:** 2px Assessment Blue outline with 2px offset on the canvas; 2px Rail Focus outline with 1px offset on the rail.

### Segmented Answer Control
The signature input. Every closed question shows its states (YES, NO, UNKNOWN, N/A, NOT OWNED) as one joined row of segments directly under the question. The selected segment fills with Assessment Blue and white text, and the others stay white with ink text. Free-text, reference and multi-select questions carry a second, smaller control labelled "Or mark it as" with only UNKNOWN, N/A and NOT OWNED; choosing one disables the value input above it. Multi-select values use rounded pills, with selected pills also filled blue.

### Unresolved Badge
When a question is answered Unknown or Not owned, a violet badge with an icon and label appears under the control, followed by a grey note "May create an evidence gap. Never read as NO." N/A gets a grey badge and "May be sent for verification." The badge carries the meaning in words, and colour only reinforces it.

### Chips
- **ID chip:** monospace 0.75rem on Code Ground, beside question text and finding rules.
- **Status badge:** Streamlit's tinted badge (a light wash of the hue with the hue as text), used for section status in the rail ("Complete", "3 / 7", "Closed", "1 open") and for outcome codes. Hue follows meaning: green done, grey neutral or counted, blue started or role, orange open or suspended, violet evidence gap, red only for a confirmed hard stop.
- **Matrix chip:** white, 1px ink border, 4px corners, 0.75rem semibold risk ID. Residual chips are dashed and transparent, and turn white-on-dark in the darkest cell.

### Cards / Containers
- **Corner Style:** 8px.
- **Background:** Surface White on the canvas; Rail Card (#16243F) inside the rail.
- **Shadow Strategy:** none (see Elevation & Depth).
- **Border:** 1px Border (#D5DCE6).
- **Internal Padding:** Streamlit's bordered-container default, about 1rem.

### Inputs / Fields
- **Style:** white field, 1px border, 8px corners, ink text; select boxes show "Select…" and text areas carry a placeholder.
- **Focus:** 2px Assessment Blue outline, 2px offset.
- **Disabled:** a value field greys out while an "Or mark it as" state is chosen.

### Navigation
The rail is the navigation. Nav items are full-width, left-aligned, borderless buttons (min height 2.15rem, 0.3rem by 0.75rem padding, 0.92rem text) in Rail Nav Ink on navy. Hover lifts to Rail Hover with white text, and the current section fills Rail Active with white text. Each item ends with its status badge. Step groups are headed by small uppercase tracked labels ("Step 1 · Core assessment") and a progress bar with an "x of y questions answered" caption. The save state sits in the status card at the top of the rail: green "Saved to file" or orange "Unsaved changes", always with an icon and a line of explanation.

### Outcome Banner
The results page leads with a full-width tinted block (8px corners, 1.1rem by 1.25rem padding) in the outcome's tint and ink: "Recommended outcome: O2 — Proceed with conditions" at 1.45rem, then one line of explanation. A caption beneath names the rule that fired, the precedence and the workbook version, and states that this is a recommendation, not the governance decision.

### Open-Item Counters
A row of five small white bordered tiles (8px corners), each a 1.35rem tabular figure followed by its label. Tiles with a zero drop to Slate at regular weight, so non-zero items lead.

### Risk Matrix
Severity rows (highest at top) by probability columns, drawn as rounded 6px tiles on a 4px gap and filled from the orange ramp. Each tile shows its level in a 0.7rem semibold label. Initial and residual risk IDs sit inside the tiles as solid and dashed chips, and a caption explains the two.

## Do's and Don'ts

### Do:
- **Do** put new work on Canvas (#F4F6FA) inside white cards with a 1px #D5DCE6 border and 8px corners.
- **Do** use Assessment Blue (#1F5EDB) for the one primary action per view and for every selected answer.
- **Do** show outcomes with their code and title in text, in their own hue: O1 green, O2 blue, O3 orange, O4 violet, O5 red.
- **Do** place risk intensity on the orange ramp only, light (#FFF7EC) to dark (#B5480F).
- **Do** give every unresolved state (Unknown, Not owned, N/A) a labelled badge and the note that it is never read as NO.
- **Do** show the ID of every question, rule, measure and risk as a small monospace chip.
- **Do** keep the rail as the single place for orientation: step, section status, current outcome and save state.
- **Do** use tabular numerals for counts, metrics and tables.

### Don't:
- **Don't** style any outcome as a pass/fail verdict (green tick versus red cross); outcomes are recommendation levels.
- **Don't** use red anywhere except a fully confirmed hard stop and the O5 outcome.
- **Don't** signal state with colour alone; every badge carries a word.
- **Don't** add drop shadows to cards; separation is tonal and bordered.
- **Don't** fall back to the default Streamlit page of stacked widgets and raw tables for results; lead with the outcome, the counters and what to do next.
- **Don't** add a dark theme, or institutional logos without confirmation; the build is light only and carries no marks.
