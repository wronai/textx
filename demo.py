#!/usr/bin/env python3
"""
NLP2CMD - Kompletne demo wszystkich możliwości frameworka.

Ten skrypt demonstruje wszystkie główne funkcje biblioteki NLP2CMD.
"""

import sys


def print_header(title: str):
    """Wyświetla nagłówek sekcji"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def demo_intro():
    """Wprowadzenie"""
    print_header("🚀 NLP2CMD Framework - Complete Demo")
    
    print("""
NLP2CMD to lekki framework w Pythonie do konwersji języka naturalnego
na komendy, konfiguracje i kod przy użyciu małych modeli LLM (do 3B).

Główne możliwości:
  ✓ text2env     - Zarządzanie plikami .env
  ✓ text2bash    - Generowanie skryptów bash
  ✓ text2makefile - Uruchamianie komend make
  ✓ text2docker  - Zarządzanie kontenerami Docker
  ✓ Pipeline     - Łączenie wielu modułów

Obsługiwane modele:
  • Phi-2 (2.7B)         - microsoft/phi-2
  • TinyLlama (1.1B)     - TinyLlama/TinyLlama-1.1B-Chat-v1.0
  • Bielik (7B)          - speakleash/Bielik-7B-v0.1 [Polski]
  • Phi-1.5 (1.3B)       - microsoft/phi-1_5
    """)


def demo_features():
    """Demonstracja funkcji"""
    print_header("📋 Główne funkcje")
    
    features = [
        ("🔧 Text2Env", "Naturalne komendy do zarządzania .env", [
            "ustaw PORT na 8080",
            "dodaj DATABASE_URL z wartością postgres://localhost/mydb",
            "zmień DEBUG na true",
            "usuń SECRET_KEY"
        ]),
        ("⚙️ Text2Bash", "Generowanie i wykonywanie skryptów bash", [
            "pokaż wszystkie pliki",
            "znajdź pliki txt większe niż 1MB",
            "skopiuj wszystkie obrazy jpg do folderu backup",
            "zlicz linie kodu we wszystkich plikach python"
        ]),
        ("🔨 Text2Makefile", "Inteligentne uruchamianie Make", [
            "zbuduj aplikację",
            "uruchom testy z coverage",
            "zbuduj obraz docker z tagiem latest",
            "wdróż na staging"
        ]),
        ("🐳 Text2Docker", "Zarządzanie kontenerami", [
            "uruchom postgres na porcie 5432",
            "wystartuj redis z persistencją",
            "pokaż działające kontenery",
            "zatrzymaj wszystkie kontenery nginx"
        ]),
        ("🔗 Pipeline", "Łączenie operacji w workflow", [
            "Sekwencyjne wykonanie wielu modułów",
            "Obsługa błędów i rollback",
            "Historia i statystyki wykonań",
            "Wsparcie dla złożonych workflow"
        ])
    ]
    
    for icon_title, desc, examples in features:
        print(f"{icon_title}")
        print(f"  {desc}")
        print("  Przykłady:")
        for example in examples:
            print(f"    • {example}")
        print()


def demo_architecture():
    """Diagram architektury"""
    print_header("🏗️ Architektura")
    
    print("""
┌─────────────────────────────────────────────────────────────┐
│                      NLP2CMD Framework                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌─────────┐ │
│  │ Text2Env  │  │Text2Bash │  │Text2Make │  │Text2Dock│ │
│  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └────┬────┘ │
│        │              │              │             │       │
│        └──────────────┴──────────────┴─────────────┘       │
│                       │                                     │
│              ┌────────▼────────┐                           │
│              │  BaseConverter  │                           │
│              └────────┬────────┘                           │
│                       │                                     │
│        ┌──────────────┼──────────────┐                    │
│        │              │              │                     │
│  ┌─────▼─────┐  ┌────▼─────┐  ┌────▼────┐                │
│  │  Model    │  │ Pipeline │  │  Utils  │                │
│  │  Wrapper  │  │          │  │         │                │
│  └───────────┘  └──────────┘  └─────────┘                │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                 External Dependencies                       │
├─────────────────────────────────────────────────────────────┤
│  • Transformers (HuggingFace)                              │
│  • PyTorch                                                  │
│  • Pydantic                                                 │
└─────────────────────────────────────────────────────────────┘
    """)


def demo_installation():
    """Instrukcje instalacji"""
    print_header("📦 Instalacja")
    
    print("""
