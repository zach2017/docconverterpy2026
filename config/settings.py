"""
Centralized configuration via environment variables.
Every setting has a sensible default so the app can start with minimal env.
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # ── Feature flags ────────────────────────────────────────────────────
    enable_api: bool = Field(True, alias="ENABLE_API")
    enable_sqs: bool = Field(True, alias="ENABLE_SQS")
    enable_rabbitmq: bool = Field(True, alias="ENABLE_RABBITMQ")
    enable_kafka: bool = Field(True, alias="ENABLE_KAFKA")
    enable_temporal: bool = Field(True, alias="ENABLE_TEMPORAL")
    use_temporal_workflows: bool = Field(True, alias="USE_TEMPORAL_WORKFLOWS")

    # ── Temporal ─────────────────────────────────────────────────────────
    temporal_host: str = Field("localhost:7233", alias="TEMPORAL_HOST")
    temporal_namespace: str = Field("default", alias="TEMPORAL_NAMESPACE")
    temporal_task_queue: str = Field("docconv-tasks", alias="TEMPORAL_TASK_QUEUE")
    temporal_workflow_timeout: int = Field(3600, alias="TEMPORAL_WORKFLOW_TIMEOUT")
    temporal_activity_timeout: int = Field(600, alias="TEMPORAL_ACTIVITY_TIMEOUT")
    temporal_retry_max_attempts: int = Field(3, alias="TEMPORAL_RETRY_MAX_ATTEMPTS")

    # ── SQS ──────────────────────────────────────────────────────────────
    sqs_endpoint_url: str = Field("http://localhost:4566", alias="SQS_ENDPOINT_URL")
    sqs_queue_name: str = Field("docconv-jobs", alias="SQS_QUEUE_NAME")
    sqs_poll_interval: int = Field(5, alias="SQS_POLL_INTERVAL")

    # ── S3 ───────────────────────────────────────────────────────────────
    s3_endpoint_url: str = Field("http://localhost:4566", alias="S3_ENDPOINT_URL")
    s3_output_bucket: str = Field("docconv-output", alias="S3_OUTPUT_BUCKET")

    # ── RabbitMQ ─────────────────────────────────────────────────────────
    rabbitmq_host: str = Field("localhost", alias="RABBITMQ_HOST")
    rabbitmq_port: int = Field(5672, alias="RABBITMQ_PORT")
    rabbitmq_user: str = Field("docconv", alias="RABBITMQ_USER")
    rabbitmq_pass: str = Field("docconv", alias="RABBITMQ_PASS")
    rabbitmq_queue: str = Field("docconv-jobs", alias="RABBITMQ_QUEUE")

    # ── Kafka ────────────────────────────────────────────────────────────
    kafka_bootstrap_servers: str = Field("localhost:9092", alias="KAFKA_BOOTSTRAP_SERVERS")
    kafka_topic: str = Field("docconv-jobs", alias="KAFKA_TOPIC")
    kafka_group_id: str = Field("docconv-group", alias="KAFKA_GROUP_ID")

    # ── AWS credentials (used by boto3) ──────────────────────────────────
    aws_access_key_id: str = Field("test", alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field("test", alias="AWS_SECRET_ACCESS_KEY")
    aws_default_region: str = Field("us-east-1", alias="AWS_DEFAULT_REGION")

    # ── Tuning ───────────────────────────────────────────────────────────
    chunk_size: int = Field(65536, alias="CHUNK_SIZE")  # 64 KB
    tmp_dir: str = Field("/tmp/docconv", alias="TMP_DIR")
    log_level: str = Field("INFO", alias="LOG_LEVEL")
    api_port: int = Field(8080, alias="API_PORT")

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
