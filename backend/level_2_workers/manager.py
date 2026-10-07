from .npc import NPCEnrichmentWorker
from backend.level_4_systems import get_npc_repository

class WorkerManager:
    """
    Owns and coordinates backend background workers.

    The manager is long-lived for the lifetime of the backend process.
    """

    def __init__(self):
        self._npc_enrichment = NPCEnrichmentWorker()

    # --------------------------------------------------------------
    # LIFECYCLE
    # --------------------------------------------------------------

    def start(self) -> None:
        """
        Start all managed workers.
        """

        self._npc_enrichment.start()

    def stop(self) -> None:
        """
        Stop all managed workers.
        """

        self._npc_enrichment.stop()

    # --------------------------------------------------------------
    # NPC ENRICHMENT
    # --------------------------------------------------------------

    def enqueue_npc_enrichment(
        self,
        npc_id: str,
        priority: int = 100,
    ) -> None:
        """
        Queue one NPC for background enrichment.
        """

        self._npc_enrichment.enqueue(
            npc_id=npc_id,
            priority=priority,
        )

    def enqueue_pending_npc_enrichment(
        self,
        priority: int = 100,
    ) -> int:
        """
        Queue every NPC still waiting for enrichment.

        Returns the number of jobs queued.
        """

        repository = get_npc_repository()

        npc_ids = repository.get_unenriched_ids()

        for npc_id in npc_ids:
            self.enqueue_npc_enrichment(
                npc_id=npc_id,
                priority=priority,
            )

        return len(npc_ids)