import random


def roll_d4() -> int:
    return random.randint(1, 4)


def roll_d6() -> int:
    return random.randint(1, 6)


def roll_d8() -> int:
    return random.randint(1, 8)


def roll_d12() -> int:
    return random.randint(1, 12)


def roll_d20() -> int:
    return random.randint(1, 20)


def roll_d100() -> int:
    return random.randint(1, 100)


def roll_dx(sides: int) -> int:
    """Roll a die with any number of sides."""
    if sides < 1:
        raise ValueError("Die must have at least 1 side.")

    return random.randint(1, sides)


def roll_range(lower: int, upper: int) -> int:
    """Roll a random integer between lower and upper, inclusive."""
    if lower > upper:
        raise ValueError("Lower bound cannot be greater than upper bound.")

    return random.randint(lower, upper)