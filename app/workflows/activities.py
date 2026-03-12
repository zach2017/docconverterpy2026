"""
Temporal activities for the document conversion pipeline.

Each activity is a single, retryable step.  Activities use the existing
converter modules internally but expose clean dataclass I/O for Temporal
serialization.

Activities send heartbeats during long operations so the Temporal server
knows the worker is still alive.
"""

import logging
import os
import uuid

from temporalio import activity

from config.settings import settings
from app.workflows.dataclasses import (
    FetchInput, FetchOutput,
    ConvertInput, ConvertOutput,
    UploadInput, UploadOutput,
    CleanupInput,
)

logger = logging.getLogger(__name__)


# ═════════════════════════════════════════════════════════════════════════════
# FETCH ACTIVITY
# ═════════════════════════════════════════════════════════════════════════════

@activity.defn(name="fetch_document")
async def fetch_document_activity(inp: FetchInput) -> FetchOutput:
    """
    Download a document from S3 / URL / FTP to a local temp file.
    Returns the local file path and size.
    """
    activity.logger.info("Fetching document  job=%s  type=%s  loc=%s",
                         inp.job_id, inp.document_type, inp.location_type)

    from app.models import ConversionJob

    # Build a ConversionJob from the activity input
    job = ConversionJob(
        job_id=inp.job_id,
        document_type=inp.document_type,
        location_type=inp.location_type,
        s3_bucket=inp.s3_bucket,
        s3_key=inp.s3_key,
        s3_endpoint_url=inp.s3_endpoint_url,
        url=inp.url,
        ftp_host=inp.ftp_host,
        ftp_port=inp.ftp_port,
        ftp_path=inp.ftp_path,
        ftp_user=inp.ftp_user,
        ftp_pass=inp.ftp_pass,
        auth_type=inp.auth_type,
        auth_username=inp.auth_username,
        auth_password=inp.auth_password,
        auth_token=inp.auth_token,
    )

    from app.fetchers.dispatch import fetch_document

    # The fetcher yields a temp path – we consume it and COPY the file
    # to a durable location so the generator cleanup doesn't delete it
    # before the next activity runs.
    durable_path = os.path.join(
        settings.tmp_dir,
        f"temporal_{inp.job_id}_{uuid.uuid4().hex[:6]}"
    )

    for tmp_path in fetch_document(job):
        activity.heartbeat(f"Downloaded to {tmp_path}")
        # Copy to a durable path that survives generator cleanup
        import shutil
        shutil.copy2(tmp_path, durable_path)

    file_size = os.path.getsize(durable_path) if os.path.exists(durable_path) else 0
    activity.logger.info("Fetch complete  job=%s  path=%s  size=%d",
                         inp.job_id, durable_path, file_size)

    return FetchOutput(local_path=durable_path, file_size_bytes=file_size)


# ═════════════════════════════════════════════════════════════════════════════
# CONVERT ACTIVITIES – one per document type
# ═════════════════════════════════════════════════════════════════════════════

def _run_converter(inp: ConvertInput, converter_module) -> ConvertOutput:
    """
    Shared helper: run a converter module, write output to a .txt temp file,
    heartbeat periodically.
    """
    output_path = os.path.join(
        settings.tmp_dir,
        f"temporal_{inp.job_id}_converted.txt"
    )
    total_chars = 0
    chunk_count = 0

    with open(output_path, "w", encoding="utf-8") as f:
        for chunk in converter_module.convert_to_text(inp.local_path):
            f.write(chunk)
            total_chars += len(chunk)
            chunk_count += 1
            # Heartbeat every 10 chunks to keep Temporal happy
            if chunk_count % 10 == 0:
                activity.heartbeat(f"Converted {total_chars} chars so far")

    activity.heartbeat(f"Conversion complete: {total_chars} chars")
    return ConvertOutput(
        text_path=output_path,
        total_chars=total_chars,
        pages_processed=chunk_count,
    )


@activity.defn(name="convert_pdf")
async def convert_pdf_activity(inp: ConvertInput) -> ConvertOutput:
    """Convert a PDF to text, including embedded image OCR."""
    activity.logger.info("Converting PDF  job=%s", inp.job_id)
    from app.converters import pdf_converter
    result = _run_converter(inp, pdf_converter)
    # Count images extracted from PDF
    with open(result.text_path, "r") as f:
        content = f.read()
    result.images_extracted = content.count("[IMAGE TEXT]")
    return result


