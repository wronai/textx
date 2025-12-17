# NLP2CMD - Rozszerzona Nomenklatura v2.0

## 📐 System Nazewnictwa

### Prefiksy Konwerterów

| Prefix | Znaczenie | Kierunek | Przykłady |
|--------|-----------|----------|-----------|
| **text2X** | Query & Execute | READ | text2bash, text2docker, text2api |
| **text3X** | Generate & Edit | WRITE | text3bash, text3docker, text3app |
| **text4X** | Communicate & Stream | BIDIRECTIONAL | text4html, text4modbus, text4usb |

### Szczegółowe Definicje

#### text2X - Query & Execute (READ Operations)
```
Cel:      Odczyt, zapytania, wykonanie poleceń
Kierunek: NL → System → Response
Output:   Dane, wyniki, status
Przykład: "pokaż listę kontenerów" → docker ps → lista kontenerów
```

#### text3X - Generate & Edit (WRITE Operations)
```
Cel:      Generowanie, tworzenie, edycja plików
Kierunek: NL → Generated Content
Output:   Pliki, kod, konfiguracje
Przykład: "stwórz dockerfile" → Dockerfile content
```

#### text4X - Communicate & Stream (BIDIRECTIONAL Operations) ⭐ NOWE!
```
Cel:      Komunikacja w czasie rzeczywistym, protokoły, streaming
Kierunek: NL ↔ Device/Protocol ↔ Response (bidirectional)
Output:   Stream, events, continuous data
Przykład: "monitoruj temperaturę przez modbus" → continuous readings
```

---

## 📋 Kompletna Lista Konwerterów (80+)

### 🖥️ Shell & System (6)

| Konwerter | Typ | Opis | Status |
|-----------|-----|------|--------|
| text2shell | READ | Interactive shell sessions | ✅ Implemented |
| text3bash | WRITE | Generate bash scripts | ✅ Implemented |
| text2makefile | READ | Execute make targets | 📋 Planned |
| text3makefile | WRITE | Generate Makefiles | 📋 Planned |
| text2systemd | READ | Query systemd services | 📋 Planned |
| text3systemd | WRITE | Generate systemd units | 📋 Planned |

### 🐳 Containers (6)

| Konwerter | Typ | Opis | Status |
|-----------|-----|------|--------|
| text2docker | READ | Docker container management | ✅ Implemented |
| text3docker | WRITE | Generate Dockerfiles | ✅ Implemented |
| text2kubernetes | READ | K8s cluster queries | ✅ Implemented |
| text3kubernetes | WRITE | Generate K8s manifests | ✅ Implemented |
| text3compose | WRITE | Generate docker-compose | 📋 Planned |
| text3helm | WRITE | Generate Helm charts | 📋 Planned |

### 🌐 API & Web (12)

| Konwerter | Typ | Opis | Status |
|-----------|-----|------|--------|
| text3app | WRITE | Generate applications | ✅ Implemented |
| text2api | READ | API testing & analysis | ✅ Implemented |
| text3restapi | WRITE | Generate REST APIs | 📋 Planned |
| text3graphql | WRITE | Generate GraphQL schemas | 📋 Planned |
| **text2html** | READ | Parse/analyze HTML | 🚧 In Progress |
| **text3html** | WRITE | Generate HTML pages | 🚧 In Progress |
| **text4html** | STREAM | Real-time HTML updates | 🚧 In Progress |
| **text2markdown** | READ | Parse/analyze Markdown | 🚧 In Progress |
| **text3markdown** | WRITE | Generate Markdown docs | 🚧 In Progress |
| **text4markdown** | STREAM | Live Markdown preview | 🚧 In Progress |
| **text3svg** | WRITE | Generate SVG graphics | 🚧 In Progress |
| **text4svg** | STREAM | Animated SVG streaming | 🚧 In Progress |

### 🏗️ Infrastructure (8)

| Konwerter | Typ | Opis | Status |
|-----------|-----|------|--------|
| text3terraform | WRITE | Generate Terraform | ✅ Implemented |
| text2terraform | READ | Query Terraform state | 📋 Planned |
| text3ansible | WRITE | Generate Ansible playbooks | 📋 Planned |
| text2ansible | READ | Execute Ansible | 📋 Planned |
| text3pulumi | WRITE | Generate Pulumi configs | 📋 Planned |
| text3cloudformation | WRITE | Generate AWS CF | 📋 Planned |
| text3crossplane | WRITE | Generate Crossplane | 📋 Planned |
| text3cdk | WRITE | Generate AWS CDK | 📋 Planned |

