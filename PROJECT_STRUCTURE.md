# NLP2CMD Project Structure

```
nlp2cmd/
│
├── README.md                    # Główna dokumentacja projektu
├── QUICKSTART.md                # Szybki start guide
├── CHANGELOG.md                 # Historia zmian
├── CONTRIBUTING.md              # Guide dla kontrybutorów
├── LICENSE                      # Licencja MIT
├── setup.py                     # Instalacja pakietu
├── requirements.txt             # Zależności produkcyjne
├── requirements-dev.txt         # Zależności deweloperskie
├── Makefile                     # Automation tasks
├── nlp2cmd.yaml                 # Przykładowa konfiguracja
├── .gitignore                   # Git ignore rules
├── demo.py                      # Kompletne demo frameworka
│
├── nlp2cmd/                     # Główny pakiet
│   ├── __init__.py              # Package exports
│   ├── cli.py                   # CLI interface
│   │
│   ├── core/                    # Podstawowa funkcjonalność
│   │   ├── __init__.py
│   │   ├── base.py              # BaseConverter, ConversionResult
│   │   ├── model.py             # ModelWrapper dla LLM
│   │   └── pipeline.py          # Pipeline system
│   │
│   ├── converters/              # Konwertery
│   │   ├── __init__.py
│   │   ├── text2env.py          # .env file management
│   │   ├── text2bash.py         # Bash script generation
│   │   ├── text2makefile.py     # Makefile execution
│   │   └── text2docker.py       # Docker management
│   │
│   └── utils/                   # Narzędzia pomocnicze
│       ├── __init__.py
│       ├── parsers.py           # Parsery formatów
│       └── validators.py        # Walidatory bezpieczeństwa
│
├── examples/                    # Przykłady użycia
│   ├── basic_usage.py           # Podstawowe przykłady
│   ├── advanced_llm.py          # Zaawansowane użycie z LLM
│   └── pipeline-example.yaml   # Przykładowe pipeline'y
│
├── tests/                       # Testy
│   └── test_nlp2cmd.py          # Testy jednostkowe i integracyjne
│
└── docs/                        # Dokumentacja (placeholder)
    └── (future documentation)
```

## Struktura modułów

### Core (`nlp2cmd/core/`)
- **base.py**: Bazowa klasa `BaseConverter` dla wszystkich konwerterów
- **model.py**: `ModelWrapper` - wrapper dla modeli HuggingFace
- **pipeline.py**: `Pipeline` - system łączenia wielu konwerterów

### Converters (`nlp2cmd/converters/`)
- **text2env.py**: Zarządzanie plikami .env przez NLP
- **text2bash.py**: Generowanie i wykonywanie bash scripts
- **text2makefile.py**: Uruchamianie Make targets
- **text2docker.py**: Zarządzanie kontenerami Docker

### Utils (`nlp2cmd/utils/`)
- **parsers.py**: Parsery dla .env, Makefile, Dockerfile, etc.
- **validators.py**: Walidatory bezpieczeństwa i sanitizery

## Główne pliki

### Dokumentacja
- **README.md**: Kompletna dokumentacja z przykładami
- **QUICKSTART.md**: Szybki start guide
- **CHANGELOG.md**: Historia zmian i release notes
- **CONTRIBUTING.md**: Guide dla kontrybutorów

### Konfiguracja
- **setup.py**: Definicja pakietu i dependencies
- **requirements.txt**: Zależności produkcyjne
- **requirements-dev.txt**: Zależności deweloperskie
- **nlp2cmd.yaml**: Przykładowy plik konfiguracyjny
- **Makefile**: Automation tasks (build, test, lint, etc.)

### Przykłady i testy
- **demo.py**: Kompleksowe demo wszystkich funkcji
- **examples/**: Katalog z przykładami użycia
- **tests/**: Testy jednostkowe i integracyjne

## Statystyki

- **Pliki Python**: 18
- **Linie kodu**: ~3500+
- **Moduły**: 4 główne konwertery
- **Testy**: Kompleksowe unit + integration tests
- **Dokumentacja**: 6 plików markdown

## Kluczowe cechy architektury

1. **Modularność**: Każdy konwerter jest niezależny
2. **Rozszerzalność**: Łatwe dodawanie nowych konwerterów
3. **Bezpieczeństwo**: Wbudowane walidatory i safe mode
4. **Pipeline**: System łączenia operacji
5. **LLM Integration**: Wsparcie dla małych modeli (1-3B)
6. **Type Safety**: Pydantic models dla walidacji
7. **Testability**: Kompleksowe testy
8. **Documentation**: Szczegółowa dokumentacja

## Dependencies

### Production
- transformers >= 4.30.0
- torch >= 2.0.0
- pydantic >= 2.0.0
- python-dotenv >= 1.0.0
- pyyaml >= 6.0

### Development
- pytest >= 7.0
- black >= 23.0
- flake8 >= 6.0
- mypy >= 1.0

## Supported Python Versions

- Python 3.8+
- Python 3.9
- Python 3.10
- Python 3.11
