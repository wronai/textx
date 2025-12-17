#!/usr/bin/env python3
"""
NLP2CMD v0.4.0 - text4X Communication Demo

Demonstruje nowe konwertery komunikacyjne:
- text2html, text3html, text4html
- text2markdown, text3markdown, text4markdown
- text3svg, text4svg
- text2modbus, text3modbus, text4modbus
- text2mqtt, text3mqtt, text4mqtt
- text2usb, text3usb, text4usb
- text2hdmi, text4hdmi
- text2serial, text3serial, text4serial
"""

import sys
sys.path.insert(0, '/home/claude/nlp2cmd')

import asyncio
from pathlib import Path
from datetime import datetime

# Import all new converters
from nlp2cmd.converters.web.html_converters import Text2HTML, Text3HTML, Text4HTML
from nlp2cmd.converters.documents.markdown_converters import Text2Markdown, Text3Markdown, Text4Markdown
from nlp2cmd.converters.web.svg_converters import Text3SVG, Text4SVG
from nlp2cmd.converters.protocols.industrial_protocols import (
    Text2Modbus, Text3Modbus, Text4Modbus,
    Text2MQTT, Text3MQTT, Text4MQTT
)
from nlp2cmd.converters.hardware.hardware_interfaces import (
    Text2USB, Text3USB, Text4USB,
    Text2HDMI, Text4HDMI,
    Text2Serial, Text3Serial, Text4Serial
)


def print_header(title: str, emoji: str = "🚀"):
    """Print formatted header"""
    print(f"\n{'='*70}")
    print(f"{emoji}  {title}")
    print(f"{'='*70}\n")


def print_result(name: str, result, show_output: bool = True):
    """Print converter result"""
    status = "✅" if result.success else "❌"
    print(f"{status} {name}")
    print(f"   Command: {result.command}")
    if show_output and result.output:
        output_preview = result.output[:200] + "..." if len(result.output) > 200 else result.output
        print(f"   Output: {output_preview}")
    if result.metadata:
        print(f"   Metadata: {result.metadata}")
    print()


def save_artifact(name: str, content: str, directory: str = "/tmp/nlp2cmd-text4x"):
    """Save artifact to file"""
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    filepath = path / name
    filepath.write_text(content)
    print(f"   💾 Saved: {filepath}")
    return str(filepath)


# ============================================================================
# DEMO 1: HTML Converters
# ============================================================================

def demo_html_converters():
    """Demo konwerterów HTML"""
    print_header("DEMO 1: HTML Converters (text2html, text3html)", "🌐")
    
    # text3html - Generate HTML
    print("📝 text3html - Generowanie HTML:\n")
    
    gen = Text3HTML()
    
    # Landing page
    result = gen.execute("wygeneruj landing page dla produktu SaaS title: CloudSync")
    print_result("Landing Page", result, show_output=False)
    if result.success:
        save_artifact("landing.html", result.output)
    
    # Form
    result = gen.execute("wygeneruj formularz kontaktowy")
    print_result("Contact Form", result, show_output=False)
    if result.success:
        save_artifact("form.html", result.output)
    
    # Table
    result = gen.execute("wygeneruj tabelę z danymi")
    print_result("Data Table", result, show_output=False)
    if result.success:
        save_artifact("table.html", result.output)
    
    # text2html - Parse HTML
    print("\n📖 text2html - Analiza HTML:\n")
    
    parser = Text2HTML()
    
    sample_html = """
    <!DOCTYPE html>
    <html>
    <head><title>Test Page</title></head>
    <body>
        <h1>Welcome</h1>
        <p>This is a test page.</p>
        <a href="https://example.com">Link 1</a>
        <a href="https://test.com">Link 2</a>
        <img src="image.jpg" alt="Test">
    </body>
    </html>
    """
    
    result = parser.execute("analyze html", sample_html)
    print_result("HTML Analysis", result)
    
    result = parser.execute("validate html", sample_html)
    print_result("HTML Validation", result)
    
    result = parser.execute("seo analysis", sample_html)
    print_result("SEO Analysis", result)
    
    return True


# ============================================================================
# DEMO 2: Markdown Converters
# ============================================================================

def demo_markdown_converters():
    """Demo konwerterów Markdown"""
    print_header("DEMO 2: Markdown Converters (text2markdown, text3markdown)", "📄")
    
    # text3markdown - Generate Markdown
    print("📝 text3markdown - Generowanie Markdown:\n")
    
    gen = Text3Markdown()
    
    # README
    result = gen.execute("wygeneruj README dla projektu NLP2CMD")
    print_result("README.md", result, show_output=False)
    if result.success:
        save_artifact("README.md", result.output)
    
    # API Documentation
    result = gen.execute("wygeneruj dokumentację API dla REST API")
    print_result("API Documentation", result, show_output=False)
    if result.success:
        save_artifact("API_DOCS.md", result.output)
    
    # Release Notes
    result = gen.execute("wygeneruj release notes dla wersji 1.0")
    print_result("Release Notes", result, show_output=False)
    if result.success:
        save_artifact("RELEASE_NOTES.md", result.output)
    
    # text2markdown - Parse Markdown
    print("\n📖 text2markdown - Analiza Markdown:\n")
    
    parser = Text2Markdown()
    
    sample_md = """
# Project Title

## Introduction

This is a sample project with **bold** and *italic* text.

## Features

- Feature 1
- Feature 2

```python
def hello():
    print("Hello World")
```

[GitHub](https://github.com)
"""
    
    result = parser.execute("analyze markdown", sample_md)
    print_result("Markdown Analysis", result)
    
    result = parser.execute("convert to html", sample_md)
    print_result("Convert to HTML", result, show_output=False)
    
    result = parser.execute("extract toc", sample_md)
    print_result("Table of Contents", result)
    
    return True


