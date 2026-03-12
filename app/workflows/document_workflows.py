"""
Per-document-type child workflows.

Each workflow handles the convert step for a specific document type, allowing
type-specific logic (e.g. PDF reports image count, PPTX reports slide count).

These are invoked as child workflows from the main DocumentConversionWorkflow,
giving full visibility in the Temporal UI for each conversion stage.
"""

from datetime import timedelta

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from config.settings import settings
    from app.workflows.dataclasses import ConvertInput, ConvertOutput

# ── Shared activity config ───────────────────────────────────────────────────

ACTIVITY_TIMEOUT = timedelta(seconds=600)  # 10 min per conversion
HEARTBEAT_TIMEOUT = timedelta(seconds=120)  # must heartbeat every 2 min


def _retry_policy():
    from temporalio.common import RetryPolicy
    return RetryPolicy(
        initial_interval=timedelta(seconds=5),
        backoff_coefficient=2.0,
        maximum_interval=timedelta(seconds=60),
        maximum_attempts=settings.temporal_retry_max_attempts,
    )


# ═════════════════════════════════════════════════════════════════════════════
# PDF Conversion Workflow
# ═════════════════════════════════════════════════════════════════════════════

@workflow.defn(name="PDFConversionWorkflow")
class PDFConversionWorkflow:
    """
    Durable PDF conversion: extracts text + embedded images with OCR.
    Retries on failure. Reports pages and images extracted.
    """

    @workflow.run
    async def run(self, inp: ConvertInput) -> ConvertOutput:
        workflow.logger.info("PDFConversionWorkflow started  job=%s", inp.job_id)

        result: ConvertOutput = await workflow.execute_activity(
            "convert_pdf",
            inp,
            start_to_close_timeout=ACTIVITY_TIMEOUT,
            heartbeat_timeout=HEARTBEAT_TIMEOUT,
            retry_policy=_retry_policy(),
        )

        workflow.logger.info(
            "PDF done  job=%s  chars=%d  pages=%d  images=%d",
            inp.job_id, result.total_chars, result.pages_processed, result.images_extracted,
        )
        return result


# ═════════════════════════════════════════════════════════════════════════════
# DOCX Conversion Workflow
# ═════════════════════════════════════════════════════════════════════════════

@workflow.defn(name="DOCXConversionWorkflow")
class DOCXConversionWorkflow:
    """Durable DOCX conversion with paragraph and table extraction."""

    @workflow.run
    async def run(self, inp: ConvertInput) -> ConvertOutput:
        workflow.logger.info("DOCXConversionWorkflow started  job=%s", inp.job_id)
        return await workflow.execute_activity(
            "convert_docx", inp,
            start_to_close_timeout=ACTIVITY_TIMEOUT,
            heartbeat_timeout=HEARTBEAT_TIMEOUT,
            retry_policy=_retry_policy(),
        )


# ═════════════════════════════════════════════════════════════════════════════
# XLSX / CSV Conversion Workflow
# ═════════════════════════════════════════════════════════════════════════════

@workflow.defn(name="XLSXConversionWorkflow")
class XLSXConversionWorkflow:
    """Durable spreadsheet conversion – handles XLSX and CSV."""

    @workflow.run
    async def run(self, inp: ConvertInput) -> ConvertOutput:
        workflow.logger.info("XLSXConversionWorkflow started  job=%s", inp.job_id)
        return await workflow.execute_activity(
            "convert_xlsx", inp,
            start_to_close_timeout=ACTIVITY_TIMEOUT,
            heartbeat_timeout=HEARTBEAT_TIMEOUT,
            retry_policy=_retry_policy(),
        )


# ═════════════════════════════════════════════════════════════════════════════
# PPTX Conversion Workflow
# ═════════════════════════════════════════════════════════════════════════════

@workflow.defn(name="PPTXConversionWorkflow")
class PPTXConversionWorkflow:
    """Durable PowerPoint conversion with slide text and speaker notes."""

    @workflow.run
    async def run(self, inp: ConvertInput) -> ConvertOutput:
        workflow.logger.info("PPTXConversionWorkflow started  job=%s", inp.job_id)
        return await workflow.execute_activity(
            "convert_pptx", inp,
            start_to_close_timeout=ACTIVITY_TIMEOUT,
            heartbeat_timeout=HEARTBEAT_TIMEOUT,
            retry_policy=_retry_policy(),
        )


