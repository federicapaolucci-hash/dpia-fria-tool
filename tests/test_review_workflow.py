"""Regression coverage for concise work plans and completed stop reviews."""
import json
import unittest

from digcon.config import default_config
from digcon.domain.action_plan import SHARED_FIELDS, approved, findings, fingerprint, next_step, share_action
from digcon.domain.models import ActionPlanItem, AssessmentState
from digcon.domain.review_progress import stop_progress
from digcon.engine import run_engine
from digcon.reporting.json_report import assessment_of, dumps
from engine_support import CTX, build_state
from test_action_plan_regression import approve


class WorkflowTests(unittest.TestCase):
    def result(self, state):
        return run_engine(default_config(), state, CTX)

    def test_completed_excluded_stops_are_not_pending(self):
        for rid in ['HS03', 'HS04', 'HS05', 'HS06']:
            state = build_state({'elements': {f'{rid}.E2': 'NOT_MET'},
                                 'human_gates': {rid: 'COMPLETED'}})
            result = self.result(state)
            status, pending = stop_progress(result.hard_stops[rid])
            self.assertIn('Review completed', status)
            self.assertFalse(pending)
            self.assertNotIn(rid, findings(result, {}))

    def test_completed_but_uncertain_still_needs_evidence(self):
        state = build_state({'elements': {'HS08.E1': 'MET', 'HS08.E2': 'UNCERTAIN', 'HS08.E3': 'MET'},
                             'human_gates': {'HS08': 'COMPLETED'}})
        status, pending = stop_progress(self.result(state).hard_stops['HS08'])
        self.assertIn('Insufficient evidence', status)
        self.assertTrue(pending)

    def test_all_met_without_review_needs_decision_not_confirmed_stop(self):
        state = build_state({'elements': {'HS06.E1': 'MET', 'HS06.E2': 'MET', 'HS06.E3': 'MET'}})
        status, pending = stop_progress(self.result(state).hard_stops['HS06'])
        self.assertIn('decision needed', status)
        self.assertTrue(pending)

    def test_confirmed_stop_remains_visible(self):
        state = build_state({'elements': {'HS06.E1': 'MET', 'HS06.E2': 'MET', 'HS06.E3': 'MET'},
                             'human_gates': {'HS06': 'COMPLETED'}})
        status, pending = stop_progress(self.result(state).hard_stops['HS06'])
        self.assertIn('confirmed', status)
        self.assertTrue(pending)

    def shared_values(self):
        return dict(action='Restrict data use', owner='Data team', due_date='2026-12-01',
                    implementation='', evidence_refs=[])

    def test_shared_plan_does_not_copy_decisions_or_clear_gaps(self):
        state = build_state({'answers': {'C43': 'NOT_VERIFIED'}})
        before = self.result(state)
        share_action(state, ['DQ-01', 'PROP-06'], self.shared_values(), 'action-1')
        after = self.result(state)
        self.assertEqual(before.outcome, after.outcome)
        self.assertEqual(before.evidence_gaps, after.evidence_gaps)
        self.assertFalse(approved(state, 'DQ-01'))
        self.assertFalse(approved(state, 'PROP-06'))

    def test_history_and_individual_reasoning_are_preserved(self):
        state = build_state()
        state.action_plan['DQ-01'] = ActionPlanItem(rule_id='DQ-01', action='Previous action',
                                                    rationale='Quality-specific reason', decision='OPEN')
        share_action(state, ['DQ-01', 'PROP-06'], self.shared_values(), 'action-1')
        self.assertEqual(state.action_plan['DQ-01'].shared_history[0]['action'], 'Previous action')
        self.assertEqual(state.action_plan['DQ-01'].rationale, 'Quality-specific reason')
        self.assertEqual(state.action_plan['DQ-01'].decision, 'OPEN')
        self.assertEqual(state.action_plan['PROP-06'].rationale, '')
        self.assertEqual(state.action_plan['PROP-06'].decision, 'PENDING')

    def test_shared_edits_update_all_members_and_invalidate_approval(self):
        state = build_state()
        approve(state, 'DQ-01')
        values = {f: getattr(state.action_plan['DQ-01'], f) for f in SHARED_FIELDS}
        share_action(state, ['DQ-01', 'PROP-06'], values, 'action-1')
        self.assertTrue(approved(state, 'DQ-01'))
        values['implementation'] = 'Implementation changed'
        share_action(state, ['PROP-06'], values, 'action-1')
        self.assertEqual(state.action_plan['DQ-01'].implementation, 'Implementation changed')
        self.assertFalse(approved(state, 'DQ-01'))
        self.assertEqual(len(state.action_plan['DQ-01'].review_history), 0)

    def test_shared_plan_roundtrips_in_report(self):
        state = build_state()
        share_action(state, ['DQ-01', 'PROP-06'], self.shared_values(), 'action-1')
        restored = AssessmentState.model_validate(assessment_of(json.loads(dumps(state, self.result(state)))))
        self.assertEqual(state.action_plan, restored.action_plan)

    def test_legacy_approval_signature_unchanged(self):
        state = build_state()
        approve(state, 'DQ-01')
        data = state.model_dump(mode='json')
        for record in data['action_plan'].values():
            record.pop('shared_action_id')
            record.pop('shared_history')
        restored = AssessmentState.model_validate(data)
        self.assertTrue(approved(restored, 'DQ-01'))
        self.assertEqual(fingerprint(state, 'DQ-01'), fingerprint(restored, 'DQ-01'))

    def test_planned_action_explains_implementation_is_pending(self):
        item = ActionPlanItem(rule_id='DQ-01', **self.shared_values())
        self.assertIn('Plan recorded', next_step(item))
        self.assertIn('implementation evidence', next_step(item))


if __name__ == '__main__':
    unittest.main()
