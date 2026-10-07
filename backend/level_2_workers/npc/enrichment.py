from itertools import count
from queue import PriorityQueue
from threading import Event, Thread

from backend.level_3_services import enrich_npc


class NPCEnrichmentWorker:
    """
    Background worker for NPC enrichment.

    Jobs are NPC IDs.
    Lower priority numbers are processed first.
    """

    def __init__(self):
        self._queue = PriorityQueue()
        self._sequence = count()

        self._stop_event = Event()

        # Set = worker may process jobs.
        # Clear = worker is paused.
        self._run_event = Event()
        self._run_event.set()

        self._thread: Thread | None = None

    # --------------------------------------------------------------
    # LIFECYCLE
    # --------------------------------------------------------------

    def start(self) -> None:
        """
        Start the worker thread.

        Calling start on an already-running worker does nothing.
        """

        if self.is_running:
            return

        self._stop_event.clear()
        self._run_event.set()

        self._thread = Thread(
            target=self._run,
            name="npc-enrichment-worker",
            daemon=True,
        )

        self._thread.start()

    def stop(self) -> None:
        """
        Stop the worker.

        Any currently executing enrichment is allowed to finish.
        """

        if not self.is_running:
            return

        self._stop_event.set()

        # Wake the worker if it is paused.
        self._run_event.set()

        # Wake the worker if it is blocked waiting for a job.
        self._queue.put(
            (
                float("-inf"),
                next(self._sequence),
                None,
            )
        )

        self._thread.join()
        self._thread = None

    def pause(self) -> None:
        """
        Pause processing after the current job finishes.
        """

        self._run_event.clear()

    def resume(self) -> None:
        """
        Resume processing queued jobs.
        """

        self._run_event.set()

    # --------------------------------------------------------------
    # QUEUE
    # --------------------------------------------------------------

    def enqueue(
        self,
        npc_id: str,
        priority: int = 100,
    ) -> None:
        """
        Add an NPC enrichment job.

        Lower numbers have higher priority.
        """

        self._queue.put(
            (
                priority,
                next(self._sequence),
                npc_id,
            )
        )

    # --------------------------------------------------------------
    # STATE
    # --------------------------------------------------------------

    @property
    def is_running(self) -> bool:
        return (
            self._thread is not None
            and self._thread.is_alive()
        )

    @property
    def is_paused(self) -> bool:
        return not self._run_event.is_set()

    @property
    def pending_jobs(self) -> int:
        return self._queue.qsize()

    # --------------------------------------------------------------
    # WORK LOOP
    # --------------------------------------------------------------

    def _run(self) -> None:
        while not self._stop_event.is_set():

            # This blocks without consuming CPU while the queue
            # is empty.
            priority, sequence, npc_id = self._queue.get()

            try:
                # Sentinel inserted by stop().
                if npc_id is None:
                    return

                # If paused, sleep here until resume() or stop().
                self._run_event.wait()

                if self._stop_event.is_set():
                    return

                enrich_npc(npc_id)

            except Exception as error:
                # Temporary development behaviour.
                # Replace with proper logging/error handling later.
                print(
                    f"NPC enrichment failed for "
                    f"{npc_id}: {error}"
                )

            finally:
                self._queue.task_done()