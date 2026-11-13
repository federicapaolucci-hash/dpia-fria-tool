"""Finding-led operational plan, persisted with the assessment."""
import streamlit as st
from digcon.domain.action_plan import ACTIONS, SHARED_FIELDS, approved, approval_ready, findings, fingerprint, title, next_step, share_action
from digcon.domain.models import ActionPlanItem
from .. import state
from ..finding_navigation import open_source
from ..labels import PHASE_TITLES, REVIEW_TITLE, RULES_TITLE, RESULT_TITLE

FIELDS = {
    'action': 'What will be done?', 'rationale': 'How does this action address this problem?',
    'owner': 'Responsible person or team', 'due_date': 'Target date (YYYY-MM-DD)',
    'implementation': 'What has been implemented?',
    'evidence_refs': 'Implementation evidence (one reference per line)',
    'verification_method': 'How was effectiveness checked?',
    'verification_result': 'What did the check establish for this problem?',
    'verification_evidence': 'Verification evidence (one reference per line)',
    'reviewer': 'Reviewer', 'review_date': 'Review date (YYYY-MM-DD)',
    'decision_reason': 'Reason for the review decision',
}


STAGES = ['🎯 1. Understand the problem', '🛠️ 2. Plan the action',
          '📎 3. Record implementation', '🔎 4. Verify and decide']
HELP = {
    'action': 'Describe a concrete change. Example: introduce a human review route for contested credit decisions.',
    'rationale': 'Explain how this change addresses this specific problem. A link to a measure is not enough.',
    'owner': 'Name the person or team responsible. Where provider and deployer must act, identify both contributions.',
    'due_date': 'When should the action be completed? Example: 2026-11-30.',
    'implementation': 'Describe what is now in operation, who implemented it and how. A planned action is not implementation.',
    'evidence_refs': 'Give traceable references, for example: complaints procedure v2, section 4; training record dated 2026-11-20.',
    'verification_method': 'Explain the test in the real use context. For a complaint route, test whether people can use it and obtain reconsideration.',
    'verification_result': 'Record what the test found for this problem, including failures and limitations. State who performed the check and when.',
    'verification_evidence': 'Reference the test report, reviewed cases or other evidence. The existence of a policy alone does not establish effectiveness.',
    'reviewer': 'Name the person deciding whether this specific problem is resolved. This role is distinct from implementing and testing the action.',
    'review_date': 'Date of the decision on this problem, in YYYY-MM-DD format.',
    'decision_reason': 'Explain why the evidence supports resolution or why the problem remains open. Refer to the implementation and verification evidence above.',
}


def _use_suggestion(rid):
    # Suggestions become editable text only after an explicit user action.
    if not state.store().get('action_plan', {}).get(rid, {}).get('action'):
        st.session_state[f'w.plan.{rid}.action'] = ACTIONS[rid][0]
        _sync(rid)


def _sync(rid):
    old = state.store().setdefault('action_plan', {}).get(rid, {})
    data = {'rule_id': rid, **old}
    for field in [*FIELDS, 'status']:
        key = f'w.plan.{rid}.{field}'
        if key not in st.session_state: continue
        value = st.session_state[key]
        data[field] = [x.strip() for x in value.splitlines() if x.strip()] if field.endswith('evidence') or field == 'evidence_refs' else value
    state.store()['action_plan'][rid] = ActionPlanItem.model_validate(data).model_dump(mode='json')
    group = data.get('shared_action_id')
    if group:
        current = state.assessment()
        values = {f: getattr(current.action_plan[rid], f) for f in SHARED_FIELDS}
        current = share_action(current, [rid], values, group)
        state.store()['action_plan'] = {r: v.model_dump(mode='json') for r, v in current.action_plan.items()}
        for other in current.action_plan:
            if other != rid and current.action_plan[other].shared_action_id == group:
                for field in SHARED_FIELDS:
                    st.session_state.pop(f'w.plan.{other}.{field}', None)


def _decide(rid, decision):
    _sync(rid)
    s = state.assessment()
    item = s.action_plan[rid]
    if decision == 'RESOLVED' and not approval_ready(item):
        st.session_state['plan_message'] = 'Complete the action, responsibility, implementation, verification, evidence and review fields first.'
        return
    data = state.store()['action_plan'][rid]
    history = list(data.get('review_history', []))
    current_fingerprint = fingerprint(s, rid)
    history.append({**{k: data.get(k) for k in ['reviewer','review_date','decision_reason']},
                    'decision': decision, 'reviewed_fingerprint': current_fingerprint})
    data.update(decision=decision, reviewed_fingerprint=current_fingerprint, review_history=history)


