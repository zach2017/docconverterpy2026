"""
Shared data classes for Temporal workflows and activities.

All classes are dataclasses (not Pydantic) to ensure clean serialization
across the Temporal boundary. Temporal uses JSON serialization by default.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class FetchInput:
    """Input for the fetch_document activity."""
    job_id: str
    location_type: str          # s3 | url | ftp
    document_type: str          # pdf | docx | ...

    # S3
    s3_bucket: Optional[str] = None
    s3_key: Optional[str] = None
    s3_endpoint_url: Optional[str] = None

    # URL
    url: Optional[str] = None

    # FTP
    ftp_host: Optional[str] = None
    ftp_port: int = 21
    ftp_path: Optional[str] = None
    ftp_user: Optional[str] = None
    ftp_pass: Optional[str] = None

    # Auth
    auth_type: str = "none"
    auth_username: Optional[str] = None
    auth_password: Optional[str] = None
    auth_token: Optional[str] = None


@dataclass
class FetchOutput:
    """Output from the fetch_document activity."""
    local_path: str             # path to the temp file on disk
    file_size_bytes: int = 0


@dataclass
class ConvertInput:
    """Input for any convert_* activity."""
    job_id: str
    local_path: str             # path to the source file
    document_type: str          # pdf | docx | ...


@dataclass
class ConvertOutput:
    """Output from any convert_* activity."""
    text_path: str              # path to the .txt output file
    total_chars: int = 0
    pages_processed: int = 0
    images_extracted: int = 0


@dataclass
class UploadInput:
    """Input for the upload_text activity."""
    job_id: str
    text_path: str              # local .txt file to upload
    output_bucket: Optional[str] = None
    output_key: Optional[str] = None


@dataclass
class UploadOutput:
    """Output from the upload_text activity."""
    bucket: str
    key: str
    total_chars: int = 0


@dataclass
class CleanupInput:
    """Input for the cleanup activity."""
    paths: list[str] = field(default_factory=list)


@dataclass
class ConversionWorkflowInput:
    """Input for the top-level DocumentConversionWorkflow."""
    job_id: str
    document_type: str
    location_type: str

    # Source fields (same as FetchInput)
    s3_bucket: Optional[str] = None
    s3_key: Optional[str] = None
    s3_endpoint_url: Optional[str] = None
    url: Optional[str] = None
    ftp_host: Optional[str] = None
    ftp_port: int = 21
    ftp_path: Optional[str] = None
    ftp_user: Optional[str] = None
    ftp_pass: Optional[str] = None
    auth_type: str = "none"
    auth_username: Optional[str] = None
    auth_password: Optional[str] = None
    auth_token: Optional[str] = None

    # Output overrides
    output_s3_bucket: Optional[str] = None
    output_s3_key: Optional[str] = None

    # For local/API uploads: path already on disk
    local_file_path: Optional[str] = None


@dataclass
class ConversionWorkflowOutput:
    """Output from the DocumentConversionWorkflow."""
    job_id: str
    success: bool
    output_bucket: Optional[str] = None
    output_key: Optional[str] = None
    error: Optional[str] = None
    total_chars: int = 0
    pages_processed: int = 0
    images_extracted: int = 0
