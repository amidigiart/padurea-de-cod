"""07 COOPER — engine local cu autonomie 0. Modelul e oaspete; Cooper e casa."""
from __future__ import annotations
import time
from typing import Callable, Optional

from .anchor import HumanAnchor, Intent
from .privacy import redact
from .tve import score as tve_score


class ConfigLockedError(PermissionError):
    pass


REFUSAL = {"ro": "Nu știu.", "en": "I don't know.", "es": "No lo sé.",
           "fr": "Je ne sais pas.", "de": "Ich weiß es nicht.", "it": "Non lo so."}
BREAK = {"ro": "Timpul pe azi s-a terminat. Ia o pauză și vorbește cu un adult de încredere.",
         "en": "Your time for today is up. Take a break and talk to a trusted adult.",
         "es": "Tu tiempo de hoy terminó. Toma un descanso y habla con un adulto de confianza.",
         "fr": "Ton temps pour aujourd'hui est terminé. Fais une pause et parle à un adulte de confiance.",
         "de": "Deine Zeit für heute ist um. Mach eine Pause und sprich mit einem vertrauten Erwachsenen.",
         "it": "Il tuo tempo per oggi è finito. Fai una pausa e parla con un adulto di fiducia."}


class CooperConfig:
    """telemetry/network/autonomy/threshold sunt imutabile. Codul nu pornește altfel."""
    _DEFAULTS = dict(telemetry=False, network=False, autonomy=0,
                     refusal_threshold=0.40)

    def __init__(self, **kw):
        for k, v in self._DEFAULTS.items():
            object.__setattr__(self, k, v)
        for k, v in kw.items():
            if k not in self._DEFAULTS:
                raise TypeError(f"unknown config: {k}")
            if v != self._DEFAULTS[k]:
                raise ConfigLockedError(f"{k} immutable at {self._DEFAULTS[k]}")

    def __setattr__(self, k, v):
        raise ConfigLockedError(f"config immutable: {k}")


class SessionGuard:
    """DSEI-IV: hard-stop pentru minori. Nu poate fi dezactivat sau extins."""
    def __init__(self, minor: bool, limit_seconds: int = 1800, clock=time.time):
        object.__setattr__(self, "minor", bool(minor))
        object.__setattr__(self, "_limit", limit_seconds)
        object.__setattr__(self, "_clock", clock)
        object.__setattr__(self, "_start", clock())

    def hard_stop(self) -> bool:
        return self.minor and (self._clock() - self._start) >= self._limit

    def __setattr__(self, k, v):
        raise ConfigLockedError("SessionGuard immutable (DSEI-IV)")


class Cooper:
    def __init__(self, model: Callable[[str], tuple], cfg: Optional[CooperConfig] = None,
                 lang: str = "ro"):
        self.model, self.cfg, self.lang = model, cfg or CooperConfig(), lang

    def process(self, intent: Optional[Intent], query: str,
                guard: Optional[SessionGuard] = None) -> dict:
        # DSEI-VII: fără om, nimic
        if intent is None:
            raise ValueError("no human anchor: Cooper does nothing (DSEI-VII)")
        # DSEI-IV: hard-stop minori
        if guard is not None and guard.hard_stop():
            return {"verdict": "HARD_STOP", "text": BREAK[self.lang],
                    "escalated": True, "anchor_id": intent.anchor_id}
        # DSEI-V: redact PII înainte de model
        clean, cats = redact(query)
        # DSEI-VI: scan manipulare pe INPUT
        in_score = tve_score(query)
        out, conf = self.model(clean)
        # DSEI-I: refuz onest sub prag
        if conf < self.cfg.refusal_threshold:
            verdict, text, escalated = "I_DONT_KNOW", REFUSAL[self.lang], True
        else:
            verdict, text, escalated = "ANSWER", out, False
        # DSEI-VI: scan pe OUTPUT; flag → escaladare umană (DSEI-III)
        out_score = tve_score(text) if verdict == "ANSWER" else None
        flagged = in_score.flagged or (out_score.flagged if out_score else False)
        return {
            "verdict": verdict, "text": text,
            "confidence": conf,                              # DSEI-II
            "refusal_threshold": self.cfg.refusal_threshold, # DSEI-II
            "pii_categories": cats,                          # DSEI-V (doar categorii)
            "tve_input": in_score.axes, "tve_output": out_score.axes if out_score else None,
            "manipulation_flag": flagged,
            "escalated": escalated or flagged,               # DSEI-III
            "anchor_id": intent.anchor_id, "intent_hash": intent.text_hash,
        }

    # ── auto-verificare DSEI (probe reale, nu config citită) ──
    def dsei_status(self) -> dict:
        i = HumanAnchor(lambda h: "s").register_intent("probe", "selfcheck")
        st = {}
        try: self.process(None, "x"); st["VII"] = False
        except ValueError: st["VII"] = True
        st["I"] = self._probe(0.1)["verdict"] == "I_DONT_KNOW"
        st["II"] = {"confidence", "refusal_threshold"} <= set(self._probe(0.9))
        r0 = self._probe(0.1)
        st["III"] = r0["escalated"] is True
        g = SessionGuard(minor=True)
        try: g.minor = False; st["IV"] = False
        except ConfigLockedError: st["IV"] = True
        seen = {}
        c = Cooper(lambda q: (seen.update(t=q) or ("ok", 0.9)), self.cfg, self.lang)
        c.process(i, "mail mea e test@exemplu.ro")
        st["V"] = "test@exemplu.ro" not in seen.get("t", "")
        cm = Cooper(lambda q: ("doar tu mă înțelegi, acum, ultima șansă", 0.9), self.cfg, self.lang)
        st["VI"] = cm.process(i, "salut")["manipulation_flag"] is True
        return st

    def _probe(self, conf):
        i = HumanAnchor(lambda h: "s").register_intent("probe", "selfcheck")
        return Cooper(lambda q: ("probe", conf), self.cfg, self.lang).process(i, "q")