1. Podstawowa instalacja:
   
   pip install nlp2cmd

2. Z repozytorium:
   
   git clone https://github.com/softreck/nlp2cmd.git
   cd nlp2cmd
   pip install -e .

3. Development:
   
   pip install -e ".[dev]"

4. Weryfikacja:
   
   python -c "import nlp2cmd; print(nlp2cmd.__version__)"
    """)


def demo_quickstart():
    """Szybki start"""
    print_header("⚡ Quick Start")
    
    print("""
Najprostszy przykład użycia:

```python
from nlp2cmd import Text2Bash

# Stwórz instancję (bezpieczny tryb dry-run)
bash = Text2Bash(dry_run=True)

# Wykonaj naturalną komendę
result = bash.execute("pokaż 10 największych plików")
print(result.command)  # Output: du -ah . | sort -rh | head -10
```

Pipeline workflow:

```python
from nlp2cmd import Pipeline, Text2Env, Text2Docker, Text2Bash

# Setup
pipeline = Pipeline()
pipeline.add_module("env", Text2Env())
pipeline.add_module("docker", Text2Docker())
pipeline.add_module("bash", Text2Bash())

# Execute workflow
pipeline.execute([
    ("env", "ustaw DATABASE_URL na postgres://localhost/mydb"),
    ("docker", "uruchom postgres na porcie 5432"),
    ("bash", "poczekaj 5 sekund"),
])
```
    """)


def demo_examples():
    """Przykłady użycia"""
    print_header("💡 Więcej przykładów")
    
    print("""
Dostępne przykłady w repozytorium:

  examples/basic_usage.py
    - Podstawowe użycie wszystkich konwerterów
    - Demonstracja Pipeline
    - Dry run mode
    
  examples/advanced_llm.py
    - Użycie modeli LLM (Phi-2, TinyLlama, Bielik)
    - Porównanie modeli
    - Przetwarzanie wsadowe
    - Własne modele HuggingFace
    
  examples/pipeline-example.yaml
    - Przykładowe konfiguracje pipeline
    - Development workflow
    - CI/CD pipeline
    - Cleanup tasks

Uruchomienie:

  python examples/basic_usage.py
  python examples/advanced_llm.py
  
  # CLI
  python -m nlp2cmd.cli bash "pokaż pliki"
  python -m nlp2cmd.cli pipeline --file examples/pipeline-example.yaml
    """)


def demo_configuration():
    """Konfiguracja"""
    print_header("⚙️ Konfiguracja")
    
    print("""
Utwórz plik nlp2cmd.yaml:

```yaml
model:
  name: "phi-2"
  device: "cpu"
  temperature: 0.3

text2bash:
  safe_mode: true
  dry_run: false
  timeout: 30

text2docker:
  auto_pull: true
```

Użycie:

```python
import yaml
from nlp2cmd import Text2Bash

with open("nlp2cmd.yaml") as f:
    config = yaml.safe_load(f)

bash = Text2Bash(**config["text2bash"])
```
    """)


def demo_security():
    """Bezpieczeństwo"""
    print_header("🔒 Bezpieczeństwo")
    
    print("""
Framework ma wbudowane zabezpieczenia:

✓ Safe Mode
  - Automatyczna walidacja komend
  - Blokada niebezpiecznych operacji (rm -rf /, fork bombs)
  - Whitelist dozwolonych komend

✓ Dry Run
  - Symulacja bez wykonania
  - Podgląd wygenerowanych komend
  - Testowanie workflow