def _choose_measure(rid):
    st.session_state['plan_focus'] = rid
    st.session_state['w.plan_view'] = 'Catalogue measures'


def _field(rid, field, stored):
    value = stored.get(field, '')
    if isinstance(value, list): value = '\n'.join(value)
    key = f'w.plan.{rid}.{field}'
    state.seed(key, value)
    short = field in ('owner', 'due_date', 'reviewer', 'review_date')
    widget = st.text_input if short else st.text_area
    widget(FIELDS[field], key=key, on_change=_sync, args=(rid,), help=HELP[field])


def _detach(rid):
    st.session_state.pop('w.plan.selected_group', None)
    st.session_state.pop('w.plan.selected_finding', None)
    state.store()['action_plan'][rid]['shared_action_id'] = ''
    st.session_state['plan_focus'] = rid


def _select_group(grouped):
    st.session_state['plan_focus'] = grouped[st.session_state['w.plan.selected_group']][0]
    st.session_state.pop('w.plan.selected_finding', None)


def _select_finding():
    st.session_state['plan_focus'] = st.session_state['w.plan.selected_finding']


def _source_links(cfg, result, rid, info, prefix):
    qids = set(info['ids'])
    if rid in result.rules:
        qids.update(result.rules[rid].input_ids)
    for q in cfg.questions.questions:
        if q.id in qids:
            st.button(q.text, key=f'{prefix}.{rid}.{q.id}', on_click=open_source,
                      args=(rid, q.id, PHASE_TITLES[q.phase]))
    st.button('Open reviewer checks', key=f'{prefix}.review.{rid}', on_click=state.go,
              args=(REVIEW_TITLE if rid.startswith('HS') else RULES_TITLE,))


def _group_form(cards, records):
    candidates = [r for r in cards if not r.startswith('HS')]
    if len(candidates) < 2:
        return
    with st.expander('Use one action for several findings'):
        st.caption('Choose findings addressed by the same concrete intervention. Existing groups are included in full. '
                   'Earlier action text is retained in history; each finding keeps its own rationale, verification and decision.')
        with st.form('plan.group'):
            selected = st.multiselect('Findings addressed', candidates, format_func=title)
            action = st.text_area('Shared action')
            owner = st.text_input('Shared owner')
            due = st.text_input('Shared target date (YYYY-MM-DD)')
            confirmed = st.checkbox('Replace the selected planning fields with this shared action; retain earlier text in history')
            submitted = st.form_submit_button('Save shared action')
        if submitted:
            if len(selected) < 2 or not action.strip() or not owner.strip() or not confirmed:
                st.warning('Select at least two findings, describe the action, name its owner and confirm the change.')
            else:
                # Do not merge different implementation evidence: users must reconcile it first.
                current = state.assessment()
                groups = {records[r].get('shared_action_id') for r in selected if r in records} - {None, ''}
                members = set(selected) | {r for r, v in records.items() if v.get('shared_action_id') in groups}
                implementations = {(records.get(r, {}).get('implementation', ''),
                                    tuple(records.get(r, {}).get('evidence_refs', []))) for r in members}
                nonempty = {v for v in implementations if v[0] or v[1]}
                if nonempty and len(implementations) > 1:
                    st.warning('These findings have different implementation records. Reconcile them individually before sharing the action; no records were changed.')
                else:
                    from uuid import uuid4
                    implementation, evidence = next(iter(implementations))
                    values = dict(action=action.strip(), owner=owner.strip(), due_date=due.strip(),
                                  implementation=implementation, evidence_refs=list(evidence))
                    share_action(current, selected, values, str(uuid4()))
                    state.store()['action_plan'] = {r: v.model_dump(mode='json') for r, v in current.action_plan.items()}
                    for key in list(st.session_state):
                        if str(key).startswith('w.plan.'):
                            del st.session_state[key]
                    st.session_state['plan_focus'] = selected[0]
                    st.rerun()