# ============================================================================
# DEMO 3: SVG Converters
# ============================================================================

def demo_svg_converters():
    """Demo konwerterów SVG"""
    print_header("DEMO 3: SVG Converters (text3svg)", "🎨")
    
    gen = Text3SVG()
    
    # Bar Chart
    result = gen.execute("wygeneruj wykres słupkowy bar chart")
    print_result("Bar Chart", result, show_output=False)
    if result.success:
        save_artifact("bar_chart.svg", result.output)
    
    # Line Chart
    result = gen.execute("wygeneruj wykres liniowy line chart")
    print_result("Line Chart", result, show_output=False)
    if result.success:
        save_artifact("line_chart.svg", result.output)
    
    # Pie Chart
    result = gen.execute("wygeneruj wykres kołowy pie chart")
    print_result("Pie Chart", result, show_output=False)
    if result.success:
        save_artifact("pie_chart.svg", result.output)
    
    # Flowchart
    result = gen.execute("wygeneruj flowchart diagram przepływu")
    print_result("Flowchart", result, show_output=False)
    if result.success:
        save_artifact("flowchart.svg", result.output)
    
    # Icons
    for icon in ["check", "star", "heart"]:
        result = gen.execute(f"wygeneruj ikonę {icon}")
        print_result(f"Icon: {icon}", result, show_output=False)
        if result.success:
            save_artifact(f"icon_{icon}.svg", result.output)
    
    return True


# ============================================================================
# DEMO 4: Modbus Converters
# ============================================================================

def demo_modbus_converters():
    """Demo konwerterów Modbus"""
    print_header("DEMO 4: Modbus Converters (text2modbus, text3modbus)", "🏭")
    
    # text2modbus - Read
    print("📖 text2modbus - Odczyt Modbus:\n")
    
    reader = Text2Modbus(host="192.168.1.100", port=502)
    
    result = reader.execute("odczytaj holding registers address 40001 count 10")
    print_result("Read Holding Registers", result)
    
    result = reader.execute("read coils address 0 count 8 slave 1")
    print_result("Read Coils", result)
    
    # text3modbus - Write
    print("\n📝 text3modbus - Zapis Modbus:\n")
    
    writer = Text3Modbus(host="192.168.1.100", port=502)
    
    result = writer.execute("write single register address 40001 value 1234")
    print_result("Write Single Register", result)
    
    result = writer.execute("write coil address 0 value 1")
    print_result("Write Single Coil", result)
    
    return True


# ============================================================================
# DEMO 5: MQTT Converters
# ============================================================================

def demo_mqtt_converters():
    """Demo konwerterów MQTT"""
    print_header("DEMO 5: MQTT Converters (text2mqtt, text3mqtt)", "📡")
    
    # text2mqtt - Subscribe
    print("📖 text2mqtt - Subskrypcja MQTT:\n")
    
    subscriber = Text2MQTT(broker="mqtt.example.com", port=1883)
    
    result = subscriber.execute("subscribe to topic sensors/#")
    print_result("Subscribe sensors/#", result)
    
    # text3mqtt - Publish
    print("\n📝 text3mqtt - Publikowanie MQTT:\n")
    
    publisher = Text3MQTT(broker="mqtt.example.com", port=1883)
    
    result = publisher.execute("publish topic sensors/temperature message 25.5")
    print_result("Publish Temperature", result)
    
    result = publisher.execute("publish topic devices/led message ON qos 1")
    print_result("Publish with QoS 1", result)
    
    return True


# ============================================================================
# DEMO 6: USB Converters
# ============================================================================

def demo_usb_converters():
    """Demo konwerterów USB"""
    print_header("DEMO 6: USB Converters (text2usb, text3usb)", "🔌")
    
    reader = Text2USB()
    
    result = reader.execute("list usb devices")
    print_result("List USB Devices", result)
    
    result = reader.execute("info device 046d:c077")
    print_result("Device Info", result)
    
    writer = Text3USB()
    result = writer.execute("reset device 046d:c077")
    print_result("Reset Device", result)
    
    return True


# ============================================================================
# DEMO 7: HDMI Converters
# ============================================================================

