"""09 STILL — notar hibrid: Ed25519 + ML-DSA-44 (FIPS 204) + SPHINCS+.
Jurnal local de audit, hash-chained, append-only. Zero outbound."""
from __future__ import annotations
import hashlib, json, os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Optional

from .anchor import Intent


def _now() -> str: return datetime.now(timezone.utc).isoformat()
def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


class HashSigner:
    """Semnatar de test (sha256 key||payload). Producție: semnatarii reali
    Ed25519 / ML-DSA-44 / SPHINCS+ din STILL WASM — aceeași interfață."""
    def __init__(self, name: str, key: str): self.name, self.key = name, key
    def sign(self, payload: bytes) -> str:
        return hashlib.sha256(self.key.encode() + payload).hexdigest()
    def verify(self, payload: bytes, sig: str) -> bool:
        return self.sign(payload) == sig


@dataclass(frozen=True)
class NotaryRecord:
    intent_hash: str
    payload_hash: str
    sigs: Dict[str, str]
    ts: str


class AuditJournal:
    """Local-only, append-only, hash-chained. DSEI-V: evenimente, nu persoane."""
    def __init__(self, path: str):
        self.path = path
        self._prev = "0" * 64
        if os.path.exists(path):
            with open(path) as f:
                for line in f:
                    self._prev = json.loads(line)["line_hash"]

    def append(self, entry: dict):
        line_json = json.dumps({"entry": entry, "prev": self._prev, "ts": _now()},
                               sort_keys=True)
        line_hash = hashlib.sha256(line_json.encode()).hexdigest()
        with open(self.path, "a") as f:
            f.write(json.dumps({"line": line_json, "line_hash": line_hash}) + "\n")
        self._prev = line_hash

    def verify(self) -> bool:
        prev = "0" * 64
        with open(self.path) as f:
            for line in f:
                obj = json.loads(line)
                inner = json.loads(obj["line"])
                if inner["prev"] != prev: return False
                if hashlib.sha256(obj["line"].encode()).hexdigest() != obj["line_hash"]:
                    return False
                prev = obj["line_hash"]
        return True


class HybridNotary:
    def __init__(self, ed, mldsa, sphincs, journal: Optional[AuditJournal] = None):
        self.signers = {"ed25519": ed, "ml_dsa_44": mldsa, "sphincs+": sphincs}
        self.journal = journal

    def notarize(self, intent_hash: str, payload: dict) -> NotaryRecord:
        canon = canonical(payload)
        payload_hash = hashlib.sha256(canon).hexdigest()
        sigs = {name: s.sign(canon) for name, s in self.signers.items()}
        rec = NotaryRecord(intent_hash, payload_hash, sigs, _now())
        if self.journal:
            self.journal.append({"kind": "notarize", "payload_hash": payload_hash})
        return rec

    def verify(self, rec: NotaryRecord, payload: dict) -> Dict[str, bool]:
        canon = canonical(payload)
        return {n: s.verify(canon, rec.sigs[n]) for n, s in self.signers.items()}

    def request_anchor(self, intent: Optional[Intent], master_hash: str,
                       n_entries: int, date: str, tags: str) -> str:
        """Ancorarea e act EXPLICIT uman (DSEI-VII). Returnează payload-ul
        pentru Tezos; trimiterea e un gest separat, tot uman."""
        if intent is None:
            raise ValueError("no human intent: no anchor (DSEI-VII)")
        return (f"BRIDGRAI-IPR|{n_entries}entries|{master_hash}|{date}|"
                f"MihaiRosca|{tags}|S(M)=R")