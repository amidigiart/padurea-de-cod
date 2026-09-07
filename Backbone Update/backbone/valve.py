"""04 VALVE — poartă de entropie + monitor RSI cu safety floor βmin.
RSI folosește exponential moving average (EMA) — mai reactiv la drift
decât media aritmetică, exact unde ScaleEngine câștigă 10/12 recovery."""
import numpy as np


class CoherenceMonitor:
    def __init__(self, beta_min: float = 0.15, phi_min: float = 0.5,
                 window: int = 50, ema_alpha: float = 0.0):
        self.beta_min, self.phi_min, self.window = beta_min, phi_min, window
        self.beta = beta_min
        self.alpha = 1.0 - beta_min
        self._buf: list = []
        self._ema: float = 0.0
        self._ema_alpha = ema_alpha if ema_alpha > 0 else 2.0 / (window + 1)
        self._count: int = 0

    def _adapt(self, phi_intern: float) -> float:
        base = 0.10 * (1.0 - phi_intern)
        if self._count < 2:
            return base
        recent = self._buf[-1] if self._buf else phi_intern
        delta = abs(recent - self._ema)
        return base + 0.15 * delta

    def update(self, phi_intern: float, phi_extern: float) -> float:
        if not (0.0 <= phi_intern <= 1.0 and 0.0 <= phi_extern <= 1.0):
            raise ValueError("phi must be in [0,1]")
        self.beta = max(self.beta_min, min(1.0, self._adapt(phi_intern)))
        self.alpha = 1.0 - self.beta
        phi_t = self.alpha * phi_intern + self.beta * phi_extern
        self._buf.append(phi_t)
        self._buf = self._buf[-self.window:]
        self._count += 1
        if self._count == 1:
            self._ema = phi_t
        else:
            self._ema = self._ema_alpha * phi_t + (1 - self._ema_alpha) * self._ema
        return self._ema                                       # RSI (EMA)

    def allow_seal(self, phi_intern: float) -> bool:
        """Entropy Valve: fără seal când oscilatorii sunt desincronizați."""
        return phi_intern >= self.phi_min

    @property
    def rsi_raw(self) -> float:
        """Media aritmetică pe fereastră (pentru comparație/debug)."""
        return float(np.mean(self._buf)) if self._buf else 0.0

    @property
    def entropy(self) -> float:
        return 1.0 - (self._buf[-1] if self._buf else 0.0)