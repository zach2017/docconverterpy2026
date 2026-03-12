#!/usr/bin/env python3
"""Generate a comprehensive User Guide DOCX for the Document Conversion Service."""

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

doc = Document()
for s in doc.sections:
    s.top_margin = s.bottom_margin = s.left_margin = s.right_margin = Cm(2.54)

style = doc.styles['Normal']
style.font.name = 'Calibri'; style.font.size = Pt(11)
style.font.color.rgb = RGBColor(0x33,0x33,0x33)
style.paragraph_format.space_after = Pt(6); style.paragraph_format.line_spacing = 1.15

for lv,(sz,co) in enumerate([(Pt(28),RGBColor(0x1a,0x56,0xc4)),
    (Pt(20),RGBColor(0x24,0x65,0xb8)),(Pt(14),RGBColor(0x2d,0x73,0xac))],1):
    h=doc.styles[f'Heading {lv}'];h.font.size=sz;h.font.color.rgb=co
    h.font.bold=True;h.font.name='Calibri'
    h.paragraph_format.space_before=Pt(18 if lv==1 else 14);h.paragraph_format.space_after=Pt(8)

def code(txt):
    p=doc.add_paragraph();p.paragraph_format.space_before=Pt(4);p.paragraph_format.space_after=Pt(4);p.paragraph_format.left_indent=Cm(0.5)
    pPr=p._element.get_or_add_pPr();shd=OxmlElement('w:shd');shd.set(qn('w:fill'),'F0F2F5');shd.set(qn('w:val'),'clear');pPr.append(shd)
    r=p.add_run(txt);r.font.name='Consolas';r.font.size=Pt(9.5);r.font.color.rgb=RGBColor(0x1e,0x1e,0x2e)

def tbl(headers,rows):
    t=doc.add_table(rows=1+len(rows),cols=len(headers));t.alignment=WD_TABLE_ALIGNMENT.LEFT;t.style='Light Grid Accent 1'
    for i,h in enumerate(headers):
        c=t.rows[0].cells[i];c.text=h
        for p in c.paragraphs:
            for r in p.runs: r.font.bold=True;r.font.size=Pt(10)
    for ri,row in enumerate(rows):
        for ci,v in enumerate(row):
            c=t.rows[ri+1].cells[ci];c.text=str(v)
            for p in c.paragraphs:
                for r in p.runs: r.font.size=Pt(10)
    doc.add_paragraph()

def bullet(txt,bold_pfx=None):
    p=doc.add_paragraph(style='List Bullet')
    if bold_pfx: r=p.add_run(bold_pfx);r.bold=True;p.add_run(txt)
    else: p.add_run(txt)

def note(txt):
    p=doc.add_paragraph();p.paragraph_format.left_indent=Cm(0.5)
    r=p.add_run("Note: ");r.bold=True;r.font.color.rgb=RGBColor(0xc0,0x6a,0x00);p.add_run(txt)

# ═══════════════════════════ COVER ═══════════════════════════════════════════
for _ in range(6): doc.add_paragraph()
p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=p.add_run("Document Conversion Service");r.font.size=Pt(36);r.font.color.rgb=RGBColor(0x1a,0x56,0xc4);r.bold=True
p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=p.add_run("Complete User Guide");r.font.size=Pt(20);r.font.color.rgb=RGBColor(0x55,0x55,0x55)
doc.add_paragraph()
p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=p.add_run("Version 2.0  •  2025");r.font.size=Pt(12);r.font.color.rgb=RGBColor(0x88,0x88,0x88)
p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.space_before=Pt(30)
r=p.add_run("A production-grade microservice that converts documents and images to plain text.\n"
    "Supports SQS, RabbitMQ, Kafka, Temporal.io durable workflows, REST API, and 10 document formats.")
r.font.size=Pt(11);r.font.color.rgb=RGBColor(0x66,0x66,0x66)
doc.add_page_break()

# ═══════════════════════════ TOC ═════════════════════════════════════════════
doc.add_heading("Table of Contents",level=1)
for item in [
    "1. Overview","2. Architecture","3. Prerequisites",
    "4. Quick Start – Docker Compose","5. Configuration Reference",
    "6. Message Schema","7. REST API Reference",
    "8. Using the API Test Console",
    "9. Message Bus Integration",
    "    9.1 Amazon SQS","    9.2 RabbitMQ","    9.3 Apache Kafka",
    "10. Temporal.io Durable Workflows",
    "    10.1 Overview & Architecture",
    "    10.2 The DocumentConversionWorkflow",
    "    10.3 Document-Type Child Workflows",
    "    10.4 Activities",
    "    10.5 Batch Processing",
    "    10.6 The Temporal Worker",
    "    10.7 Temporal Web UI",
    "    10.8 Workflow API Endpoints",
    "    10.9 Execution Modes",
    "    10.10 Starting Workflows from Python",
    "11. Document Converters","12. Image OCR",
    "13. File Fetchers (S3, URL, FTP)","14. Output Storage (S3)",
    "15. Memory Efficiency & Streaming","16. Testing",
    "17. Troubleshooting","18. curl Examples Cookbook",
]:
    p=doc.add_paragraph(item);p.paragraph_format.space_after=Pt(2);p.runs[0].font.size=Pt(11)
doc.add_page_break()

# ═══════════════════════════ 1. OVERVIEW ═════════════════════════════════════
doc.add_heading("1. Overview",level=1)
doc.add_paragraph(
    "The Document Conversion Service is a containerized Python microservice that accepts "
    "conversion jobs from multiple sources – three message buses (Amazon SQS, RabbitMQ, "
    "Apache Kafka), Temporal.io durable workflows, and an optional REST API – and converts "
    "documents and images into plain text. The extracted text is uploaded to an Amazon S3 "
    "bucket (or S3-compatible storage like LocalStack or MinIO).")
