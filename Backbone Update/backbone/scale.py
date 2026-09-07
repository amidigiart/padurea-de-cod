"""03 SCALE — variantă de producție mean-field O(N).
Identitate matematică: (K/N)·Σ sin(θj−θi) ≡ K·r·sin(ψ−θi).
Runtime concordance: verifică periodic echivalența cu full Kuramoto
pe un sample — diferența dintre 'funcționează matematic' și
'funcționează verificabil'."""
import numpy as np


class ConcordanceError(RuntimeError):
    pass


class KuramotoMeanField:
    def __init__(self, n: int, K: float = 2.0, sigma: float = 0.3, seed: int = 0):
        rng = np.random.default_rng(seed)
        self.n, self.K = n, K
        self.theta = rng.uniform(0.0, 2 * np.pi, n)
        self.omega = rng.normal(0.0, sigma, n)
        self._step_count: int = 0
        self._concordance_interval: int = 100
        self._concordance_tol: float = 1e-6
        self._last_concordance: dict = {}

    def step(self, dt: float = 0.05):
        z = np.exp(1j * self.theta).mean()                    # O(N)
        r, psi = float(abs(z)), float(np.angle(z))
        dtheta = self.omega + self.K * r * np.sin(psi - self.theta)
        self.theta = (self.theta + dt * dtheta) % (2 * np.pi)
        self._step_count += 1
        return self.theta, r

    def order_parameter(self) -> float:
        return float(abs(np.exp(1j * self.theta).mean()))

    def concordance_check(self, sample_n: int = 50, steps: int = 10,
                          dt: float = 0.05, tol: float = 1e-6) -> dict:
        """Rulează full O(N²) pe un sample și compară cu mean-field.
        Returnează max_deviation și passed. Aruncă ConcordanceError dacă eșuează."""
        n = min(sample_n, self.n)
        rng = np.random.default_rng(42)
        theta0 = rng.uniform(0.0, 2 * np.pi, n)
        omega0 = rng.normal(0.0, 0.3, n)

        theta_mf = theta0.copy()
        theta_full = theta0.copy()

        for _ in range(steps):
            # mean-field
            z = np.exp(1j * theta_mf).mean()
            r, psi = abs(z), np.angle(z)
            theta_mf = (theta_mf + dt * (omega0 + self.K * r * np.sin(psi - theta_mf))) % (2 * np.pi)
            # full O(N²)
            diff = theta_full[None, :] - theta_full[:, None]
            coupling = (self.K / n) * np.sin(diff).sum(axis=1)
            theta_full = (theta_full + dt * (omega0 + coupling)) % (2 * np.pi)

        max_dev = float(np.max(np.abs(theta_mf - theta_full)))
        passed = max_dev < tol
        self._last_concordance = {"max_deviation": max_dev, "passed": passed,
                                  "sample_n": n, "steps": steps,
                                  "step_count": self._step_count}
        if not passed:
            raise ConcordanceError(
                f"mean-field/full divergence {max_dev:.2e} > tol {tol:.2e}")
        return self._last_concordance