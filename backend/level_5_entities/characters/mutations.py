import random

from .attributes import clamp_attribute
from .npc import NPC
from .resources import clamp_resource
from .schemas import NPCMutationData
from .skills import CORE_SKILLS, clamp_skill
from .stat_bands import StatBand
from .stat_generator import generate_skills
from .status_effects import StatusEffect


# Fields that can be changed directly without requiring
# dedicated mechanical mutation logic.
EDITABLE_NPC_FIELDS = {
    "name",
    "age",
    "species",
    "sex",
    "faction",
    "occupation",
    "rank",
    "home",
    "current_location",
    "tier",
    "alive",
}


# ------------------------------------------------------------------
# PROFILE / WORLD STATE
# ------------------------------------------------------------------

def update_npc(
    npc: NPC,
    **changes,
) -> NPC:
    """
    Update ordinary NPC profile/world-state fields.

    Mechanical fields are handled by dedicated mutation functions.
    """

    for field_name, value in changes.items():

        if field_name not in EDITABLE_NPC_FIELDS:
            raise ValueError(
                f"'{field_name}' cannot be changed through update_npc."
            )

        if field_name == "tier":
            if value not in {"low", "medium", "high"}:
                raise ValueError(
                    "NPC tier must be low, medium, or high."
                )

        setattr(
            npc,
            field_name,
            value,
        )

    return npc


# ------------------------------------------------------------------
# ATTRIBUTES
# ------------------------------------------------------------------

def update_attribute(
    npc: NPC,
    attribute_name: str,
    value: int,
) -> int:
    """
    Set an existing character attribute.

    Attribute values are clamped to the game's valid 1-20 range.
    """

    attribute_name = (
        attribute_name
        .strip()
        .lower()
    )

    if attribute_name not in npc.attributes:
        raise ValueError(
            f"NPC does not have attribute '{attribute_name}'."
        )

    value = clamp_attribute(value)

    npc.attributes[attribute_name] = value

    return value


# ------------------------------------------------------------------
# SKILLS
# ------------------------------------------------------------------

def add_skill(
    npc: NPC,
    skill_name: str,
    band: StatBand | str,
    seed: str | int | None = None,
) -> int:
    """
    Add a new dynamic skill.

    The caller supplies a capability band.
    The character engine generates the exact numerical value.
    """

    skill_name = (
        skill_name
        .strip()
        .lower()
    )

    if not skill_name:
        raise ValueError(
            "Skill name cannot be empty."
        )

    if skill_name in npc.skills:
        raise ValueError(
            f"NPC already has skill '{skill_name}'."
        )

    rng = random.Random(seed)

    generated = generate_skills(
        level=npc.level,
        bands={
            skill_name: band,
        },
        rng=rng,
    )

    value = generated[skill_name]

    npc.skills[skill_name] = value

    return value


def update_skill(
    npc: NPC,
    skill_name: str,
    value: int,
) -> int:
    """
    Set the numerical value of an existing skill.

    Values are clamped to the character's current skill cap.
    """

    skill_name = (
        skill_name
        .strip()
        .lower()
    )

    if skill_name not in npc.skills:
        raise ValueError(
            f"NPC does not have skill '{skill_name}'."
        )

    value = clamp_skill(
        skill_level=value,
        character_level=npc.level,
    )

    npc.skills[skill_name] = value

    return value


def remove_skill(
    npc: NPC,
    skill_name: str,
) -> None:
    """
    Remove a specialist skill.

    Core skills cannot be removed.
    """

    skill_name = (
        skill_name
        .strip()
        .lower()
    )

    if skill_name in CORE_SKILLS:
        raise ValueError(
            f"Core skill '{skill_name}' cannot be removed."
        )

    if skill_name not in npc.skills:
        raise ValueError(
            f"NPC does not have skill '{skill_name}'."
        )

    del npc.skills[skill_name]


# ------------------------------------------------------------------
# RESOURCES
# ------------------------------------------------------------------