### 🗄️ Database (8)

| Konwerter | Typ | Opis | Status |
|-----------|-----|------|--------|
| text3database | WRITE | Generate schemas | ✅ Implemented |
| text2database | READ | Query databases | 📋 Planned |
| text3sql | WRITE | Generate SQL queries | 📋 Planned |
| text2sql | READ | Execute SQL | 📋 Planned |
| text3mongodb | WRITE | Generate MongoDB schemas | 📋 Planned |
| text3redis | WRITE | Generate Redis configs | 📋 Planned |
| text3elasticsearch | WRITE | Generate ES mappings | 📋 Planned |
| text4database | STREAM | Real-time DB sync | 📋 Planned |

### 🔌 Industrial Protocols (10) ⭐ NOWE!

| Konwerter | Typ | Opis | Status |
|-----------|-----|------|--------|
| **text2modbus** | READ | Read Modbus registers | 🚧 In Progress |
| **text3modbus** | WRITE | Write Modbus registers | 🚧 In Progress |
| **text4modbus** | STREAM | Continuous Modbus monitoring | 🚧 In Progress |
| **text2opcua** | READ | Read OPC UA nodes | 📋 Planned |
| **text3opcua** | WRITE | Write OPC UA nodes | 📋 Planned |
| **text4opcua** | STREAM | OPC UA subscriptions | 📋 Planned |
| **text2canbus** | READ | Read CAN bus messages | 📋 Planned |
| **text4canbus** | STREAM | CAN bus monitoring | 📋 Planned |
| **text2profinet** | READ | Read PROFINET data | 📋 Planned |
| **text4profinet** | STREAM | PROFINET streaming | 📋 Planned |

### 🔗 Hardware Interfaces (12) ⭐ NOWE!

| Konwerter | Typ | Opis | Status |
|-----------|-----|------|--------|
| **text2usb** | READ | Read USB device data | 🚧 In Progress |
| **text3usb** | WRITE | Send USB commands | 🚧 In Progress |
| **text4usb** | STREAM | USB data streaming | 🚧 In Progress |
| **text2serial** | READ | Read serial port | 📋 Planned |
| **text3serial** | WRITE | Write serial port | 📋 Planned |
| **text4serial** | STREAM | Serial monitoring | 📋 Planned |
| **text2hdmi** | READ | Read HDMI info | 🚧 In Progress |
| **text4hdmi** | STREAM | HDMI capture/stream | 🚧 In Progress |
| **text2gpio** | READ | Read GPIO pins | 📋 Planned |
| **text3gpio** | WRITE | Write GPIO pins | 📋 Planned |
| **text4gpio** | STREAM | GPIO event streaming | 📋 Planned |
| **text2i2c** | READ | Read I2C devices | 📋 Planned |

### 📡 Network & IoT (12) ⭐ NOWE!

| Konwerter | Typ | Opis | Status |
|-----------|-----|------|--------|
| text2ssh | READ | SSH operations | ✅ Implemented |
| **text4ssh** | STREAM | SSH session streaming | 📋 Planned |
| **text2mqtt** | READ | Read MQTT messages | 🚧 In Progress |
| **text3mqtt** | WRITE | Publish MQTT messages | 🚧 In Progress |
| **text4mqtt** | STREAM | MQTT subscriptions | 🚧 In Progress |
| **text2websocket** | READ | WebSocket receive | 📋 Planned |
| **text3websocket** | WRITE | WebSocket send | 📋 Planned |
| **text4websocket** | STREAM | WebSocket bidirectional | 📋 Planned |
| **text2lorawan** | READ | LoRaWAN receive | 📋 Planned |
| **text3lorawan** | WRITE | LoRaWAN send | 📋 Planned |
| **text4lorawan** | STREAM | LoRaWAN gateway | 📋 Planned |
| **text4coap** | STREAM | CoAP observe | 📋 Planned |

### 📊 Data & Documents (10)