doc.add_paragraph(
    "Every component is independently toggleable via environment variables. You can run "
    "the service as a pure queue consumer, a Temporal workflow worker, an API-only service, "
    "or any combination.")
doc.add_heading("Key Features",level=3)
for f in [
    "10 document formats: PDF, DOCX, XLSX, PPTX, HTML, RTF, ODT, TXT, CSV, Image (OCR)",
    "3 message buses: SQS, RabbitMQ, Kafka – all using the same JSON message schema",
    "Temporal.io durable execution: automatic retries, crash recovery, queryable state, full audit trail",
    "Per-document-type Temporal child workflows with specialized orchestration",
    "Batch workflow: convert multiple documents in parallel via a single Temporal invocation",
    "REST API with file upload, JSON job submission, and workflow status endpoints",
    "Web-based API Test Console (built-in HTML UI) + Temporal Web UI on port 8088",
    "3 document sources: S3, HTTP/HTTPS URLs, FTP servers",
    "Authentication support: None, Basic, Bearer token",
    "Memory-efficient streaming via Python generators and temporary files",
    "PDF image extraction with OCR (Tesseract)",
    "Full Docker Compose stack with LocalStack, RabbitMQ, Kafka, Temporal, FTP",
    "Every component can be enabled/disabled via environment variables",
    "Automatic fallback from Temporal to direct processing if Temporal is unavailable",
]: bullet(f)

# ═══════════════════════════ 2. ARCHITECTURE ═════════════════════════════════
doc.add_page_break()
doc.add_heading("2. Architecture",level=1)
doc.add_heading("System Diagram",level=3)
doc.add_paragraph("The service follows a pipeline pattern: Ingest → Fetch → Convert → Upload. "
    "When Temporal is enabled, each step becomes a durable, retryable activity within a workflow.")
code(
    "┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌────────────────┐\n"
    "│    SQS    │ │ RabbitMQ  │ │   Kafka   │ │ REST API  │ │  Temporal.io   │\n"
    "│  Queue    │ │  Queue    │ │  Topic    │ │ (FastAPI) │ │  Client SDK    │\n"
    "└─────┬─────┘ └─────┬─────┘ └─────┬─────┘ └─────┬─────┘ └───────┬────────┘\n"
    "      │             │             │             │               │\n"
    "      └─────────────┴──────┬──────┴─────────────┘               │\n"
    "                           ▼                                    ▼\n"
    "            ┌──────────────────────────────────────────────────────────┐\n"
    "            │              Processor (routing layer)                    │\n"
    "            │  USE_TEMPORAL_WORKFLOWS=true → Temporal Workflow          │\n"
    "            │  USE_TEMPORAL_WORKFLOWS=false → Direct Pipeline           │\n"
    "            └───────────────────────┬──────────────────────────────────┘\n"
    "                                    ▼\n"
    "           ┌─────────────────────────────────────────────────────┐\n"
    "           │        DocumentConversionWorkflow (Temporal)         │\n"
    "           │  Activity 1: Fetch   (S3 / URL / FTP → tmp file)    │\n"
    "           │  Child WF:   Convert (PDF / DOCX / XLSX / ... )     │\n"
    "           │  Activity 3: Upload  (tmp → S3 output bucket)       │\n"
    "           │  Activity 4: Cleanup (remove tmp files)              │\n"
    "           └─────────────────────────────────────────────────────┘")

doc.add_heading("Docker Services",level=3)
tbl(["Service","Image","Ports","Purpose"],[
    ["localstack","localstack/localstack:3.4","4566","SQS queues + S3 buckets"],
    ["rabbitmq","rabbitmq:3.13-management-alpine","5672, 15672","RabbitMQ bus + Management UI"],
    ["zookeeper","confluentinc/cp-zookeeper:7.6.1","2181","Kafka coordination"],
    ["kafka","confluentinc/cp-kafka:7.6.1","9092","Kafka message bus"],
    ["temporal-postgresql","postgres:16-alpine","—","Temporal persistence DB"],
    ["temporal-server","temporalio/auto-setup:1.24.2","7233","Temporal gRPC frontend"],
    ["temporal-admin-tools","temporalio/admin-tools:1.24.2","—","Temporal CLI tools"],
    ["temporal-ui","temporalio/ui:2.26.2","8088","Temporal Web UI"],
    ["ftp","fauria/vsftpd","21, 21100-21110","Demo FTP server"],
    ["docconv-app","Built from Dockerfile","8080","The conversion service"],
])

doc.add_heading("Project Structure",level=3)
code(
    "docconv-service/\n"
    "├── docker-compose.yml          # Full stack (10 services)\n"
    "├── Dockerfile\n"
    "├── requirements.txt\n"
    "├── .env.example\n"
    "├── config/settings.py          # Pydantic settings\n"
    "├── app/\n"
    "│   ├── main.py                 # ★ Entry point\n"
    "│   ├── models.py               # Pydantic models\n"
    "│   ├── api.py                  # FastAPI + workflow endpoints\n"
    "│   ├── processor.py            # Direct / Temporal routing\n"
    "│   ├── storage.py              # S3 output uploader\n"
    "│   ├── static/index.html       # API Test Console\n"
    "│   ├── bus/                    # SQS, RabbitMQ, Kafka listeners\n"
    "│   ├── fetchers/              # S3, URL, FTP download\n"
    "│   ├── converters/            # One module per document type\n"
    "│   └── workflows/             # ★ Temporal.io integration\n"
    "│       ├── dataclasses.py     #   Serializable I/O types\n"
    "│       ├── activities.py      #   12 Temporal activities\n"
    "│       ├── document_workflows.py # 9 child workflows\n"
    "│       ├── conversion_workflow.py # Main + Batch workflow\n"
    "│       ├── worker.py          #   Worker thread\n"
    "│       └── client.py          #   Start workflows from code\n"
    "├── scripts/\n"
    "│   ├── init-localstack.sh\n"
    "│   └── demo.py\n"
    "└── tests/\n"
    "    └── test_full_flow.py      # 48 integration tests")

