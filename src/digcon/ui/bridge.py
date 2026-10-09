"""Browser bridge: autosave the assessment in the browser's localStorage and scroll to the top on section change.

The assessment never leaves the user's browser: no server-side file is written, so one participant's
answers can never reach another. The stored copy survives a reload; "Discard answers and start over"
clears it, and the JSON download stays the way to move or keep an assessment.
"""

from __future__ import annotations

import streamlit as st
from streamlit.errors import StreamlitAPIException

STORAGE_KEY = "digcon.assessment.v1"
LOADED = "bridge_loaded"  # session flag: the browser copy has been read (or there was none)

_JS = """
export default function(component) {
    const { data, setStateValue } = component;
    if (!window.__digconLoaded) {
        window.__digconLoaded = true;
        let stored = "";
        try { stored = window.localStorage.getItem(data.storage_key) || ""; } catch (e) { stored = ""; }
        setStateValue("stored", stored);
    }
    if (data.allow_save) {
        try {
            if (data.save) { window.localStorage.setItem(data.storage_key, data.save); }
            else { window.localStorage.removeItem(data.storage_key); }
        } catch (e) { /* storage full or disabled: the JSON download still works */ }
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


def sync(save_json: str | None, nav: str) -> str | None:
    """Mount the bridge. Returns the stored assessment JSON the first time it is read in a session, else None."""
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
    return stored or None
