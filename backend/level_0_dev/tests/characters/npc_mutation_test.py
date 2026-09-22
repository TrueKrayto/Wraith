from backend.entities.characters.mutations import (
    add_skill,
    add_status_effect,
)
from backend.entities.characters.status_effects import StatusEffect
from backend.entities.characters.temp_store import (
    load_npcs,
    save_npcs,
)


npcs = load_npcs()


print("\n--- STORED NPCS ---")

for npc_id, npc in npcs.items():
    print(f"{npc.name} - {npc_id}")


npc_id = input("\nNPC ID: ").strip()

if npc_id not in npcs:
    raise ValueError("NPC not found.")


npc = npcs[npc_id]


print(f"\nSelected: {npc.name}")


# Add a dynamically inferred skill.
dance_score = add_skill(
    npc,
    skill_name="dancing",
    band="mid",
)

print(f"Added dancing: {dance_score}")


# Add a freeform status effect.
add_status_effect(
    npc,
    StatusEffect(
        name="Poisoned",
        source="test poison",
        effect="damage",
        resource="health",
        amount=5,
        duration=4,
    ),
)


save_npcs(npcs)


print("\n--- UPDATED NPC ---")

print(f"Name: {npc.name}")

print("\nSkills:")
for name, value in npc.skills.items():
    print(f"{name}: {value}")

print("\nStatus Effects:")
for name, effect in npc.status_effects.items():
    print(
        f"{name}: "
        f"effect={effect.effect}, "
        f"resource={effect.resource}, "
        f"amount={effect.amount}, "
        f"duration={effect.duration}"
    )