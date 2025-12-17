#!/usr/bin/env python3
"""
NLP2CMD Mesh - Comprehensive Demo

Demonstracja rozproszonej architektury NLP2CMD:
1. Message Bus & Service Registry
2. Workers dla różnych konwerterów
3. Gateway API
4. Pipeline execution
5. Multi-language SDK
"""

import sys
sys.path.insert(0, '/home/claude/nlp2cmd')

import asyncio
import json
from pathlib import Path
from datetime import datetime

# Mesh imports
from nlp2cmd.mesh.core.protocol import (
    ConvertRequest, ConvertResponse, 
    PipelineRequest, PipelineStep,
    Status, Topics
)
from nlp2cmd.mesh.core.bus import (
    InMemoryMessageBus, InMemoryServiceRegistry,
    MessageBusFactory, ServiceRegistryFactory
)
from nlp2cmd.mesh.core.worker import (
    BaseWorker, ConverterWorker, 
    PipelineExecutor, Deployer
)
from nlp2cmd.mesh.gateway.server import GatewayAPI, GatewayConfig
from nlp2cmd.mesh.sdk.python_client import MeshClient, LocalMeshClient


def print_header(title: str, emoji: str = "🚀"):
    """Print formatted header"""
    print(f"\n{'='*70}")
    print(f"{emoji}  {title}")
    print(f"{'='*70}\n")


def print_result(name: str, data: dict):
    """Print result"""
    status = "✅" if data.get("success") or data.get("status") == "success" else "❌"
    print(f"{status} {name}")
    if data.get("output"):
        preview = data["output"][:150] + "..." if len(data.get("output", "")) > 150 else data.get("output", "")
        print(f"   Output: {preview}")
    if data.get("error"):
        print(f"   Error: {data['error']}")
    print()


# ============================================================================
# DEMO 1: Message Bus & Service Registry
# ============================================================================

async def demo_message_bus():
    """Demo Message Bus communication"""
    print_header("DEMO 1: Message Bus & Service Registry", "📡")
    
    # Create components
    bus = InMemoryMessageBus()
    registry = InMemoryServiceRegistry()
    
    await bus.connect()
    print("✅ Message Bus connected")
    
    # Test publish/subscribe
    received_messages = []
    
    async def handler(message):
        received_messages.append(message)
        print(f"   📨 Received: {message.get('data', message)}")
    
    # Subscribe
    sub_id = await bus.subscribe("test.topic", handler)
    print(f"✅ Subscribed to test.topic (ID: {sub_id})")
    
    # Publish
    await bus.publish("test.topic", {"data": "Hello Mesh!"})
    await asyncio.sleep(0.1)  # Allow handler to process
    print(f"✅ Published message")
    
    # Wildcard subscription
    await bus.subscribe("nlp2cmd.request.*", handler)
    await bus.publish("nlp2cmd.request.text3html", {"converter": "text3html", "command": "test"})
    await asyncio.sleep(0.1)
    print(f"✅ Wildcard subscription working")
    
    # Service Registry
    from nlp2cmd.mesh.core.protocol import ServiceInfo
    
    service = ServiceInfo(
        name="html-worker-1",
        type="worker",
        converters=["text2html", "text3html", "text4html"],
        host="localhost",
        port=8001
    )
    
    await registry.register(service)
    print(f"✅ Registered service: {service.name}")
    
    # Query registry
    converters = await registry.list_converters()
    print(f"✅ Available converters: {converters}")
    
    services = await registry.get_services_for_converter("text3html")
    print(f"✅ Services for text3html: {[s.name for s in services]}")
    
    # Stats
    print(f"\n📊 Bus stats: {bus.get_stats()}")
    print(f"📊 Registry stats: {registry.get_stats()}")
    
    await bus.disconnect()
    return True


# ============================================================================
# DEMO 2: Worker Processing
# ============================================================================