@activity.defn(name="convert_docx")
async def convert_docx_activity(inp: ConvertInput) -> ConvertOutput:
    """Convert a DOCX to text."""
    activity.logger.info("Converting DOCX  job=%s", inp.job_id)
    from app.converters import docx_converter
    return _run_converter(inp, docx_converter)


@activity.defn(name="convert_xlsx")
async def convert_xlsx_activity(inp: ConvertInput) -> ConvertOutput:
    """Convert an XLSX/CSV to text."""
    activity.logger.info("Converting XLSX/CSV  job=%s", inp.job_id)
    from app.converters import xlsx_converter
    return _run_converter(inp, xlsx_converter)


@activity.defn(name="convert_pptx")
async def convert_pptx_activity(inp: ConvertInput) -> ConvertOutput:
    """Convert a PPTX to text."""
    activity.logger.info("Converting PPTX  job=%s", inp.job_id)
    from app.converters import pptx_converter
    return _run_converter(inp, pptx_converter)


@activity.defn(name="convert_html")
async def convert_html_activity(inp: ConvertInput) -> ConvertOutput:
    """Convert HTML to text."""
    activity.logger.info("Converting HTML  job=%s", inp.job_id)
    from app.converters import html_converter
    return _run_converter(inp, html_converter)


@activity.defn(name="convert_rtf")
async def convert_rtf_activity(inp: ConvertInput) -> ConvertOutput:
    """Convert RTF to text."""
    activity.logger.info("Converting RTF  job=%s", inp.job_id)
    from app.converters import rtf_converter
    return _run_converter(inp, rtf_converter)


@activity.defn(name="convert_odt")
async def convert_odt_activity(inp: ConvertInput) -> ConvertOutput:
    """Convert ODT to text."""
    activity.logger.info("Converting ODT  job=%s", inp.job_id)
    from app.converters import odt_converter
    return _run_converter(inp, odt_converter)


@activity.defn(name="convert_txt")
async def convert_txt_activity(inp: ConvertInput) -> ConvertOutput:
    """Convert plain text (encoding detection + passthrough)."""
    activity.logger.info("Converting TXT  job=%s", inp.job_id)
    from app.converters import text_converter
    return _run_converter(inp, text_converter)


@activity.defn(name="convert_image")
async def convert_image_activity(inp: ConvertInput) -> ConvertOutput:
    """OCR an image to text."""
    activity.logger.info("Converting Image (OCR)  job=%s", inp.job_id)
    from app.converters import image_converter
    return _run_converter(inp, image_converter)


# ═════════════════════════════════════════════════════════════════════════════
# UPLOAD ACTIVITY
# ═════════════════════════════════════════════════════════════════════════════

@activity.defn(name="upload_text")
async def upload_text_activity(inp: UploadInput) -> UploadOutput:
    """Upload the converted text file to S3."""
    activity.logger.info("Uploading text  job=%s  path=%s", inp.job_id, inp.text_path)

    import boto3

    bucket = inp.output_bucket or settings.s3_output_bucket
    key = inp.output_key or f"converted/{inp.job_id}.txt"

    client = boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_default_region,
    )

    activity.heartbeat("Starting S3 upload")
    client.upload_file(inp.text_path, bucket, key)

    # Count chars for the result
    total_chars = 0
    with open(inp.text_path, "r", encoding="utf-8") as f:
        for line in f:
            total_chars += len(line)

    activity.logger.info("Upload complete  s3://%s/%s  (%d chars)", bucket, key, total_chars)
    return UploadOutput(bucket=bucket, key=key, total_chars=total_chars)


# ═════════════════════════════════════════════════════════════════════════════
# CLEANUP ACTIVITY
# ═════════════════════════════════════════════════════════════════════════════

@activity.defn(name="cleanup_temp_files")
async def cleanup_activity(inp: CleanupInput) -> bool:
    """Remove temporary files after processing."""
    for path in inp.paths:
        try:
            if path and os.path.exists(path):
                os.unlink(path)
                activity.logger.debug("Cleaned up: %s", path)
        except OSError as e:
            activity.logger.warning("Cleanup failed for %s: %s", path, e)
    return True


# ═════════════════════════════════════════════════════════════════════════════
# ACTIVITY REGISTRY – used by the worker to register all activities
# ═════════════════════════════════════════════════════════════════════════════

ALL_ACTIVITIES = [
    fetch_document_activity,
    convert_pdf_activity,
    convert_docx_activity,
    convert_xlsx_activity,
    convert_pptx_activity,
    convert_html_activity,
    convert_rtf_activity,
    convert_odt_activity,
    convert_txt_activity,
    convert_image_activity,
    upload_text_activity,
    cleanup_activity,
]
