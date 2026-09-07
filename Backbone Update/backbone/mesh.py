"""10 MESH — protocol A2A: 9 agenți cu identitate Ed25519, hub local, zero outbound.
Mesaj fără anchor_id/intent_hash/semnătură validă = drop + log local."""
from __future__ import annotations
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional

from .still import HashSigner, AuditJournal

AGENTS = ("UKBE", "CASP", "HASN", "SENS", "ACR",
          "CONCORDANCE", "CALIBRATION", "HERITAGE", "GUARDIAN")

def _now() -> str: return datetime.now(timezone.utc).isoformat()
def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


@dataclass(frozen=True)
class A2AMessage:
    msg_id: str; src: str; dst: str
    anchor_id: str; intent_hash: str
    ts: str; kind: str; payload: dict
    sig: str


class Agent:
    def __init__(self, name: str, key: str):
        if name not in AGENTS:
            raise ValueError(f"unknown agent: {name}")
        self.name = name
        self.signer = HashSigner(name, key)

    def send(self, dst, kind, payload, anchor_id, intent_hash, msg_id) -> A2AMessage:
        body = {"msg_id": msg_id, "src": self.name, "dst": dst,
                "anchor_id": anchor_id, "intent_hash": intent_hash,
                "ts": _now(), "kind": kind, "payload": payload}
        return A2AMessage(sig=self.signer.sign(canonical(body)), **body)


class MeshHub:
    """Hub local (:8100). Validează la intrare; drop + log pe invalid; zero outbound."""
    def __init__(self, agents: Dict[str, Agent], journal: Optional[AuditJournal] = None):
        self.agents = agents
        self.journal = journal
        self.delivered: List[A2AMessage] = []
        self.dropped: List[dict] = []

    @staticmethod
    def _body(m: A2AMessage) -> dict:
        return {"msg_id": m.msg_id, "src": m.src, "dst": m.dst,
                "anchor_id": m.anchor_id, "intent_hash": m.intent_hash,
                "ts": m.ts, "kind": m.kind, "payload": m.payload}

    def submit(self, m: A2AMessage) -> bool:
        reasons = []
        if not m.anchor_id or not m.intent_hash: reasons.append("missing_anchor")
        ag = self.agents.get(m.src)
        if ag is None: reasons.append("unknown_src")
        elif not ag.signer.verify(canonical(self._body(m)), m.sig): reasons.append("bad_sig")
        if m.dst not in self.agents: reasons.append("unknown_dst")
        if reasons:
            self.dropped.append({"msg_id": m.msg_id, "reasons": reasons})
            if self.journal:
                self.journal.append({"kind": "drop", "msg_id": m.msg_id, "reasons": reasons})
            return False
        self.delivered.append(m)
        if self.journal:
            self.journal.append({"kind": "deliver", "msg_id": m.msg_id})
        return True

    def outbound(self, *a, **k):
        raise PermissionError("zero outbound: mesh is local-only")