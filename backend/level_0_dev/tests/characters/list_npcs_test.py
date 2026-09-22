from backend.entities.characters.temp_store import load_npcs


npcs = load_npcs()


print("\n--- STORED NPCS ---")

if not npcs:
    print("No NPCs currently stored.")

for npc_id, npc in npcs.items():
    print(f"{npc.name} - {npc_id}")