# ═══════════════════════════ 3. PREREQUISITES ════════════════════════════════
doc.add_page_break()
doc.add_heading("3. Prerequisites",level=1)
tbl(["Requirement","Version","Notes"],[
    ["Docker","20.10+","Docker Desktop or Docker Engine"],
    ["Docker Compose","v2.0+","Included with Docker Desktop"],
    ["Disk space","~4 GB","For container images (including Temporal)"],
    ["RAM","8 GB recommended","Kafka + Temporal + LocalStack need headroom"],
    ["Python","3.10+ (optional)","Only for running demo.py or tests locally"],
])
note("All service dependencies are installed inside the Docker image.")

# ═══════════════════════════ 4. QUICK START ══════════════════════════════════
doc.add_heading("4. Quick Start – Docker Compose",level=1)
for step,title,cmd,desc in [
    (1,"Extract and enter the project","unzip docconv-service.zip\ncd docconv-service",None),
    (2,"Make the init script executable","chmod +x scripts/init-localstack.sh",None),
    (3,"Build and start all services","docker compose up --build -d",
     "Builds the app, pulls all infrastructure images (LocalStack, RabbitMQ, Kafka, Temporal), and starts 10 containers."),
    (4,"Verify services are healthy","docker compose ps",
     "All services should show 'healthy' or 'running'. Temporal may take 30-40 seconds."),
    (5,"Open the API Test Console",None,"Open http://localhost:8080 in your browser."),
    (6,"Open the Temporal Web UI",None,"Open http://localhost:8088 to view workflows, activities, and execution history."),
    (7,"Watch logs","docker compose logs -f docconv-app",None),
    (8,"Run the demo script (optional)","pip install boto3 pika confluent-kafka requests\npython scripts/demo.py",None),
    (9,"Stop the stack","docker compose down          # Stop\ndocker compose down -v       # Stop + remove volumes",None),
]:
    doc.add_heading(f"Step {step}: {title}",level=3)
    if cmd: code(cmd)
    if desc: doc.add_paragraph(desc)

# ═══════════════════════════ 5. CONFIGURATION ════════════════════════════════
doc.add_page_break()
doc.add_heading("5. Configuration Reference",level=1)
doc.add_paragraph("All configuration is via environment variables. Copy .env.example to .env for local overrides.")

doc.add_heading("Feature Flags",level=3)
tbl(["Variable","Default","Description"],[
    ["ENABLE_API","true","Start the FastAPI HTTP server"],
    ["ENABLE_SQS","true","Start the SQS listener thread"],
    ["ENABLE_RABBITMQ","true","Start the RabbitMQ consumer thread"],
    ["ENABLE_KAFKA","true","Start the Kafka consumer thread"],
    ["ENABLE_TEMPORAL","true","Start the Temporal worker thread"],
    ["USE_TEMPORAL_WORKFLOWS","true","Route all jobs through Temporal (vs direct pipeline)"],
])
doc.add_paragraph('Set any flag to "false" to disable that component. When USE_TEMPORAL_WORKFLOWS is false, '
    "jobs still process successfully via the direct pipeline even if ENABLE_TEMPORAL is true (the worker runs but isn't invoked).")

for section,vars in [
    ("SQS Settings",[
        ["SQS_ENDPOINT_URL","http://localstack:4566","SQS endpoint"],
        ["SQS_QUEUE_NAME","docconv-jobs","Queue to poll"],
        ["SQS_POLL_INTERVAL","5","Long-poll wait (seconds)"],
    ]),
    ("S3 Output Settings",[
        ["S3_ENDPOINT_URL","http://localstack:4566","S3 endpoint for uploads"],
        ["S3_OUTPUT_BUCKET","docconv-output","Default output bucket"],
    ]),
    ("RabbitMQ Settings",[
        ["RABBITMQ_HOST","rabbitmq","Server hostname"],
        ["RABBITMQ_PORT","5672","AMQP port"],
        ["RABBITMQ_USER","docconv","Username"],
        ["RABBITMQ_PASS","docconv","Password"],
        ["RABBITMQ_QUEUE","docconv-jobs","Queue name"],
    ]),
    ("Kafka Settings",[
        ["KAFKA_BOOTSTRAP_SERVERS","kafka:29092","Broker address"],
        ["KAFKA_TOPIC","docconv-jobs","Topic to subscribe"],
        ["KAFKA_GROUP_ID","docconv-group","Consumer group ID"],
    ]),
    ("Temporal.io Settings",[
        ["TEMPORAL_HOST","temporal-server:7233","Temporal gRPC endpoint"],
        ["TEMPORAL_NAMESPACE","default","Temporal namespace"],
        ["TEMPORAL_TASK_QUEUE","docconv-tasks","Worker task queue name"],
        ["TEMPORAL_WORKFLOW_TIMEOUT","3600","Max workflow duration (seconds)"],
        ["TEMPORAL_ACTIVITY_TIMEOUT","600","Max single activity duration (seconds)"],
        ["TEMPORAL_RETRY_MAX_ATTEMPTS","3","Retry attempts per activity on failure"],
    ]),
    ("AWS Credentials",[
        ["AWS_ACCESS_KEY_ID","test","Used by boto3"],
        ["AWS_SECRET_ACCESS_KEY","test","Used by boto3"],
        ["AWS_DEFAULT_REGION","us-east-1","AWS region"],
    ]),
    ("Tuning",[
        ["CHUNK_SIZE","65536","Read/write chunk size (64 KB)"],
        ["TMP_DIR","/tmp/docconv","Temporary file directory"],
        ["LOG_LEVEL","INFO","Logging level"],
        ["API_PORT","8080","HTTP server port"],
    ]),
]:
    doc.add_heading(section,level=3)
    tbl(["Variable","Default","Description"],vars)