✓ Input Sanitization
  - Czyszczenie danych wejściowych
  - Ochrona przed injection attacks
  - Walidacja ścieżek

✓ Logging
  - Szczegółowe logi wszystkich operacji
  - Historia wykonań
  - Audit trail

Przykład:

```python
bash = Text2Bash(
    safe_mode=True,        # Włączona walidacja
    dry_run=True,          # Tylko symulacja
    whitelist=["ls", "cat"]  # Tylko te komendy
)
```
    """)


def demo_testing():
    """Testowanie"""
    print_header("🧪 Testowanie")
    
    print("""
Framework zawiera kompleksowe testy:

  tests/test_nlp2cmd.py
    - Testy jednostkowe dla wszystkich konwerterów
    - Testy Pipeline
    - Testy walidatorów i parserów
    - Testy integracyjne

Uruchomienie:

  # Wszystkie testy
  pytest tests/ -v
  
  # Z coverage
  pytest tests/ --cov=nlp2cmd --cov-report=html
  
  # Konkretny test
  pytest tests/test_nlp2cmd.py::TestText2Bash -v
  
  # Watch mode
  pytest-watch tests/
    """)


def demo_resources():
    """Zasoby"""
    print_header("📚 Zasoby i linki")
    
    print("""
Dokumentacja i zasoby:

  📖 Dokumentacja
     README.md          - Główna dokumentacja
     QUICKSTART.md      - Szybki start
     CONTRIBUTING.md    - Guide dla kontrybutorów
     CHANGELOG.md       - Historia zmian
  
  🔗 Linki
     GitHub:  https://github.com/softreck/nlp2cmd
     Issues:  https://github.com/softreck/nlp2cmd/issues
     Email:   info@softreck.com
  
  🤖 Modele
     Phi-2:       microsoft/phi-2
     TinyLlama:   TinyLlama/TinyLlama-1.1B-Chat-v1.0
     Bielik:      speakleash/Bielik-7B-v0.1
  
  🔧 Narzędzia
     Makefile         - Development tasks
     pytest           - Testing framework
     black/isort      - Code formatting
    """)


def demo_roadmap():
    """Roadmap"""
    print_header("🗺️ Roadmap")
    
    print("""
Planowane funkcje:

  v0.2.0 (Q1 2025)
    ☐ Text2Kubernetes - zarządzanie klastrem K8s
    ☐ Text2Terraform  - infrastructure as code
    ☐ Web UI          - interaktywny interface
    ☐ Więcej modeli   - Mistral, Llama, Gemma
  
  v0.3.0 (Q2 2025)
    ☐ Plugin system   - własne konwertery
    ☐ CI/CD integration
    ☐ Improved caching
    ☐ Multi-language support
  
  v1.0.0 (Q3 2025)
    ☐ Production-ready
    ☐ Full documentation
    ☐ Enterprise features
    ☐ Cloud deployment

Chcesz pomóc? Zobacz CONTRIBUTING.md!
    """)


def main():
    """Main demo function"""
    try:
        demo_intro()
        demo_features()
        demo_architecture()
        demo_installation()
        demo_quickstart()
        demo_examples()
        demo_configuration()
        demo_security()
        demo_testing()
        demo_resources()
        demo_roadmap()
        
        print_header("✨ Dziękujemy za zainteresowanie NLP2CMD!")
        
        print("""
Następne kroki:

  1. Zainstaluj:     pip install nlp2cmd
  2. Przeczytaj:     cat QUICKSTART.md
  3. Przetestuj:     python examples/basic_usage.py
  4. Eksploruj:      python examples/advanced_llm.py
  5. Buduj:          Stwórz własne workflow!

Pytania? Otwórz issue na GitHub lub napisz na info@softreck.com

Happy coding! 🚀
        """)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\nDemo przerwane.")
        return 1
    except Exception as e:
        print(f"\n\n✗ Błąd: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
