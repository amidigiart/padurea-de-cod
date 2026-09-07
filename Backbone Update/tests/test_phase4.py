import pytest

from backbone.anchor import HumanAnchor
from backbone.mesh import Agent, MeshHub, AGENTS
from backbone.heritage import HeritageVault, IntegrityError
from backbone.manifest import IPManifest
from backbone.still import HashSigner, HybridNotary, AuditJournal
from backbone.agik import consensus_round, ObserverScore, SealedVerdict, PILLARS


def _intent(): return HumanAnchor(lambda h: "s").register_intent("q", "human-001")

def _mesh(tmp=None):
    agents = {n: Agent(n, "k-" + n) for n in ("SENS", "GUARDIAN", "HASN")}
    return MeshHub(agents, journal=tmp), agents


# ── MESH ──
def test_valid_message_delivered():
    hub, ag = _mesh()
    i = _intent()
    m = ag["SENS"].send("GUARDIAN", "safety_score", {"MANIP": 0.8},
                        i.anchor_id, i.text_hash, "m1")
    assert hub.submit(m) is True and len(hub.delivered) == 1

def test_missing_anchor_dropped_and_logged(tmp_path):
    hub, ag = _mesh(AuditJournal(str(tmp_path / "a.log")))
    i = _intent()
    m = ag["SENS"].send("GUARDIAN", "x", {}, "", "", "m2")
    assert hub.submit(m) is False
    assert hub.dropped[0]["reasons"] == ["missing_anchor"]
    assert hub.journal.verify()

def test_tampered_payload_dropped():
    hub, ag = _mesh()
    i = _intent()
    m = ag["SENS"].send("GUARDIAN", "x", {"ok": 1}, i.anchor_id, i.text_hash, "m3")
    m.payload["ok"] = 999                      # tamper după semnare
    assert hub.submit(m) is False
    assert "bad_sig" in hub.dropped[0]["reasons"]

def test_zero_outbound():
    hub, _ = _mesh()
    with pytest.raises(PermissionError): hub.outbound()


# ── HERITAGE ──
def test_seal_restore_ok():
    v = HeritageVault()
    v.seal("b1", b"padurea de cod")
    assert v.restore("b1") == b"padurea de cod"

def test_tamper_detected():
    v = HeritageVault()
    v.seal("b1", b"continuity")
    v._contents["b1"] = b"corrupted"
    with pytest.raises(IntegrityError): v.restore("b1")

def test_succession_requires_human_intent():
    v = HeritageVault()
    with pytest.raises(ValueError): v.designate_successor(None, "patrick-001")
    r = v.designate_successor(_intent(), "patrick-001")
    assert r["successor"] == "patrick-001"
    assert r["notarized"] is False

def test_succession_notarized_on_still_and_manifest(tmp_path):
    """Succesiunea lui Patrick e notarizată pe STILL și înregistrată în MANIFEST."""
    j = AuditJournal(str(tmp_path / "a.log"))
    n = HybridNotary(HashSigner("ed", "k1"), HashSigner("mld", "k2"),
                     HashSigner("sph", "k3"), journal=j)
    mf = IPManifest()
    v = HeritageVault()
    intent = _intent()
    r = v.designate_successor(intent, "patrick-001", notary=n, manifest=mf)
    assert r["notarized"] is True
    assert "payload_hash" in r
    assert len(r["sigs"]) == 3
    assert r["manifest_version"].startswith("v")
    assert r["manifest_hash"] is not None
    assert mf.verify()
    assert v.succession_record is not None
    assert v.succession_record.successor_anchor_id == "patrick-001"
    assert j.verify()


# ── MANIFEST ──
def test_chain_verifies():
    m = IPManifest()
    m.append([{"id": 121}]); m.append([{"id": 121}, {"id": 122}])
    assert m.verify()
    assert m.versions[1].prev_hash == m.versions[0].master_hash

def test_tamper_detected():
    m = IPManifest()
    m.append([{"id": 1}])
    m.versions[0].master_hash = "f" * 64
    assert m.verify() is False

def test_tx_marked_by_human():
    m = IPManifest()
    v = m.append([{"id": 1}])
    m.mark_tx(v.version, "opXYZ")
    assert m.versions[0].tx_hash == "opXYZ"


# ── POARTA FAZEI 4: pipeline complet → payload Tezos ──
def test_integration_full_pipeline(tmp_path):
    j = AuditJournal(str(tmp_path / "a.log"))
    hub, ag = _mesh(j)
    i = _intent()
    # 1) mesaj A2A valid
    m = ag["SENS"].send("GUARDIAN", "safety_score", {"DEPEND": 0.78},
                        i.anchor_id, i.text_hash, "m9")
    assert hub.submit(m)
    # 2) consens AGIK
    obs = [ObserverScore(k, "NOT_SAFE", {p: 0.8 for p in PILLARS}, f"r{k}")
           for k in "ABC"]
    r = consensus_round(obs)
    assert isinstance(r, SealedVerdict)
    # 3) notarizare STILL
    n = HybridNotary(HashSigner("ed", "k1"), HashSigner("mld", "k2"),
                     HashSigner("sph", "k3"), journal=j)
    rec = n.notarize(i.text_hash, {"verdict": r.verdict, "reasoning_hash": r.reasoning_hash})
    assert all(n.verify(rec, {"verdict": r.verdict, "reasoning_hash": r.reasoning_hash}).values())
    # 4) manifest v_next
    mf = IPManifest()
    v = mf.append([{"asset": "backbone-phase4", "hash": rec.payload_hash}])
    assert mf.verify()
    # 5) payload Tezos — gest explicit uman
    p = n.request_anchor(i, v.master_hash, v.n_entries, "2026-09-06", "BACKBONE-v1.0")
    assert p.endswith("S(M)=R") and v.master_hash in p
    assert j.verify()