def render(cfg, result):
    st.markdown('**Your action plan.** Record the action, owner and target date first. '
                'Implementation and verification can wait until evidence is available.')
    st.caption('Planning does not resolve a finding. Save or export your assessment to keep this work.')
    if 'plan_message' in st.session_state: st.warning(st.session_state.pop('plan_message'))
    records = state.store().setdefault('action_plan', {})
    cards = findings(result, records)
    gap_cards = {r: i for r, i in cards.items() if 'Information needed' in i['kinds']}
    st.caption(f'{len(gap_cards)} findings need information · {len(result.open_remediations)} findings need corrective action')
    if gap_cards:
        with st.expander(f'Complete missing information ({len(gap_cards)})', expanded=st.session_state.get('plan_focus') in gap_cards):
            st.caption('These gaps can keep the outcome at O4. Update the source answer or review; writing an action plan does not fill them.')
            for rid, info in sorted(gap_cards.items(), key=lambda pair: pair[0] != st.session_state.get('plan_focus')):
                st.markdown('**' + title(rid) + '**')
                for finding in result.evidence_gaps:
                    if finding.rule_id == rid:
                        st.caption(finding.message)
                _source_links(cfg, result, rid, info, 'gap.source')
    include_saved = st.checkbox('Include saved plans without a current corrective action', key='w.plan.include_saved')
    # Pure evidence/verification work is directed to the source, without a mitigation form.
    work = {r: i for r, i in cards.items() if (include_saved and r in records) or any(k in i['kinds'] for k in
            ['Corrective action needed', 'Ongoing condition', 'Stop condition: legal review'])}
    active_groups = {records[r].get('shared_action_id') for r in work if r in records} - {None, ''}
    work.update({r: cards[r] for r, v in records.items() if v.get('shared_action_id') in active_groups})
    review_only = {r: i for r, i in cards.items() if r not in work and r not in gap_cards and i['kinds'] != ['Saved work — check current assessment']}
    if review_only:
        with st.expander(f'Checks and decisions to record ({len(review_only)})', expanded=st.session_state.get('plan_focus') in review_only):
            for rid, info in review_only.items():
                st.markdown('**' + title(rid) + '**')
                _source_links(cfg, result, rid, info, 'check.source')
    if not work:
        st.caption('No corrective action currently needs a plan. Complete any information and checks listed above.')
        return
    _group_form(work, records)
    grouped = {}
    for rid in work:
        group = records.get(rid, {}).get('shared_action_id') or rid
        grouped.setdefault(group, []).append(rid)
    focus = st.session_state.get('plan_focus')
    group_ids = list(grouped)
    focused_group = next((g for g, members in grouped.items() if focus in members), group_ids[0])
    def group_label(g):
        members = grouped[g]
        text = records.get(members[0], {}).get('action') or title(members[0])
        return text[:100] + (f' · {len(members)} findings' if len(members) > 1 else '')
    if st.session_state.get('w.plan.selected_group') not in group_ids:
        st.session_state['w.plan.selected_group'] = focused_group
    group = st.selectbox('Choose an intervention', group_ids, key='w.plan.selected_group',
                         format_func=group_label, on_change=_select_group, args=(grouped,))
    members = grouped[group]
    if len(members) > 1:
        st.caption('Shared action, owner, target date and implementation evidence. Review each linked finding separately.')
    if st.session_state.get('w.plan.selected_finding') not in members:
        st.session_state['w.plan.selected_finding'] = focus if focus in members else members[0]
    selected = st.selectbox('Finding to review', members, key='w.plan.selected_finding',
                            format_func=title, on_change=_select_finding)
    cards = {selected: work[selected]}
    for rid, info in sorted(cards.items(), key=lambda x: (x[0] != focus, not x[0].startswith('HS'), title(x[0]))):
        stored = records.get(rid, {})
        with st.expander(title(rid), expanded=True):
            st.caption(' · '.join(info['kinds']))
            current = state.assessment()
            if rid.startswith('HS'):
                st.caption('Next: review the facts and the legal determination in section 3.5.')
                st.button('Open this stop review', key=f'plan.stop.{rid}', on_click=state.go, args=(REVIEW_TITLE,))
            else:
                st.caption('Next: ' + next_step(current.action_plan.get(rid), approved(current, rid)))
            if 'Information needed' in info['kinds']:
                st.warning('This finding also has an evidence gap. Update the source information above; planning alone cannot clear it.')
            if rid.startswith('HS'):
                steps = ('Read the facts and the grounds for the stop condition; identify what would need to change.',
                         'Document any changes and obtain a new reasoned legal determination. This action card cannot override the stop condition.')
            elif rid in ACTIONS:
                steps = ACTIONS[rid]
            else:
                steps = ('Review the source information below and specify the missing evidence or corrective action.',
                         'Record who will act, implement the action and submit the evidence for review.')
            stage = st.radio('Choose a step', STAGES, key=f'plan.stage.{rid}', horizontal=True)
            if stage == STAGES[0]:
                st.markdown('**First:** ' + steps[0] + '\n\n**Then:** ' + steps[1])
                qids = [q for q in result.rules[rid].input_ids if any(x.id == q for x in cfg.questions.questions)] if rid in result.rules else []
                with st.expander('Information used in this finding'):
                    for qid in qids:
                        q = cfg.question(qid); a = state.store()['answers'].get(qid, {})
                        if qid == 'C31' and state.store().get('alternatives_review') is not None:
                            from ..alternatives import EXISTENCE, DECISIONS
                            from digcon.domain.alternatives import decision
                            alt = state.store()['alternatives_review']
                            st.markdown('**Alternatives and justification of the choice**')
                            st.write(EXISTENCE[alt['existence']])
                            st.write(alt['comparison'] or 'Comparison not yet documented')
                            st.caption(DECISIONS[decision(state.assessment())])
                        else:
                            st.markdown('**' + q.text + '**')
                            st.write(a.get('value') or a.get('state') or 'Not answered')
                            if a.get('detail'): st.write(a['detail'])
                        st.button('Review this answer', key=f'plan.source.{rid}.{qid}', on_click=open_source, args=(rid, qid, PHASE_TITLES[q.phase]))
                    if not qids: st.caption('This finding requires review of the assessment evidence and judgement.')
            if stage == STAGES[1]:
                if rid in ACTIONS:
                    st.info('Suggested action: ' + ACTIONS[rid][0])
                    if not stored.get('action'):
                        st.button('Use this suggestion and edit it', key=f'plan.suggest.{rid}',
                                  on_click=_use_suggestion, args=(rid,))
                for f in ['action','owner','due_date']:
                    _field(rid, f, stored)
                with st.expander('Optional: progress and catalogue measures'):
                    key=f'w.plan.{rid}.status'; state.seed(key, stored.get('status', 'TODO'))
                    st.selectbox('Work progress', ['TODO','IN_PROGRESS','AWAITING_REVIEW'], key=key,
                                 format_func=lambda v: {'TODO':'Action proposed / implementation pending',
                                                       'IN_PROGRESS':'Implementation in progress',
                                                       'AWAITING_REVIEW':'Submitted for verification — effectiveness not yet established'}[v],
                                 on_change=_sync,args=(rid,))
                    linked = [m for m in state.assessment().mitigations.values() if rid in m.linked_rule_ids and m.activated]
                    st.caption('Linked measures: ' + ('; '.join(cfg.mitigation(m.mitigation_id).measure for m in linked) or 'None yet'))
                    st.button('Choose a measure for this problem', key=f'plan.measure.{rid}',
                              on_click=_choose_measure, args=(rid,))
                    st.caption('Linking a measure alone never closes this problem.')
            if stage == STAGES[2]:
                st.info('Complete this step when the action has been carried out. Include who implemented it and what changed.')
                for f in ['implementation','evidence_refs']:
                    _field(rid,f,stored)
            if stage == STAGES[3]:
                st.caption('First record the effectiveness check, including the verifier and date. Then record the decision on this specific problem.')
                for f in ['rationale','verification_method','verification_result','verification_evidence']:
                    _field(rid,f,stored)
            if stage == STAGES[3]:
                for f in ['reviewer','review_date','decision_reason']: _field(rid,f,stored)
                if rid.startswith('HS'):
                    st.button('Reopen legal assessment', key=f'plan.hs.{rid}',on_click=state.go,args=(REVIEW_TITLE,))
                else:
                    st.button('Approve resolution for this finding',key=f'plan.resolve.{rid}',on_click=_decide,args=(rid,'RESOLVED'))
                    st.button('Keep this finding open',key=f'plan.open.{rid}',on_click=_decide,args=(rid,'OPEN'))
                current = state.assessment()
                if stored.get('decision') == 'RESOLVED':
                    if approved(current,rid): st.success('Resolution approved for the recorded evidence. The engine still checks all applicable conditions.')
                    else: st.warning('The approval is incomplete or its supporting information changed. Review again.')
                elif stored.get('decision') == 'OPEN': st.info('Reviewer decision: the finding remains open.')
                st.caption('Missing answers must be updated at source. An approval does not erase evidence gaps or legal stop conditions.')
            with st.expander('Technical details'):
                st.code(rid)
                if stored.get('shared_action_id'):
                    st.button('Make this finding a separate action', key=f'plan.detach.{rid}',
                              on_click=_detach, args=(rid,))
                st.write(info['ids'])
                if stored.get('review_history'): st.json(stored['review_history'])
                if stored.get('shared_history'):
                    st.caption('Earlier shared action text')
                    st.json(stored['shared_history'])
