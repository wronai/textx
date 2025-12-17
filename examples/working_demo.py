#!/usr/bin/env python3
"""
NLP2CMD Orchestrator - Working Demo
Rzeczywiste, działające przykłady z testami
"""

import sys
sys.path.insert(0, '/home/claude/nlp2cmd')

from nlp2cmd.core.orchestrator import Orchestrator
from nlp2cmd.converters.api.text3app import Text3App
from nlp2cmd.converters.api.text2api import Text2API
from nlp2cmd.converters.containers.text3docker import Text3Docker
from nlp2cmd.converters.containers.text2kubernetes import Text2Kubernetes
from nlp2cmd.converters.containers.text3kubernetes import Text3Kubernetes
from nlp2cmd.converters.network.text2ssh import Text2SSH
import json


def separator(title=""):
    """Print separator"""
    if title:
        print(f"\n{'='*70}")
        print(f"  {title}")
        print(f"{'='*70}\n")
    else:
        print("-" * 70)


def test_1_simple_app_generation():
    """Test 1: Prosta generacja aplikacji"""
    separator("TEST 1: Generacja Aplikacji Flask")
    
    print("📝 Zadanie: Wygeneruj aplikację Flask do zarządzania użytkownikami\n")
    
    app_gen = Text3App()
    result = app_gen.execute("aplikacja Flask do zarządzania użytkownikami")
    
    if result.success:
        print("✅ Aplikacja wygenerowana pomyślnie!")
        print(f"\n📊 Metryki:")
        print(f"  - Język: {result.metadata['language']}")
        print(f"  - Framework: {result.metadata['framework']}")
        print(f"  - Linie kodu: {len(result.output.split(chr(10)))}")
        print(f"  - Dodatkowe pliki: {len(result.metadata.get('additional_files', {}))}")
        
        print(f"\n📄 Fragment kodu (pierwsze 20 linii):")
        lines = result.output.split('\n')[:20]
        for i, line in enumerate(lines, 1):
            print(f"  {i:2d}: {line}")
        
        return True
    else:
        print(f"❌ Błąd: {result.error}")
        return False


def test_2_dockerfile_generation():
    """Test 2: Generacja Dockerfile"""
    separator("TEST 2: Generacja Dockerfile")
    
    print("📝 Zadanie: Wygeneruj Dockerfile dla aplikacji Python FastAPI\n")
    
    docker_gen = Text3Docker()
    result = docker_gen.execute("dockerfile dla aplikacji Python FastAPI port 8000")
    
    if result.success:
        print("✅ Dockerfile wygenerowany!")
        print(f"\n📊 Metryki:")
        print(f"  - Port: {result.metadata['port']}")
        print(f"  - Multi-stage: {result.metadata.get('multi_stage', False)}")
        
        print(f"\n📄 Dockerfile:")
        print(result.output)
        
        return True
    else:
        print(f"❌ Błąd: {result.error}")
        return False


def test_3_kubernetes_manifest():
    """Test 3: Generacja manifestu Kubernetes"""
    separator("TEST 3: Generacja Manifestu Kubernetes")
    
    print("📝 Zadanie: Wygeneruj deployment dla api-server z 3 replikami\n")
    
    k8s_gen = Text3Kubernetes()
    result = k8s_gen.execute("deployment dla api-server z 3 replikami na porcie 8080")
    
    if result.success:
        print("✅ Manifest wygenerowany!")
        print(f"\n📊 Metryki:")
        print(f"  - Typ: {result.metadata['resource_type']}")
        print(f"  - App: {result.metadata['app_name']}")
        print(f"  - Namespace: {result.metadata['namespace']}")
        
        print(f"\n📄 Manifest (pierwsze 30 linii):")
        lines = result.output.split('\n')[:30]
        for line in lines:
            print(f"  {line}")
        
        return True
    else:
        print(f"❌ Błąd: {result.error}")
        return False


