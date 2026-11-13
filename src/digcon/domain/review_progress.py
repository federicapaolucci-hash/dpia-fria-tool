"""Presentation of stop reviews, independent of whether a trigger ever opened."""
from digcon.domain.enums import HumanGate, RuleElementState


def stop_progress(hs):
    """Return a status and whether the user still has work to do."""
    if hs.state is RuleElementState.MET:
        return '🔴 Stop condition confirmed', True
    if hs.gate is HumanGate.COMPLETED:
        if hs.state is RuleElementState.NOT_MET:
            return '🟢 Review completed — stop not established', False
        return '🟡 Insufficient evidence to conclude', True
    if hs.opened or hs.gate is HumanGate.REQUIRED:
        return '🟡 Reviewer decision needed', True
    return '⚪ Not opened', False