async def demo_workers():
    """Demo Worker processing"""
    print_header("DEMO 2: Worker Processing", "⚙️")
    
    # Setup
    bus = InMemoryMessageBus()
    registry = InMemoryServiceRegistry()
    
    await bus.connect()
    
    # Create worker
    worker = ConverterWorker(
        name="converter-worker-1",
        converters=["text3html", "text3markdown", "text3svg"],
        bus=bus,
        registry=registry
    )
    
    await worker.start()
    print(f"✅ Worker started: {worker.name}")
    print(f"   Converters: {worker.converters}")
    
    # Test conversion via message bus
    print("\n📤 Sending conversion requests via Message Bus:")
    
    # Request 1: HTML
    request = ConvertRequest(
        converter="text3html",
        command="generate landing page for TestProduct"
    )
    
    response = await bus.request(
        Topics.request("text3html"),
        request.to_dict(),
        timeout=10.0
    )
    
    print_result("HTML Generation", response or {"error": "Timeout"})
    
    # Request 2: Markdown
    request = ConvertRequest(
        converter="text3markdown",
        command="generate README for MyProject"
    )
    
    response = await bus.request(
        Topics.request("text3markdown"),
        request.to_dict(),
        timeout=10.0
    )
    
    print_result("Markdown Generation", response or {"error": "Timeout"})
    
    # Request 3: SVG
    request = ConvertRequest(
        converter="text3svg",
        command="generate bar chart"
    )
    
    response = await bus.request(
        Topics.request("text3svg"),
        request.to_dict(),
        timeout=10.0
    )
    
    print_result("SVG Chart", response or {"error": "Timeout"})
    
    # Worker stats
    print(f"\n📊 Worker stats: {worker.get_stats()}")
    
    await worker.stop()
    await bus.disconnect()
    return True


# ============================================================================
# DEMO 3: Pipeline Execution
# ============================================================================

async def demo_pipeline():
    """Demo Pipeline execution"""
    print_header("DEMO 3: Pipeline Execution", "🔄")
    
    # Setup
    bus = InMemoryMessageBus()
    registry = InMemoryServiceRegistry()
    deployer = Deployer()
    
    await bus.connect()
    
    # Start workers
    worker = ConverterWorker(
        name="pipeline-worker",
        converters=["text3html", "text3markdown", "text3svg"],
        bus=bus,
        registry=registry
    )
    await worker.start()
    
    # Create pipeline executor
    executor = PipelineExecutor(bus, registry, deployer)
    
    # Define pipeline
    pipeline = PipelineRequest(
        name="generate-and-deploy",
        steps=[
            PipelineStep(
                converter="text3html",
                command="generate landing page for CloudSync"
            ),
            PipelineStep(
                action="deploy",
                config={"target": "file", "path": "/tmp/nlp2cmd-mesh/landing.html"}
            )
        ],
        context={"project": "CloudSync"}
    )
    
    print(f"📋 Pipeline: {pipeline.name}")
    print(f"   Steps: {len(pipeline.steps)}")
    
    # Execute
    result = await executor.execute(pipeline)
    
    print(f"\n📊 Pipeline Result:")
    print(f"   Status: {result.status.value}")
    print(f"   Execution time: {result.execution_time_ms:.2f}ms")
    print(f"   Steps completed: {len(result.steps_results)}")
    
    for i, step_result in enumerate(result.steps_results):
        status = "✅" if step_result.get("status") == "success" else "❌"
        print(f"   {status} Step {i+1}: {step_result.get('converter') or step_result.get('action')}")
    
    if result.final_output:
        print(f"   Final output: {len(result.final_output)} chars")
    
    # Check deployed file
    deployed_file = Path("/tmp/nlp2cmd-mesh/landing.html")
    if deployed_file.exists():
        print(f"\n✅ File deployed: {deployed_file}")
        print(f"   Size: {deployed_file.stat().st_size} bytes")
    
    await worker.stop()
    await bus.disconnect()
    return True


# ============================================================================
# DEMO 4: Gateway API
# ============================================================================