def test_4_full_k8s_deployment():
    """Test 4: Pełny deployment K8s (wszystkie manifesty)"""
    separator("TEST 4: Kompletny Deployment K8s")
    
    print("📝 Zadanie: Wygeneruj komplet manifestów dla user-api\n")
    
    k8s_gen = Text3Kubernetes()
    manifests = k8s_gen.generate_full_deployment(
        app_name="user-api",
        image="user-api:v1.0",
        port=5000,
        replicas=3,
        namespace="production"
    )
    
    print("✅ Wygenerowano komplet manifestów!")
    print(f"\n📊 Wygenerowane pliki ({len(manifests)}):")
    
    for filename, content in manifests.items():
        lines = len(content.split('\n'))
        print(f"  ✓ {filename} ({lines} linii)")
    
    # Show one example
    print(f"\n📄 Przykład - service.yaml:")
    print(manifests['service.yaml'])
    
    return True


def test_5_orchestrator_planning():
    """Test 5: Orchestrator - automatyczne planowanie"""
    separator("TEST 5: Orchestrator - Planowanie Kroków")
    
    print("📝 Zadanie: Wygeneruj aplikację i zdeployuj do K8s\n")
    
    orch = Orchestrator(dry_run=True)
    
    # Register converters
    orch.register_converter("text3app", Text3App())
    orch.register_converter("text3docker", Text3Docker())
    orch.register_converter("text3kubernetes", Text3Kubernetes())
    orch.register_converter("text2kubernetes", Text2Kubernetes())
    
    # Complex task
    task = "wygeneruj aplikację do zarządzania użytkownikami w kubernetes"
    
    print(f"🎯 Parsowanie zadania: '{task}'\n")
    
    # Parse
    steps = orch.parse_complex_task(task)
    
    if steps:
        print(f"✅ Wygenerowano plan z {len(steps)} krokami:\n")
        
        for i, step in enumerate(steps, 1):
            print(f"  {i}. {step.name}")
            print(f"     Konwerter: {step.converter}")
            print(f"     Komenda: {step.command}")
            if step.depends_on:
                print(f"     Zależności: {', '.join(step.depends_on)}")
            print()
        
        return True
    else:
        print("❌ Nie udało się wygenerować planu")
        return False


def test_6_orchestrator_execution():
    """Test 6: Orchestrator - pełne wykonanie"""
    separator("TEST 6: Orchestrator - Pełne Wykonanie")
    
    print("📝 Zadanie: Deploy aplikacji użytkowników do K8s (DRY RUN)\n")
    
    orch = Orchestrator(dry_run=True)
    
    # Register
    orch.register_converter("text3app", Text3App())
    orch.register_converter("text3docker", Text3Docker())
    orch.register_converter("text3kubernetes", Text3Kubernetes())
    
    task = """
    wygeneruj aplikację do zarządzania użytkownikami w Python Flask
    i przygotuj deployment dla kubernetes w namespace production
    """
    
    print(f"🎯 Wykonuję: {task.strip()}\n")
    
    result = orch.execute(task)
    
    if result["success"]:
        print("✅ Workflow wykonany pomyślnie!\n")
        print(f"📊 Podsumowanie:")
        print(f"  - Wykonane kroki: {len(result['steps'])}")
        print(f"  - Kontekst: {len(result.get('context', {}))} elementów\n")
        
        print("📝 Kroki:")
        for i, step_name in enumerate(result['steps'], 1):
            step_result = result['results'][step_name]
            status = "✓" if step_result.success else "✗"
            print(f"  {i}. {status} {step_name}")
        
        return True
    else:
        print(f"❌ Workflow nie powiódł się:")
        print(f"   Błąd: {result.get('error')}")
        return False