# ═══════════════════════════ 6. MESSAGE SCHEMA ═══════════════════════════════
doc.add_page_break()
doc.add_heading("6. Message Schema",level=1)
doc.add_paragraph("Every bus, the REST API, and Temporal workflows accept the same JSON schema.")
doc.add_heading("Full JSON Schema",level=3)
code('{\n  "job_id": "optional-caller-id",\n  "document_type": "pdf",\n'
     '  "location_type": "s3",\n  "s3_bucket": "my-bucket",\n  "s3_key": "path/to/file.pdf",\n'
     '  "s3_endpoint_url": null,\n  "url": "https://example.com/doc.pdf",\n'
     '  "ftp_host": "ftp.example.com",\n  "ftp_port": 21,\n  "ftp_path": "/path/to/file",\n'
     '  "ftp_user": "user",  "ftp_pass": "pass",\n'
     '  "auth_type": "none",\n  "auth_username": null,  "auth_password": null,\n  "auth_token": null,\n'
     '  "output_s3_bucket": null,\n  "output_s3_key": null\n}')

doc.add_heading("Supported document_type values",level=3)
tbl(["Value","Description","Converter / Child Workflow"],[
    ["pdf","PDF with embedded image OCR","pdf_converter / PDFConversionWorkflow"],
    ["docx","Microsoft Word","docx_converter / DOCXConversionWorkflow"],
    ["xlsx","Microsoft Excel","xlsx_converter / XLSXConversionWorkflow"],
    ["pptx","Microsoft PowerPoint","pptx_converter / PPTXConversionWorkflow"],
    ["html","HTML web pages","html_converter / HTMLConversionWorkflow"],
    ["rtf","Rich Text Format","rtf_converter / RTFConversionWorkflow"],
    ["odt","OpenDocument Text","odt_converter / ODTConversionWorkflow"],
    ["txt","Plain text (encoding detection)","text_converter / TXTConversionWorkflow"],
    ["csv","Comma-separated values","xlsx_converter / XLSXConversionWorkflow"],
    ["image","JPEG/PNG/TIFF/BMP/WEBP (OCR)","image_converter / ImageConversionWorkflow"],
])

# ═══════════════════════════ 7. REST API ═════════════════════════════════════
doc.add_page_break()
doc.add_heading("7. REST API Reference",level=1)
doc.add_paragraph("Base URL: http://localhost:8080")

for ep,method,desc,curl_cmd,resp in [
    ("GET /","GET","Returns the API Test Console HTML page.",None,None),
    ("GET /health","GET","Returns service status and all enabled components.",
     "curl http://localhost:8080/health",
     '{"status":"ok","api_enabled":true,"sqs_enabled":true,\n "rabbitmq_enabled":true,"kafka_enabled":true,\n "temporal_enabled":true,"temporal_workflows_active":true,\n "temporal_host":"temporal-server:7233",\n "temporal_task_queue":"docconv-tasks"}'),
    ("POST /convert/job","POST","Submit a remote-source conversion job.",
     'curl -X POST http://localhost:8080/convert/job \\\n  -H "Content-Type: application/json" \\\n'
     '  -d \'{"document_type":"html","location_type":"url",\n       "url":"https://example.com"}\'',
     '{"job_id":"a1b2c3d4e5f6","success":true,\n "output_bucket":"docconv-output",\n "output_key":"converted/a1b2c3d4e5f6.txt",\n "characters_extracted":1256}'),
    ("POST /convert/upload","POST","Upload a file directly (multipart form).",
     'curl -X POST http://localhost:8080/convert/upload \\\n  -F "file=@report.pdf" -F "document_type=pdf"',None),
    ("GET /workflow/{id}/status","GET","Query status of a Temporal workflow.",
     "curl http://localhost:8080/workflow/docconv-a1b2c3d4e5f6/status",
     '{"workflow_id":"docconv-a1b2c3d4e5f6",\n "status":"COMPLETED","custom_status":"COMPLETED",\n "current_step":"DONE","task_queue":"docconv-tasks"}'),
    ("POST /workflow/{id}/cancel","POST","Send a cancellation signal to a running workflow.",
     "curl -X POST http://localhost:8080/workflow/docconv-abc123/cancel",
     '{"workflow_id":"docconv-abc123",\n "message":"Cancellation signal sent"}'),
    ("GET /workflows/recent","GET","List recent workflows from Temporal.",
     "curl http://localhost:8080/workflows/recent?limit=5",None),
    ("GET /docs","GET","FastAPI auto-generated Swagger/OpenAPI docs.",None,None),
]:
    doc.add_heading(ep,level=3)
    doc.add_paragraph(desc)
    if curl_cmd: code(curl_cmd)
    if resp:
        doc.add_paragraph("Response:")
        code(resp)

