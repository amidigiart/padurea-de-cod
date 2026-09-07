"""Mecanism Adler — regula de proiectare a safety floor-ului."""
import numpy as np


def lock_condition(delta_omega_max: float, K_eff: float) -> bool:
    return K_eff >= delta_omega_max


def design_coupling(delta_omega_max: float, margin: float = 1.5) -> float:
    """Keff ≥ 1.5 · Δωmax — marja de proiectare."""
    return margin * delta_omega_max


def adler_fixed_point(delta_omega: float, K_eff: float):
    """Punct fix stabil al dΔ/dt = Δω − Keff·sin(Δ); None = drift (fără lock)."""
    if abs(delta_omega) > K_eff:
        return None
    return float(np.arcsin(delta_omega / K_eff))