# ═════════════════════════════════════════════════════════════════════════════
# HTML Conversion Workflow
# ═════════════════════════════════════════════════════════════════════════════

@workflow.defn(name="HTMLConversionWorkflow")
class HTMLConversionWorkflow:
    """Durable HTML-to-text conversion with tag stripping."""

    @workflow.run
    async def run(self, inp: ConvertInput) -> ConvertOutput:
        workflow.logger.info("HTMLConversionWorkflow started  job=%s", inp.job_id)
        return await workflow.execute_activity(
            "convert_html", inp,
            start_to_close_timeout=ACTIVITY_TIMEOUT,
            heartbeat_timeout=HEARTBEAT_TIMEOUT,
            retry_policy=_retry_policy(),
        )


# ═════════════════════════════════════════════════════════════════════════════
# RTF Conversion Workflow
# ═════════════════════════════════════════════════════════════════════════════

@workflow.defn(name="RTFConversionWorkflow")
class RTFConversionWorkflow:
    """Durable RTF conversion."""

    @workflow.run
    async def run(self, inp: ConvertInput) -> ConvertOutput:
        workflow.logger.info("RTFConversionWorkflow started  job=%s", inp.job_id)
        return await workflow.execute_activity(
            "convert_rtf", inp,
            start_to_close_timeout=ACTIVITY_TIMEOUT,
            heartbeat_timeout=HEARTBEAT_TIMEOUT,
            retry_policy=_retry_policy(),
        )


# ═════════════════════════════════════════════════════════════════════════════
# ODT Conversion Workflow
# ═════════════════════════════════════════════════════════════════════════════

@workflow.defn(name="ODTConversionWorkflow")
class ODTConversionWorkflow:
    """Durable OpenDocument Text conversion."""

    @workflow.run
    async def run(self, inp: ConvertInput) -> ConvertOutput:
        workflow.logger.info("ODTConversionWorkflow started  job=%s", inp.job_id)
        return await workflow.execute_activity(
            "convert_odt", inp,
            start_to_close_timeout=ACTIVITY_TIMEOUT,
            heartbeat_timeout=HEARTBEAT_TIMEOUT,
            retry_policy=_retry_policy(),
        )


# ═════════════════════════════════════════════════════════════════════════════
# TXT Conversion Workflow
# ═════════════════════════════════════════════════════════════════════════════

@workflow.defn(name="TXTConversionWorkflow")
class TXTConversionWorkflow:
    """Durable plain text conversion (encoding detection)."""

    @workflow.run
    async def run(self, inp: ConvertInput) -> ConvertOutput:
        workflow.logger.info("TXTConversionWorkflow started  job=%s", inp.job_id)
        return await workflow.execute_activity(
            "convert_txt", inp,
            start_to_close_timeout=ACTIVITY_TIMEOUT,
            heartbeat_timeout=HEARTBEAT_TIMEOUT,
            retry_policy=_retry_policy(),
        )


# ═════════════════════════════════════════════════════════════════════════════
# Image OCR Conversion Workflow
# ═════════════════════════════════════════════════════════════════════════════

@workflow.defn(name="ImageConversionWorkflow")
class ImageConversionWorkflow:
    """Durable image OCR conversion (Tesseract)."""

    @workflow.run
    async def run(self, inp: ConvertInput) -> ConvertOutput:
        workflow.logger.info("ImageConversionWorkflow started  job=%s", inp.job_id)
        return await workflow.execute_activity(
            "convert_image", inp,
            start_to_close_timeout=ACTIVITY_TIMEOUT,
            heartbeat_timeout=HEARTBEAT_TIMEOUT,
            retry_policy=_retry_policy(),
        )


# ═════════════════════════════════════════════════════════════════════════════
# Registry – map document type strings to child workflow classes
# ═════════════════════════════════════════════════════════════════════════════

CHILD_WORKFLOW_MAP = {
    "pdf":   PDFConversionWorkflow,
    "docx":  DOCXConversionWorkflow,
    "xlsx":  XLSXConversionWorkflow,
    "csv":   XLSXConversionWorkflow,
    "pptx":  PPTXConversionWorkflow,
    "html":  HTMLConversionWorkflow,
    "rtf":   RTFConversionWorkflow,
    "odt":   ODTConversionWorkflow,
    "txt":   TXTConversionWorkflow,
    "image": ImageConversionWorkflow,
}

ALL_CHILD_WORKFLOWS = list({cls for cls in CHILD_WORKFLOW_MAP.values()})
