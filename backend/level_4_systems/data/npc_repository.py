from threading import Lock
from typing import Protocol

from backend.level_5_entities.characters import NPC

from .temp_store import (
    load_npcs,
    save_npcs,
)


class NPCRepository(Protocol):
    """
    Persistence interface for NPC storage.

    Callers should depend on this interface rather than caring
    whether NPCs are stored in JSON, a database, memory, or
    somewhere else.
    """

    def get(
        self,
        npc_id: str,
    ) -> NPC | None:
        ...

    def save(
        self,
        npc: NPC,
    ) -> NPC:
        ...

    def get_all(
        self,
    ) -> list[NPC]:
        ...

    def get_unenriched_ids(
        self,
    ) -> list[str]:
        ...

    def delete(
        self,
        npc_id: str,
    ) -> bool:
        ...


class TempJSONNPCRepository:
    """
    Temporary JSON-backed NPC repository.

    This implementation exists only for development.

    It uses the current temp_store underneath, while exposing the
    same repository API that a future database implementation will
    use.
    """

    def __init__(self):
        # Prevent two operations in this process from writing the
        # temporary JSON file at exactly the same time.
        self._lock = Lock()

    def get(
        self,
        npc_id: str,
    ) -> NPC | None:
        """
        Load one NPC by ID.
        """

        npcs = load_npcs()

        return npcs.get(npc_id)

    def save(
        self,
        npc: NPC,
    ) -> NPC:
        """
        Insert or update one NPC.
        """

        with self._lock:
            npcs = load_npcs()

            npcs[npc.npc_id] = npc

            save_npcs(npcs)

        return npc

    def get_all(
        self,
    ) -> list[NPC]:
        """
        Return every stored NPC.
        """

        npcs = load_npcs()

        return list(npcs.values())

    def get_unenriched_ids(
        self,
    ) -> list[str]:
        """
        Return the IDs of NPCs still waiting for enrichment.

        Returning IDs rather than complete NPC objects allows the
        enrichment worker to load the latest character state only
        when it is ready to process that NPC.
        """

        npcs = load_npcs()

        return [
            npc.npc_id
            for npc in npcs.values()
            if not npc.enriched
        ]

    def delete(
        self,
        npc_id: str,
    ) -> bool:
        """
        Delete one NPC.

        Returns True if an NPC was deleted.
        Returns False if the ID did not exist.
        """

        with self._lock:
            npcs = load_npcs()

            if npc_id not in npcs:
                return False

            del npcs[npc_id]

            save_npcs(npcs)

        return True


# ------------------------------------------------------------------
# ACTIVE REPOSITORY
# ------------------------------------------------------------------

_repository: NPCRepository = TempJSONNPCRepository()


def get_npc_repository() -> NPCRepository:
    """
    Return the currently configured NPC repository.

    The rest of the application should obtain NPC persistence through
    this function rather than constructing a storage implementation
    directly.
    """

    return _repository


def set_npc_repository(
    repository: NPCRepository,
) -> None:
    """
    Replace the active repository implementation.

    Useful later for:

    - database repositories
    - tests
    - in-memory repositories
    - alternate persistence backends
    """

    global _repository

    _repository = repository