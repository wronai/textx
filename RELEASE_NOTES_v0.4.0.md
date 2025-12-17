# 🎉 NLP2CMD v0.4.0 - Communication & Protocols Release

## 🚀 Major Update: text4X Streaming & Hardware Interfaces

**Data wydania**: 17 grudnia 2024  
**Wersja**: 0.4.0  
**Status**: Production-Ready  
**Nowe konwertery**: +18 (27 total)  
**Nowy kod**: +5000 linii  

---

## 🎯 Nowa Nomenklatura: text4X

```
text2X - READ   - Query, Execute, Parse
text3X - WRITE  - Generate, Create, Edit  
text4X - STREAM - Bidirectional, Real-time ⭐ NEW!
```

## 📊 Nowe Konwertery (18)

### 🌐 Web (5)
- **text2html** - Parse, analyze HTML
- **text3html** - Generate HTML pages
- **text4html** - Live reload streaming
- **text3svg** - Generate SVG charts
- **text4svg** - Animated SVG

### 📄 Documents (3)
- **text2markdown** - Parse Markdown
- **text3markdown** - Generate docs
- **text4markdown** - Live preview

### 🏭 Industrial (6)
- **text2modbus** - Read Modbus
- **text3modbus** - Write Modbus
- **text4modbus** - Stream Modbus
- **text2mqtt** - Subscribe MQTT
- **text3mqtt** - Publish MQTT
- **text4mqtt** - Stream MQTT

### 🔌 Hardware (8)
- **text2usb/text3usb/text4usb** - USB
- **text2hdmi/text4hdmi** - HDMI
- **text2serial/text3serial/text4serial** - Serial

## 📊 Stats

- Konwertery: 9 → 27 (+18)
- Kod: ~20,000 linii
- Testy: 100% pass
- Kategorie: 10

## 🎯 Quick Start

```python
# HTML
from nlp2cmd.converters import Text3HTML
html = Text3HTML()
result = html.execute("generate landing page")

# Modbus
from nlp2cmd.converters import Text2Modbus
modbus = Text2Modbus()
result = modbus.execute("read registers 40001")

# MQTT Streaming
from nlp2cmd.converters import Text4MQTT
stream = Text4MQTT()
await stream.connect("mqtt://broker:1883")
async for event in stream.stream():
    print(event.data)
```

Made with ❤️ by Softreck
