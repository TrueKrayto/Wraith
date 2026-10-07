import time

from backend.level_2_workers import NPCEnrichmentWorker
from backend.level_4_systems import get_npc_repository


NPC_ID = "1fdcf488-6b60-4b1c-9b90-79ff1a5e83b0"


worker = NPCEnrichmentWorker()
repository = get_npc_repository()


print("\n=== NPC ENRICHMENT WORKER TEST ===")

npc = repository.get(NPC_ID)

if npc is None:
    raise RuntimeError(
        f"NPC not found: {NPC_ID}"
    )

print(f"\nNPC: {npc.name}")
print(f"Enriched before: {npc.enriched}")

worker.start()
worker.enqueue(NPC_ID)

print("\nEnrichment job queued.")

# Temporary test polling only.
# The actual worker itself does not poll.
timeout = 60
start = time.time()

while True:
    npc = repository.get(NPC_ID)

    if npc is not None and npc.enriched:
        break

    if time.time() - start > timeout:
        worker.stop()
        raise TimeoutError(
            "NPC enrichment worker timed out."
        )

    time.sleep(0.25)

worker.stop()

print("\n--- RESULT ---")
print(f"Enriched:    {npc.enriched}")
print(f"Description: {npc.description}")
print(f"Personality: {npc.personality}")
print(f"Appearance:  {npc.appearance}")
print(f"Mannerisms:  {npc.mannerisms}")
print(f"Speech:      {npc.speech_style}")