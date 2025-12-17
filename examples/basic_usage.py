#!/usr/bin/env python3
"""
Podstawowe przykłady użycia NLP2CMD.

Ten skrypt demonstruje jak używać poszczególnych konwerterów.
"""

from nlp2cmd import Text2Env, Text2Bash, Text2Makefile, Text2Docker, Pipeline


def demo_text2env():
    """Przykład użycia Text2Env"""
    print("=" * 60)
    print("TEXT2ENV - Zarządzanie plikami .env")
    print("=" * 60)
    
    # Stwórz instancję
    env = Text2Env(env_file="example.env", dry_run=True)
    
    # Różne operacje
    commands = [
        "ustaw PORT na 8080",
        "dodaj DATABASE_URL z wartością postgres://localhost/mydb",
        "zmień DEBUG na true",
        "usuń SECRET_KEY",
    ]
    
    for cmd in commands:
        print(f"\n➜ {cmd}")
        result = env.execute(cmd)
        print(f"  Komenda: {result.command}")
        print(f"  Status: {'✓ OK' if result.success else '✗ BŁĄD'}")
        if result.output:
            print(f"  Output: {result.output}")


def demo_text2bash():
    """Przykład użycia Text2Bash"""
    print("\n" + "=" * 60)
    print("TEXT2BASH - Generowanie skryptów bash")
    print("=" * 60)
    
    bash = Text2Bash(dry_run=True)
    
    commands = [
        "pokaż wszystkie pliki",
        "znajdź pliki txt",
        "pokaż 10 największych plików",
        "poczekaj 5 sekund",
    ]
    
    for cmd in commands:
        print(f"\n➜ {cmd}")
        result = bash.execute(cmd)
        print(f"  Komenda: {result.command}")
        print(f"  Status: {'✓ OK' if result.success else '✗ BŁĄD'}")


def demo_text2makefile():
    """Przykład użycia Text2Makefile"""
    print("\n" + "=" * 60)
    print("TEXT2MAKEFILE - Uruchamianie make")
    print("=" * 60)
    
    make = Text2Makefile(makefile="Makefile", dry_run=True)
    
    commands = [
        "zbuduj aplikację",
        "uruchom testy",
        "zbuduj obraz docker",
    ]
    
    for cmd in commands:
        print(f"\n➜ {cmd}")
        result = make.execute(cmd)
        print(f"  Komenda: {result.command}")
        print(f"  Status: {'✓ OK' if result.success else '✗ BŁĄD'}")


def demo_text2docker():
    """Przykład użycia Text2Docker"""
    print("\n" + "=" * 60)
    print("TEXT2DOCKER - Zarządzanie Docker")
    print("=" * 60)
    
    docker = Text2Docker(dry_run=True)
    
    commands = [
        "uruchom postgres na porcie 5432",
        "uruchom redis",
        "pokaż działające kontenery",
        "zatrzymaj postgres",
    ]
    
    for cmd in commands:
        print(f"\n➜ {cmd}")
        result = docker.execute(cmd)
        print(f"  Komenda: {result.command}")
        print(f"  Status: {'✓ OK' if result.success else '✗ BŁĄD'}")


def demo_pipeline():
    """Przykład użycia Pipeline"""
    print("\n" + "=" * 60)
    print("PIPELINE - Łączenie modułów")
    print("=" * 60)
    
    # Stwórz pipeline
    pipeline = Pipeline()
    pipeline.add_module("env", Text2Env(dry_run=True))
    pipeline.add_module("docker", Text2Docker(dry_run=True))
    pipeline.add_module("bash", Text2Bash(dry_run=True))
    
    # Wykonaj sekwencję
    steps = [
        ("env", "ustaw DATABASE_URL na postgres://localhost/mydb"),
        ("docker", "uruchom postgres na porcie 5432"),
        ("bash", "poczekaj 5 sekund"),
        ("bash", "pokaż działające procesy"),
    ]
    
    print("\n📋 Wykonuję pipeline:")
    for i, (module, cmd) in enumerate(steps, 1):
        print(f"  {i}. [{module}] {cmd}")
    
    results = pipeline.execute(steps)
    
    print("\n📊 Wyniki:")
    for i, result in enumerate(results, 1):
        status = "✓" if result.success else "✗"
        print(f"  {i}. {status} {result.command}")
    
    # Podsumowanie
    summary = pipeline.get_summary()
    print(f"\n📈 Podsumowanie:")
    print(f"  Wykonano: {summary['total_executions']}")
    print(f"  Sukces: {summary['successful']}")
    print(f"  Błędy: {summary['failed']}")
    print(f"  Wskaźnik sukcesu: {summary['success_rate']:.1%}")


def main():
    """Uruchom wszystkie demo"""
    print("\n🚀 NLP2CMD - Przykłady użycia\n")
    
    try:
        demo_text2env()
        demo_text2bash()
        demo_text2makefile()
        demo_text2docker()
        demo_pipeline()
        
        print("\n" + "=" * 60)
        print("✓ Wszystkie przykłady wykonane pomyślnie!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Błąd: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
