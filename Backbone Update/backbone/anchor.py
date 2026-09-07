"""01 ANCHOR — identitate umană + intenție semnată. DSEI-VII."""
from __future__ import annotations
import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class AnchorError(ValueError):
    pass


@dataclass(frozen=True)
class Intent:
    anchor_id: str
    text_hash: str
    ts: str
    sig: str


class HumanAnchor:
    """Fără om nu există acțiune. Intenție vidă = eroare structurală."""

    def __init__(self, signer):
        # signer: callable(hash_hex) -> sig_hex (ex: Ed25519)
        self._sign = signer

    def register_intent(self, text: str, anchor_id: str) -> Intent:
        if not text or not text.strip():
            raise AnchorError("empty intent: no human, no action (DSEI-VII)")
        if not anchor_id or not anchor_id.strip():
            raise AnchorError("missing anchor_id")
        h = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return Intent(anchor_id=anchor_id, text_hash=h, ts=_now(), sig=self._sign(h))