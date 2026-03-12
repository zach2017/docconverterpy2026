"""
Temporal worker for the document conversion service.

Registers all workflows and activities, connects to the Temporal server,
and polls for tasks.  Designed to run in a background thread alongside
the API and bus listeners.
"""

import asyncio
import logging
import time

from temporalio.client import Client
from temporalio.worker import Worker

from config.settings import settings
from app.workflows.activities import ALL_ACTIVITIES
from app.workflows.document_workflows import ALL_CHILD_WORKFLOWS
from app.workflows.conversion_workflow import (
    DocumentConversionWorkflow,
    BatchConversionWorkflow,
)

logger = logging.getLogger(__name__)

# All workflow classes to register
ALL_WORKFLOWS = [
    DocumentConversionWorkflow,
    BatchConversionWorkflow,
    *ALL_CHILD_WORKFLOWS,
]


async def _run_worker():
    """Async entry point: connect to Temporal and run the worker."""
    logger.info(
        "Temporal worker connecting  host=%s  namespace=%s  queue=%s",
        settings.temporal_host,
        settings.temporal_namespace,
        settings.temporal_task_queue,
    )

    # Retry connection (Temporal may still be starting)
    client = None
    for attempt in range(30):
        try:
            client = await Client.connect(
                settings.temporal_host,
                namespace=settings.temporal_namespace,
            )
            logger.info("Connected to Temporal server")
            break
        except Exception as exc:
            logger.debug(
                "Temporal connection attempt %d failed: %s", attempt + 1, exc
            )
            await asyncio.sleep(3)

    if client is None:
        logger.error("Could not connect to Temporal – worker exiting")
        return

    worker = Worker(
        client,
        task_queue=settings.temporal_task_queue,
        workflows=ALL_WORKFLOWS,
        activities=ALL_ACTIVITIES,
    )

    logger.info(
        "Temporal worker running  workflows=%d  activities=%d",
        len(ALL_WORKFLOWS),
        len(ALL_ACTIVITIES),
    )
    await worker.run()


def run_temporal_worker():
    """
    Blocking entry point for running the Temporal worker in a thread.

    Creates a new asyncio event loop (since this runs in a daemon thread,
    not the main thread).
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_run_worker())
    except Exception as exc:
        logger.exception("Temporal worker crashed: %s", exc)
    finally:
        loop.close()
