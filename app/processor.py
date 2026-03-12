"""
Processing pipeline: fetch → convert → upload.

Supports two execution modes:
  1. Direct (USE_TEMPORAL_WORKFLOWS=false): inline pipeline, same as before.
  2. Temporal (USE_TEMPORAL_WORKFLOWS=true): submits a durable workflow to
     Temporal and waits for the result.

The mode is controlled by the USE_TEMPORAL_WORKFLOWS env var.
"""

import logging
import os
import uuid

from app.models import ConversionJob, ConversionResult, LocationType
from app.fetchers.dispatch import fetch_document
from app.converters.dispatch import convert_document
from app.storage import upload_text_chunks
from config.settings import settings

logger = logging.getLogger(__name__)


def process_job(job: ConversionJob, local_file_path: str | None = None) -> ConversionResult:
    """
    Execute the full conversion pipeline for a single job.

    If USE_TEMPORAL_WORKFLOWS is enabled and Temporal is running, this
    will route through a durable Temporal workflow.  Otherwise, it runs
    the pipeline directly (inline).
    """
    if settings.use_temporal_workflows and settings.enable_temporal:
        return _process_via_temporal(job, local_file_path)
    else:
        return _process_direct(job, local_file_path)


def _process_via_temporal(
    job: ConversionJob, local_file_path: str | None = None
) -> ConversionResult:
    """Submit a job to Temporal and wait for the result."""
    job_id = job.job_id or uuid.uuid4().hex[:12]
    job.job_id = job_id
    logger.info("Routing job %s through Temporal workflow", job_id)

    try:
        from app.workflows.client import start_conversion_workflow_sync
        return start_conversion_workflow_sync(
            job, local_file_path, wait_for_result=True
        )
    except Exception as exc:
        logger.warning(
            "Temporal routing failed for job %s, falling back to direct: %s",
            job_id, exc,
        )
        # Fall back to direct processing
        return _process_direct(job, local_file_path)


def _process_direct(
    job: ConversionJob, local_file_path: str | None = None
) -> ConversionResult:
    """
    Direct (inline) processing – the original pipeline.
    """
    job_id = job.job_id or uuid.uuid4().hex[:12]
    logger.info("Processing job %s directly  type=%s  loc=%s",
                job_id, job.document_type, job.location_type)

    try:
        if job.location_type == LocationType.LOCAL and local_file_path:
            text_gen = convert_document(local_file_path, job.document_type)
            bucket, key, total_chars = upload_text_chunks(
                text_gen,
                bucket=job.output_s3_bucket,
                key=job.output_s3_key,
                job_id=job_id,
            )
            try:
                os.unlink(local_file_path)
            except OSError:
                pass
        else:
            for tmp_path in fetch_document(job):
                text_gen = convert_document(tmp_path, job.document_type)
                bucket, key, total_chars = upload_text_chunks(
                    text_gen,
                    bucket=job.output_s3_bucket,
                    key=job.output_s3_key,
                    job_id=job_id,
                )

        logger.info("Job %s complete → s3://%s/%s  (%d chars)",
                     job_id, bucket, key, total_chars)
        return ConversionResult(
            job_id=job_id,
            success=True,
            output_bucket=bucket,
            output_key=key,
            characters_extracted=total_chars,
        )

    except Exception as exc:
        logger.exception("Job %s failed: %s", job_id, exc)
        return ConversionResult(
            job_id=job_id,
            success=False,
            error=str(exc),
        )
