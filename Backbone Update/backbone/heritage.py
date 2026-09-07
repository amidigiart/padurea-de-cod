"""11 HERITAGE — continuitate, arhivă, succesiune.
Producție: bundle-uri pe USB criptat + printouts; aici, model conceptual.
Succesiunea e notarizată pe STILL și înregistrată în MANIFEST —
nu doar în memorie, ci pe blockchain. Patrick moștenește verificabil."""
from __future__ import annotations
import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from .anchor import Intent


class IntegrityError(RuntimeError):
    pass


def _now() -> str: return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class SealedBundle:
    bundle_id: str
    content_hash: str
    ts: str
    note: str


@dataclass(frozen=True)
class SuccessionRecord:
    successor_anchor_id: str
    intent_hash: str
    notary_payload_hash: str
    ts: str


class HeritageVault:
    def __init__(self):
        self.bundles = {}
        self._contents = {}
        self.successor: Optional[str] = None
        self.succession_record: Optional[SuccessionRecord] = None

    def seal(self, bundle_id: str, content: bytes, note: str = "") -> SealedBundle:
        b = SealedBundle(bundle_id, hashlib.sha256(content).hexdigest(), _now(), note)
        self.bundles[bundle_id] = b
        self._contents[bundle_id] = content
        return b

    def restore(self, bundle_id: str) -> bytes:
        c = self._contents[bundle_id]
        if hashlib.sha256(c).hexdigest() != self.bundles[bundle_id].content_hash:
            raise IntegrityError("bundle corrupted: hash mismatch")
        return c

    def designate_successor(self, intent: Optional[Intent],
                            successor_anchor_id: str,
                            notary=None, manifest=None) -> dict:
        """Succesiunea e act uman explicit (DSEI-VII).
        Dacă notary și manifest sunt furnizate, actul e sigilat
        criptografic și înregistrat în lanțul IP."""
        if intent is None:
            raise ValueError("no human intent: no succession (DSEI-VII)")
        self.successor = successor_anchor_id

        result = {"successor": successor_anchor_id, "ts": _now(),
                  "intent_hash": intent.text_hash}

        if notary is not None:
            payload = {"act": "succession", "from": intent.anchor_id,
                       "to": successor_anchor_id,
                       "intent_hash": intent.text_hash}
            rec = notary.notarize(intent.text_hash, payload)
            result["notarized"] = True
            result["payload_hash"] = rec.payload_hash
            result["sigs"] = list(rec.sigs.keys())
            self.succession_record = SuccessionRecord(
                successor_anchor_id, intent.text_hash, rec.payload_hash, _now())

            if manifest is not None:
                v = manifest.append([{"asset": "succession-act",
                                      "successor": successor_anchor_id,
                                      "hash": rec.payload_hash}])
                result["manifest_version"] = v.version
                result["manifest_hash"] = v.master_hash
        else:
            result["notarized"] = False

        return result