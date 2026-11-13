"""Keep the route from results to a finding and its source answer visible."""
import streamlit as st

from digcon.domain.action_plan import title
from . import state
from .labels import MITIGATION_TITLE, RESULT_TITLE


def open_finding(rule_id):
    st.session_state.pop('w.plan.selected_group', None)
    st.session_state.pop('w.plan.selected_finding', None)
    st.session_state['plan_focus'] = rule_id
    st.session_state['w.plan_view'] = 'Your action plan'
    st.session_state.pop('finding_source', None)
    state.go(MITIGATION_TITLE)


def open_source(rule_id, question_id, section):
    st.session_state['plan_focus'] = rule_id
    st.session_state['finding_source'] = question_id
    state.go(section)


def return_to_results():
    st.session_state.pop('finding_source', None)
    state.go(RESULT_TITLE)


def render():
    current = st.session_state.get(state.NAV)
    rid = st.session_state.get('plan_focus')
    if current == RESULT_TITLE or not (rid or current == MITIGATION_TITLE):
        return
    with st.container(border=True):
        st.caption('Your route: Assessment findings → Selected issue → Supporting answer')
        if rid:
            st.markdown('**Working on:** ' + title(rid))
        left, right = st.columns(2)
        left.button('← Back to assessment findings (4.1)', key='finding.nav.results',
                    on_click=return_to_results)
        if rid and (current != MITIGATION_TITLE or st.session_state.get('w.plan_view') != 'Your action plan'):
            right.button('← Back to this issue', key='finding.nav.issue',
                         on_click=open_finding, args=(rid,))
        st.caption('Changes are applied when you leave the field. Return to 4.1 to see the updated findings. '
                   'Use the assessment export to keep a downloadable copy.')
