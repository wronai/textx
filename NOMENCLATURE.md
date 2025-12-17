# NLP2CMD - Nomenklatura i Struktura Projektu

## 📋 Konwencja nazewnictwa

### text2X - Query & Execute (Read Operations)
**Cel**: Czytanie, analiza i wykonywanie istniejących zasobów
- Uruchamianie komend
- Query do systemów
- Interakcje read-only
- Diagnostyka

### text3X - Generate & Edit (Write Operations)
**Cel**: Generowanie, edycja i tworzenie nowych zasobów
- Generowanie plików
- Modyfikacja konfiguracji
- Tworzenie nowych zasobów
- Operacje write

## 📊 Aktualna struktura (do reorganizacji)

```
nlp2cmd/converters/
├── text2env.py         -> text3env.py (edycja .env)
├── text2bash.py        -> text2bash.py (uruchamianie) + text3bash.py (generowanie)
├── text2makefile.py    -> text2makefile.py (uruchamianie) + text3makefile.py (generowanie)
└── text2docker.py      -> text2docker.py (zarządzanie)
```

## 🎯 Nowa struktura - Reorganizacja

### Grupa 1: Environment & Configuration
```
text2env.py          # Query .env (czytanie wartości)
text3env.py          # Edit .env (modyfikacja wartości)

text2config.py       # Query YAML/JSON configs
text3config.py       # Generate/Edit configs
```

### Grupa 2: Shell & Scripts
```
text2bash.py         # Execute bash commands
text3bash.py         # Generate bash scripts

text2shell.py        # Interactive shell session (NEW)
text3shell.py        # Generate shell scripts

text2makefile.py     # Execute make targets
text3makefile.py     # Generate Makefiles
```

### Grupa 3: Containers & Orchestration
```
text2docker.py       # Manage containers (run, stop, inspect)
text3docker.py       # Generate Dockerfiles

text2kubernetes.py   # Query K8s cluster (get, describe) (NEW)
text3kubernetes.py   # Generate K8s manifests (NEW)

text2compose.py      # Query docker-compose (NEW)
text3compose.py      # Generate docker-compose.yml (NEW)
```

### Grupa 4: Infrastructure & Cloud
```
text2terraform.py    # Query terraform state (NEW)
text3terraform.py    # Generate terraform configs (NEW)

text2ansible.py      # Execute ansible playbooks (NEW)
text3ansible.py      # Generate ansible playbooks (NEW)

text2cloud.py        # Query cloud resources (AWS/Azure/GCP) (NEW)
text3cloud.py        # Generate cloud configs (NEW)
```

### Grupa 5: Network & Remote
```
text2ssh.py          # SSH connections & commands (NEW)
text3ssh.py          # Generate SSH configs (NEW)

text2network.py      # Network diagnostics (ping, traceroute) (NEW)
text3network.py      # Generate network configs (NEW)

text2ftp.py          # FTP operations (NEW)
text3ftp.py          # Generate FTP scripts (NEW)
```

### Grupa 6: APIs & Services
```
text2restapi.py      # REST API queries (NEW)
text3restapi.py      # Generate API clients (NEW)

text2graphql.py      # GraphQL queries (NEW)
text3graphql.py      # Generate GraphQL schemas (NEW)

text2dql.py          # DOM + GraphQL queries (NEW)
text3dql.py          # Generate query builders (NEW)
```

### Grupa 7: Communication
```
text2email.py        # Read/search emails (NEW)
text3email.py        # Compose/send emails (NEW)

text2slack.py        # Query Slack messages (NEW)
text3slack.py        # Send Slack messages (NEW)

text2webhook.py      # Receive webhooks (NEW)
text3webhook.py      # Generate webhook handlers (NEW)
```

### Grupa 8: CMS & Databases
```
text2wordpress.py    # Query WordPress content (NEW)
text3wordpress.py    # Create WordPress posts/pages (NEW)

text2database.py     # Execute SQL queries (NEW)
text3database.py     # Generate SQL schemas (NEW)

text2mongodb.py      # Query MongoDB (NEW)
text3mongodb.py      # Generate MongoDB schemas (NEW)
```

