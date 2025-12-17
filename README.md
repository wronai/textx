# NLP2CMD - Natural Language to Command Framework

Lekki framework w Pythonie do konwersji języka naturalnego na komendy, konfiguracje i kod przy użyciu małych modeli językowych (do 3B parametrów).

## 🚀 Możliwości

- **text2env** - Zmiana konfiguracji .env przez komendy w języku naturalnym
- **text2makefile** - Uruchamianie poleceń make z parametrami
- **text2bash** - Generowanie skryptów bash na podstawie opisów
- **text2docker** - Automatyczna konfiguracja i uruchamianie kontenerów Docker
- **Łączenie modułów** - Pipeline'y kombinujące wiele konwerterów

## 📦 Instalacja

```bash
pip install nlp2cmd
```

Lub z repozytorium:

```bash
git clone https://github.com/softreck/nlp2cmd.git
cd nlp2cmd
pip install -e .
```

## 🎯 Przykłady użycia

### Text2Env - Zarządzanie konfiguracją

```python
from nlp2cmd import Text2Env

env = Text2Env(env_file=".env")

# Naturalne komendy
env.execute("ustaw port na 8080")
env.execute("zmień bazę danych na production_db")
env.execute("dodaj klucz API_KEY z wartością abc123")
env.execute("usuń DEBUG")
```

### Text2Makefile - Uruchamianie make

```python
from nlp2cmd import Text2Makefile

make = Text2Makefile(makefile="Makefile")

# Uruchom target
make.execute("zbuduj aplikację")
make.execute("uruchom testy jednostkowe")
make.execute("zbuduj obraz docker z tagiem latest")
```

### Text2Bash - Generowanie skryptów

```python
from nlp2cmd import Text2Bash

bash = Text2Bash()

# Generuj skrypt
script = bash.generate("skopiuj wszystkie pliki txt do folderu backup")
print(script)
# Output: cp *.txt backup/

# Wykonaj bezpośrednio
bash.execute("pokaż 10 największych plików w bieżącym katalogu")
```

### Text2Docker - Zarządzanie kontenerami

```python
from nlp2cmd import Text2Docker

docker = Text2Docker()

# Uruchom usługi
docker.execute("uruchom postgres na porcie 5432")
docker.execute("wystartuj redis z persistencją")
docker.execute("zatrzymaj wszystkie kontenery nginx")
```

### Pipeline - Łączenie modułów

```python
from nlp2cmd import Pipeline

# Stwórz pipeline
pipeline = Pipeline()
pipeline.add_module("env", Text2Env())
pipeline.add_module("docker", Text2Docker())
pipeline.add_module("bash", Text2Bash())

# Wykonaj sekwencję
pipeline.execute([
    ("env", "ustaw DATABASE_URL na postgres://localhost/mydb"),
    ("docker", "uruchom postgres na porcie 5432"),
    ("bash", "poczekaj 5 sekund"),
    ("bash", "sprawdź czy postgres działa")
])
```

## 🧠 Obsługiwane modele

Framework domyślnie używa małych, wydajnych modeli:

- **Phi-2** (2.7B) - Microsoft
- **TinyLlama** (1.1B) - Szybki model dla prostych zadań
- **Bielik-7B-v0.1** - Polski model językowy (opcjonalnie)

Można używać własnych modeli:

```python
from nlp2cmd import Text2Bash

bash = Text2Bash(
    model_name="microsoft/phi-2",
    device="cuda"  # lub "cpu"
)
```

## 🏗️ Architektura

```
nlp2cmd/
├── core/
│   ├── base.py          # Bazowa klasa dla wszystkich konwerterów
│   ├── model.py         # Wrapper dla modeli LLM
│   └── pipeline.py      # System łączenia modułów
├── converters/
│   ├── text2env.py      # Konwerter dla .env
│   ├── text2makefile.py # Konwerter dla Makefile
│   ├── text2bash.py     # Generator bash
│   └── text2docker.py   # Konwerter dla Docker
└── utils/
    ├── parsers.py       # Parsery dla różnych formatów
    └── validators.py    # Walidatory komend
```

## ⚙️ Konfiguracja

Utwórz `nlp2cmd.yaml` dla własnych ustawień:

```yaml
model:
  name: "microsoft/phi-2"
  device: "cuda"
  max_length: 512
  temperature: 0.3

modules:
  text2env:
    env_file: ".env"
    backup: true
  
  text2bash:
    safe_mode: true
    dry_run: false
  
  text2docker:
    docker_host: "unix://var/run/docker.sock"
```

## 🔒 Bezpieczeństwo

- **Safe mode** - Walidacja komend przed wykonaniem
- **Dry run** - Podgląd bez wykonywania
- **Whitelist** - Dozwolone komendy i operacje
- **Sandboxing** - Izolacja wykonywania (opcjonalnie)

## 📚 Dokumentacja

Pełna dokumentacja dostępna w [docs/](docs/)

## 🤝 Rozwój

```bash
# Sklonuj repozytorium
git clone https://github.com/softreck/nlp2cmd.git
cd nlp2cmd

# Instaluj dependencies deweloperskie
pip install -e ".[dev]"

# Uruchom testy
pytest tests/

# Formatowanie
black nlp2cmd/
```

## 📄 Licencja

MIT License - szczegóły w [LICENSE](LICENSE)

## 🌟 Roadmap

- [ ] Wsparcie dla więcej modeli (Mistral, Llama)
- [ ] Text2Kubernetes - zarządzanie klastrem
- [ ] Text2Terraform - infrastruktura jako kod
- [ ] Web UI dla interaktywnej pracy
- [ ] Integration z CI/CD pipelines
- [ ] Plugin system dla własnych konwerterów

## 👥 Autorzy

Softreck - [https://softreck.com](https://softreck.com)

## 🙏 Podziękowania

- Hugging Face Transformers
- Społeczność Bielik LLM