def demo_hdmi_converters():
    """Demo konwerterów HDMI"""
    print_header("DEMO 7: HDMI Converters (text2hdmi)", "🖥️")
    
    reader = Text2HDMI()
    
    result = reader.execute("info hdmi port 0")
    print_result("HDMI Info", result)
    
    result = reader.execute("get resolution hdmi 0")
    print_result("Resolution", result)
    
    return True


# ============================================================================
# DEMO 8: Serial Converters
# ============================================================================

def demo_serial_converters():
    """Demo konwerterów Serial"""
    print_header("DEMO 8: Serial Converters (text2serial, text3serial)", "🔗")
    
    reader = Text2Serial()
    
    result = reader.execute("list serial ports")
    print_result("List Ports", result)
    
    result = reader.execute("read /dev/ttyUSB0 9600 baud")
    print_result("Read from ttyUSB0", result)
    
    writer = Text3Serial()
    result = writer.execute("send data 'AT+GMR' to /dev/ttyUSB0")
    print_result("Send AT Command", result)
    
    return True


# ============================================================================
# DEMO 9: text4X Streaming (Async)
# ============================================================================

async def demo_text4x_streaming():
    """Demo streamingu text4X"""
    print_header("DEMO 9: text4X Streaming (Real-time)", "⚡")
    
    print("🔄 Demonstracja streamingu w czasie rzeczywistym\n")
    
    # text4modbus
    print("--- text4modbus Stream (3 readings) ---")
    modbus_stream = Text4Modbus()
    await modbus_stream.connect("192.168.1.100:502")
    
    count = 0
    async for event in modbus_stream.stream():
        print(f"  📊 Modbus: {event.data}")
        count += 1
        if count >= 3:
            modbus_stream.stop()
            break
    
    await modbus_stream.disconnect()
    print()
    
    # text4mqtt
    print("--- text4mqtt Stream (3 messages) ---")
    mqtt_stream = Text4MQTT()
    await mqtt_stream.connect("mqtt://broker:1883")
    mqtt_stream.add_subscription("sensors/#")
    
    count = 0
    async for event in mqtt_stream.stream():
        print(f"  📨 MQTT: {event.data}")
        count += 1
        if count >= 3:
            mqtt_stream.stop()
            break
    
    await mqtt_stream.disconnect()
    print()
    
    # text4serial
    print("--- text4serial Stream (3 lines) ---")
    serial_stream = Text4Serial()
    await serial_stream.connect("/dev/ttyUSB0:9600")
    
    count = 0
    async for event in serial_stream.stream():
        print(f"  📟 Serial: {event.data}")
        count += 1
        if count >= 3:
            serial_stream.stop()
            break
    
    await serial_stream.disconnect()
    
    return True


# ============================================================================
# Main Execution
# ============================================================================

def main():
    """Execute all demos"""
    print("\n" + "🚀" * 35)
    print("\nNLP2CMD v0.4.0 - text4X COMMUNICATION DEMO")
    print("HTML • Markdown • SVG • Modbus • MQTT • USB • HDMI • Serial")
    print("\n" + "🚀" * 35)
    
    demos = [
        ("Demo 1: HTML Converters", demo_html_converters),
        ("Demo 2: Markdown Converters", demo_markdown_converters),
        ("Demo 3: SVG Converters", demo_svg_converters),
        ("Demo 4: Modbus Converters", demo_modbus_converters),
        ("Demo 5: MQTT Converters", demo_mqtt_converters),
        ("Demo 6: USB Converters", demo_usb_converters),
        ("Demo 7: HDMI Converters", demo_hdmi_converters),
        ("Demo 8: Serial Converters", demo_serial_converters),
    ]
    
    results = []
    
    for name, demo_func in demos:
        try:
            success = demo_func()
            results.append((name, success))
            print(f"\n✅ {name} - SUKCES")
        except Exception as e:
            print(f"\n❌ {name} - BŁĄD: {e}")
            results.append((name, False))
            import traceback
            traceback.print_exc()
    
    # Async demos
    print("\n" + "="*70)
    print("🔄 ASYNC STREAMING DEMOS")
    print("="*70)
    
    try:
        asyncio.run(demo_text4x_streaming())
        results.append(("Demo 9: text4X Streaming", True))
        print(f"\n✅ Demo 9: text4X Streaming - SUKCES")
    except Exception as e:
        print(f"\n❌ Demo 9: text4X Streaming - BŁĄD: {e}")
        results.append(("Demo 9: text4X Streaming", False))
    
    # Summary
    print_header("PODSUMOWANIE", "🎉")
    
    success_count = sum(1 for _, success in results if success)
    
    print(f"✅ Wykonano: {success_count}/{len(results)} demos\n")
    
    for i, (name, success) in enumerate(results, 1):
        status = "✅" if success else "❌"
        print(f"  {i:2}. {status} {name}")
    
    print(f"\n📁 Artefakty zapisane w: /tmp/nlp2cmd-text4x/")
    
    print("\n" + "="*70)
    print("\n🎉 Demo text4X zakończone!")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏸  Demo przerwane przez użytkownika")
    except Exception as e:
        print(f"\n\n❌ Błąd krytyczny: {e}")
        import traceback
        traceback.print_exc()
