# NLP2CMD Converter Nomenclature

## Prawidłowa nomenklatura text2X / text3X / text4X

| Prefix | Znaczenie | Opis |
|--------|-----------|------|
| **text2X** | GENERATE | Generuje nowy kod/plik X z opisu tekstowego |
| **text3X** | EDIT | Edytuje istniejący plik X (dodaj/usuń/zmień) |
| **text4X** | SERVICE | Rozproszona usługa do gen/edit na wszystkich warstwach |

## Przykłady

### HTML
- `text2html` - Generuje HTML z opisu: "generate landing page for CloudSync"
- `text3html` - Edytuje HTML: "add button to form", "change title to 'New'"
- `text4html` - Usługa: REST API + WebSocket do gen/edit z dowolnego języka

### Markdown
- `text2markdown` - Generuje MD: "generate README for MyProject"
- `text3markdown` - Edytuje MD: "add section Installation"
- `text4markdown` - Usługa do gen/edit Markdown

### SVG
- `text2svg` - Generuje SVG: "generate bar chart"
- `text3svg` - Edytuje SVG: "change color to blue"
- `text4svg` - Usługa do gen/edit SVG

### Modbus
- `text2modbus` - Generuje komendy Modbus: "read holding registers 40001"
- `text3modbus` - Edytuje konfigurację: "set register 40001 to 100"
- `text4modbus` - Usługa: ciągłe monitorowanie/zapis Modbus

### MQTT
- `text2mqtt` - Generuje komendy MQTT: "subscribe to sensors/#"
- `text3mqtt` - Edytuje: "publish to topic/test message 'hello'"
- `text4mqtt` - Usługa: streaming MQTT

### USB
- `text2usb` - Generuje komendy USB: "list devices", "read from 046d:c077"
- `text3usb` - Edytuje: "reset device", "write data"
- `text4usb` - Usługa: streaming danych USB

### Serial
- `text2serial` - Generuje komendy: "read from /dev/ttyUSB0"
- `text3serial` - Edytuje: "send 'AT' to COM1"
- `text4serial` - Usługa: streaming portu szeregowego

### HDMI
- `text2hdmi` - Generuje info: "get resolution", "read EDID"
- `text4hdmi` - Usługa: capture streaming

## Użycie w kodzie

```python
from nlp2cmd.converters.web.html_converters_v2 import Text2HTML, Text3HTML, Text4HTML

# GENERATE - tworzenie nowego HTML
generator = Text2HTML()
result = generator.execute("generate landing page title: CloudSync")
html = result.output

# EDIT - modyfikacja istniejącego HTML
editor = Text3HTML()
result = editor.execute("add button to form", html_content=html)
modified_html = result.output

# SERVICE - rozproszona usługa
service = Text4HTML()
await service.connect("session_123")
await service.send({"action": "generate", "command": "generate form"})
event = await service.receive()
```

## Użycie z MeshClient (SDK)

```python
from nlp2cmd.mesh.sdk import MeshClient

client = MeshClient("http://gateway:8080")

# Generate
result = client.convert("text2html", "generate landing page")

# Edit
result = client.convert("text3html", "add button", html_content=existing_html)

# Service (streaming)
async for event in client.stream("text4html", "generate dashboard"):
    print(event)

# Pipeline
result = client.pipeline([
    {"converter": "text2html", "command": "generate page"},
    {"converter": "text3html", "command": "add footer"},
    {"action": "deploy", "config": {"target": "file", "path": "/var/www/page.html"}}
])
```

## Warstwy aplikacji

text4X może być wywoływane z dowolnej warstwy:

```
┌─────────────────────────────────────────────────────────────┐
│                      text4X SERVICE                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ Firmware │  │ Backend  │  │ Database │  │ Frontend │    │
│  │   (C)    │  │ (Python) │  │  (SQL)   │  │   (JS)   │    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘    │
│       │             │             │             │           │
│       └─────────────┴─────────────┴─────────────┘           │
│                          │                                   │
│                    Message Bus                               │
│                   (NATS/Redis)                              │
│                          │                                   │
│              ┌───────────┴───────────┐                      │
│              │      text4X Worker    │                      │
│              │  (text2X + text3X)    │                      │
│              └───────────────────────┘                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```
