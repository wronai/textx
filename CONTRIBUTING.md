# Contributing to NLP2CMD

Dziękujemy za zainteresowanie rozwojem NLP2CMD! 🎉

## 🤝 Jak mogę pomóc?

### Zgłaszanie błędów

1. Sprawdź czy błąd nie został już zgłoszony w [Issues](https://github.com/softreck/nlp2cmd/issues)
2. Stwórz nowy issue z:
   - Opisem problemu
   - Krokami do reprodukcji
   - Oczekiwanym zachowaniem
   - Wersją Pythona i systemu operacyjnego
   - Przykładowym kodem

### Propozycje funkcji

1. Otwórz issue z tagiem `enhancement`
2. Opisz:
   - Problem który rozwiązuje funkcja
   - Proponowane rozwiązanie
   - Alternatywne podejścia
   - Dodatkowy kontekst

### Pull Requests

1. Fork repozytorium
2. Stwórz branch dla swojej funkcji: `git checkout -b feature/amazing-feature`
3. Wprowadź zmiany
4. Dodaj testy
5. Uruchom linter i testy
6. Commit: `git commit -m 'Add amazing feature'`
7. Push: `git push origin feature/amazing-feature`
8. Otwórz Pull Request

## 💻 Development Setup

```bash
# Klonowanie
git clone https://github.com/softreck/nlp2cmd.git
cd nlp2cmd

# Instalacja w trybie dev
pip install -e ".[dev]"

# Uruchom testy
pytest tests/ -v

# Formatowanie
black nlp2cmd/ tests/
isort nlp2cmd/ tests/

# Linting
flake8 nlp2cmd/ tests/
mypy nlp2cmd/
```

## 📝 Coding Standards

### Style Guide

- Używamy [Black](https://black.readthedocs.io/) do formatowania kodu
- PEP 8 jako podstawa
- Maksymalna długość linii: 100 znaków
- Docstringi w stylu Google

### Type Hints

```python
def parse_intent(self, text: str) -> Dict[str, Any]:
    """
    Parsuje intencję użytkownika.
    
    Args:
        text: Komenda w języku naturalnym
        
    Returns:
        Dict z rozparsowaną intencją
    """
    pass
```

### Tests

- Każda nowa funkcja wymaga testów
- Minimum 80% code coverage
- Używamy pytest

```python
def test_parse_command():
    """Test parsowania komendy"""
    parser = Parser()
    result = parser.parse("test command")
    assert result["action"] == "test"
```

## 🏗️ Architektura

### Dodawanie nowego konwertera

1. Stwórz klasę dziedziczącą z `BaseConverter`:

```python
from nlp2cmd.core.base import BaseConverter, ConversionResult

class Text2YourTool(BaseConverter):
    def parse_intent(self, text: str) -> Dict[str, Any]:
        # Implementacja
        pass
    
    def generate_command(self, intent: Dict[str, Any]) -> str:
        # Implementacja
        pass
    
    def execute(self, text: str) -> ConversionResult:
        # Implementacja
        pass
```

2. Dodaj testy w `tests/test_your_tool.py`
3. Zaktualizuj dokumentację
4. Dodaj przykłady użycia

### Struktura projektu

```
nlp2cmd/
├── nlp2cmd/
│   ├── core/          # Podstawowa funkcjonalność
│   ├── converters/    # Konwertery (text2env, text2bash, etc.)
│   └── utils/         # Narzędzia pomocnicze
├── tests/             # Testy
├── examples/          # Przykłady użycia
└── docs/              # Dokumentacja
```

## 🔍 Code Review Process

1. Wszystkie PR wymagają review
2. Testy muszą przechodzić
3. Code coverage nie może spaść
4. Dokumentacja musi być aktualna

## 📚 Dokumentacja

### Docstrings

```python
def function(param1: str, param2: int) -> bool:
    """
    Krótki opis funkcji.
    
    Dłuższy opis funkcji jeśli potrzebny.
    
    Args:
        param1: Opis pierwszego parametru
        param2: Opis drugiego parametru
        
    Returns:
        Opis zwracanej wartości
        
    Raises:
        ValueError: Kiedy wartość jest nieprawidłowa
        
    Example:
        >>> function("test", 42)
        True
    """
    pass
```

### README

- Aktualizuj README.md przy dodawaniu funkcji
- Dodaj przykłady użycia
- Zaktualizuj listę funkcji

## 🐛 Debugging Tips

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Wszystkie operacje będą szczegółowo logowane
```

## 🌍 Internacjonalizacja

- Framework wspiera polskie i angielskie komendy
- Dodając nowe patterny, dodaj wersje w obu językach:

```python
PATTERNS = {
    "action": [
        r"zrób coś|do something",
        r"wykonaj|execute",
    ]
}
```

## 🏷️ Versioning

Używamy [Semantic Versioning](https://semver.org/):
- MAJOR: Breaking changes
- MINOR: Nowe funkcje (backward compatible)
- PATCH: Bug fixes

## 📜 License

Zgłaszając kod, zgadzasz się na licencję MIT.

## ❓ Questions?

- Otwórz issue z tagiem `question`
- Email: info@softreck.com
- Discord: [coming soon]

## 🙏 Podziękowania

Dziękujemy wszystkim kontrybutom:
- Bug reports
- Feature requests
- Code contributions
- Documentation improvements
- Feedback

Każdy wkład jest ważny! 💚