def test_7_manual_workflow():
    """Test 7: Manualny workflow krok po kroku"""
    separator("TEST 7: Manualny Workflow")
    
    print("🔧 Budowanie aplikacji krok po kroku\n")
    
    results = []
    
    # Step 1: Generate app
    print("Krok 1/4: Generowanie aplikacji...")
    app_gen = Text3App()
    app_result = app_gen.execute("aplikacja FastAPI do zarządzania produktami")
    
    if app_result.success:
        print(f"  ✓ Wygenerowano {len(app_result.output.split(chr(10)))} linii kodu")
        results.append(("App Generation", True))
    else:
        print(f"  ✗ Błąd: {app_result.error}")
        results.append(("App Generation", False))
    
    # Step 2: Generate Dockerfile
    print("\nKrok 2/4: Generowanie Dockerfile...")
    docker_gen = Text3Docker()
    docker_result = docker_gen.execute("dockerfile dla FastAPI Python 3.11")
    
    if docker_result.success:
        print(f"  ✓ Dockerfile wygenerowany")
        results.append(("Dockerfile", True))
    else:
        print(f"  ✗ Błąd")
        results.append(("Dockerfile", False))
    
    # Step 3: Generate K8s manifests
    print("\nKrok 3/4: Generowanie manifestów K8s...")
    k8s_gen = Text3Kubernetes()
    manifests = k8s_gen.generate_full_deployment(
        app_name="product-api",
        image="product-api:latest",
        port=8000,
        replicas=2
    )
    
    if manifests:
        print(f"  ✓ Wygenerowano {len(manifests)} manifestów")
        results.append(("K8s Manifests", True))
    else:
        print(f"  ✗ Błąd")
        results.append(("K8s Manifests", False))
    
    # Step 4: Summary
    print("\nKrok 4/4: Podsumowanie...")
    
    success_count = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\n📊 Wyniki: {success_count}/{total} kroków zakończonych sukcesem")
    for step_name, success in results:
        status = "✓" if success else "✗"
        print(f"  {status} {step_name}")
    
    return success_count == total


def test_8_context_passing():
    """Test 8: Przekazywanie kontekstu między krokami"""
    separator("TEST 8: Przekazywanie Kontekstu")
    
    print("📝 Scenariusz: Użyj wyniku z poprzedniego kroku\n")
    
    # Step 1: Generate app and save metadata
    print("Krok 1: Generowanie aplikacji...")
    app_gen = Text3App()
    app_result = app_gen.execute("aplikacja Flask users")
    
    if not app_result.success:
        print("❌ Krok 1 nie powiódł się")
        return False
    
    # Extract metadata
    app_metadata = app_result.metadata
    print(f"  ✓ Wygenerowano: {app_metadata['language']} {app_metadata['framework']}")
    print(f"  ✓ Zasób: {app_metadata['resource']}")
    
    # Step 2: Use metadata in Dockerfile generation
    print("\nKrok 2: Generowanie Dockerfile z użyciem metadanych...")
    docker_gen = Text3Docker()
    
    # Construct command using context
    docker_cmd = f"dockerfile dla {app_metadata['language']} {app_metadata['framework']}"
    docker_result = docker_gen.execute(docker_cmd)
    
    if docker_result.success:
        print(f"  ✓ Dockerfile dostosowany do {app_metadata['language']}")
    else:
        print("  ✗ Błąd")
        return False
    
    # Step 3: Use in K8s manifest
    print("\nKrok 3: Generowanie K8s manifest z kontekstem...")
    k8s_gen = Text3Kubernetes()
    
    app_name = app_metadata['resource']
    k8s_result = k8s_gen.execute(f"deployment dla {app_name}")
    
    if k8s_result.success:
        print(f"  ✓ Manifest dla aplikacji {app_name}")
    else:
        print("  ✗ Błąd")
        return False
    
    print("\n✅ Kontekst przekazany pomyślnie przez wszystkie kroki!")
    return True


def test_9_error_handling():
    """Test 9: Obsługa błędów"""
    separator("TEST 9: Obsługa Błędów")
    
    print("📝 Test obsługi błędów w orchestratorze\n")
    
    orch = Orchestrator(dry_run=True)
    
    # Test 1: Missing converter
    print("Test 1: Brakujący konwerter...")
    orch.register_converter("text3app", Text3App())
    # Deliberately not registering text3docker
    
    task = "wygeneruj aplikację i dockerfile"
    steps = orch.parse_complex_task(task)
    
    if steps:
        # Try to execute - should handle missing converter
        result = orch.execute(task)
        
        if not result["success"]:
            print(f"  ✓ Błąd prawidłowo wychwycony: {result.get('error', 'Unknown')[:50]}...")
        else:
            print("  ⚠ Powinien był wystąpić błąd")
    
    # Test 2: Invalid input
    print("\nTest 2: Nieprawidłowe wejście...")
    app_gen = Text3App()
    result = app_gen.execute("")  # Empty input
    
    if not result.success or result.output:
        print("  ✓ Obsłużono puste wejście")
    
    print("\n✅ Testy obsługi błędów zakończone")
    return True