### Grupa 9: CI/CD & Monitoring
```
text2cicd.py         # Query CI/CD status (Jenkins, GitLab, GitHub Actions) (NEW)
text3cicd.py         # Generate CI/CD configs (NEW)

text2monitoring.py   # Query monitoring (Prometheus, Grafana) (NEW)
text3monitoring.py   # Generate monitoring configs (NEW)

text2logs.py         # Query and analyze logs (NEW)
text3logs.py         # Generate log parsers (NEW)
```

### Grupa 10: Security & Secrets
```
text2secrets.py      # Query secrets (Vault, AWS Secrets Manager) (NEW)
text3secrets.py      # Generate secret configs (NEW)

text2security.py     # Security scans and audits (NEW)
text3security.py     # Generate security policies (NEW)
```

## 🔄 Plan migracji

### Faza 1: Reorganizacja istniejących (TERAZ)
1. ✅ Pozostaw `text2bash.py` (execute)
2. ✅ Dodaj `text3bash.py` (generate scripts)
3. ✅ Pozostaw `text2makefile.py` (execute)
4. ✅ Dodaj `text3makefile.py` (generate Makefiles)
5. ✅ Zmień `text2env.py` na `text3env.py` (głównie edycja)
6. ✅ Dodaj `text2env.py` (query only)
7. ✅ Pozostaw `text2docker.py`
8. ✅ Dodaj `text3docker.py` (Dockerfile generation)

### Faza 2: Nowe konwertery - DevOps Core (PRIORYTET)
1. ✅ `text2shell.py` - Interactive shell
2. ✅ `text2kubernetes.py` + `text3kubernetes.py`
3. ✅ `text2ssh.py` + `text3ssh.py`
4. ✅ `text2network.py`
5. ✅ `text2terraform.py` + `text3terraform.py`

### Faza 3: API & Communication
1. ⏳ `text2restapi.py` + `text3restapi.py`
2. ⏳ `text2graphql.py` + `text3graphql.py`
3. ⏳ `text2email.py` + `text3email.py`
4. ⏳ `text2dql.py` + `text3dql.py`

### Faza 4: CMS & Extended
1. ⏳ `text2wordpress.py` + `text3wordpress.py`
2. ⏳ `text2database.py` + `text3database.py`
3. ⏳ `text2cicd.py` + `text3cicd.py`
4. ⏳ Pozostałe według potrzeb

## 📁 Docelowa struktura katalogów

```
nlp2cmd/
├── core/
│   ├── base.py              # BaseConverter, ConversionResult
│   ├── model.py             # ModelWrapper
│   └── pipeline.py          # Pipeline
│
├── converters/
│   ├── __init__.py
│   │
│   ├── environment/         # Environment & Config
│   │   ├── text2env.py
│   │   ├── text3env.py
│   │   ├── text2config.py
│   │   └── text3config.py
│   │
│   ├── shell/               # Shell & Scripts
│   │   ├── text2bash.py
│   │   ├── text3bash.py
│   │   ├── text2shell.py
│   │   ├── text3shell.py
│   │   ├── text2makefile.py
│   │   └── text3makefile.py
│   │
│   ├── containers/          # Containers & Orchestration
│   │   ├── text2docker.py
│   │   ├── text3docker.py
│   │   ├── text2kubernetes.py
│   │   ├── text3kubernetes.py
│   │   ├── text2compose.py
│   │   └── text3compose.py
│   │
│   ├── infrastructure/      # IaC & Cloud
│   │   ├── text2terraform.py
│   │   ├── text3terraform.py
│   │   ├── text2ansible.py
│   │   ├── text3ansible.py
│   │   ├── text2cloud.py
│   │   └── text3cloud.py
│   │
│   ├── network/             # Network & Remote
│   │   ├── text2ssh.py
│   │   ├── text3ssh.py
│   │   ├── text2network.py
│   │   ├── text3network.py
│   │   ├── text2ftp.py
│   │   └── text3ftp.py
│   │
│   ├── api/                 # APIs & Services
│   │   ├── text2restapi.py
│   │   ├── text3restapi.py
│   │   ├── text2graphql.py
│   │   ├── text3graphql.py
│   │   ├── text2dql.py
│   │   └── text3dql.py
│   │
│   ├── communication/       # Communication
│   │   ├── text2email.py
│   │   ├── text3email.py
│   │   ├── text2slack.py
│   │   ├── text3slack.py
│   │   ├── text2webhook.py
│   │   └── text3webhook.py
│   │
│   ├── data/                # CMS & Databases
│   │   ├── text2wordpress.py
│   │   ├── text3wordpress.py
│   │   ├── text2database.py
│   │   ├── text3database.py
│   │   ├── text2mongodb.py
│   │   └── text3mongodb.py
│   │
│   ├── devops/              # CI/CD & Monitoring
│   │   ├── text2cicd.py
│   │   ├── text3cicd.py
│   │   ├── text2monitoring.py
│   │   ├── text3monitoring.py
│   │   ├── text2logs.py
│   │   └── text3logs.py
│   │
│   └── security/            # Security & Secrets
│       ├── text2secrets.py
│       ├── text3secrets.py
│       ├── text2security.py
│       └── text3security.py
│
└── utils/
    ├── parsers.py
    ├── validators.py
    ├── formatters.py        # NEW
    └── templates.py         # NEW (dla text3X)
```