# ═══════════════════════════ 8. TEST CONSOLE ═════════════════════════════════
doc.add_heading("8. Using the API Test Console",level=1)
doc.add_paragraph("Open http://localhost:8080 for the built-in web UI.")
for f in [
    "Health Check tab – verify connectivity and see all enabled components (including Temporal status)",
    "Upload tab – drag-and-drop files with auto-detection of document type",
    "Job tab – build JSON jobs for S3/URL/FTP sources with live preview",
    "Schema tab – full message reference with supported values",
    "Request history – logs every request with method, status code, and timing",
]: bullet(f)

# ═══════════════════════════ 9. MESSAGE BUSES ════════════════════════════════
doc.add_page_break()
doc.add_heading("9. Message Bus Integration",level=1)
doc.add_paragraph("Each listener runs in its own daemon thread. When USE_TEMPORAL_WORKFLOWS is enabled, "
    "messages received from any bus are routed through a Temporal workflow for durable execution.")

doc.add_heading("9.1  Amazon SQS",level=2)
doc.add_paragraph("Long-polls the configured SQS queue. Uses LocalStack locally; point to real AWS in production.")
doc.add_heading("Sending via Python",level=3)
code('import boto3, json\nsqs = boto3.client("sqs", endpoint_url="http://localhost:4566",\n'
     '    aws_access_key_id="test", aws_secret_access_key="test", region_name="us-east-1")\n'
     'url = sqs.get_queue_url(QueueName="docconv-jobs")["QueueUrl"]\n'
     'sqs.send_message(QueueUrl=url, MessageBody=json.dumps(\n'
     '    {"document_type":"pdf","location_type":"s3",\n'
     '     "s3_bucket":"docconv-input","s3_key":"test.pdf"}))')

doc.add_heading("9.2  RabbitMQ",level=2)
doc.add_paragraph("Connects via AMQP. Management UI at http://localhost:15672 (docconv/docconv).")
doc.add_heading("Sending via Python",level=3)
code('import pika, json\ncreds = pika.PlainCredentials("docconv","docconv")\n'
     'conn = pika.BlockingConnection(pika.ConnectionParameters("localhost",5672,credentials=creds))\n'
     'ch = conn.channel(); ch.queue_declare(queue="docconv-jobs",durable=True)\n'
     'ch.basic_publish(exchange="",routing_key="docconv-jobs",\n'
     '    body=json.dumps({"document_type":"html","location_type":"url",\n'
     '                     "url":"https://example.com"}),\n'
     '    properties=pika.BasicProperties(delivery_mode=2))\nconn.close()')

doc.add_heading("9.3  Apache Kafka",level=2)
doc.add_paragraph("Subscribes to the configured topic. Auto-topic creation is enabled.")
doc.add_heading("Sending via Python",level=3)
code('from confluent_kafka import Producer\nimport json\n'
     'p = Producer({"bootstrap.servers":"localhost:9092"})\n'
     'p.produce("docconv-jobs",value=json.dumps(\n'
     '    {"document_type":"docx","location_type":"url",\n'
     '     "url":"https://example.com/doc.docx"}).encode("utf-8"))\np.flush()')

# ═══════════════════════════ 10. TEMPORAL ════════════════════════════════════
doc.add_page_break()
doc.add_heading("10. Temporal.io Durable Workflows",level=1)

doc.add_heading("10.1  Overview & Architecture",level=2)
doc.add_paragraph(
    "Temporal.io is an open-source durable execution system that guarantees workflows run to "
    "completion even if the worker process crashes, restarts, or the server reboots. When enabled, "
    "every document conversion job is executed as a Temporal workflow, giving you automatic retries, "
    "queryable state, cancellation signals, a full audit trail, and crash recovery – for free.")
doc.add_paragraph(
    "The integration uses a three-tier design: a top-level DocumentConversionWorkflow orchestrates "
    "the pipeline, delegates conversion to one of 9 document-type-specific child workflows, "
    "and each child workflow invokes a dedicated Temporal activity. Every step is independently "
    "retryable with exponential backoff.")
code(
    "DocumentConversionWorkflow (top-level)\n"
    "  │\n"
    "  ├─ Activity: fetch_document     (S3 / URL / FTP → tmp file)\n"
    "  │\n"
    "  ├─ Child WF: PDFConversionWorkflow\n"
    "  │    └─ Activity: convert_pdf   (pdfplumber + OCR → text)\n"
    "  │   OR\n"
    "  ├─ Child WF: DOCXConversionWorkflow\n"
    "  │    └─ Activity: convert_docx  (python-docx → text)\n"
    "  │   OR ... (one child WF per document type)\n"
    "  │\n"
    "  ├─ Activity: upload_text        (text → S3 output bucket)\n"
    "  │\n"
    "  └─ Activity: cleanup_temp_files (remove tmp files)")

doc.add_heading("10.2  The DocumentConversionWorkflow",level=2)
doc.add_paragraph(
    "The main workflow (conversion_workflow.py) orchestrates 4 sequential steps: Fetch, Convert, "
    "Upload, Cleanup. It provides three Temporal features that make it observable and controllable:")
bullet("Queryable state: ", "Queryable state: ")
p=doc.add_paragraph(style='List Bullet')
p.add_run('Use the "get_status" query to check the current phase (FETCHING, CONVERTING_PDF, UPLOADING, '
    'COMPLETED, FAILED). Use "get_step" for the specific sub-step.')
bullet("Cancellation signal: ", "Cancellation signal: ")
p=doc.add_paragraph(style='List Bullet')
p.add_run('Send the "cancel" signal to gracefully stop a running workflow. The workflow checks for '
    'cancellation between each step and returns a CANCELLED result.')
bullet("Automatic fallback: ", "Automatic fallback: ")
p=doc.add_paragraph(style='List Bullet')
p.add_run("If a Temporal workflow fails to start (e.g. server unreachable), the processor "
    "automatically falls back to the direct (inline) pipeline so jobs never get stuck.")
