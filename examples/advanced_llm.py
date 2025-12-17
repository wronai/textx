#!/usr/bin/env python3
"""
Zaawansowany przykład użycia NLP2CMD z modelami LLM.

Ten skrypt pokazuje jak używać małych modeli (Phi-2, TinyLlama)
do konwersji bardziej złożonych komend.
"""

from nlp2cmd import Text2Bash, Text2Docker, Pipeline
from nlp2cmd.core.model import ModelWrapper


def demo_with_phi2():
    """Przykład z modelem Phi-2"""
    print("=" * 60)
    print("Użycie modelu Phi-2 (2.7B parametrów)")
    print("=" * 60)
    
    # Uwaga: To wymaga pobrania modelu (może zająć chwilę)
    bash = Text2Bash(
        model_name="phi-2",  # Alias dla microsoft/phi-2
        device="cpu",  # Zmień na "cuda" jeśli masz GPU
        dry_run=True
    )
    
    # Bardziej złożone komendy
    commands = [
        "znajdź wszystkie pliki python zmodyfikowane w ostatnich 7 dniach",
        "zlicz linie kodu we wszystkich plikach javascript",
        "skopiuj wszystkie obrazy jpg i png do folderu backup",
        "znajdź 5 największych plików w katalogu home",
    ]
    
    print("\n🤖 Generowanie komend z użyciem LLM:\n")
    
    for cmd in commands:
        print(f"➜ {cmd}")
        result = bash.execute(cmd)
        print(f"  ⚙️  {result.command}")
        print(f"  {'✓' if result.success else '✗'} Status: {'OK' if result.success else 'ERROR'}")
        print()


def demo_model_comparison():
    """Porównanie różnych modeli"""
    print("=" * 60)
    print("Porównanie modeli")
    print("=" * 60)
    
    models = ["phi-2", "tinyllama"]
    test_command = "znajdź wszystkie pliki większe niż 100MB"
    
    print(f"\n📝 Komenda: '{test_command}'\n")
    
    for model in models:
        print(f"🤖 Model: {model}")
        
        try:
            bash = Text2Bash(
                model_name=model,
                device="cpu",
                dry_run=True
            )
            
            result = bash.execute(test_command)
            print(f"  ⚙️  Wygenerowana komenda: {result.command}")
            print(f"  {'✓' if result.success else '✗'} Status")
        except Exception as e:
            print(f"  ✗ Błąd: {e}")
        
        print()


def demo_custom_model():
    """Przykład z własnym modelem"""
    print("=" * 60)
    print("Użycie własnego modelu")
    print("=" * 60)
    
    # Możesz użyć dowolnego modelu z HuggingFace
    # Np. Bielik (polski model)
    print("\n🇵🇱 Przykład z polskim modelem Bielik:\n")
    
    try:
        bash = Text2Bash(
            model_name="speakleash/Bielik-7B-v0.1",  # Polski model 7B
            device="cpu",
            use_8bit=True,  # 8-bit quantization dla oszczędności pamięci
            dry_run=True
        )
        
        polish_commands = [
            "wyświetl ostatnie 20 linii z pliku log",
            "sprawdź ile miejsca zostało na dysku",
            "znajdź wszystkie foldery większe niż 1GB",
        ]
        
        for cmd in polish_commands:
            print(f"➜ {cmd}")
            result = bash.execute(cmd)
            print(f"  ⚙️  {result.command}")
            print(f"  {'✓' if result.success else '✗'}\n")
            
    except Exception as e:
        print(f"✗ Nie udało się załadować modelu: {e}")
        print("  Upewnij się że masz wystarczająco pamięci RAM/GPU")


def demo_model_info():
    """Informacje o modelu"""
    print("=" * 60)
    print("Informacje o załadowanym modelu")
    print("=" * 60)
    
    try:
        model = ModelWrapper(
            model_name="phi-2",
            device="cpu"
        )
        
        info = model.get_model_info()
        
        print("\n📊 Szczegóły modelu:")
        print(f"  Nazwa: {info['model_name']}")
        print(f"  Urządzenie: {info['device']}")
        print(f"  Parametry: {info['num_parameters_millions']:.1f}M")
        print(f"  Typ danych: {info['dtype']}")
        print(f"  8-bit quantization: {info['use_8bit']}")
        
    except Exception as e:
        print(f"\n✗ Nie można załadować modelu: {e}")


def demo_direct_model_usage():
    """Bezpośrednie użycie modelu"""
    print("\n" + "=" * 60)
    print("Bezpośrednie użycie ModelWrapper")
    print("=" * 60)
    
    try:
        model = ModelWrapper(model_name="phi-2", device="cpu")
        
        # Bezpośrednie generowanie
        prompt = """Przekonwertuj komendę na bash:
Input: pokaż 10 ostatnich plików
Output:"""
        
        output = model.generate(
            prompt=prompt,
            max_new_tokens=50,
            temperature=0.2
        )
        
        print(f"\n📝 Prompt:\n{prompt}")
        print(f"\n🤖 Output:\n{output}")
        
    except Exception as e:
        print(f"\n✗ Błąd: {e}")


def demo_batch_processing():
    """Przetwarzanie wsadowe"""
    print("\n" + "=" * 60)
    print("Przetwarzanie wsadowe z modelem")
    print("=" * 60)
    
    bash = Text2Bash(model_name="phi-2", device="cpu", dry_run=True)
    
    commands = [
        "pokaż pliki",
        "znajdź readme",
        "zlicz pliki txt",
        "sprawdź użycie dysku",
        "pokaż procesy python",
    ]
    
    print("\n🔄 Przetwarzanie wsadowe:\n")
    
    results = []
    for i, cmd in enumerate(commands, 1):
        print(f"[{i}/{len(commands)}] {cmd}")
        result = bash.execute(cmd)
        results.append(result)
    
    # Statystyki
    success_count = sum(1 for r in results if r.success)
    print(f"\n✓ Sukces: {success_count}/{len(results)}")


def main():
    """Uruchom wszystkie demo"""
    print("\n🚀 NLP2CMD - Zaawansowane przykłady z LLM\n")
    
    print("⚠️  UWAGA: Te przykłady wymagają pobrania modeli LLM.")
    print("   Pierwsze uruchomienie może potrwać kilka minut.\n")
    
    try:
        # Podstawowe demo
        # demo_with_phi2()
        
        # Porównanie modeli
        # demo_model_comparison()
        
        # Polski model
        # demo_custom_model()
        
        # Informacje o modelu
        demo_model_info()
        
        # Bezpośrednie użycie
        # demo_direct_model_usage()
        
        # Batch processing
        # demo_batch_processing()
        
        print("\n" + "=" * 60)
        print("✓ Demo zakończone!")
        print("=" * 60)
        print("\n💡 TIP: Odkomentuj poszczególne demo w funkcji main()")
        print("   aby przetestować różne funkcje.")
        
    except Exception as e:
        print(f"\n✗ Błąd: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
