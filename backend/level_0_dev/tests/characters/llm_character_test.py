from backend.level_4_systems.llm.clients import (
    get_llm_client,
    get_llm_model,
)
from backend.level_4_systems.llm.npc import generate_npc_data
from backend.level_5_entities.characters import create_npc


client = get_llm_client()
model = get_llm_model()

prompt = input("Describe your character: ")


# --------------------------------------------------
# LLM CREATION PASS
# --------------------------------------------------

payload = generate_npc_data(
    client=client,
    model=model,
    npc_prompt=prompt,
)


# --------------------------------------------------
# CHARACTER ENGINE
# --------------------------------------------------

npc = create_npc(
    payload=payload,
)


# --------------------------------------------------
# OUTPUT
# --------------------------------------------------

print("\n--- GENERATED NPC PROFILE ---")

print(f"Name: {npc.name}")
print(f"Age: {npc.age}")
print(f"Species: {npc.species}")
print(f"Sex: {npc.sex}")
print(f"Faction: {npc.faction}")
print(f"Occupation: {npc.occupation}")
print(f"Rank: {npc.rank}")
print(f"Home: {npc.home}")
print(f"Current Location: {npc.current_location}")

print(f"Tier: {npc.tier}")
print(f"Level: {npc.level}")
print(f"Alive: {npc.alive}")
print(f"NPC ID: {npc.npc_id}")

print(f"Description: {npc.description}")
print(f"Personality: {npc.personality}")
print(f"Enriched: {npc.enriched}")


print("\n--- LLM ATTRIBUTE BANDS ---")

for name, band in payload.attributes.model_dump().items():
    print(f"{name}: {band}")


print("\n--- GENERATED ATTRIBUTES ---")

for name, score in npc.attributes.items():
    print(f"{name}: {score}")


print("\n--- LLM SKILL BANDS ---")

for name, band in payload.skills.items():
    print(f"{name}: {band}")


print("\n--- GENERATED SKILLS ---")

for name, score in npc.skills.items():
    print(f"{name}: {score}")


print("\n--- RESOURCES ---")

for name, resource in npc.resources.items():
    print(
        f"{name}: "
        f"{resource['current']}/{resource['maximum']}"
    )