## 🎯 Priorytety implementacji

### P0 - Krytyczne (DevOps Core)
1. ✅ `text2shell.py` - Interactive shell
2. ✅ `text2kubernetes.py` + `text3kubernetes.py`
3. ✅ `text2ssh.py` + `text3ssh.py`
4. ✅ `text3docker.py` - Dockerfile generation
5. ✅ `text3bash.py` - Script generation

### P1 - Wysokie (Infrastructure)
6. ⏳ `text2terraform.py` + `text3terraform.py`
7. ⏳ `text2network.py`
8. ⏳ `text2compose.py` + `text3compose.py`
9. ⏳ `text2ansible.py` + `text3ansible.py`

### P2 - Średnie (Integration)
10. ⏳ `text2restapi.py` + `text3restapi.py`
11. ⏳ `text2cicd.py` + `text3cicd.py`
12. ⏳ `text2database.py` + `text3database.py`
13. ⏳ `text2email.py` + `text3email.py`

### P3 - Niskie (Extended)
14. ⏳ Wszystkie pozostałe

## 💡 Przykłady użycia

### text2X (Query & Execute)
```python
# Query .env
env = Text2Env()
result = env.execute("jaka jest wartość PORT")

# Execute bash
bash = Text2Bash()
result = bash.execute("pokaż działające procesy")

# Query Kubernetes
k8s = Text2Kubernetes()
result = k8s.execute("pokaż wszystkie pody w namespace production")

# SSH command
ssh = Text2SSH()
result = ssh.execute("połącz się z server.com i sprawdź uptime")
```

### text3X (Generate & Edit)
```python
# Generate bash script
bash = Text3Bash()
script = bash.generate("skrypt do backupu bazy danych")

# Generate Dockerfile
docker = Text3Docker()
dockerfile = docker.generate("kontener dla aplikacji Python Flask")

# Generate K8s manifest
k8s = Text3Kubernetes()
manifest = k8s.generate("deployment dla nginx z 3 replikami")

# Generate email
email = Text3Email()
message = email.generate("podziękowanie za współpracę dla klienta")
```

## 🔧 Narzędzia wspierające

### templates/ (dla text3X)
```
templates/
├── docker/
│   ├── python.j2
│   ├── node.j2
│   └── nginx.j2
├── kubernetes/
│   ├── deployment.j2
│   ├── service.j2
│   └── ingress.j2
├── terraform/
│   ├── aws-ec2.j2
│   └── aws-s3.j2
└── scripts/
    ├── backup.j2
    └── deploy.j2
```

## 📝 Wnioski

1. **Jasna separacja**: text2X (read/execute) vs text3X (write/generate)
2. **Modularność**: Grupowanie w katalogi tematyczne
3. **Skalowalność**: Łatwe dodawanie nowych konwerterów
4. **DevOps Focus**: Priorytet dla narzędzi DevOps
5. **Template System**: Wsparcie dla text3X generators
