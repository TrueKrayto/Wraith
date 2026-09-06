from backend.game.checks import calculate_check_power
from backend.game.combat import resolve_attack


attacker_power = calculate_check_power(
    character_level=10,
    attribute=10,
    core_skill=20,
    specialization=15,
)

defender_power = calculate_check_power(
    character_level=10,
    attribute=8,
    core_skill=10,
    specialization=5,
)

result = resolve_attack(
    attacker_power=attacker_power,
    defender_power=defender_power,
    base_damage=10,
    character_level=10,
    core_skill=20,
    specialization=15,
)

print(result)

from backend.game.checks import difficulty_check


skill_test = difficulty_check(
    character_power=40,
    difficulty=45,
)

print(skill_test)