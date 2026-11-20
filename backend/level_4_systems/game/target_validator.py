"""Deterministic target identity checks for proposed player actions.

This module validates identities only. It never resolves action feasibility,
performs mechanics, or mutates canonical NPC/location state.
"""

import re

from backend.level_5_entities import (
    ActionProposal,
    Location,
    NPC,
)


_REFERENCE_FILLERS = {
    "a", "an", "the", "this", "that", "these", "those",
    "named", "called", "near", "beside", "by", "at", "in",
    "on", "with", "standing", "to", "from", "of",
}

_PRONOUN_REFERENCES = {
    "he", "him", "his", "she", "her", "hers",
    "they", "them", "their", "theirs", "it", "its",
    "this one", "that one", "the one", "you",
}


def _normalise(value: str | None) -> str:
    """Normalise case, punctuation and whitespace for whole-word matching."""
    if not value:
        return ""
    return " ".join(re.findall(r"\w+", value.casefold()))


def _contains_phrase(text: str, phrase: str) -> bool:
    """Match whole words (Mark must not match Martin)."""
    text = _normalise(text)
    phrase = _normalise(phrase)
    return bool(text and phrase and f" {phrase} " in f" {text} ")


def _find_npc_candidates(
    reference: str | None,
    npcs: tuple[NPC, ...] | list[NPC],
) -> tuple[list[NPC], str | None]:
    """Find independently supported NPC identities in canonical scene order.

    Full names outrank partial names and role descriptors. In particular,
    'Robert Brown' must not match 'John Brown' merely by surname.
    """
    if not reference:
        return [], None

    # 1. Exact full-name phrase, including one-word canonical names.
    full_name_matches = [
        npc for npc in npcs
        if npc.name and _contains_phrase(reference, npc.name)
    ]
    if full_name_matches:
        return full_name_matches, "full_name"

    words = [
        word for word in _normalise(reference).split()
        if word not in _REFERENCE_FILLERS
    ]
    if not words:
        return [], None

    # A reference resembling a multiword name must match an actual full name.
    # This prevents 'Robert Brown' from matching 'John Brown', regardless
    # of what the LLM wrote in target_resolution.
    # A combination such as 'John the guard' is permitted when each word is
    # supported by a name part or descriptor for the same NPC.
    all_name_parts = {
        part
        for npc in npcs
        for part in _normalise(npc.name).split()
    }
    all_descriptor_parts = {
        part
        for npc in npcs
        for descriptor in (npc.occupation, npc.rank)
        for part in _normalise(descriptor).split()
    }

    if len(words) > 1 and any(word in all_name_parts for word in words):
        if any(
            word not in all_name_parts and word not in all_descriptor_parts
            for word in words
        ):
            return [], "unsupported_name"

    # 2. Partial personal names, e.g. 'John' in a scene with two Johns.
    # Only allow partial matching when EVERY informative word has evidence.
    name_matches = []
    for npc in npcs:
        name_parts = set(_normalise(npc.name).split())
        descriptor_parts = {
            part
            for descriptor in (npc.occupation, npc.rank)
            for part in _normalise(descriptor).split()
        }
        if (
            any(word in name_parts for word in words)
            and all(
                word in name_parts or word in descriptor_parts
                for word in words
            )
        ):
            name_matches.append(npc)

    if name_matches:
        return name_matches, "partial_name"

    # 3. Role/rank matching: 'guard', 'captain', 'baker'.
    # A role must account for the reference, rather than matching just an
    # incidental word while ignoring an explicit different name.
    descriptor_matches = []
    for npc in npcs:
        descriptor_parts = {
            part
            for descriptor in (npc.occupation, npc.rank)
            for part in _normalise(descriptor).split()
        }
        if descriptor_parts and all(word in descriptor_parts for word in words):
            descriptor_matches.append(npc)

    if descriptor_matches:
        return descriptor_matches, "descriptor"

    return [], None


def _is_unmatched_name(reference: str | None) -> bool:
    """Detect an unsupported personal-name-like reference.

    This is deliberately conservative. A capitalised name or a two-word
    name cannot be used to justify assigning an unrelated scene NPC.
    Pronouns remain available for genuine contextual resolution.
    """
    if not reference:
        return False

    value = _normalise(reference)
    if value in _PRONOUN_REFERENCES:
        return False

    words = [
        word for word in value.split()
        if word not in _REFERENCE_FILLERS
    ]

    if not words:
        return False

    # Two capitalised name components, such as 'Robert Brown'.
    capitalised = re.findall(r"\b[A-Z][a-zA-Z'-]*\b", reference)
    if len(capitalised) >= 2:
        return True

    # A single named target, such as 'Rowan'.
    if len(words) == 1 and capitalised:
        return True

    return False