def update_resource(
    npc: NPC,
    resource_name: str,
    current: int | None = None,
    maximum: int | None = None,
) -> dict[str, int]:
    """
    Update an existing character resource.

    Either current, maximum, or both may be changed.

    Current is always kept between 0 and maximum.
    If maximum is reduced below the existing current value,
    current is automatically clamped down.
    """

    resource_name = (
        resource_name
        .strip()
        .lower()
    )

    if resource_name not in npc.resources:
        raise ValueError(
            f"NPC does not have resource '{resource_name}'."
        )

    if current is None and maximum is None:
        raise ValueError(
            "Resource update requires current, maximum, or both."
        )

    resource = npc.resources[resource_name]

    # Update maximum first so current can be clamped
    # against the new value.
    if maximum is not None:

        if maximum < 0:
            raise ValueError(
                "Resource maximum cannot be negative."
            )

        resource["maximum"] = maximum

        resource["current"] = clamp_resource(
            current=resource["current"],
            maximum=resource["maximum"],
        )

    if current is not None:
        resource["current"] = clamp_resource(
            current=current,
            maximum=resource["maximum"],
        )

    return resource


# ------------------------------------------------------------------
# STATUS EFFECTS
# ------------------------------------------------------------------

def add_status_effect(
    npc: NPC,
    status_effect: StatusEffect,
    replace: bool = False,
) -> StatusEffect:
    """
    Add a freeform status effect.

    If replace=True, an existing effect with the same name
    is refreshed/replaced.
    """

    key = (
        status_effect.name
        .strip()
        .lower()
    )

    if not key:
        raise ValueError(
            "Status effect name cannot be empty."
        )

    if status_effect.parent_effect is not None:

        parent_key = (
            status_effect.parent_effect
            .strip()
            .lower()
        )

        if not parent_key:
            parent_key = None

        if parent_key == key:
            raise ValueError(
                "A status effect cannot be its own parent."
            )

        if (
            parent_key is not None
            and parent_key not in npc.status_effects
        ):
            raise ValueError(
                f"Parent status effect '{parent_key}' does not exist."
            )

        status_effect.parent_effect = parent_key

    if key in npc.status_effects and not replace:
        raise ValueError(
            f"NPC already has status effect "
            f"'{status_effect.name}'."
        )

    npc.status_effects[key] = status_effect

    return status_effect


def update_status_effect(
    npc: NPC,
    name: str,
    **changes,
) -> StatusEffect:
    """
    Update stored status-effect state.

    This does not resolve, tick, apply, or expire the effect.
    """

    key = (
        name
        .strip()
        .lower()
    )

    if key not in npc.status_effects:
        raise ValueError(
            f"NPC does not have status effect '{name}'."
        )

    status_effect = npc.status_effects[key]

    editable_fields = {
        "name",
        "source",
        "effect",
        "resource",
        "amount",
        "duration",
        "parent_effect",
    }

    for field_name in changes:
        if field_name not in editable_fields:
            raise ValueError(
                f"'{field_name}' is not a valid "
                f"status-effect field."
            )

    new_name = changes.get(
        "name",
        status_effect.name,
    )

    new_key = (
        new_name
        .strip()
        .lower()
    )

    if not new_key:
        raise ValueError(
            "Status effect name cannot be empty."
        )

    if (
        new_key != key
        and new_key in npc.status_effects
    ):
        raise ValueError(
            f"NPC already has status effect '{new_name}'."
        )

    if "parent_effect" in changes:

        parent = changes["parent_effect"]

        if parent is not None:

            parent = (
                parent
                .strip()
                .lower()
            )

            if not parent:
                parent = None

            if parent == new_key:
                raise ValueError(
                    "A status effect cannot be its own parent."
                )

            if (
                parent is not None
                and parent not in npc.status_effects
            ):
                raise ValueError(
                    f"Parent status effect '{parent}' does not exist."
                )

        changes["parent_effect"] = parent

    for field_name, value in changes.items():
        setattr(
            status_effect,
            field_name,
            value,
        )

    # If the effect itself is renamed, preserve all
    # child dependency links.
    if new_key != key:

        del npc.status_effects[key]

        npc.status_effects[new_key] = status_effect

        for child in npc.status_effects.values():

            if child.parent_effect == key:
                child.parent_effect = new_key

    return status_effect


