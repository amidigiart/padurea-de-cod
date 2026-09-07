"""12 MANIFEST — lanț de hash-uri IP → Tezos. Fiecare versiune = creație nouă ancorată."""
from __future__ import annotations
import hashlib, json
from dataclasses import dataclass
from typing import List, Optional

def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


@dataclass
class ManifestVersion:
    version: str
    n_entries: int
    master_hash: str
    prev_hash: str
    tx_hash: Optional[str] = None     # completat DOAR după ce omul trimite TX


class IPManifest:
    def __init__(self, major: int = 1, minor: int = 8):
        self.versions: List[ManifestVersion] = []
        self._major, self._minor = major, minor
        self._prev = "0" * 64
        self._history: List[List[dict]] = []

    def append(self, entries: List[dict]) -> ManifestVersion:
        self._minor += 1
        master = hashlib.sha256(canonical({"prev": self._prev, "entries": entries})).hexdigest()
        v = ManifestVersion(f"v{self._major}.{self._minor}", len(entries),
                            master, self._prev)
        self.versions.append(v)
        self._history.append(entries)
        self._prev = master
        return v

    def mark_tx(self, version: str, tx_hash: str):
        """Gest uman: după ce TX-ul e confirmat pe Tezos."""
        for v in self.versions:
            if v.version == version:
                v.tx_hash = tx_hash
                return
        raise KeyError(version)

    def verify(self) -> bool:
        prev = "0" * 64
        for v, entries in zip(self.versions, self._history):
            if v.prev_hash != prev: return False
            h = hashlib.sha256(canonical({"prev": prev, "entries": entries})).hexdigest()
            if h != v.master_hash: return False
            prev = v.master_hash
        return True