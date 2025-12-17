# NLP2CMD Docker Examples

Przykłady użycia NLP2CMD jako usług Docker zgodnie z architekturą opisaną w `TODO/MESH_ARCHITECTURE.md`.

## Struktura

```
├── 1/                      # NLP2CMD API Service (text4 backend)
│   ├── app.py              # FastAPI application
│   ├── Dockerfile          # Simplified Dockerfile
│   ├── Dockerfile.full     # Full Dockerfile (includes nlp2cmd)
│   ├── docker-compose.yml  # Standalone compose
│   ├── requirements.txt    # Python dependencies
│   ├── README.md           # Service documentation
│   └── output/             # Generated files output
│
├── 2/                      # Web Frontend Service
│   ├── index.html          # Interactive HTML generator UI
│   ├── Dockerfile          # Nginx Dockerfile
│   ├── nginx.conf          # Nginx configuration
│   ├── docker-compose.yml  # Compose with API dependency
│   └── README.md           # Frontend documentation
│
└── docker-compose.yml      # Main compose (both services)
```

## Szybki start

```bash
# Uruchom oba serwisy
cd /home/tom/github/wronai/textx
docker-compose up -d

# Sprawdź status
docker-compose ps

# Otwórz w przeglądarce:
# - Frontend: http://localhost:8081
# - API:      http://localhost:8001
# - Demo:     http://localhost:8001/demo
```

## Usługi

### 1. NLP2CMD API (`./1/`)

Backend REST API z konwerterami text2X/text3X/text4X:

| Endpoint | Opis |
|----------|------|
| `GET /` | Info o usłudze |
| `GET /health` | Health check |
| `GET /api/v1/converters` | Lista konwerterów |
| `POST /api/v1/convert/text3html` | Generowanie HTML |
| `POST /api/v1/convert/text2html` | Analiza HTML |
| `POST /api/v1/pipeline` | Pipeline przetwarzania |
| `WS /api/v1/stream` | WebSocket streaming |
| `GET /demo` | Demo page |

### 2. Web Frontend (`./2/`)

Interaktywny interfejs użytkownika:

- Wybór szablonów (landing, form, table, card, page)
- Input w języku naturalnym
- Podgląd HTML w czasie rzeczywistym
- Pipeline (generuj → waliduj)
- Export (copy/download)

## Przykłady API

### Generowanie Landing Page

```bash
curl -X POST http://localhost:8001/api/v1/convert/text3html \
  -H "Content-Type: application/json" \
  -d '{"command": "generate landing page title: CloudSync"}'
```

### Generowanie formularza

```bash
curl -X POST http://localhost:8001/api/v1/convert/text3html \
  -H "Content-Type: application/json" \
  -d '{"command": "generate form for contact"}'
```

### Analiza SEO

```bash
curl -X POST http://localhost:8001/api/v1/convert/text2html \
  -H "Content-Type: application/json" \
  -d '{
    "command": "seo analysis",
    "html_content": "<!DOCTYPE html><html><head><title>Test</title></head><body><h1>Hello</h1></body></html>"
  }'
```

### Pipeline

```bash
curl -X POST http://localhost:8001/api/v1/pipeline \
  -H "Content-Type: application/json" \
  -d '{
    "name": "generate-and-validate",
    "steps": [
      {"converter": "text3html", "command": "generate landing page title: My App"},
      {"converter": "text2html", "command": "validate"}
    ]
  }'
```

### WebSocket (JavaScript)

```javascript
const ws = new WebSocket('ws://localhost:8001/api/v1/stream');

ws.onopen = () => {
    ws.send(JSON.stringify({
        action: 'generate',
        command: 'generate landing page title: CloudSync'
    }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Generated:', data.output);
};
```

### Python SDK

```python
from nlp2cmd.mesh.sdk import MeshClient

# Synchronous
client = MeshClient("http://localhost:8001")
result = client.convert("text3html", "generate landing page")

# Async
async with MeshClient("http://localhost:8001") as client:
    result = await client.convert_async("text3html", "generate landing page")

# Pipeline
result = client.pipeline([
    {"converter": "text3html", "command": "generate page"},
    {"action": "deploy", "config": {"target": "file", "path": "/var/www/page.html"}}
])
```

## Architektura

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Docker Network                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌─────────────────┐         ┌─────────────────┐                   │
│   │  Web Frontend   │────────▶│  NLP2CMD API    │                   │
│   │  (nginx:80)     │  HTTP   │  (FastAPI:8000) │                   │
│   │  Port: 8080     │  WS     │  Port: 8000     │                   │
│   └─────────────────┘         └─────────────────┘                   │
│           │                           │                              │
│           │                           ▼                              │
│           │                   ┌─────────────────┐                   │
│           │                   │   Converters    │                   │
│           │                   │  text2html      │                   │
│           │                   │  text3html      │                   │
│           │                   │  text4html      │                   │
│           │                   └─────────────────┘                   │
│           │                           │                              │
│           ▼                           ▼                              │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                      Output Volume                           │   │
│   │                    ./1/output/                               │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Komendy Docker

```bash
# Uruchom
docker-compose up -d

# Zatrzymaj
docker-compose down

# Logi
docker-compose logs -f
docker-compose logs -f nlp2cmd-api
docker-compose logs -f web-frontend

# Rebuild
docker-compose build --no-cache
docker-compose up -d --build

# Status
docker-compose ps

# Shell do kontenera
docker exec -it nlp2cmd-text4-api bash
docker exec -it nlp2cmd-web-frontend sh
```

## Rozszerzenia

Zgodnie z `TODO/MESH_ARCHITECTURE.md`, architektura może być rozszerzona o:

1. **Message Bus** - NATS/Redis dla komunikacji między usługami
2. **Workers** - Skalowalne workery dla różnych konwerterów
3. **Service Registry** - Odkrywanie usług
4. **Deployer** - Automatyczny deployment wygenerowanego HTML
5. **Kubernetes** - Deployment w klastrze K8s

## Powiązane pliki

- `TODO/TODO.md` - Wymagania
- `TODO/MESH_ARCHITECTURE.md` - Architektura rozproszona
- `TODO/mesh_demo.py` - Demo architektury mesh