doc.add_paragraph("Workflow ID format: docconv-{job_id} (e.g. docconv-a1b2c3d4e5f6)")

doc.add_heading("10.3  Document-Type Child Workflows",level=2)
doc.add_paragraph("Each document type has a dedicated child workflow that wraps a single conversion "
    "activity. This gives per-type visibility in the Temporal UI and allows type-specific retry "
    "policies or timeout tuning.")
tbl(["Document Type","Child Workflow","Activity Name"],[
    ["PDF","PDFConversionWorkflow","convert_pdf"],
    ["DOCX","DOCXConversionWorkflow","convert_docx"],
    ["XLSX / CSV","XLSXConversionWorkflow","convert_xlsx"],
    ["PPTX","PPTXConversionWorkflow","convert_pptx"],
    ["HTML","HTMLConversionWorkflow","convert_html"],
    ["RTF","RTFConversionWorkflow","convert_rtf"],
    ["ODT","ODTConversionWorkflow","convert_odt"],
    ["TXT","TXTConversionWorkflow","convert_txt"],
    ["Image (OCR)","ImageConversionWorkflow","convert_image"],
])
doc.add_paragraph("The child workflow ID format is: docconv-convert-{job_id}")

doc.add_heading("10.4  Activities",level=2)
doc.add_paragraph("Activities are the individual, retryable steps executed by the Temporal worker. "
    "There are 12 activities registered:")
tbl(["Activity","Module","Description"],[
    ["fetch_document","activities.py","Download source file to local tmp (S3/URL/FTP)"],
    ["convert_pdf","activities.py","PDF text extraction + embedded image OCR"],
    ["convert_docx","activities.py","DOCX paragraph + table extraction"],
    ["convert_xlsx","activities.py","XLSX/CSV spreadsheet extraction"],
    ["convert_pptx","activities.py","PPTX slide text + speaker notes"],
    ["convert_html","activities.py","HTML tag stripping"],
    ["convert_rtf","activities.py","RTF control word stripping"],
    ["convert_odt","activities.py","OpenDocument text extraction"],
    ["convert_txt","activities.py","Plain text with encoding detection"],
    ["convert_image","activities.py","Image OCR via Tesseract"],
    ["upload_text","activities.py","Upload converted text to S3"],
    ["cleanup_temp_files","activities.py","Remove temporary files"],
])
doc.add_paragraph("Every activity sends heartbeats during long operations (every 10 chunks for "
    "converters, at key checkpoints for fetch/upload). The heartbeat timeout is 120 seconds – "
    "if the Temporal server doesn't receive a heartbeat within that window, it considers the "
    "worker dead and reschedules the activity on another worker.")
doc.add_paragraph("Retry policy: exponential backoff starting at 5 seconds, doubling up to 60 seconds, "
    "with a maximum of TEMPORAL_RETRY_MAX_ATTEMPTS (default 3) attempts per activity.")

doc.add_heading("10.5  Batch Processing",level=2)
doc.add_paragraph("The BatchConversionWorkflow accepts a list of ConversionWorkflowInput objects "
    "and launches them as parallel child workflows. Each child runs independently with its own "
    "retry logic. The batch workflow provides a queryable progress counter.")
code('# Start a batch workflow\nhandle = await client.start_workflow(\n'
     '    "BatchConversionWorkflow",\n'
     '    [input1, input2, input3],\n'
     '    id="batch-001",\n'
     '    task_queue="docconv-tasks")\n\n'
     '# Query progress\nprogress = await handle.query("get_batch_progress")\n'
     '# {"total": 3, "completed": 2, "failed": 0}')

doc.add_heading("10.6  The Temporal Worker",level=2)
doc.add_paragraph("The worker (worker.py) runs in a daemon thread alongside the API and bus listeners. "
    "It registers all 11+ workflows and 12 activities, connects to the Temporal server with "
    "automatic retry (30 attempts, 3-second intervals), and polls the docconv-tasks queue for work.")
doc.add_paragraph("To run the worker separately (e.g. on a dedicated host), set ENABLE_API=false, "
    "ENABLE_SQS=false, ENABLE_RABBITMQ=false, ENABLE_KAFKA=false, ENABLE_TEMPORAL=true.")

doc.add_heading("10.7  Temporal Web UI",level=2)
doc.add_paragraph("The Temporal Web UI is available at http://localhost:8088 and provides:")
for f in [
    "Workflow list with filtering by status, type, and ID",
    "Detailed execution history for each workflow showing every activity attempt",
    "Visual timeline of workflow execution with durations",
    "Query panel to run get_status and get_step queries on running workflows",
    "Signal panel to send cancel signals to running workflows",
    "Stack trace view for debugging failed activities",
]: bullet(f)

doc.add_heading("10.8  Workflow API Endpoints",level=2)
doc.add_paragraph("Three REST endpoints interact with Temporal workflows:")
code("GET  /workflow/{workflow_id}/status  – Query current state\n"
     "POST /workflow/{workflow_id}/cancel  – Send cancellation signal\n"
     "GET  /workflows/recent?limit=20     – List recent workflows")
doc.add_paragraph("The workflow_id follows the format docconv-{job_id}. For example, if you submit "
    "a job with job_id='abc123', query status at /workflow/docconv-abc123/status.")

