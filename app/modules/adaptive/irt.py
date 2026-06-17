"""IRT 2PL adaptive engine (ADR-003). Pure functions — easy to unit test (SOLID: SRP)."""
import math


def p_correct(theta: float, a: float, b: float) -> float:
    return 1.0 / (1.0 + math.exp(-a * (theta - b)))


def update_theta(theta: float, a: float, b: float, correct: int, k: float) -> float:
    """Online ability update; k shrinks as the standard error falls."""
    return theta + k * (correct - p_correct(theta, a, b))
