# NLP2CMD Text4 API Service

Usługa Docker z REST API do konwersji tekstu na HTML przy użyciu NLP2CMD.

## Funkcje

- **text2html** - Parsowanie i analiza HTML (SEO, walidacja, ekstrakcja)
- **text3html** - Generowanie HTML z opisu w języku naturalnym
- **text4html** - Streaming HTML w czasie rzeczywistym (WebSocket)

## Uruchomienie

```bash
# Z docker-compose (zalecane)
docker-compose up -d

# Lub bezpośrednio
docker build -t nlp2cmd-api -f Dockerfile.full ..
docker run -p 8000:8000 nlp2cmd-api
```

## API Endpoints

| Endpoint | Metoda | Opis |
|----------|--------|------|
| `/` | GET | Informacje o usłudze |
| `/health` | GET | Health check |
| `/api/v1/converters` | GET | Lista dostępnych konwerterów |
| `/api/v1/convert/text2html` | POST | Analiza HTML |
| `/api/v1/convert/text3html` | POST | Generowanie HTML |
| `/api/v1/pipeline` | POST | Wykonanie pipeline |
| `/api/v1/stream` | WebSocket | Streaming w czasie rzeczywistym |
| `/demo` | GET | Demo strona |

## Przykłady użycia

### Generowanie Landing Page

```bash
curl -X POST http://localhost:8001/api/v1/convert/text3html \
  -H "Content-Type: application/json" \
  -d '{"command": "generate landing page title: My Product"}'
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

### Pipeline (generuj + waliduj)

```bash
curl -X POST http://localhost:8001/api/v1/pipeline \
  -H "Content-Type: application/json" \
  -d '{
    "name": "generate-and-validate",
    "steps": [
      {"converter": "text3html", "command": "generate landing page"},
      {"converter": "text2html", "command": "validate"}
    ]
  }'
```

### WebSocket Streaming

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
    console.log('Generated HTML:', data.output);
};
```

## Środowisko

- Python 3.11
- FastAPI
- Uvicorn
- Port: 8000

## Integracja z frontendem

Ta usługa jest przeznaczona do współpracy z usługą frontendową w folderze `../2/`.
Obie usługi można uruchomić razem używając głównego `docker-compose.yml`.