doc.add_heading("10.9  Execution Modes",level=2)
doc.add_paragraph("The service supports two execution modes, controlled by environment variables:")
tbl(["Setting","Behavior"],[
    ["USE_TEMPORAL_WORKFLOWS=true","All jobs route through Temporal. Full durability, retries, and visibility."],
    ["USE_TEMPORAL_WORKFLOWS=false","Jobs process inline (direct pipeline). Faster for dev/testing."],
    ["ENABLE_TEMPORAL=false","Temporal worker doesn't start. All jobs use direct pipeline regardless of USE_TEMPORAL_WORKFLOWS."],
    ["Temporal server down","Automatic fallback to direct pipeline with a warning log."],
])

doc.add_heading("10.10  Starting Workflows from Python",level=2)
doc.add_paragraph("You can start workflows directly from Python code using the client helper:")
code('from app.workflows.client import start_conversion_workflow_sync\n'
     'from app.models import ConversionJob\n\n'
     'job = ConversionJob(\n'
     '    job_id="my-job-001",\n'
     '    document_type="pdf",\n'
     '    location_type="s3",\n'
     '    s3_bucket="docconv-input",\n'
     '    s3_key="docs/report.pdf",\n'
     ')\n\nresult = start_conversion_workflow_sync(job)\n'
     'print(f"Success: {result.success}")\n'
     'print(f"Output: s3://{result.output_bucket}/{result.output_key}")')
doc.add_paragraph("For async code, use start_conversion_workflow() instead.")

# ═══════════════════════════ 11. CONVERTERS ══════════════════════════════════
doc.add_page_break()
doc.add_heading("11. Document Converters",level=1)
doc.add_paragraph("Each converter is a standalone Python module yielding text chunks via generators.")
for title,desc in [
    ("PDF (pdf_converter.py)",
     "Extracts selectable text via pdfplumber page-by-page. Falls back to full-page OCR for "
     "scanned pages. Extracts and OCRs embedded images tagged as [IMAGE TEXT]."),
    ("DOCX (docx_converter.py)",
     "Reads paragraphs in batches of 50 using python-docx. Extracts table content with cell delimiters."),
    ("XLSX / CSV (xlsx_converter.py)",
     "XLSX: reads each sheet with openpyxl in read-only mode, 200 rows per batch. CSV: stdlib csv module."),
    ("PPTX (pptx_converter.py)",
     "Reads slide shapes (text frames + tables) and speaker notes. One slide per yield."),
    ("HTML (html_converter.py)","Strips script/style tags via BeautifulSoup + lxml. Chunks by size."),
    ("RTF (rtf_converter.py)","Strips RTF control words via striprtf. Chunks by size."),
    ("ODT (odt_converter.py)","Reads OpenDocument paragraphs via odfpy. 50 paragraphs per batch."),
    ("TXT (text_converter.py)","Detects encoding via chardet, reads in CHUNK_SIZE chunks."),
]:
    doc.add_heading(title,level=3); doc.add_paragraph(desc)

# ═══════════════════════════ 12. IMAGE OCR ═══════════════════════════════════
doc.add_heading("12. Image OCR",level=1)
doc.add_paragraph("Handles JPEG, PNG, TIFF (multi-frame), BMP, WEBP via Pillow + Tesseract. "
    "Down-scales images >4000px. Converts to RGB if needed. PDF converter also extracts and OCRs embedded images.")

# ═══════════════════════════ 13. FETCHERS ════════════════════════════════════
doc.add_heading("13. File Fetchers (S3, URL, FTP)",level=1)
doc.add_paragraph("Each fetcher streams to a local tmp file in CHUNK_SIZE chunks using generators.")
for title,points in [
    ("S3 Fetcher",["Uses boto3 streaming","Supports custom endpoint URLs for LocalStack/MinIO"]),
    ("URL Fetcher",["requests with stream=True","Supports none/basic/bearer auth","120s timeout"]),
    ("FTP Fetcher",["stdlib ftplib retrbinary","Supports anonymous and authenticated access"]),
]:
    doc.add_heading(title,level=3)
    for pt in points: bullet(pt)

# ═══════════════════════════ 14. OUTPUT ══════════════════════════════════════
doc.add_heading("14. Output Storage (S3)",level=1)
doc.add_paragraph("Text chunks write to a local tmp file, then upload to S3. Default path:")
code("s3://{S3_OUTPUT_BUCKET}/converted/{job_id}.txt")
doc.add_heading("Checking Output",level=3)
code('aws --endpoint-url=http://localhost:4566 s3 ls s3://docconv-output/converted/ --recursive\n'
     'aws --endpoint-url=http://localhost:4566 s3 cp s3://docconv-output/converted/JOB_ID.txt -')

# ═══════════════════════════ 15. MEMORY ══════════════════════════════════════
doc.add_heading("15. Memory Efficiency & Streaming",level=1)
for b,t in [
    ("Fetchers: ","Stream to disk in CHUNK_SIZE chunks via generators. Auto-deleted after processing."),
    ("Converters: ","Yield text one page/chunk at a time. Never buffer full text in memory."),
    ("Upload: ","Writes chunks to a tmp file, then uploads to S3. No full-text buffering."),
    ("PDF images: ","Rendered to tmp PNG files for OCR, deleted immediately after each page."),
    ("API uploads: ","Streamed to disk in chunks from the HTTP request body."),
    ("Temporal: ","Activities use the same generators. Files persist across activity boundaries via durable tmp paths."),
]: bullet(t,b)

