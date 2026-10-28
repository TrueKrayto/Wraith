from uuid import uuid4

from backend.level_5_entities import (
    IntentResult,
    PreparedTurn,
    Scene,
)


class SceneManager:
    """
    Orchestrates active scenes and player turns.

    Dependencies are supplied on creation.

    SceneManager does not directly import:
    - NPC repositories
    - Location repositories
    - LLM clients
    - Intent extraction implementations

    Responsibilities:
    - manage active scenes
    - load relevant world context
    - receive player input
    - request intent extraction
    - prepare structured turns
    - track turn lifecycle

    Mechanical resolution is handled separately.
    """

    def __init__(
        self,
        *,
        intent_extractor,
        location_repository,
        npc_repository,
    ):
        self._intent_extractor = intent_extractor

        self._location_repository = (
            location_repository
        )

        self._npc_repository = (
            npc_repository
        )

        # Temporary in-memory scene storage.
        self._scenes: dict[str, Scene] = {}

    # --------------------------------------------------------------
    # START SCENE
    # --------------------------------------------------------------

    def start_scene(
        self,
        *,
        location_id: str,
        player_character_id: str,
        npc_ids: list[str] | None = None,
    ) -> Scene:

        location = self._location_repository.get(
            location_id
        )

        if location is None:
            raise ValueError(
                f"Location not found: {location_id}"
            )

        if not player_character_id.strip():
            raise ValueError(
                "Player character ID is required."
            )

        npc_ids = list(
            dict.fromkeys(npc_ids or [])
        )

        for npc_id in npc_ids:

            if self._npc_repository.get(npc_id) is None:
                raise ValueError(
                    f"NPC not found: {npc_id}"
                )

        scene = Scene(
            location_id=location_id,
            player_character_id=player_character_id,
            npc_ids=npc_ids,
        )

        self._scenes[scene.scene_id] = scene

        return scene

    # --------------------------------------------------------------
    # GET SCENE
    # --------------------------------------------------------------

    def get_scene(
        self,
        scene_id: str,
    ) -> Scene | None:

        return self._scenes.get(
            scene_id
        )

    # --------------------------------------------------------------
    # PREPARE TURN
    # --------------------------------------------------------------

    def prepare_turn(
        self,
        *,
        scene_id: str,
        player_input: str,
    ) -> PreparedTurn:
        """
        Receive raw player input and extract intentions.

        This does not perform mechanical resolution.

        If intent extraction fails, the scene remains
        ready and the player may retry.
        """

        scene = self.get_scene(
            scene_id
        )

        if scene is None:
            raise ValueError(
                f"Scene not found: {scene_id}"
            )

        if scene.phase != "ready":
            raise RuntimeError(
                "Scene already has a pending turn."
            )

        player_input = player_input.strip()

        if not player_input:
            raise ValueError(
                "Player input cannot be empty."
            )

        # ----------------------------------------------------------
        # LOAD CANONICAL CONTEXT
        # ----------------------------------------------------------

        location = self._location_repository.get(
            scene.location_id
        )

        if location is None:
            raise RuntimeError(
                "Current scene location no longer exists."
            )

        npcs = []

        for npc_id in scene.npc_ids:

            npc = self._npc_repository.get(
                npc_id
            )

            if npc is None:
                raise RuntimeError(
                    f"Scene NPC no longer exists: {npc_id}"
                )

            npcs.append(npc)

        # ----------------------------------------------------------
        # EXTRACT PLAYER INTENT
        # ----------------------------------------------------------

        intent = self._intent_extractor(
            player_input=player_input,
            location=location,
            npcs=tuple(npcs),
        )

        if not isinstance(intent, IntentResult):
            raise TypeError(
                "Intent extractor must return IntentResult."
            )

        # ----------------------------------------------------------
        # PREPARE TURN
        # ----------------------------------------------------------

        turn_id = str(uuid4())

        prepared = PreparedTurn(
            turn_id=turn_id,
            scene_id=scene.scene_id,
            turn_number=scene.turn_number + 1,
            player_input=player_input,
            player_character_id=scene.player_character_id,
            location_id=scene.location_id,
            npc_ids=tuple(scene.npc_ids),
            intent=intent,
        )

        # Only mark the turn as pending after extraction
        # has completed successfully.

        scene.pending_turn_id = turn_id
        scene.phase = "awaiting_resolution"

        return prepared

    # --------------------------------------------------------------
    # COMPLETE TURN
    # --------------------------------------------------------------

    def complete_turn(
        self,
        *,
        scene_id: str,
        turn_id: str,
    ) -> Scene:
        """
        Complete the current pending turn.

        Temporary lifecycle implementation.

        Later this will receive the TurnResolver result
        and apply authorised changes before advancing.
        """

        scene = self.get_scene(
            scene_id
        )

        if scene is None:
            raise ValueError(
                f"Scene not found: {scene_id}"
            )

        if (
            scene.phase != "awaiting_resolution"
            or scene.pending_turn_id != turn_id
        ):
            raise RuntimeError(
                "Turn does not match the pending scene turn."
            )

        scene.turn_number += 1

        scene.pending_turn_id = None
        scene.phase = "ready"

        return scene