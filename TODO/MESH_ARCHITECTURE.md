# NLP2CMD Mesh - Rozproszona Architektura Usług

## 🎯 Cel

System umożliwiający:
- Wywołanie dowolnego konwertera text2X/text3X/text4X z dowolnego języka
- Asynchroniczną komunikację między usługami (firmware → backend → frontend)
- Pipeline'y przetwarzania w locie
- Deployment wyników do dowolnego celu

---

## 🏗️ Architektura

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           NLP2CMD MESH                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        MESSAGE BUS (NATS/Redis)                       │   │
│  │   nlp2cmd.request.* │ nlp2cmd.result.* │ nlp2cmd.stream.* │ events  │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
│       ▲           ▲           ▲           ▲           ▲           ▲         │
│       │           │           │           │           │           │         │
│  ┌────┴────┐ ┌────┴────┐ ┌────┴────┐ ┌────┴────┐ ┌────┴────┐ ┌────┴────┐   │
│  │ Gateway │ │ Worker  │ │ Worker  │ │ Worker  │ │ Worker  │ │ Deployer│   │
│  │  API    │ │ text3X  │ │ text4X  │ │ text2X  │ │  DB     │ │ Service │   │
│  │REST/WS  │ │ (HTML)  │ │(Stream) │ │ (Parse) │ │(Schema) │ │(Deploy) │   │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘   │
│       ▲                                                           │         │
│       │                                                           ▼         │
│  ┌────┴────────────────────────────────────────────────────────────────┐   │
│  │                         CLIENT SDKs                                  │   │
│  │  Python │ JavaScript │ Go │ Rust │ C/C++ │ Java │ PHP │ Bash/CLI   │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                      INTEGRATION LAYER                                │   │
│  │  Firmware(ESP32) │ Backend(FastAPI) │ Database │ Frontend(React)     │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Komponenty

### 1. Message Bus (NATS/Redis Streams)

Centralna magistrala komunikacyjna:

```
Topics:
  nlp2cmd.request.{converter}     - żądania do konwerterów
  nlp2cmd.result.{request_id}     - wyniki
  nlp2cmd.stream.{session_id}     - streaming text4X
  nlp2cmd.deploy.{target}         - deployment
  nlp2cmd.events                  - eventy systemowe
```

### 2. Gateway API

Uniwersalny interfejs (REST, WebSocket, gRPC):

```
POST   /api/v1/convert           - jednorazowa konwersja
POST   /api/v1/pipeline          - pipeline wielu kroków
WS     /api/v1/stream            - streaming text4X
POST   /api/v1/deploy            - deployment wyniku
GET    /api/v1/converters        - lista dostępnych konwerterów
```

### 3. Workers

Skalowalne workery dla każdego typu konwertera:

```
nlp2cmd-worker-text3html
nlp2cmd-worker-text3markdown
nlp2cmd-worker-text4modbus
nlp2cmd-worker-database
nlp2cmd-worker-deployer
```

### 4. Client SDKs

Klienty w każdym języku:

```python
# Python
client.convert("text3html", "generate landing page")

// JavaScript
client.convert("text3html", "generate landing page")

// Go
client.Convert("text3html", "generate landing page")

// Rust
client.convert("text3html", "generate landing page").await

// C (firmware)
nlp2cmd_convert("text3html", "generate landing page")
```

---

## 📊 Message Protocol

### Request Message

```json
{
  "id": "req_abc123",
  "converter": "text3html",
  "command": "generate landing page for CloudSync",
  "context": {
    "project": "cloudync",
    "style": "modern"
  },
  "options": {
    "async": true,
    "timeout": 30,
    "callback_url": "https://api.example.com/webhook",
    "deploy_to": "s3://bucket/path"
  },
  "pipeline": [
    {"converter": "text3html", "command": "generate page"},
    {"converter": "text2html", "command": "validate"},
    {"action": "deploy", "target": "nginx"}
  ],
  "metadata": {
    "source": "backend",
    "user_id": "user123",
    "timestamp": "2024-12-17T12:00:00Z"
  }
}
```

### Result Message

