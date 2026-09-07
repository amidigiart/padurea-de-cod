import numpy as np
import pytest

from backbone.anchor import HumanAnchor, AnchorError
from backbone.kuramoto import KuramotoFull
from backbone.scale import KuramotoMeanField
from backbone.valve import CoherenceMonitor
from backbone.adler import design_coupling, lock_condition, adler_fixed_point


# ───────────── 01 ANCHOR ─────────────
def _fake_signer(h): return "sig:" + h[:8]

def test_anchor_empty_intent_raises():
    with pytest.raises(AnchorError):
        HumanAnchor(_fake_signer).register_intent("   ", "human-001")

def test_anchor_missing_anchor_id_raises():
    with pytest.raises(AnchorError):
        HumanAnchor(_fake_signer).register_intent("vand moto aprilia", "  ")

def test_anchor_hash_deterministic_and_signed():
    a = HumanAnchor(_fake_signer)
    i1 = a.register_intent("test intent", "human-001")
    i2 = a.register_intent("test intent", "human-002")
    assert i1.text_hash == i2.text_hash
    assert i1.sig.startswith("sig:")


# ───────────── 02/03 UKBE vs SCALE ─────────────
def test_order_parameter_bounds():
    _, r = KuramotoFull(40, seed=1).step()
    assert 0.0 <= r <= 1.0

def test_sync_increases_with_coupling():
    k = KuramotoMeanField(200, K=3.0, sigma=0.3, seed=2)
    r0 = k.order_parameter()
    for _ in range(200):
        _, r = k.step()
    assert r > r0 and r > 0.9

def test_scale_equivalence_with_full():
    """POARTA 1: SCALE ≡ UKBE (echivalență numerică)."""
    full, mean = KuramotoFull(100, K=2.0, seed=7), KuramotoMeanField(100, K=2.0, seed=7)
    for _ in range(50):
        tf, rf = full.step()
        tm, rm = mean.step()
    assert np.max(np.abs(tf - tm)) < 1e-6
    assert abs(rf - rm) < 0.02

def test_scale_handles_large_n():
    k = KuramotoMeanField(5000, K=2.0, seed=5)   # scala de producție
    for _ in range(10):
        _, r = k.step()
    assert 0.0 <= r <= 1.0


# ───────────── 04 VALVE + RSI ─────────────
def test_beta_never_below_floor():
    """POARTA 2: β ≥ βmin invariant, pe orice traiectorie."""
    m = CoherenceMonitor(beta_min=0.15)
    rng = np.random.default_rng(3)
    for _ in range(500):
        m.update(rng.uniform(0, 1), rng.uniform(0, 1))
        assert m.beta >= m.beta_min - 1e-12

def test_floor_is_what_saves_human_weight():
    m = CoherenceMonitor(beta_min=0.15)
    assert m._adapt(1.0) == pytest.approx(0.0)      # fără floor: om ignorat
    m.update(1.0, 0.5)                              # coerență internă maximă
    assert m.beta == pytest.approx(0.15)            # floor ține omul în buclă

def test_rsi_in_unit_interval():
    m = CoherenceMonitor()
    rng = np.random.default_rng(4)
    for _ in range(100):
        rsi = m.update(rng.uniform(0, 1), rng.uniform(0, 1))
    assert 0.0 <= rsi <= 1.0

def test_valve_blocks_low_coherence():
    """POARTA 3: valve-ul blochează seal sub Φmin."""
    m = CoherenceMonitor(phi_min=0.5)
    assert m.allow_seal(0.8) is True
    assert m.allow_seal(0.5) is True
    assert m.allow_seal(0.49) is False

def test_phi_out_of_range_raises():
    with pytest.raises(ValueError):
        CoherenceMonitor().update(1.2, 0.5)


def test_ema_rsi_vs_raw_diverge():
    """EMA reacționează mai rapid la drift decât media aritmetică."""
    m = CoherenceMonitor(window=20)
    for _ in range(30):
        m.update(0.8, 0.8)
    m.update(0.1, 0.1)
    assert abs(m.update(0.1, 0.1) - m.rsi_raw) > 0.01


def test_ema_rsi_tracks_stable_signal():
    m = CoherenceMonitor(window=10)
    for _ in range(50):
        rsi = m.update(0.7, 0.7)
    assert abs(rsi - m.rsi_raw) < 0.05


# ───────────── 03 SCALE — concordance check ─────────────
def test_concordance_check_passes():
    """Mean-field și full Kuramoto converg pe sample mic."""
    from backbone.scale import ConcordanceError
    k = KuramotoMeanField(100, K=2.0, seed=42)
    result = k.concordance_check(sample_n=30, steps=5, tol=1e-4)
    assert result["passed"] is True
    assert result["max_deviation"] < 1e-4


def test_concordance_check_records_step_count():
    k = KuramotoMeanField(50, K=2.0, seed=7)
    for _ in range(10):
        k.step()
    result = k.concordance_check(sample_n=20, steps=3, tol=1e-4)
    assert result["step_count"] == 10


# ───────────── Adler / safety floor ─────────────
def test_design_coupling_margin():
    K = design_coupling(0.6)
    assert K == pytest.approx(1.5 * 0.6)
    assert lock_condition(0.6, K)

def test_adler_lock_vs_drift():
    assert adler_fixed_point(0.5, 1.0) is not None   # lock
    assert adler_fixed_point(1.5, 1.0) is None       # drift