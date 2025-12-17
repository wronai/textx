# NLP2CMD Web Frontend

Interaktywny frontend HTML do generowania kodu HTML za pomocą NLP2CMD Text4 API.

## Funkcje

- **Generowanie HTML** - Wpisz opis w języku naturalnym, otrzymaj gotowy HTML
- **Podgląd w czasie rzeczywistym** - Preview wygenerowanego HTML
- **Wybór szablonów** - Landing page, formularz, tabela, karta, strona
- **Pipeline** - Wielokrokowe przetwarzanie (generuj → waliduj)
- **WebSocket** - Streaming w czasie rzeczywistym
- **Export** - Kopiuj lub pobierz wygenerowany HTML

## Uruchomienie

### Z docker-compose (zalecane)

```bash
# Uruchom frontend + API razem
docker-compose up -d

# Frontend dostępny na: http://localhost:8080
# API dostępne na: http://localhost:8000
```

### Tylko frontend (wymaga działającego API)

```bash
docker build -t nlp2cmd-web .
docker run -p 8080:80 nlp2cmd-web
```

## Architektura

```
┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│  NLP2CMD API    │
│   (nginx:80)    │     │  (FastAPI:8000) │
│   port: 8080    │     │  port: 8000     │
└─────────────────┘     └─────────────────┘
         │                      │
         └──────────────────────┘
              Docker Network
```

## Użycie

1. **Otwórz** http://localhost:8080
2. **Wybierz szablon** (Landing, Form, Table, Card, Page)
3. **Wpisz polecenie** np. "generate landing page title: My Product"
4. **Kliknij Generate** lub **Pipeline**
5. **Podejrzyj wynik** w zakładce Preview/Code/Metadata
6. **Eksportuj** - Copy lub Download

## Przykłady poleceń

| Polecenie | Rezultat |
|-----------|----------|
| `generate landing page title: CloudSync` | Landing page z hero section |
| `generate form for contact` | Formularz kontaktowy |
| `generate table` | Tabela z przykładowymi danymi |
| `generate card` | Komponent karty |
| `generate page title: About Us` | Prosta strona HTML |

## Integracja

Frontend proxy'uje żądania do API przez nginx:
- `/api/*` → `http://nlp2cmd-api:8000/api/*`
- `/health` → `http://nlp2cmd-api:8000/health`
- `/ws/` → WebSocket do streaming

## Środowisko

- Nginx Alpine
- Port: 8080 (frontend), 8000 (API)
- Docker Network: nlp2cmd-network