def remove_status_effect(
    npc: NPC,
    name: str,
) -> None:
    """
    Remove a status effect and all dependent child effects.

    Child removal is recursive.
    """

    key = (
        name
        .strip()
        .lower()
    )

    if key not in npc.status_effects:
        raise ValueError(
            f"NPC does not have status effect '{name}'."
        )

    effects_to_remove: set[str] = set()

    def collect_children(
        parent_key: str,
    ) -> None:

        if parent_key in effects_to_remove:
            return

        effects_to_remove.add(
            parent_key
        )

        for (
            child_key,
            child_effect,
        ) in npc.status_effects.items():

            if child_effect.parent_effect is None:
                continue

            child_parent = (
                child_effect.parent_effect
                .strip()
                .lower()
            )

            if child_parent == parent_key:
                collect_children(
                    child_key
                )

    collect_children(key)

    for effect_key in effects_to_remove:
        npc.status_effects.pop(
            effect_key,
            None,
        )


def has_status_effect(
    npc: NPC,
    name: str,
) -> bool:
    """
    Check whether an NPC currently has a named status effect.
    """

    key = (
        name
        .strip()
        .lower()
    )

    return key in npc.status_effects


# ------------------------------------------------------------------
# COMPLETE MUTATION PAYLOAD
# ------------------------------------------------------------------

def apply_npc_mutation(
    npc: NPC,
    mutation: NPCMutationData,
) -> NPC:
    """
    Apply a validated NPCMutationData payload.

    This function only changes character state.

    Persistence and turn/mechanics resolution are handled
    elsewhere.
    """

    if mutation.npc_id != npc.npc_id:
        raise ValueError(
            "Mutation target does not match NPC."
        )

    # --------------------------------------------------------------
    # Profile / world state
    # --------------------------------------------------------------

    if mutation.field_updates:
        update_npc(
            npc,
            **mutation.field_updates,
        )

    # --------------------------------------------------------------
    # Attributes
    # --------------------------------------------------------------

    for (
        attribute_name,
        value,
    ) in mutation.attribute_updates.items():

        update_attribute(
            npc=npc,
            attribute_name=attribute_name,
            value=value,
        )

    # --------------------------------------------------------------
    # Existing skills
    # --------------------------------------------------------------

    for (
        skill_name,
        value,
    ) in mutation.skill_updates.items():

        update_skill(
            npc=npc,
            skill_name=skill_name,
            value=value,
        )

    # --------------------------------------------------------------
    # Skill removal / creation
    # --------------------------------------------------------------

    for skill_name in mutation.remove_skills:

        remove_skill(
            npc=npc,
            skill_name=skill_name,
        )

    for skill in mutation.add_skills:

        add_skill(
            npc=npc,
            skill_name=skill.name,
            band=skill.band,
        )

    # --------------------------------------------------------------
    # Resources
    # --------------------------------------------------------------

    for (
        resource_name,
        resource_update,
    ) in mutation.resource_updates.items():

        update_resource(
            npc=npc,
            resource_name=resource_name,
            current=resource_update.current,
            maximum=resource_update.maximum,
        )

    # --------------------------------------------------------------
    # Status removals
    #
    # Parent removal automatically clears dependent children.
    # --------------------------------------------------------------

    for effect_name in mutation.remove_status_effects:

        if has_status_effect(
            npc=npc,
            name=effect_name,
        ):
            remove_status_effect(
                npc=npc,
                name=effect_name,
            )

    # --------------------------------------------------------------
    # Status additions
    #
    # Effects may arrive in any order from the model.
    # Child effects wait until their parent exists.
    # --------------------------------------------------------------

    pending_effects = list(
        mutation.add_status_effects
    )

    while pending_effects:

        progress = False

        for effect_data in pending_effects[:]:

            parent_key = None

            if effect_data.parent_effect is not None:

                parent_key = (
                    effect_data.parent_effect
                    .strip()
                    .lower()
                )

            # Wait until the parent status exists.
            if (
                parent_key is not None
                and parent_key not in npc.status_effects
            ):
                continue

            status_effect = StatusEffect(
                name=effect_data.name,
                source=effect_data.source,
                effect=effect_data.effect,
                resource=effect_data.resource,
                amount=effect_data.amount,
                duration=effect_data.duration,
                parent_effect=parent_key,
            )

            add_status_effect(
                npc=npc,
                status_effect=status_effect,
                replace=True,
            )

            pending_effects.remove(
                effect_data
            )

            progress = True

        if not progress:

            unresolved = [
                {
                    "name": effect.name,
                    "parent_effect": effect.parent_effect,
                }
                for effect in pending_effects
            ]

            raise ValueError(
                "Status effects contain missing or circular "
                f"parent dependencies: {unresolved}"
            )

    return npc