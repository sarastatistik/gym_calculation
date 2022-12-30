def epley(weight: float, reps: int) -> float:
    return weight * (1 + (reps / 30))


def brzycki(weight: float, reps: int) -> float:
    return weight / (1.0278 - (0.0278 * reps))