# ═══════════════════════════ 16. TESTING ═════════════════════════════════════
doc.add_page_break()
doc.add_heading("16. Testing",level=1)
doc.add_heading("Running the Integration Test Suite",level=3)
code("cd docconv-service\npip install -r requirements.txt reportlab httpx temporalio\npython -m tests.test_full_flow")
doc.add_heading("What the Tests Cover (48 tests)",level=3)
tbl(["Section","Count","Description"],[
    ["Sample Generation","10","Creates sample files for every format"],
    ["Converter Unit Tests","10","Tests each converter module individually"],
    ["Dispatcher Tests","10","Verifies DocumentType → converter routing"],
    ["Pipeline Tests","10","End-to-end: file → convert → output"],
    ["Model Validation","4","Pydantic schema validation and rejection"],
    ["REST API Tests","7","Health, upload (5 formats), validation"],
    ["Temporal Tests","7","Dataclasses, input/output mapping, registries, fallback"],
])

# ═══════════════════════════ 17. TROUBLESHOOTING ═════════════════════════════
doc.add_heading("17. Troubleshooting",level=1)
for title,sol in [
    ("Services fail to start",
     'Run "docker compose logs <service>". Ensure ports 4566, 5672, 7233, 8080, 8088, 9092 '
     'are free. Increase Docker memory to 8 GB.'),
    ("Temporal server takes long to start",
     "The temporal-server container runs auto-setup which creates the database schema on first boot. "
     "This can take 30-40 seconds. The healthcheck has a 40-second start_period for this reason."),
    ("Temporal worker says 'Could not connect'",
     "The worker retries 30 times with 3-second intervals. Ensure temporal-server is healthy: "
     "docker compose logs temporal-server. The Temporal gRPC port is 7233."),
    ("Workflow shows FAILED in Temporal UI",
     "Click the workflow ID to see the full execution history. Each activity shows its "
     "input, output, and error stack trace. Check which activity failed and its retry count."),
    ("SQS listener says 'queue not found'",
     "LocalStack may still be initializing. Check that init-localstack.sh is executable."),
    ("OCR returns empty text",
     "Ensure tesseract-ocr is installed in the Docker image (it is by default). Check image quality."),
    ("PDF conversion is slow",
     "Full-page OCR renders at 200 DPI per page. Selectable-text PDFs are fast (no OCR)."),
    ("Upload fails with 'Connection refused'",
     "The S3 upload targets LocalStack. Check: curl http://localhost:4566/_localstack/health"),
    ("RabbitMQ connection refused",
     "Auto-retries every 5 seconds. RabbitMQ may take 10-15 seconds to start."),
    ("Kafka consumer not receiving messages",
     "Verify auto-topic creation is enabled. Check bootstrap server address."),
    ("API Test Console shows 'Disconnected'",
     "Click 'Test Connection'. If Docker runs in a VM, use the VM's IP instead of localhost."),
    ("Temporal fallback keeps triggering",
     "Check TEMPORAL_HOST points to the correct address. Inside Docker it should be "
     "temporal-server:7233. From the host it should be localhost:7233."),
]:
    doc.add_heading(title,level=3); doc.add_paragraph(sol)

# ═══════════════════════════ 18. CURL EXAMPLES ═══════════════════════════════
doc.add_page_break()
doc.add_heading("18. curl Examples Cookbook",level=1)
for title,cmd in [
    ("Health check","curl http://localhost:8080/health"),
    ("Upload a PDF",'curl -X POST http://localhost:8080/convert/upload \\\n  -F "file=@document.pdf" -F "document_type=pdf"'),
    ("Upload an image for OCR",'curl -X POST http://localhost:8080/convert/upload \\\n  -F "file=@scan.png" -F "document_type=image"'),
    ("Upload DOCX with custom output key",'curl -X POST http://localhost:8080/convert/upload \\\n  -F "file=@report.docx" -F "document_type=docx" \\\n  -F "output_s3_key=reports/2025/q1.txt"'),
    ("Convert from URL",'curl -X POST http://localhost:8080/convert/job \\\n  -H "Content-Type: application/json" \\\n  -d \'{"document_type":"html","location_type":"url","url":"https://example.com"}\''),
    ("Convert from URL with Basic auth",'curl -X POST http://localhost:8080/convert/job \\\n  -H "Content-Type: application/json" \\\n  -d \'{"document_type":"pdf","location_type":"url",\n       "url":"https://secure.example.com/doc.pdf",\n       "auth_type":"basic","auth_username":"user","auth_password":"pass"}\''),
    ("Convert from S3 (LocalStack)",'curl -X POST http://localhost:8080/convert/job \\\n  -H "Content-Type: application/json" \\\n  -d \'{"document_type":"pdf","location_type":"s3",\n       "s3_bucket":"docconv-input","s3_key":"docs/report.pdf",\n       "s3_endpoint_url":"http://localstack:4566"}\''),
    ("Convert from FTP",'curl -X POST http://localhost:8080/convert/job \\\n  -H "Content-Type: application/json" \\\n  -d \'{"document_type":"txt","location_type":"ftp",\n       "ftp_host":"ftp","ftp_path":"/data/file.txt",\n       "ftp_user":"docconv","ftp_pass":"docconv"}\''),
    ("Query Temporal workflow status","curl http://localhost:8080/workflow/docconv-abc123/status"),
    ("Cancel a running Temporal workflow","curl -X POST http://localhost:8080/workflow/docconv-abc123/cancel"),
    ("List recent Temporal workflows","curl http://localhost:8080/workflows/recent?limit=10"),
    ("List converted output files",'aws --endpoint-url=http://localhost:4566 s3 ls \\\n  s3://docconv-output/converted/ --recursive'),
    ("Download and view converted text",'aws --endpoint-url=http://localhost:4566 s3 cp \\\n  s3://docconv-output/converted/JOB_ID.txt -'),
]:
    doc.add_heading(title,level=3); code(cmd)

# ── Save ─────────────────────────────────────────────────
output_path = "/home/claude/docconv-service/DocConv_User_Guide.docx"
doc.save(output_path)
print(f"User guide saved to {output_path}")