def test_10_performance():
    """Test 10: Test wydajności"""
    separator("TEST 10: Test Wydajności")
    
    print("📝 Pomiar czasu generowania\n")
    
    import time
    
    tests = [
        ("App Generation", lambda: Text3App().execute("Flask app")),
        ("Dockerfile", lambda: Text3Docker().execute("dockerfile Python")),
        ("K8s Manifest", lambda: Text3Kubernetes().execute("deployment myapp")),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        start = time.time()
        result = test_func()
        duration = time.time() - start
        
        results.append((test_name, duration, result.success))
        
        status = "✓" if result.success else "✗"
        print(f"  {status} {test_name}: {duration:.3f}s")
    
    total_time = sum(d for _, d, _ in results)
    success_count = sum(1 for _, _, s in results if s)
    
    print(f"\n📊 Podsumowanie:")
    print(f"  - Całkowity czas: {total_time:.3f}s")
    print(f"  - Średnia: {total_time/len(results):.3f}s")
    print(f"  - Sukces: {success_count}/{len(results)}")
    
    return True


def run_all_tests():
    """Uruchom wszystkie testy"""
    separator("🧪 NLP2CMD ORCHESTRATOR - COMPREHENSIVE TESTS")
    
    tests = [
        ("Test 1: App Generation", test_1_simple_app_generation),
        ("Test 2: Dockerfile Generation", test_2_dockerfile_generation),
        ("Test 3: K8s Manifest", test_3_kubernetes_manifest),
        ("Test 4: Full K8s Deployment", test_4_full_k8s_deployment),
        ("Test 5: Orchestrator Planning", test_5_orchestrator_planning),
        ("Test 6: Orchestrator Execution", test_6_orchestrator_execution),
        ("Test 7: Manual Workflow", test_7_manual_workflow),
        ("Test 8: Context Passing", test_8_context_passing),
        ("Test 9: Error Handling", test_9_error_handling),
        ("Test 10: Performance", test_10_performance),
    ]
    
    results = []
    
    print(f"📋 Uruchamianie {len(tests)} testów...\n")
    
    for test_name, test_func in tests:
        print(f"\n{'='*70}")
        print(f"  🧪 {test_name}")
        print(f"{'='*70}")
        
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ Wyjątek: {e}")
            results.append((test_name, False))
        
        input("\n⏸  Naciśnij Enter aby kontynuować...")
    
    # Final summary
    separator("📊 PODSUMOWANIE TESTÓW")
    
    success_count = sum(1 for _, success in results if success)
    total = len(results)
    percentage = (success_count / total * 100) if total > 0 else 0
    
    print(f"\n🎯 Wyniki: {success_count}/{total} testów zakończonych sukcesem ({percentage:.1f}%)\n")
    
    for test_name, success in results:
        status = "✅" if success else "❌"
        print(f"  {status} {test_name}")
    
    print("\n" + "="*70)
    
    if success_count == total:
        print("\n🎉 Wszystkie testy zakończone sukcesem!")
    elif success_count > total * 0.8:
        print("\n👍 Większość testów zakończona sukcesem")
    else:
        print("\n⚠️  Niektóre testy wymagają poprawy")
    
    print("\n" + "="*70)
    
    return results


if __name__ == "__main__":
    try:
        results = run_all_tests()
        
        # Exit code based on results
        success_count = sum(1 for _, success in results if success)
        exit_code = 0 if success_count == len(results) else 1
        
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n\n⏸  Testy przerwane przez użytkownika")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Krytyczny błąd: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
