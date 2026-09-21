"""Lightweight asynchronous in-process task worker and queue."""

import asyncio
import logging
from typing import Callable, Any, Coroutine, Dict, Tuple, Optional

logger = logging.getLogger(__name__)


class TaskWorker:
    """Async in-process worker queue for executing non-blocking background jobs."""

    def __init__(self, max_concurrency: int = 5):
        self._queue: Optional[asyncio.Queue[Tuple[Callable[..., Coroutine[Any, Any, Any]], tuple, Dict[str, Any]]]] = None
        self.max_concurrency = max_concurrency
        self.running = False
        self._workers: list[asyncio.Task] = []

    @property
    def queue(self) -> asyncio.Queue:
        if self._queue is None:
            self._queue = asyncio.Queue()
        return self._queue

    async def start(self) -> None:
        """Start worker task consumers."""
        if self.running:
            return
        self._queue = asyncio.Queue()
        self.running = True
        for i in range(self.max_concurrency):
            task = asyncio.create_task(self._consumer_loop(i))
            self._workers.append(task)
        logger.info("TaskWorker started with %d consumers", self.max_concurrency)

    async def stop(self) -> None:
        """Gracefully drain and cancel worker tasks."""
        self.running = False
        for task in self._workers:
            task.cancel()
        if self._workers:
            await asyncio.gather(*self._workers, return_exceptions=True)
            self._workers.clear()
        self._queue = None
        logger.info("TaskWorker stopped")

    async def enqueue(self, func: Callable[..., Coroutine[Any, Any, Any]], *args: Any, **kwargs: Any) -> None:
        """Add an asynchronous job to the execution queue."""
        await self.queue.put((func, args, kwargs))

    async def _consumer_loop(self, worker_id: int) -> None:
        """Background loop consuming and executing jobs from the queue."""
        while self.running:
            try:
                func, args, kwargs = await self.queue.get()
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error("Worker %d queue retrieval error: %s", worker_id, exc)
                break

            try:
                await func(*args, **kwargs)
            except Exception as exc:
                logger.error("Task execution failed in worker %d: %s", worker_id, exc, exc_info=True)
            finally:
                self.queue.task_done()


task_worker = TaskWorker()
