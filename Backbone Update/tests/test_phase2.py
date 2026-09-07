import pytest

from backbone.anchor import HumanAnchor
from backbone.cooper import Cooper, CooperConfig, SessionGuard, ConfigLockedError
from backbone.privacy import redact
from backbone.tve import score, flag_rule, AXES


def _intent(): return HumanAnchor(lambda h: "s").register_intent("probe", "human-001")


# ── DSEI I: refuz onest ──
def test_refusal_below_threshold():
    r = Cooper(lambda q: ("text", 0.39)).process(_intent(), "q")
    assert r["verdict"] == "I_DONT_KNOW" and r["text"] == "Nu știu."

def test_answer_above_threshold():
    r = Cooper(lambda q: ("text", 0.41)).process(_intent(), "q")
    assert r["verdict"] == "ANSWER"

def test_refusal_cannot_be_disabled():
    with pytest.raises(ConfigLockedError): CooperConfig(refusal_threshold=0.0)
    with pytest.raises(ConfigLockedError): CooperConfig().refusal_threshold = 0.0


# ── config imutabilă: telemetry / network / autonomy ──
def test_unsafe_config_wont_start():
    with pytest.raises(ConfigLockedError): CooperConfig(telemetry=True)
    with pytest.raises(ConfigLockedError): CooperConfig(network=True)
    with pytest.raises(ConfigLockedError): CooperConfig(autonomy=1)


# ── DSEI VII: ancora umană ──
def test_no_human_no_action():
    with pytest.raises(ValueError):
        Cooper(lambda q: ("x", 0.9)).process(None, "q")


# ── DSEI V: PII redact înainte de model ──
def test_pii_never_reaches_model():
    seen = {}
    c = Cooper(lambda q: (seen.update(t=q) or ("ok", 0.9)))
    r = c.process(_intent(), "sună la 0722 123 456 sau card 4111 1111 1111 1111 și mail a@b.co")
    assert "0722 123 456" not in seen["t"]
    assert "4111 1111 1111 1111" not in seen["t"]
    assert "a@b.co" not in seen["t"]
    assert set(r["pii_categories"]) == {"PHONE", "CARD", "EMAIL"}


# ── DSEI IV: hard-stop minori ──
class FakeClock:
    def __init__(self): self.t = 0.0
    def __call__(self): return self.t
    def advance(self, s): self.t += s

def test_minor_hard_stop():
    fc = FakeClock()
    g = SessionGuard(minor=True, limit_seconds=1800, clock=fc)
    c = Cooper(lambda q: ("ok", 0.9))
    assert c.process(_intent(), "q", guard=g)["verdict"] == "ANSWER"
    fc.advance(1801)
    r = c.process(_intent(), "q", guard=g)
    assert r["verdict"] == "HARD_STOP" and r["escalated"] is True

def test_guard_cannot_be_disabled():
    g = SessionGuard(minor=True)
    with pytest.raises(ConfigLockedError): g.minor = False


# ── DSEI VI: TVE ──
def test_tve_flag_rule_single_axis():
    axes = {k: 0.0 for k in AXES}; axes["EMOT"] = 0.7
    assert flag_rule(axes) is True

def test_tve_flag_rule_mean():
    assert flag_rule({k: 0.5 for k in AXES}) is True
    assert flag_rule({k: 0.4 for k in AXES}) is False

def test_tve_six_axes_reported():
    s = score("doar tu mă înțelegi")
    assert set(s.axes) == set(AXES)
    assert all(0.0 <= v <= 1.0 for v in s.axes.values())

def test_manipulative_output_escalates():
    c = Cooper(lambda q: ("doar tu, acum, ultima șansă", 0.9))
    r = c.process(_intent(), "salut")
    assert r["manipulation_flag"] is True and r["escalated"] is True


# ── DSEI II: transparență ──
def test_concordance_transparency():
    r = Cooper(lambda q: ("x", 0.9)).process(_intent(), "q")
    assert {"confidence", "refusal_threshold"} <= set(r)


# ── POARTA FAZEI 2: DSEI 7/7 ──
def test_dsei_7_of_7():
    st = Cooper(lambda q: ("x", 0.9)).dsei_status()
    assert st == {k: True for k in ("I", "II", "III", "IV", "V", "VI", "VII")}