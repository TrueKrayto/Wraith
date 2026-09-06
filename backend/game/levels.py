MAX_LEVEL = 50
MIN_LEVEL = 1


def clamp_level(level: int) -> int:
    """Keep a character level inside the valid game range."""
    return max(MIN_LEVEL, min(level, MAX_LEVEL))