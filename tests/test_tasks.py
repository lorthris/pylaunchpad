"""Automated tests for asynchronous background task worker."""

import asyncio
import pytest
from pylaunchpad.tasks.worker import TaskWorker


@pytest.mark.asyncio
async def test_task_worker_lifecycle_and_execution():
    """Verify that background tasks are queued and executed asynchronously."""
    worker = TaskWorker(max_concurrency=2)
    await worker.start()

    executed_jobs = []

    async def sample_background_job(job_id: str, value: int):
        await asyncio.sleep(0.01)
        executed_jobs.append((job_id, value * 2))

    # Enqueue multiple jobs
    await worker.enqueue(sample_background_job, "job_1", 10)
    await worker.enqueue(sample_background_job, "job_2", 25)

    # Wait for queue to drain
    await asyncio.wait_for(worker.queue.join(), timeout=2.0)
    await worker.stop()

    assert len(executed_jobs) == 2
    assert ("job_1", 20) in executed_jobs
    assert ("job_2", 50) in executed_jobs
