"""08 AGIK — consens multi-agent pentru siguranța copiilor.
≥2/3 acord → verdict sigilat; altfel → escaladare umană (DSEI-III)."""
from __future__ import annotations
import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, List, Optional, Union

from .valve import CoherenceMonitor

PILLARS = ("MANIP", "AGE", "EMOT", "PRIV", "BOUND", "DEPEND")


def _now() -> str: return datetime.now(timezone.utc).isoformat()
def _sha(s: str) -> str: return hashlib.sha256(s.encode()).hexdigest()


@dataclass(frozen=True)
class ObserverScore:
    observer_id: str
    verdict: str                      # SAFE | REVIEW | NOT_SAFE
    pillars: dict                     # toți cei 6 piloni, valori în [0,1]
    reasoning: str

    def __post_init__(self):
        if set(self.pillars) != set(PILLARS):
            raise ValueError("observer must score all 6 pillars")
        if not all(0.0 <= v <= 1.0 for v in self.pillars.values()):
            raise ValueError("pillar values must be in [0,1]")
        if self.verdict not in ("SAFE", "REVIEW", "NOT_SAFE"):
            raise ValueError("unknown verdict")


@dataclass(frozen=True)
class SealedVerdict:
    verdict: str
    confidence: float
    mode: str                         # "unanim" | "majority"
    reasoning_hash: str               # SHA-256 al traseelor de raționament
    ts: str


@dataclass(frozen=True)
class Escalation:
    """DSEI-III: arbitrul NU are câmp de verdict — omul decide."""
    reason: str
    ts: str


@dataclass(frozen=True)
class PendingStabilization:
    """Entropy Valve: coerență prea scăzută → fără seal, sistemul așteaptă."""
    phi_intern: float
    phi_min: float
    ts: str


RoundResult = Union[SealedVerdict, Escalation, PendingStabilization]


def consensus_round(scores: List[ObserverScore],
                    seal_fn: Optional[Callable[[dict], str]] = None,
                    valve: Optional[CoherenceMonitor] = None,
                    phi_intern: Optional[float] = None) -> RoundResult:
    if len(scores) < 3:
        raise ValueError("AGIK requires >=3 independent observers")
    # Entropy Valve: nu se sigilează când oscilatorii sunt desincronizați
    if valve is not None and phi_intern is not None and not valve.allow_seal(phi_intern):
        return PendingStabilization(phi_intern, valve.phi_min, _now())

    verdicts = [s.verdict for s in scores]
    reasoning_hash = _sha("||".join(s.reasoning for s in scores))

    def seal(verdict, conf, mode):
        if seal_fn is not None:
            seal_fn({"verdict": verdict, "confidence": conf,
                     "mode": mode, "reasoning_hash": reasoning_hash})
        return SealedVerdict(verdict, conf, mode, reasoning_hash, _now())

    if len(set(verdicts)) == 1:
        return seal(verdicts[0], 1.0, "unanim")
    maj = max(set(verdicts), key=verdicts.count)
    if verdicts.count(maj) >= 2:
        return seal(maj, verdicts.count(maj) / len(verdicts), "majority")
    return Escalation("no_convergence", _now())