import sys
import textwrap

from backend.level_4_systems import (
    get_npc_repository,
)

from backend.level_5_entities.characters import (
    CORE_SKILLS,
)


SHEET_WIDTH = 78
TEXT_WIDTH = 74


# ==================================================================
# FORMATTING HELPERS
# ==================================================================

def _value(value) -> str:
    """
    Display None and empty values cleanly.
    """

    if value is None:
        return "-"

    if value == "":
        return "-"

    return str(value)


def _label_value(
    label: str,
    value,
) -> str:
    return f"{label:<18} {_value(value)}"


def _wrap_text(
    text: str | None,
) -> str:
    """
    Wrap narrative fields for terminal display.
    """

    if not text:
        return "-"

    return textwrap.fill(
        text,
        width=TEXT_WIDTH,
    )


def _format_skill_name(
    name: str,
) -> str:
    return (
        name
        .replace("_", " ")
        .title()
    )


# ==================================================================
# CHARACTER SHEET
# ==================================================================

def build_character_sheet(
    npc_id: str,
) -> str:
    """
    Load one NPC by ID and return a formatted character sheet.

    This does not mutate the NPC and makes no LLM calls.
    """

    repository = get_npc_repository()

    npc = repository.get(
        npc_id
    )

    if npc is None:
        raise ValueError(
            f"NPC not found: {npc_id}"
        )

    lines: list[str] = []

    # ------------------------------------------------------------------
    # HEADER
    # ------------------------------------------------------------------

    lines.append(
        "=" * SHEET_WIDTH
    )

    lines.append(
        npc.name.upper()
    )

    lines.append(
        "=" * SHEET_WIDTH
    )

    lines.append("")

    # ------------------------------------------------------------------
    # IDENTITY
    # ------------------------------------------------------------------

    lines.append(
        "--- IDENTITY ---"
    )

    lines.append(
        _label_value(
            "NPC ID:",
            npc.npc_id,
        )
    )

    lines.append(
        _label_value(
            "Species:",
            npc.species,
        )
    )

    lines.append(
        _label_value(
            "Sex:",
            npc.sex,
        )
    )

    lines.append(
        _label_value(
            "Age:",
            npc.age,
        )
    )

    lines.append(
        _label_value(
            "Alive:",
            npc.alive,
        )
    )

    lines.append("")

    # ------------------------------------------------------------------
    # WORLD / SOCIAL
    # ------------------------------------------------------------------

    lines.append(
        "--- WORLD IDENTITY ---"
    )

    lines.append(
        _label_value(
            "Faction:",
            npc.faction,
        )
    )

    lines.append(
        _label_value(
            "Occupation:",
            npc.occupation,
        )
    )

    lines.append(
        _label_value(
            "Rank:",
            npc.rank,
        )
    )

    lines.append(
        _label_value(
            "Home:",
            npc.home,
        )
    )

    lines.append(
        _label_value(
            "Current Location:",
            npc.current_location,
        )
    )

    lines.append("")

    # ------------------------------------------------------------------
    # PROGRESSION
    # ------------------------------------------------------------------

    lines.append(
        "--- CHARACTER ---"
    )

    lines.append(
        _label_value(
            "Tier:",
            npc.tier,
        )
    )

    lines.append(
        _label_value(
            "Level:",
            npc.level,
        )
    )

    lines.append(
        _label_value(
            "Enriched:",
            npc.enriched,
        )
    )

    lines.append("")

    # ------------------------------------------------------------------
    # ATTRIBUTES
    # ------------------------------------------------------------------

    lines.append(
        "--- ATTRIBUTES ---"
    )

    attribute_width = 14

    for name, score in npc.attributes.items():

        display_name = (
            name
            .replace("_", " ")
            .title()
        )

        lines.append(
            f"{display_name:<{attribute_width}} {score}"
        )

    lines.append("")

    # ------------------------------------------------------------------
    # RESOURCES
    # ------------------------------------------------------------------

    lines.append(
        "--- RESOURCES ---"
    )

    for name, resource in npc.resources.items():

        display_name = (
            name
            .replace("_", " ")
            .title()
        )

        current = resource.get(
            "current",
            0,
        )

        maximum = resource.get(
            "maximum",
            0,
        )

        lines.append(
            f"{display_name:<14} "
            f"{current}/{maximum}"
        )

    lines.append("")

    # ------------------------------------------------------------------
    # CORE SKILLS
    # ------------------------------------------------------------------

    lines.append(
        "--- CORE SKILLS ---"
    )

    for skill_name in CORE_SKILLS:

        score = npc.skills.get(
            skill_name,
            0,
        )

        lines.append(
            f"{_format_skill_name(skill_name):<22} "
            f"{score}"
        )

    lines.append("")

    # ------------------------------------------------------------------
    # SPECIALIST SKILLS
    # ------------------------------------------------------------------

    specialist_skills = {
        name: score
        for name, score in npc.skills.items()
        if name not in CORE_SKILLS
    }

    lines.append(
        "--- SPECIALIST SKILLS ---"
    )

    if specialist_skills:

        for (
            skill_name,
            score,
        ) in specialist_skills.items():

            lines.append(
                f"{_format_skill_name(skill_name):<22} "
                f"{score}"
            )

    else:
        lines.append(
            "None"
        )

    lines.append("")

    # ------------------------------------------------------------------
    # NARRATIVE IDENTITY
    # ------------------------------------------------------------------

    lines.append(
        "--- DESCRIPTION ---"
    )

    lines.append(
        _wrap_text(
            npc.description
        )
    )

    lines.append("")

    lines.append(
        "--- APPEARANCE ---"
    )

    lines.append(
        _wrap_text(
            npc.appearance
        )
    )

    lines.append("")

    lines.append(
        "--- PERSONALITY ---"
    )

    lines.append(
        _wrap_text(
            npc.personality
        )
    )

    lines.append("")

    lines.append(
        "--- MANNERISMS ---"
    )

    lines.append(
        _wrap_text(
            npc.mannerisms
        )
    )

    lines.append("")

    lines.append(
        "--- SPEECH STYLE ---"
    )

    lines.append(
        _wrap_text(
            npc.speech_style
        )
    )

    lines.append("")

    # ------------------------------------------------------------------
    # STATUS EFFECTS
    # ------------------------------------------------------------------

    lines.append(
        "--- STATUS EFFECTS ---"
    )

    if not npc.status_effects:

        lines.append(
            "None"
        )

    else:

        for (
            effect_name,
            effect,
        ) in npc.status_effects.items():

            lines.append(
                f"{effect.name}"
            )

            lines.append(
                f"  Source:        "
                f"{_value(effect.source)}"
            )

            lines.append(
                f"  Effect:        "
                f"{_value(effect.effect)}"
            )

            lines.append(
                f"  Resource:      "
                f"{_value(effect.resource)}"
            )

            lines.append(
                f"  Amount:        "
                f"{_value(effect.amount)}"
            )

            lines.append(
                f"  Duration:      "
                f"{_value(effect.duration)}"
            )

            lines.append(
                f"  Parent Effect: "
                f"{_value(effect.parent_effect)}"
            )

    lines.append("")

    lines.append(
        "=" * SHEET_WIDTH
    )

    return "\n".join(
        lines
    )


def print_character_sheet(
    npc_id: str,
) -> None:
    """
    Print one NPC character sheet.
    """

    print(
        build_character_sheet(
            npc_id
        )
    )


# ==================================================================
# DIRECT TEST
# ==================================================================

if __name__ == "__main__":

    print()
    print(
        "WRAITH CHARACTER SHEET SHOWCASE"
    )
    print()

    if len(sys.argv) > 1:

        npc_id = (
            sys.argv[1]
            .strip()
        )

    else:

        npc_id = input(
            "NPC ID:\n> "
        ).strip()

    if not npc_id:
        raise ValueError(
            "NPC ID is required."
        )

    print()

    print_character_sheet(
        npc_id
    )