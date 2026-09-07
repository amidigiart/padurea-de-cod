"""02 UKBE — nucleu de coerență, referință all-pairs O(N²)."""
import numpy as np


class KuramotoFull:
    def __init__(self, n: int, K: float = 2.0, sigma: float = 0.3, seed: int = 0):
        rng = np.random.default_rng(seed)
        self.n, self.K = n, K
        self.theta = rng.uniform(0.0, 2 * np.pi, n)
        self.omega = rng.normal(0.0, sigma, n)

    def _coupling(self) -> np.ndarray:
        diff = self.theta[None, :] - self.theta[:, None]      # N x N
        return (self.K / self.n) * np.sin(diff).sum(axis=1)

    def step(self, dt: float = 0.05):
        self.theta = (self.theta + dt * (self.omega + self._coupling())) % (2 * np.pi)
        return self.theta, self.order_parameter()

    def order_parameter(self) -> float:
        return float(abs(np.exp(1j * self.theta).mean()))     # Φintern = r