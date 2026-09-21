from backend.entities.characters.statblock_generator import (
    generate_character_statblock,
)


payload = {
    "level": 10,

    "attributes": {
        "strength": "mid",
        "agility": "mid",
        "endurance": "high",
        "intellect": "high",
        "attunement": "high",
        "presence": "low",
    },

    "skills": {
        "combat": "high",
        "magic": "high",
        "perception": "mid",
        "charisma": "low",
        "stealth": "low",
        "survival": "low",
        "swordsmanship": "high",
        "alchemy": "mid",
    },

    "seed": "test_battlemage",
}


statblock = generate_character_statblock(payload)


print("\n--- LEVEL 10 BATTLEMAGE ---")

print("\nATTRIBUTES")
for name, value in statblock["attributes"].items():
    print(f"{name}: {value}")

print("\nSKILLS")
for name, value in statblock["skills"].items():
    print(f"{name}: {value}")

print("\nRESOURCES")
for name, values in statblock["resources"].items():
    print(
        f"{name}: "
        f"{values['current']}/{values['maximum']}"
    )