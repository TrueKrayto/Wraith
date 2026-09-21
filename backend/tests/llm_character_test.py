from backend.llm.npc_creator import generate_npc


prompt = input("Describe your character: ")

npc = generate_npc(prompt)


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


print("\n--- ATTRIBUTES ---")

for name, score in npc.attributes.items():
    print(f"{name}: {score}")


print("\n--- SKILLS ---")

for name, score in npc.skills.items():
    print(f"{name}: {score}")


print("\n--- RESOURCES ---")

for name, resource in npc.resources.items():
    print(
        f"{name}: "
        f"{resource['current']}/{resource['maximum']}"
    )