def validate_action_targets(
    *,
    proposal: ActionProposal,
    location: Location,
    npcs: tuple[NPC, ...] | list[NPC],
) -> ActionProposal:
    """Return a copy whose canonical targets are checked against scene data.

    Unmatched NPC references remain attempted actions with null target_id;
    unregistered ordinary objects remain descriptive targets. No action is
    discarded for lacking a registered identity.
    """
    validated = proposal.model_copy(deep=True)

    npc_by_id = {str(npc.npc_id): npc for npc in npcs}
    location_id = str(location.location_id)

    for action in validated.actions:
        reference = action.target_reference
        target_id = str(action.target_id) if action.target_id is not None else None
        target_type = action.target_type

        # --------------------------------------------------------------
        # MOVEMENT TO A KNOWN NPC (LLM DESTINATION-ONLY BACKSTOP)
        # --------------------------------------------------------------
        # The LLM sometimes writes 'walk to Mary Jones' using only
        # destination_reference. Recover her canonical NPC identity when
        # the destination itself matches a scene NPC. Do not invent IDs
        # for ordinary places or environmental destinations.
        if (
            action.action_type == "movement"
            and target_id is None
            and target_type is None
            and not reference
            and action.destination_reference
        ):
            destination_matches, destination_match_type = _find_npc_candidates(
                action.destination_reference, npcs
            )
            if destination_matches:
                chosen = destination_matches[0]
                action.target_reference = action.destination_reference
                action.target_type = "npc"
                action.target_id = str(chosen.npc_id)
                action.target_resolution = (
                    "default" if len(destination_matches) > 1
                    else "explicit" if destination_match_type in ("full_name", "partial_name")
                    else "contextual"
                )
                reference = action.target_reference
                target_id = action.target_id
                target_type = action.target_type

        # --------------------------------------------------------------
        # NPC TARGETS
        # --------------------------------------------------------------
        if target_type == "npc" or (target_type is None and target_id in npc_by_id):
            action.target_type = "npc"
            candidates, match_type = _find_npc_candidates(reference, npcs)
            candidate_ids = {str(npc.npc_id) for npc in candidates}

            if candidates:
                # A supported name/description wins over a contradictory ID.
                if target_id in candidate_ids:
                    action.target_id = target_id
                    if action.target_resolution is None:
                        action.target_resolution = (
                            "explicit" if match_type == "full_name" else "contextual"
                        )
                else:
                    chosen = candidates[0]
                    action.target_id = str(chosen.npc_id)
                    action.target_resolution = (
                        "default" if len(candidates) > 1
                        else "explicit" if match_type in ("full_name", "partial_name")
                        else "contextual"
                    )
                continue

            # No matching name or role. Reject unsupported proper names even
            # when the LLM calls them 'contextual' and supplies a valid UUID.
            # 'Robert Brown' -> John Brown is NOT contextual identification.
            if match_type == "unsupported_name" or _is_unmatched_name(reference):
                action.target_id = None
                action.target_resolution = "unresolved"

            # Pronoun-based/contextual references may legitimately have no
            # literal name match; retain ONLY a scene-valid ID.
            elif target_id in npc_by_id:
                action.target_id = target_id
                if action.target_resolution is None:
                    action.target_resolution = "contextual"
                continue

            else:
                action.target_id = None
                action.target_resolution = "unresolved"

            if reference and reference not in validated.unresolved_references:
                validated.unresolved_references.append(reference)
            continue

        # --------------------------------------------------------------
        # LOCATION TARGETS (CURRENT LOCATION ONLY IN V1)
        # --------------------------------------------------------------
        if target_type == "location":
            if target_id == location_id:
                action.target_id = target_id
                if action.target_resolution is None:
                    action.target_resolution = "explicit"
            else:
                action.target_id = None
                action.target_resolution = "unresolved"
                if reference and reference not in validated.unresolved_references:
                    validated.unresolved_references.append(reference)
            continue

        # --------------------------------------------------------------
        # UNREGISTERED OBJECTS / FEATURES
        # --------------------------------------------------------------
        if reference:
            action.target_id = None
            action.target_resolution = "descriptive"
            continue

        # --------------------------------------------------------------
        # ACTIONS WITHOUT A TARGET
        # --------------------------------------------------------------
        action.target_id = None
        action.target_type = None
        action.target_resolution = None

    # Remove obsolete unresolved references if they were resolved by the
    # deterministic validator, while preserving any other raw references.
    still_unresolved = {
        action.target_reference
        for action in validated.actions
        if action.target_resolution == "unresolved" and action.target_reference
    }
    validated.unresolved_references = [
        reference for reference in dict.fromkeys(validated.unresolved_references)
        if reference in still_unresolved
    ]

    return validated
