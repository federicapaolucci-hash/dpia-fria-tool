"""DIGCON risk calibration (04_RISK_ANALYSIS): non-compensatory, matrix-based."""

from __future__ import annotations

from digcon.domain.enums import ORDINAL, Probability, Reversibility, RiskLevel, Scale, Scope, Severity
from digcon.domain.models import CalibrationSpec

_SEVERITY_BY_ORDINAL = {ORDINAL[s]: s for s in Severity}


def severity(scale: Scale, scope: Scope, reversibility: Reversibility) -> Severity:
    """severity = MAX(scale, scope, reversibility) on the 1–4 scale."""
    return _SEVERITY_BY_ORDINAL[max(ORDINAL[scale], ORDINAL[scope], ORDINAL[reversibility])]


def risk_level(
    cal: CalibrationSpec,
    scale: Scale | None,
    scope: Scope | None,
    reversibility: Reversibility | None,
    probability: Probability | None,
) -> tuple[Severity | None, RiskLevel | None]:
    """Calibrated level, or (None, None) when any dimension is missing: no level is ever guessed."""
    if scale is None or scope is None or reversibility is None or probability is None:
        return None, None
    sev = severity(scale, scope, reversibility)
    return sev, cal.matrix[sev][probability]
