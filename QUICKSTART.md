# Quick Start Guide - NLP2CMD

## 🚀 Szybki Start

### Instalacja

```bash
# Klonowanie repozytorium
git clone https://github.com/softreck/nlp2cmd.git
cd nlp2cmd

# Instalacja
pip install -e .
```

### Pierwszy przykład - Text2Env

```python
from nlp2cmd import Text2Env

# Stwórz instancję
env = Text2Env(env_file=".env")

# Użyj naturalnych komend
env.execute("ustaw PORT na 8080")
env.execute("dodaj DATABASE_URL z wartością postgres://localhost/mydb")
env.execute("zmień DEBUG na true")
```

### Text2Bash - Generowanie skryptów

```python
from nlp2cmd import Text2Bash

bash = Text2Bash()

# Proste komendy
bash.execute("pokaż pliki")
bash.execute("znajdź pliki txt")
bash.execute("sprawdź użycie dysku")

# Złożone operacje
bash.execute("znajdź wszystkie pliki większe niż 100MB")
bash.execute("skopiuj wszystkie obrazy jpg do folderu backup")
```

### Text2Docker - Zarządzanie kontenerami

```python
from nlp2cmd import Text2Docker

docker = Text2Docker()

# Uruchom usługi
docker.execute("uruchom postgres na porcie 5432")
docker.execute("wystartuj redis")

# Zarządzanie
docker.execute("pokaż działające kontenery")
docker.execute("zatrzymaj postgres")
```

### Pipeline - Łączenie modułów

```python
from nlp2cmd import Pipeline, Text2Env, Text2Docker, Text2Bash

# Stwórz pipeline
pipeline = Pipeline()
pipeline.add_module("env", Text2Env())
pipeline.add_module("docker", Text2Docker())
pipeline.add_module("bash", Text2Bash())

# Wykonaj workflow
pipeline.execute([
    ("env", "ustaw DATABASE_URL na postgres://localhost/mydb"),
    ("docker", "uruchom postgres na porcie 5432"),
    ("bash", "poczekaj 5 sekund"),
    ("bash", "sprawdź czy postgres działa")
])
```

## 🤖 Użycie z modelami LLM

### Małe modele (1-3B)

```python
from nlp2cmd import Text2Bash

# Phi-2 (2.7B parametrów)
bash = Text2Bash(
    model_name="phi-2",
    device="cpu"
)

# TinyLlama (1.1B parametrów) - najszybszy
bash = Text2Bash(
    model_name="tinyllama",
    device="cpu"
)
```

### Polski model Bielik

```python
from nlp2cmd import Text2Bash

bash = Text2Bash(
    model_name="bielik",  # Alias dla Bielik-7B
    device="cpu",
    use_8bit=True  # 8-bit quantization
)

bash.execute("wyświetl ostatnie 20 linii z pliku log")
```

## ⚙️ Konfiguracja

Utwórz plik `nlp2cmd.yaml`:

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
  timeout: 60
```

Użycie:

```python
from nlp2cmd import Text2Bash
import yaml

# Załaduj config
with open("nlp2cmd.yaml") as f:
    config = yaml.safe_load(f)

# Użyj w module
bash = Text2Bash(**config["text2bash"])
```

## 🔒 Bezpieczeństwo

### Safe Mode

```python
# Domyślnie włączone
bash = Text2Bash(safe_mode=True)

# Próba niebezpiecznej komendy
result = bash.execute("rm -rf /")
# ✗ Zostanie odrzucone
```

### Dry Run

```python
# Tylko symulacja, bez wykonania
bash = Text2Bash(dry_run=True)

result = bash.execute("usuń wszystkie pliki")
print(result.output)  # "[DRY RUN] Would execute: ..."
```

### Whitelist

```python
# Tylko dozwolone komendy
bash = Text2Bash(
    safe_mode=True,
    whitelist=["ls", "cat", "grep"]
)
```

## 📊 Monitorowanie

```python
from nlp2cmd import Pipeline

pipeline = Pipeline()
# ... dodaj moduły ...

# Wykonaj
results = pipeline.execute(steps)

# Sprawdź wyniki
for result in results:
    print(f"{'✓' if result.success else '✗'} {result.command}")

# Statystyki
summary = pipeline.get_summary()
print(f"Sukces: {summary['success_rate']:.1%}")
```

## 🐛 Debugging

```python
import logging

# Włącz szczegółowe logi
logging.basicConfig(level=logging.DEBUG)

# Teraz wszystkie operacje będą logowane
bash = Text2Bash()
bash.execute("pokaż pliki")
```

## 💡 Wskazówki

1. **Rozpocznij od dry_run=True** - Zawsze testuj komendy w trybie dry run
2. **Używaj safe_mode** - Chroni przed niebezpiecznymi komendami
3. **Wybierz odpowiedni model** - TinyLlama dla szybkości, Phi-2 dla jakości
4. **Pipeline dla workflow** - Łącz wiele operacji w jeden proces
5. **Konfiguracja YAML** - Centralna konfiguracja dla wszystkich modułów

## 📚 Więcej przykładów

```bash
# Uruchom przykłady
python examples/basic_usage.py
python examples/advanced_llm.py

# Testy
pytest tests/ -v

# Dokumentacja
make docs
```

## 🆘 Pomoc

```python
# Informacje o modelu
from nlp2cmd.core.model import ModelWrapper

model = ModelWrapper(model_name="phi-2")
info = model.get_model_info()
print(info)
```

## 🔗 Linki

- GitHub: https://github.com/softreck/nlp2cmd
- Dokumentacja: https://nlp2cmd.readthedocs.io
- Issues: https://github.com/softreck/nlp2cmd/issues
