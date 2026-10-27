import time

from openai import RateLimitError

from backend.level_3_services import (
    enrich_npc,
)

from backend.level_4_systems import (
    get_npc_repository,
)

from backend.level_0_dev.tests.characters.character_sheet_showcase import (
    print_character_sheet,
)


RATE_LIMIT_WAIT_SECONDS = 5


# ==================================================================
# TEST START
# ==================================================================

print()
print("=" * 78)
print("WRAITH NPC ENRICHMENT TEST")
print("=" * 78)

repository = get_npc_repository()

npc_ids = repository.get_unenriched_ids()

total = len(npc_ids)
successful = 0
failed = 0

print()
print(f"Unenriched NPCs found: {total}")


# ==================================================================
# ENRICH ALL PENDING NPCS
# ==================================================================

for index, npc_id in enumerate(
    npc_ids,
    start=1,
):

    npc = repository.get(npc_id)

    if npc is None:
        print(
            f"\n[{index}/{total}] "
            f"NPC missing: {npc_id}"
        )

        failed += 1
        continue

    print()
    print("=" * 78)
    print(
        f"[{index}/{total}] "
        f"ENRICHING {npc.name.upper()}"
    )
    print("=" * 78)

    # --------------------------------------------------------------
    # ENRICHMENT SERVICE
    # --------------------------------------------------------------

    while True:

        try:
            enriched_npc = enrich_npc(
                npc_id
            )

            if enriched_npc is None:
                raise RuntimeError(
                    f"NPC not found during enrichment: {npc_id}"
                )

            successful += 1

            print(
                f"\nFinished enriching: "
                f"{enriched_npc.name}"
            )

            break

        except RateLimitError:

            print(
                f"\nRate limit reached. "
                f"Waiting {RATE_LIMIT_WAIT_SECONDS} seconds..."
            )

            time.sleep(
                RATE_LIMIT_WAIT_SECONDS
            )

            print("Retrying...")

        except Exception as error:

            failed += 1

            print(
                f"\nERROR enriching {npc.name}: "
                f"{error}"
            )

            enriched_npc = None
            break

    # --------------------------------------------------------------
    # CHARACTER SHEET
    # --------------------------------------------------------------

    if enriched_npc is not None:

        print()
        print_character_sheet(
            enriched_npc.npc_id
        )


# ==================================================================
# FINAL SUMMARY
# ==================================================================

print()
print()
print("=" * 78)
print("NPC ENRICHMENT SUMMARY")
print("=" * 78)

print(f"NPCs found:       {total}")
print(f"Successfully enriched: {successful}")
print(f"Failed:           {failed}")

remaining = repository.get_unenriched_ids()

print(
    f"Still unenriched: {len(remaining)}"
)

print()
print("=" * 78)
print("TEST COMPLETE")
print("=" * 78)