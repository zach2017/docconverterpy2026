"""
Temporal client helper.

Provides a simple interface for starting document conversion workflows
from the API endpoints and message bus listeners.
"""

import asyncio
import logging
import uuid
from typing import Optional

from temporalio.client import Client

from config.settings import settings
from app.models import ConversionJob, ConversionResult
from app.workflows.dataclasses import (
    ConversionWorkflowInput,
    ConversionWorkflowOutput,
)

logger = logging.getLogger(__name__)

# Module-level cached client
_client: Optional[Client] = None


async def _get_client() -> Client:
    """Get or create a Temporal client (cached)."""
    global _client
    if _client is None:
        _client = await Client.connect(
            settings.temporal_host,
            namespace=settings.temporal_namespace,
        )
    return _client


def _job_to_workflow_input(
    job: ConversionJob,
    local_file_path: Optional[str] = None,
) -> ConversionWorkflowInput:
    """Convert a ConversionJob model to a Temporal workflow input."""
    return ConversionWorkflowInput(
        job_id=job.job_id or uuid.uuid4().hex[:12],
        document_type=job.document_type.value,
        location_type=job.location_type.value,
        s3_bucket=job.s3_bucket,
        s3_key=job.s3_key,
        s3_endpoint_url=job.s3_endpoint_url,
        url=job.url,
        ftp_host=job.ftp_host,
        ftp_port=job.ftp_port,
        ftp_path=job.ftp_path,
        ftp_user=job.ftp_user,
        ftp_pass=job.ftp_pass,
        auth_type=job.auth_type.value if job.auth_type else "none",
        auth_username=job.auth_username,
        auth_password=job.auth_password,
        auth_token=job.auth_token,
        output_s3_bucket=job.output_s3_bucket,
        output_s3_key=job.output_s3_key,
        local_file_path=local_file_path,
    )


def _workflow_output_to_result(out: ConversionWorkflowOutput) -> ConversionResult:
    """Convert a Temporal workflow output to a ConversionResult."""
    return ConversionResult(
        job_id=out.job_id,
        success=out.success,
        output_bucket=out.output_bucket,
        output_key=out.output_key,
        error=out.error,
        pages_processed=out.pages_processed,
        characters_extracted=out.total_chars,
    )


async def start_conversion_workflow(
    job: ConversionJob,
    local_file_path: Optional[str] = None,
    wait_for_result: bool = True,
) -> ConversionResult:
    """
    Start a Temporal DocumentConversionWorkflow for the given job.

    Parameters
    ----------
    job : ConversionJob
        The conversion job descriptor.
    local_file_path : str | None
        If the file is already on disk (API upload), pass the path.
    wait_for_result : bool
        If True, blocks until the workflow completes and returns the result.
        If False, returns immediately with a "pending" result.

    Returns
    -------
    ConversionResult
    """
    inp = _job_to_workflow_input(job, local_file_path)
    client = await _get_client()

    workflow_id = f"docconv-{inp.job_id}"

    logger.info(
        "Starting Temporal workflow  id=%s  type=%s  loc=%s",
        workflow_id, inp.document_type, inp.location_type,
    )

    handle = await client.start_workflow(
        "DocumentConversionWorkflow",
        inp,
        id=workflow_id,
        task_queue=settings.temporal_task_queue,
    )

    if wait_for_result:
        output: ConversionWorkflowOutput = await handle.result()
        return _workflow_output_to_result(output)
    else:
        return ConversionResult(
            job_id=inp.job_id,
            success=True,  # pending
            error=None,
        )


def start_conversion_workflow_sync(
    job: ConversionJob,
    local_file_path: Optional[str] = None,
    wait_for_result: bool = True,
) -> ConversionResult:
    """
    Synchronous wrapper for start_conversion_workflow.

    Used by the message bus listeners (which run in threads, not async).
    """
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(
            start_conversion_workflow(job, local_file_path, wait_for_result)
        )
    finally:
        loop.close()