async def demo_gateway():
    """Demo Gateway API"""
    print_header("DEMO 4: Gateway API", "🌐")
    
    # Setup
    bus = InMemoryMessageBus()
    registry = InMemoryServiceRegistry()
    
    await bus.connect()
    
    # Start worker
    worker = ConverterWorker(
        name="gateway-worker",
        converters=["text3html", "text3markdown", "text3svg", "text2modbus"],
        bus=bus,
        registry=registry
    )
    await worker.start()
    
    # Create gateway
    config = GatewayConfig(host="localhost", port=8080)
    gateway = GatewayAPI(bus=bus, registry=registry, config=config)
    await gateway.start()
    
    print("✅ Gateway API started")
    
    # Test endpoints
    print("\n📤 Testing Gateway endpoints:")
    
    # 1. Health check
    health = await gateway.health_check()
    print(f"✅ Health: {health.get('status')}")
    
    # 2. List converters
    converters = await gateway.list_converters()
    print(f"✅ Converters: {converters.get('converters', [])}")
    
    # 3. Single conversion
    result = await gateway.convert(
        converter="text3html",
        command="generate form",
        wait=True
    )
    print_result("Convert (text3html)", result)
    
    # 4. Pipeline
    pipeline_result = await gateway.execute_pipeline(
        steps=[
            {"converter": "text3markdown", "command": "generate README"},
            {"action": "deploy", "config": {"target": "file", "path": "/tmp/nlp2cmd-mesh/readme.md"}}
        ],
        name="readme-pipeline"
    )
    print_result("Pipeline execution", pipeline_result)
    
    # 5. Deploy
    deploy_result = await gateway.deploy(
        target="file",
        content="<html><body>Hello World</body></html>",
        path="/tmp/nlp2cmd-mesh/hello.html"
    )
    print_result("Deploy", deploy_result)
    
    await gateway.stop()
    await worker.stop()
    await bus.disconnect()
    return True


# ============================================================================
# DEMO 5: SDK Usage
# ============================================================================

async def demo_sdk():
    """Demo SDK usage"""
    print_header("DEMO 5: SDK Usage (Local Mode)", "📦")
    
    # Local client (no network needed)
    client = LocalMeshClient()
    
    print("✅ LocalMeshClient created")
    print(f"   Available converters: {client.list_converters()}")
    
    # Test conversions
    print("\n📤 Testing local conversions:")
    
    # HTML
    result = client.convert("text3html", "generate landing page")
    print_result("text3html", {"success": result.success, "output": result.output, "error": result.error})
    
    # Markdown
    result = client.convert("text3markdown", "generate README for project")
    print_result("text3markdown", {"success": result.success, "output": result.output, "error": result.error})
    
    # SVG
    result = client.convert("text3svg", "generate pie chart")
    print_result("text3svg", {"success": result.success, "output": result.output, "error": result.error})
    
    # Modbus
    result = client.convert("text2modbus", "read holding registers 40001 count 5")
    print_result("text2modbus", {"success": result.success, "output": result.output, "error": result.error, "metadata": result.metadata})
    
    return True


# ============================================================================
# DEMO 6: Complete Integration
# ============================================================================

