# NLP2CMD - Implementacja Nowej Nomenklatury

## 📊 Status Implementacji

### ✅ Zaimplementowane (P0 - Krytyczne)

#### 1. text2shell.py - Interactive Shell
**Lokalizacja**: `nlp2cmd/converters/shell/text2shell.py`
**Funkcje**:
- Wieloetapowe wykonywanie komend
- Interaktywne sesje (ssh, ftp, mysql, psql)
- Zachowanie kontekstu między komendami
- Obsługa promptów i uwierzytelniania
- Session management

**Przykład**:
```python
from nlp2cmd.converters.shell import Text2Shell

shell = Text2Shell()
result = shell.execute("połącz się z server.com, przejdź do /var/log, pokaż ostatnie logi")
```

#### 2. text3bash.py - Bash Script Generation
**Lokalizacja**: `nlp2cmd/converters/shell/text3bash.py`
**Funkcje**:
- Generowanie kompletnych skryptów bash
- Szablony dla backup, deploy, monitor, cron
- Funkcje logowania i error handling
- Argument parsing
- Best practices (set -e, -u, -o pipefail)

**Przykład**:
```python
from nlp2cmd.converters.shell import Text3Bash

bash = Text3Bash()
result = bash.execute("skrypt do backupu bazy danych z logowaniem")
script = result.output
```

#### 3. text3docker.py - Dockerfile Generation
**Lokalizacja**: `nlp2cmd/converters/containers/text3docker.py`
**Funkcje**:
- Generowanie Dockerfiles dla Python, Node, Go, Java, PHP, Ruby
- Multi-stage builds
- Optymalizacja warstw
- Security hardening (non-root user)
- Healthchecks
- Framework support (Flask, Django, Express, etc.)

**Przykład**:
```python
from nlp2cmd.converters.containers import Text3Docker

docker = Text3Docker()
result = docker.execute("kontener dla aplikacji Python Flask na porcie 5000")
dockerfile = result.output
```

#### 4. text2kubernetes.py - K8s Query & Management
**Lokalizacja**: `nlp2cmd/converters/containers/text2kubernetes.py`
**Funkcje**:
- Query zasobów (get, describe, logs)
- Zarządzanie deployments
- Scaling
- Namespace operations
- Wsparcie dla wszystkich głównych zasobów K8s

**Przykład**:
```python
from nlp2cmd.converters.containers import Text2Kubernetes

k8s = Text2Kubernetes()
result = k8s.execute("pokaż wszystkie pody w namespace production")
```

## 📁 Nowa Struktura Katalogów

```
nlp2cmd/converters/
├── shell/                      # ✅ Zaimplementowane
│   ├── __init__.py
│   ├── text2bash.py           # (przeniesione z root)
│   ├── text2shell.py          # ✅ NOWE - Interactive shell
│   ├── text3bash.py           # ✅ NOWE - Script generation
│   ├── text2makefile.py       # (przeniesione z root)
│   └── text3makefile.py       # ⏳ TODO
│
├── containers/                 # ✅ Zaimplementowane
│   ├── __init__.py
│   ├── text2docker.py         # (przeniesione z root)
│   ├── text3docker.py         # ✅ NOWE - Dockerfile generation
│   ├── text2kubernetes.py     # ✅ NOWE - K8s query
│   ├── text3kubernetes.py     # ⏳ TODO - Manifest generation
│   ├── text2compose.py        # ⏳ TODO
│   └── text3compose.py        # ⏳ TODO
│
├── network/                    # ⏳ TODO
│   ├── text2ssh.py
│   ├── text3ssh.py
│   ├── text2network.py
│   └── text2ftp.py
│
├── infrastructure/             # ⏳ TODO
│   ├── text2terraform.py
│   ├── text3terraform.py
│   ├── text2ansible.py
│   └── text3ansible.py
│
└── api/                        # ⏳ TODO
    ├── text2restapi.py
    ├── text3restapi.py
    ├── text2graphql.py
    └── text3graphql.py
```

## 🎯 Następne Kroki (P0 - Do dokończenia)

### 1. text3kubernetes.py - K8s Manifest Generation
**Priorytet**: Wysoki
**Funkcje do implementacji**:
- Generowanie Deployment manifests
- Generowanie Service manifests
- Generowanie Ingress
- Generowanie ConfigMap/Secret
- Support dla różnych typów aplikacji

### 2. text2ssh.py - SSH Operations
**Priorytet**: Wysoki
**Funkcje do implementacji**:
- Połączenia SSH
- Wykonywanie komend zdalnych
- Transfer plików (SCP/SFTP)
- SSH config management
- Key management

### 3. text3makefile.py - Makefile Generation
**Priorytet**: Średni
**Funkcje do implementacji**:
- Generowanie Makefiles
- Common targets (build, test, deploy, clean)
- Variables i dependencies
- Phony targets

## 📝 Plan Migracji Istniejących Plików

### Krok 1: Przeniesienie do nowych katalogów
```bash
# Shell
mv text2bash.py shell/text2bash.py
mv text2makefile.py shell/text2makefile.py

# Containers
mv text2docker.py containers/text2docker.py

# Environment (zachowujemy w root lub tworzymy environment/)
# text2env.py -> text3env.py (głównie edycja)
```

### Krok 2: Aktualizacja importów
```python
# Stare
from nlp2cmd.converters.text2bash import Text2Bash

# Nowe
from nlp2cmd.converters.shell.text2bash import Text2Bash
```

