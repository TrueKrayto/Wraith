from dataclasses import dataclass


@dataclass
class StatusEffect:
    # Human-readable status name.
    name: str

    # What originally caused/applied the effect.
    source: str | None = None

    # Freeform mechanical or narrative effect.
    effect: str = "none"

    # Optional resource affected.
    resource: str | None = None

    # Optional numerical magnitude.
    amount: int | None = None

    # Optional duration stored as state.
    duration: int | None = None

    # Optional parent status this effect depends upon.
    #
    # Example:
    # drunk
    #   └── friendly
    #
    # Removing the parent automatically removes its children.
    parent_effect: str | None = None