| Konwerter | Typ | Opis | Status |
|-----------|-----|------|--------|
| text2json | READ | Parse JSON | 📋 Planned |
| text3json | WRITE | Generate JSON | 📋 Planned |
| text2yaml | READ | Parse YAML | 📋 Planned |
| text3yaml | WRITE | Generate YAML | 📋 Planned |
| text2xml | READ | Parse XML | 📋 Planned |
| text3xml | WRITE | Generate XML | 📋 Planned |
| text2csv | READ | Parse CSV | 📋 Planned |
| text3csv | WRITE | Generate CSV | 📋 Planned |
| text3pdf | WRITE | Generate PDF | 📋 Planned |
| text2pdf | READ | Parse PDF | 📋 Planned |

---

## 🔄 text4X - Communication Protocol Details

### Architektura text4X

```
┌─────────────────────────────────────────────────────────────┐
│                    NLP2CMD text4X System                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Natural    │───▶│   Protocol   │◀──▶│   Device/    │  │
│  │   Language   │◀───│   Handler    │    │   Service    │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                   │           │
│         │                   ▼                   │           │
│         │           ┌──────────────┐            │           │
│         └──────────▶│   Stream     │◀───────────┘           │
│                     │   Manager    │                        │
│                     └──────────────┘                        │
│                            │                                │
│                            ▼                                │
│                     ┌──────────────┐                        │
│                     │   Event      │                        │
│                     │   Callbacks  │                        │
│                     └──────────────┘                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Kluczowe Różnice

| Aspekt | text2X/text3X | text4X |
|--------|---------------|--------|
| Kierunek | Jednokierunkowy | Dwukierunkowy |
| Czas życia | Request-Response | Continuous |
| State | Stateless | Stateful |
| Output | Single result | Stream of events |
| Use case | One-time operations | Real-time monitoring |

### Przykłady text4X

#### text4modbus
```python
# Ciągłe monitorowanie temperatury
stream = text4modbus.connect("192.168.1.100:502")
stream.subscribe("monitoruj temperaturę co 1s z rejestru 40001")

async for reading in stream:
    print(f"Temperatura: {reading.value}°C")
```

#### text4mqtt
```python
# Subskrypcja MQTT
stream = text4mqtt.connect("mqtt://broker:1883")
stream.subscribe("nasłuchuj na topic sensors/#")

async for message in stream:
    print(f"Topic: {message.topic}, Data: {message.payload}")
```

#### text4html
```python
# Real-time HTML updates (like live reload)
stream = text4html.watch("./src/*.html")

async for update in stream:
    browser.reload()
    print(f"Updated: {update.file}")
```

---

## 📊 Implementation Priority Matrix

### Phase 1 - Core Communication (v0.4.0)
```
HIGH PRIORITY:
├── text4modbus   - Industrial IoT base
├── text4mqtt     - IoT messaging
├── text3html     - Web generation
├── text3markdown - Documentation
└── text3svg      - Graphics generation

MEDIUM PRIORITY:
├── text4usb      - Hardware interface
├── text4serial   - Embedded systems
└── text2html     - Web scraping
```

### Phase 2 - Extended Protocols (v0.5.0)
```
├── text4opcua    - Industrial automation
├── text4websocket - Real-time web
├── text4hdmi     - Video streaming
└── text4canbus   - Automotive
```

### Phase 3 - Complete Coverage (v1.0)
```
├── All remaining converters
├── Protocol bridges
├── Plugin ecosystem
└── Enterprise features
```

---

## 🎯 Total Converter Count

| Category | Count | Implemented | Planned |
|----------|-------|-------------|---------|
| Shell & System | 6 | 2 | 4 |
| Containers | 6 | 4 | 2 |
| API & Web | 12 | 2 | 10 |
| Infrastructure | 8 | 1 | 7 |
| Database | 8 | 1 | 7 |
| Industrial Protocols | 10 | 0 | 10 |
| Hardware Interfaces | 12 | 0 | 12 |
| Network & IoT | 12 | 1 | 11 |
| Data & Documents | 10 | 0 | 10 |
| **TOTAL** | **84** | **11** | **73** |

---

## 🚀 Quick Reference

### Read Operations (text2X)
```bash
text2X command  # Execute and return result
```

### Write Operations (text3X)
```bash
text3X command  # Generate content/files
```

### Stream Operations (text4X)
```bash
text4X command  # Start bidirectional stream
  .subscribe()  # Add subscription
  .publish()    # Send data
  .close()      # End stream
```
