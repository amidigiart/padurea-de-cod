import json
import pytest

from backbone.agik import (ObserverScore, SealedVerdict, Escalation,
                           PendingStabilization, consensus_round, PILLARS)
from backbone.still import HashSigner, HybridNotary, AuditJournal
from backbone.valve import CoherenceMonitor
from backbone.anchor import HumanAnchor


def _notary(tmp=None):
    return HybridNotary(HashSigner("ed", "k1"), HashSigner("mld", "k2"),
                        HashSigner("sph", "k3"), journal=tmp)

def obs(oid, verdict, reasoning=None, **pill):
    return ObserverScore(oid, verdict,
                         {k: pill.get(k, 0.1) for k in PILLARS},
                         reasoning or f"r-{oid}")


# ── validare observatori ──
def test_observer_must_score_all_pillars():
    with pytest.raises(ValueError):
        ObserverScore("A", "SAFE", {"MANIP": 0.1}, "r")

def test_requires_three_observers():
    with pytest.raises(ValueError):
        consensus_round([obs("A", "SAFE"), obs("B", "SAFE")])


# ── consens ──
def test_unanimous_sealed():
    r = consensus_round([obs("A", "NOT_SAFE", "dependency"),
                         obs("B", "NOT_SAFE", "secrecy"),
                         obs("C", "NOT_SAFE", "isolation")])
    assert isinstance(r, SealedVerdict)
    assert r.confidence == 1.0 and r.mode == "unanim" and len(r.reasoning_hash) == 64

def test_majority_sealed():
    r = consensus_round([obs("A", "SAFE"), obs("B", "NOT_SAFE"), obs("C", "NOT_SAFE")])
    assert r.verdict == "NOT_SAFE" and r.confidence == pytest.approx(2/3)

def test_no_convergence_escalates_without_verdict():
    """POARTA: DSEI-III — arbitrul nu are câmp de verdict."""
    r = consensus_round([obs("A", "SAFE"), obs("B", "REVIEW"), obs("C", "NOT_SAFE")])
    assert isinstance(r, Escalation)
    assert not hasattr(r, "verdict")

def test_entropy_valve_blocks_seal():
    r = consensus_round([obs("A", "SAFE")]*3,
                        valve=CoherenceMonitor(phi_min=0.5), phi_intern=0.4)
    assert isinstance(r, PendingStabilization)


# ── STILL ──
def test_three_signatures_verify():
    n = _notary()
    p = {"statement": "vand moto aprilia catre mihai rosca"}
    rec = n.notarize("intenthash", p)
    assert set(rec.sigs) == {"ed25519", "ml_dsa_44", "sphincs+"}
    assert all(n.verify(rec, p).values())

def test_tamper_detected():
    n = _notary()
    rec = n.notarize("h", {"x": 1})
    assert not all(n.verify(rec, {"x": 2}).values())


# ── jurnal de audit ──
def test_journal_chain_verifies_and_tamper_fails(tmp_path):
    j = AuditJournal(str(tmp_path / "audit.log"))
    j.append({"a": 1}); j.append({"b": 2})
    assert j.verify()
    lines = open(j.path).readlines()
    obj = json.loads(lines[0]); obj["line_hash"] = "f" * 64
    lines[0] = json.dumps(obj) + "\n"
    open(j.path, "w").writelines(lines)
    assert not AuditJournal(j.path).verify()


# ── ancorare explicit umană ──
def test_anchor_requires_human_intent():
    with pytest.raises(ValueError):
        _notary().request_anchor(None, "h", 124, "2026-09-06", "t")

def test_tezos_payload_format():
    i = HumanAnchor(lambda h: "s").register_intent("anchor", "human-001")
    p = _notary().request_anchor(i, "abc123", 124, "2026-09-06", "STILL+AGIK")
    assert "|124entries|" in p and "abc123" in p and p.endswith("S(M)=R")


# ── POARTA FAZEI 3: consens + notarizare cap-coadă ──
def test_integration_consensus_to_notary(tmp_path):
    j = AuditJournal(str(tmp_path / "audit.log"))
    n = _notary(j)
    r = consensus_round([obs("A", "NOT_SAFE", "dependency pattern"),
                         obs("B", "NOT_SAFE", "secrecy request"),
                         obs("C", "NOT_SAFE", "isolation signals")])
    assert isinstance(r, SealedVerdict)
    payload = {"verdict": r.verdict, "reasoning_hash": r.reasoning_hash}
    rec = n.notarize("intent", payload)
    assert all(n.verify(rec, payload).values())
    assert j.verify()