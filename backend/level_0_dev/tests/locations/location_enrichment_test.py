from backend.level_3_services.location import enrich_location
from backend.level_4_systems import get_location_repository


TARGET_LOCATION_NAME = "Azzinoth"


print("\n=== LOCATION ENRICHMENT TEST ===")


repository = get_location_repository()


# ------------------------------------------------------------------
# FIND TARGET
# ------------------------------------------------------------------

matches = [
    location
    for location in repository.get_all()
    if location.name == TARGET_LOCATION_NAME
]

if not matches:
    raise ValueError(
        f"Location not found: {TARGET_LOCATION_NAME}"
    )


# If we've generated the same named location more than once during
# testing, use the most recently stored one.
location = matches[-1]


print("\n--- BEFORE ENRICHMENT ---")

print(f"Name: {location.name}")
print(f"Type: {location.location_type}")
print(f"ID: {location.location_id}")
print(f"Enriched: {location.enriched}")
print(f"Brief: {location.brief_description}")
print(f"Description: {location.description}")


print("\n--- KNOWN CHILDREN ---")

children = repository.get_children(
    location.location_id
)

for child in children:
    print(
        f"- {child.name} "
        f"[{child.location_type}] "
        f"| {child.brief_description}"
    )


# ------------------------------------------------------------------
# ENRICH
# ------------------------------------------------------------------

print("\n--- RUNNING ENRICHMENT ---")

enriched_location = enrich_location(
    location.location_id
)

if enriched_location is None:
    raise ValueError(
        "Location enrichment returned None."
    )


# ------------------------------------------------------------------
# RELOAD FROM REPOSITORY
# ------------------------------------------------------------------

persisted_location = repository.get(
    location.location_id
)

if persisted_location is None:
    raise ValueError(
        "Enriched location was not found in repository."
    )


print("\n--- AFTER ENRICHMENT ---")

print(f"Name: {persisted_location.name}")
print(f"Type: {persisted_location.location_type}")
print(f"ID: {persisted_location.location_id}")
print(f"Enriched: {persisted_location.enriched}")
print(f"Brief: {persisted_location.brief_description}")

print("\nFULL DESCRIPTION:\n")
print(persisted_location.description)


print("\n--- STRUCTURE CHECK ---")

persisted_children = repository.get_children(
    persisted_location.location_id
)

for child in persisted_children:
    print(
        f"- {child.name} "
        f"[{child.location_type}] "
        f"| structure_generated="
        f"{child.structure_generated}"
    )


print("\n--- SUMMARY ---")

print(
    f"Location: "
    f"{persisted_location.name}"
)

print(
    f"Enriched: "
    f"{persisted_location.enriched}"
)

print(
    f"Known children preserved: "
    f"{len(persisted_children)}"
)

print(
    f"Description length: "
    f"{len(persisted_location.description or '')} characters"
)