### Krok 3: Aktualizacja __init__.py
```python
# nlp2cmd/converters/__init__.py
from nlp2cmd.converters.shell.text2bash import Text2Bash
from nlp2cmd.converters.shell.text2shell import Text2Shell
from nlp2cmd.converters.shell.text3bash import Text3Bash
from nlp2cmd.converters.containers.text2docker import Text2Docker
from nlp2cmd.converters.containers.text3docker import Text3Docker
from nlp2cmd.converters.containers.text2kubernetes import Text2Kubernetes
```

## 💡 Przykłady Użycia Nowych Konwerterów

### 1. Interactive Shell (text2shell)
```python
from nlp2cmd import Text2Shell

# Multi-step execution
shell = Text2Shell()
result = shell.execute("""
    połącz się z production.example.com,
    przejdź do /var/www/html,
    sprawdź logi aplikacji z ostatniej godziny
""")
```

### 2. Bash Script Generation (text3bash)
```python
from nlp2cmd import Text3Bash

bash = Text3Bash(
    include_logging=True,
    include_colors=True
)

# Generate backup script
result = bash.execute("skrypt do backupu bazy PostgreSQL z rotacją")
script = result.output

# Save to file
bash.save_script(script, "backup.sh", make_executable=True)
```

### 3. Dockerfile Generation (text3docker)
```python
from nlp2cmd import Text3Docker

docker = Text3Docker(
    multi_stage=True,
    include_healthcheck=True
)

# Generate Dockerfile
result = docker.execute("""
    kontener dla aplikacji FastAPI w Pythonie 3.11,
    użyj Alpine, port 8000, z nginx
""")

dockerfile = result.output
docker.save_dockerfile(dockerfile, ".", "Dockerfile")
```

### 4. Kubernetes Operations (text2kubernetes)
```python
from nlp2cmd import Text2Kubernetes

k8s = Text2Kubernetes(namespace="production")

# Query resources
k8s.execute("pokaż wszystkie pody")
k8s.execute("opisz deployment api-server")
k8s.execute("logi z poda frontend-xyz w namespace staging")

# Management
k8s.execute("skaluj deployment api do 5 replik")
k8s.execute("restart deployment frontend")

# Get structured data
pods = k8s.get_pods("production")
namespaces = k8s.get_namespaces()
```

## 📚 Dokumentacja do Aktualizacji

### Pliki do zaktualizowania:
1. ✅ NOMENCLATURE.md - Kompletna nomenklatura (utworzony)
2. ⏳ README.md - Dodać nowe konwertery
3. ⏳ QUICKSTART.md - Przykłady użycia nowych funkcji
4. ⏳ examples/ - Nowe przykłady
5. ⏳ tests/ - Testy dla nowych konwerterów

## 🔧 Dependencies do Dodania

```txt
# requirements.txt - dodatkowe zależności

# Dla text2shell (interactive sessions)
pexpect>=4.8.0

# Dla text2kubernetes
pyyaml>=6.0  # już jest

# Dla text2ssh (w przyszłości)
paramiko>=3.0.0

# Dla text2network (w przyszłości)
# ping3>=4.0.0
# scapy>=2.5.0
```

## 🎯 Metryki Postępu

### Konwertery
- ✅ Zaimplementowane: 4/10 (40%)
- ⏳ W trakcie: 0/10 (0%)
- 📋 Zaplanowane: 6/10 (60%)

### Struktura
- ✅ Katalogi utworzone: shell/, containers/
- ⏳ Do utworzenia: network/, infrastructure/, api/
- 📋 Dokumentacja: Częściowo kompletna

### Funkcjonalność
- ✅ P0 (Krytyczne): 4/5 (80%)
- ⏳ P1 (Wysokie): 0/5 (0%)
- 📋 P2 (Średnie): 0/4 (0%)
- 📋 P3 (Niskie): 0/20+ (0%)

## 🚀 Quick Start z Nowymi Konwerterami

```python
#!/usr/bin/env python3
"""Przykład użycia nowych konwerterów"""

from nlp2cmd.converters.shell import Text2Shell, Text3Bash
from nlp2cmd.converters.containers import Text3Docker, Text2Kubernetes

# 1. Generate Dockerfile
docker_gen = Text3Docker()
dockerfile_result = docker_gen.execute("kontener dla aplikacji Flask")
print(dockerfile_result.output)

# 2. Generate bash script
bash_gen = Text3Bash()
script_result = bash_gen.execute("skrypt backup z logowaniem")
bash_gen.save_script(script_result.output, "backup.sh")

# 3. Interactive shell session
shell = Text2Shell()
shell_result = shell.execute("""
    połącz się z server.com,
    sprawdź uptime,
    pokaż użycie dysku
""")
print(shell_result.output)

# 4. Kubernetes operations
k8s = Text2Kubernetes()
k8s.execute("pokaż pody w production")
k8s.execute("skaluj api do 3 replik")
```

## 📞 Wsparcie

Dla dodatkowych pytań lub sugestii:
- GitHub Issues: https://github.com/softreck/nlp2cmd/issues
- Email: info@softreck.com
- Dokumentacja: NOMENCLATURE.md

---

**Ostatnia aktualizacja**: 2024-12-16
**Wersja**: 0.2.0-dev
**Status**: W trakcie implementacji P0 priorytetów