```json
{
  "id": "res_xyz789",
  "request_id": "req_abc123",
  "status": "success",
  "converter": "text3html",
  "output": "<!DOCTYPE html>...",
  "metadata": {
    "lines": 68,
    "size_bytes": 2401,
    "execution_time_ms": 45
  },
  "deploy_result": {
    "url": "https://cdn.example.com/page.html",
    "status": "deployed"
  },
  "next_step": {
    "converter": "text2html",
    "command": "validate"
  }
}
```

### Stream Message (text4X)

```json
{
  "session_id": "stream_abc",
  "event_type": "data",
  "data": {
    "values": [25.5, 48.2],
    "timestamp": "2024-12-17T12:00:01Z"
  },
  "source": "text4modbus://192.168.1.100:502"
}
```

---

## 🔄 Pipeline Examples

### Example 1: Generate & Deploy HTML

```yaml
pipeline:
  - converter: text3html
    command: "generate landing page for CloudSync"
    
  - converter: text2html
    command: "validate seo"
    
  - action: deploy
    target: nginx
    path: /var/www/html/landing.html
    
  - action: notify
    webhook: https://slack.com/webhook
```

### Example 2: IoT Data → Dashboard → Deploy

```yaml
pipeline:
  # 1. Read from PLC
  - converter: text4modbus
    command: "stream holding registers 40001 count 10"
    duration: 60s
    
  # 2. Aggregate data
  - action: aggregate
    method: average
    window: 10s
    
  # 3. Generate SVG chart
  - converter: text3svg
    command: "generate bar chart from data"
    
  # 4. Embed in HTML dashboard
  - converter: text3html
    command: "generate dashboard with chart"
    
  # 5. Deploy to CDN
  - action: deploy
    target: s3
    bucket: dashboards
    
  # 6. Notify frontend via WebSocket
  - action: broadcast
    channel: dashboard-updates
```

### Example 3: Full Stack Generation

```yaml
pipeline:
  # Backend
  - converter: text3app
    command: "generate FastAPI for users CRUD"
    output: backend/
    
  # Database
  - converter: text3database
    command: "generate PostgreSQL schema users"
    output: database/
    
  # Frontend
  - converter: text3html
    command: "generate admin panel"
    output: frontend/
    
  # Docker
  - converter: text3docker
    command: "generate multi-stage for FastAPI"
    output: ./
    
  # Kubernetes
  - converter: text3kubernetes
    command: "generate deployment HA replicas 3"
    output: k8s/
    
  # Terraform
  - converter: text3terraform
    command: "generate AWS EKS cluster"
    output: terraform/
    
  # Deploy all
  - action: deploy
    target: kubernetes
    namespace: production
```

---

## 🌐 Integration Patterns

### Pattern 1: Firmware → Cloud

```
ESP32 (C) → MQTT → NLP2CMD Gateway → Process → Deploy
```

### Pattern 2: Backend Service

```
FastAPI → NLP2CMD Client → Message Bus → Workers → Result
```

### Pattern 3: Frontend Real-time

```
React → WebSocket → Gateway → text4X Stream → Live Updates
```

### Pattern 4: CI/CD Pipeline

```
GitHub Action → NLP2CMD CLI → Generate → Validate → Deploy
```

---

## 🚀 Deployment Options

### Option 1: Single Node (Docker Compose)

```yaml
services:
  nats:
    image: nats:latest
  gateway:
    image: nlp2cmd/gateway
  worker-html:
    image: nlp2cmd/worker-html
  worker-modbus:
    image: nlp2cmd/worker-modbus
```

### Option 2: Kubernetes Cluster

```yaml
# Horizontally scalable workers
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nlp2cmd-worker-html
spec:
  replicas: 5  # Scale based on load
```

### Option 3: Serverless (AWS Lambda)

```
API Gateway → Lambda (nlp2cmd) → S3/DynamoDB
```

---

## 📦 SDK Examples

See `nlp2cmd/mesh/sdk/` for implementations in:
- Python
- JavaScript/TypeScript
- Go
- Rust
- C (for firmware)
- Java
- PHP
- CLI (Bash)