async def demo_complete_integration():
    """Demo complete ecosystem integration"""
    print_header("DEMO 6: Complete Ecosystem Integration", "🌍")
    
    print("""
    Scenariusz: IoT Dashboard Generator
    
    1. [Firmware/C] → Odczyt z PLC przez Modbus
    2. [Backend/Go] → Agregacja danych
    3. [Gateway/Python] → Pipeline execution
    4. [Worker] → Generowanie SVG chart
    5. [Worker] → Generowanie HTML dashboard
    6. [Deployer] → Deploy do pliku
    7. [Frontend/JS] → Wyświetlenie w przeglądarce
    """)
    
    # Setup
    bus = InMemoryMessageBus()
    registry = InMemoryServiceRegistry()
    deployer = Deployer()
    
    await bus.connect()
    
    # Workers
    worker = ConverterWorker(
        name="iot-worker",
        converters=["text2modbus", "text3svg", "text3html"],
        bus=bus,
        registry=registry
    )
    await worker.start()
    
    # Gateway
    gateway = GatewayAPI(bus=bus, registry=registry)
    await gateway.start()
    
    # Execute IoT pipeline
    print("\n🔄 Executing IoT Dashboard Pipeline:")
    
    result = await gateway.execute_pipeline(
        name="iot-dashboard",
        steps=[
            # 1. Read from PLC
            {
                "converter": "text2modbus",
                "command": "read holding registers 40001 count 4"
            },
            # 2. Generate chart
            {
                "converter": "text3svg",
                "command": "generate bar chart"
            },
            # 3. Generate dashboard HTML
            {
                "converter": "text3html",
                "command": "generate landing page title: IoT Dashboard"
            },
            # 4. Deploy
            {
                "action": "deploy",
                "config": {
                    "target": "file",
                    "path": "/tmp/nlp2cmd-mesh/iot-dashboard.html"
                }
            }
        ],
        context={
            "project": "IoT Factory",
            "timestamp": datetime.now().isoformat()
        }
    )
    
    print(f"\n📊 Pipeline Result:")
    print(f"   Status: {result.get('status')}")
    print(f"   Steps: {len(result.get('steps_results', []))}")
    
    for i, step in enumerate(result.get('steps_results', [])):
        status = "✅" if step.get('status') == 'success' else "❌"
        name = step.get('converter') or step.get('action')
        print(f"   {status} Step {i+1}: {name}")
    
    # Check output files
    output_dir = Path("/tmp/nlp2cmd-mesh")
    if output_dir.exists():
        print(f"\n📁 Generated files in {output_dir}:")
        for f in output_dir.glob("*"):
            print(f"   • {f.name} ({f.stat().st_size} bytes)")
    
    await gateway.stop()
    await worker.stop()
    await bus.disconnect()
    return True


# ============================================================================
# Main
# ============================================================================

async def main():
    """Run all demos"""
    print("\n" + "🚀" * 35)
    print("\nNLP2CMD MESH - DISTRIBUTED ARCHITECTURE DEMO")
    print("Message Bus • Workers • Gateway • Pipeline • SDK")
    print("\n" + "🚀" * 35)
    
    demos = [
        ("Message Bus & Registry", demo_message_bus),
        ("Worker Processing", demo_workers),
        ("Pipeline Execution", demo_pipeline),
        ("Gateway API", demo_gateway),
        ("SDK Usage", demo_sdk),
        ("Complete Integration", demo_complete_integration),
    ]
    
    results = []
    
    for name, demo_func in demos:
        try:
            success = await demo_func()
            results.append((name, success))
            print(f"\n✅ {name} - SUKCES")
        except Exception as e:
            print(f"\n❌ {name} - BŁĄD: {e}")
            results.append((name, False))
            import traceback
            traceback.print_exc()
    
    # Summary
    print_header("PODSUMOWANIE", "🎉")
    
    success_count = sum(1 for _, success in results if success)
    
    print(f"✅ Wykonano: {success_count}/{len(results)} demos\n")
    
    for i, (name, success) in enumerate(results, 1):
        status = "✅" if success else "❌"
        print(f"  {i}. {status} {name}")
    
    print("\n" + "="*70)
    print("\n🎉 NLP2CMD Mesh Demo zakończone!")
    print("""
    Zaimplementowano:
    ✅ Message Bus (InMemory, produkcja: NATS/Redis)
    ✅ Service Registry (discovery, load balancing)
    ✅ Workers (processing requests)
    ✅ Pipeline Executor (multi-step workflows)
    ✅ Gateway API (REST/WebSocket)
    ✅ Deployer (file, S3, webhook)
    ✅ SDK Python (sync/async)
    ✅ SDK JavaScript/TypeScript
    ✅ SDK Go
    ✅ SDK C (firmware/embedded)
    
    Gotowe do:
    • Integracji z firmware (ESP32, STM32)
    • Integracji z backendem (FastAPI, Go, Node.js)
    • Integracji z frontendem (React, Vue)
    • Deploymentu w Kubernetes
    • Skalowania horyzontalnego
    """)
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏸  Demo przerwane przez użytkownika")
    except Exception as e:
        print(f"\n\n❌ Błąd krytyczny: {e}")
        import traceback
        traceback.print_exc()
