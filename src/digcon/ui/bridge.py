"""Browser bridge: autosave the assessment in the browser's localStorage and scroll to the top on section change.

The assessment never leaves the user's browser: no server-side file is written, so one participant's
answers can never reach another. The stored copy survives a reload; "Discard answers and start over"
clears it, and the JSON download stays the way to move or keep an assessment.

Streamlit sends a text field to the server only when it loses focus, so text typed just before a reload
would be lost. The script therefore also keeps keystroke-level drafts of text fields, which are laid over
the last saved copy on restore. The section that was open is kept too.
"""

from __future__ import annotations

import json
import re
from typing import Any

import streamlit as st
from streamlit.errors import StreamlitAPIException

from digcon.domain.enums import AnswerKind
from digcon.domain.models import ConfigBundle

STORAGE_KEY = "digcon.assessment.v1"
LOADED = "bridge_loaded"  # session flag: the browser copy has been read (or there was none)

_JS = """
export default function(component) {
    const { data, setStateValue } = component;
    const KEY = data.storage_key, DRAFTS = KEY + ".drafts", NAV = KEY + ".nav";
    const read = (k, fallback) => { try { return window.localStorage.getItem(k) ?? fallback; } catch (e) { return fallback; } };
    const write = (k, v) => { try { window.localStorage.setItem(k, v); } catch (e) { /* full or disabled */ } };
    const drop = (k) => { try { window.localStorage.removeItem(k); } catch (e) {} };

    if (!window.__digconLoaded) {
        window.__digconLoaded = true;
        let drafts = {};
        try { drafts = JSON.parse(read(DRAFTS, "{}") || "{}"); } catch (e) { drafts = {}; }
        setStateValue("stored", JSON.stringify({ assessment: read(KEY, ""), drafts: drafts, nav: read(NAV, "") }));
    }
    if (!window.__digconDraftListener) {
        window.__digconDraftListener = true;
        document.addEventListener("input", (ev) => {
            const el = ev.target;
            const isText = el instanceof HTMLTextAreaElement || (el instanceof HTMLInputElement && el.type === "text");
            if (!isText) return;
            const box = el.closest('[class*="st-key-w-"]');
            const m = box && box.className.match(/st-key-(w-[A-Za-z0-9-]+)/);
            if (!m) return;
            let drafts = {};
            try { drafts = JSON.parse(read(DRAFTS, "{}") || "{}"); } catch (e) { drafts = {}; }
            drafts[m[1]] = el.value;
            write(DRAFTS, JSON.stringify(drafts));
        }, true);
    }
    if (data.allow_save) {
        if (data.save) { write(KEY, data.save); } else { drop(KEY); }
        drop(DRAFTS);  // a save follows a committed edit: every draft typed so far is now in the saved copy
        write(NAV, data.nav);
    }
    if (window.__digconNav !== undefined && window.__digconNav !== data.nav) {
        const top = () => {
            window.scrollTo(0, 0);
            for (const el of document.querySelectorAll('[data-testid="stMain"], section.stMain, [data-testid="stAppViewContainer"]')) {
                el.scrollTo(0, 0);
            }
        };
        top();
        setTimeout(top, 60);
        setTimeout(top, 250);
    }
    window.__digconNav = data.nav;
}
"""


def _register():
    return st.components.v2.component("digcon_bridge", js=_JS)


_bridge = _register()


def _noop() -> None:
    pass


def sync(save_json: str | None, nav: str) -> dict[str, Any] | None:
    """Mount the bridge. The first time the browser copy is read in a session, return
    ``{"assessment": str, "drafts": {widget class key: text}, "nav": str}``; otherwise None."""
    global _bridge
    loaded = st.session_state.get(LOADED, False)
    args = dict(
        key="digcon_bridge",
        data={"storage_key": STORAGE_KEY, "save": save_json or "", "allow_save": loaded, "nav": nav},
        default={"stored": None},
        height=0,
        on_stored_change=_noop,
    )
    try:
        result = _bridge(**args)
    except StreamlitAPIException:  # a new runtime (e.g. a fresh test app) has an empty component registry
        _bridge = _register()
        result = _bridge(**args)
    stored = getattr(result, "stored", None)
    if loaded or stored is None:
        return None
    st.session_state[LOADED] = True
    try:
        payload = json.loads(stored)
    except (TypeError, ValueError):
        return None
    return payload if isinstance(payload, dict) else None


_QUESTION_FIELD = re.compile(r"^w-([A-Za-z0-9]+)-(value|detail)$")
_GOV_FIELD = re.compile(r"^w-gov-(G\d+)$")
_SEP_FIELD = re.compile(r"^w-sep-(SEP[0-9A-Za-z]+)$")


def apply_drafts(cfg: ConfigBundle, data: dict[str, Any], drafts: dict[str, str],
                 governance_fields: dict[str, str], sep_enum_fields: set[str]) -> None:
    """Lay typed-but-unsent text over the saved assessment (in place). Unknown keys are ignored."""
    answers = data.setdefault("answers", {})
    for key, raw in drafts.items():
        if not isinstance(raw, str):
            continue
        text = raw.strip()
        if key == "w-meta-id":
            if text:
                data["assessment_id"] = text
        elif m := _QUESTION_FIELD.match(key):
            qid, part = m.groups()
            try:
                q = cfg.question(qid)
            except KeyError:
                continue
            current = answers.get(qid)
            if part == "value" and q.kind in (AnswerKind.TEXT, AnswerKind.REFERENCE):
                if current and current.get("state"):
                    continue  # marked UNKNOWN / N/A / NOT OWNED: the text box is disabled
                if text:
                    answers[qid] = {"question_id": qid, "value": text}
                else:
                    answers.pop(qid, None)
            elif part == "detail" and current:
                if text:
                    current["detail"] = text
                else:
                    current.pop("detail", None)
        elif (m := _GOV_FIELD.match(key)) and m.group(1) in governance_fields:
            data.setdefault("governance", {})[governance_fields[m.group(1)]] = text or None
        elif (m := _SEP_FIELD.match(key)) and m.group(1) not in sep_enum_fields:
            texts = data.setdefault("sep", {}).setdefault("texts", {})
            if text:
                texts[m.group(1)] = text
            else:
                texts.pop(m.group(1), None)
