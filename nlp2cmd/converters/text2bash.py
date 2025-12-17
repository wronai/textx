"""
Text2Bash - Konwersja języka naturalnego na skryptu bash
"""

import subprocess
import re
from typing import Dict, Any, Optional, List
from nlp2cmd.core.base import BaseConverter, ConversionResult
import logging

logger = logging.getLogger(__name__)


class Text2Bash(BaseConverter):
    """
    Konwerter dla generowania i wykonywania skryptów bash.
    
    Obsługuje:
    - Proste komendy: "pokaż pliki", "skopiuj plik.txt"
    - Operacje na plikach: "znajdź pliki txt większe niż 1MB"
    - Operacje systemowe: "sprawdź użycie dysku"
    - Złożone skrypty: "dla każdego pliku txt stwórz backup"
    """
    
    # Mapowanie popularnych fraz na komendy bash
    COMMON_COMMANDS = {
        # Listowanie
        r"pokaż pliki": "ls -lh",
        r"list files": "ls -lh",
        r"pokaż wszystkie pliki": "ls -lah",
        
        # Nawigacja
        r"przejdź do (.+)": "cd {0}",
        r"go to (.+)": "cd {0}",
        
        # Wyszukiwanie
        r"znajdź (.+)": "find . -name '*{0}*'",
        r"find (.+)": "find . -name '*{0}*'",
        r"szukaj (.+)": "grep -r '{0}' .",
        
        # Informacje systemowe
        r"użycie dysku": "df -h",
        r"disk usage": "df -h",
        r"pamięć": "free -h",
        r"memory": "free -h",
        r"procesy": "ps aux",
        r"processes": "ps aux",
        
        # Operacje na plikach
        r"skopiuj (.+) do (.+)": "cp {0} {1}",
        r"copy (.+) to (.+)": "cp {0} {1}",
        r"przenieś (.+) do (.+)": "mv {0} {1}",
        r"move (.+) to (.+)": "mv {0} {1}",
        r"usuń (.+)": "rm {0}",
        r"delete (.+)": "rm {0}",
        
        # Archiwizacja
        r"spakuj (.+)": "tar -czf {0}.tar.gz {0}",
        r"compress (.+)": "tar -czf {0}.tar.gz {0}",
        r"rozpakuj (.+)": "tar -xzf {0}",
        r"extract (.+)": "tar -xzf {0}",
        
        # Sieć
        r"ping (.+)": "ping -c 4 {0}",
        r"pobierz (.+)": "wget {0}",
        r"download (.+)": "wget {0}",
        
        # Czas
        r"poczekaj (\d+) sekund": "sleep {0}",
        r"wait (\d+) seconds": "sleep {0}",
    }
    
    def __init__(
        self,
        allow_dangerous: bool = False,
        timeout: int = 30,
        **kwargs
    ):
        """
        Inicjalizacja Text2Bash.
        
        Args:
            allow_dangerous: Czy pozwolić na potencjalnie niebezpieczne komendy
            timeout: Maksymalny czas wykonania komendy (sekundy)
        """
        super().__init__(**kwargs)
        self.allow_dangerous = allow_dangerous
        self.timeout = timeout
    
    def parse_intent(self, text: str) -> Dict[str, Any]:
        """
        Parsuje intencję z tekstu.
        
        Returns:
            {
                "command": str,  # Komenda bash
                "description": str,  # Opis operacji
                "matched_pattern": str | None  # Dopasowany pattern
            }
        """
        text = text.strip().lower()
        
        # Sprawdź znane patterny
        for pattern, command_template in self.COMMON_COMMANDS.items():
            match = re.match(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                command = command_template.format(*groups) if groups else command_template
                
                return {
                    "command": command,
                    "description": text,
                    "matched_pattern": pattern
                }
        
        # Jeśli nie dopasowano i jest model, użyj modelu
        if self.model:
            return self._generate_with_model(text)
        
        # Jako fallback, zwróć surowy tekst (ryzykowne!)
        logger.warning(f"Nie znaleziono dopasowania dla: {text}")
        return {
            "command": text,
            "description": text,
            "matched_pattern": None
        }
    
    def _generate_with_model(self, text: str) -> Dict[str, Any]:
        """Generuje komendę bash używając modelu LLM"""
        system_prompt = """Jesteś ekspertem bash. Konwertuj język naturalny na komendy bash.

Zasady:
- Jedna linia kodu bash
- Bezpieczne komendy (unikaj rm -rf /, fork bombs)
- Używaj standardowych narzędzi Unix
- Bez wyjaśnień, tylko komenda

Jeśli komenda jest niebezpieczna, zwróć: DANGEROUS"""
        
        examples = [
            {
                "input": "pokaż 10 największych plików",
                "output": "du -ah . | sort -rh | head -10"
            },
            {
                "input": "znajdź pliki txt zmodyfikowane dzisiaj",
                "output": "find . -name '*.txt' -mtime 0"
            },
            {
                "input": "zlicz linie kodu w plikach python",
                "output": "find . -name '*.py' -exec wc -l {} + | tail -1"
            },
            {
                "input": "skopiuj wszystkie pliki jpg do folderu photos",
                "output": "cp *.jpg photos/"
            }
        ]
        
        command = self.model.extract_command(text, system_prompt, examples)
        
        if "DANGEROUS" in command:
            raise ValueError("Model uznał komendę za niebezpieczną")
        
        return {
            "command": command.strip(),
            "description": text,
            "matched_pattern": "llm_generated"
        }
    
    def generate_command(self, intent: Dict[str, Any]) -> str:
        """Zwraca wygenerowaną komendę bash"""
        return intent["command"]
    
    def execute(self, text: str) -> ConversionResult:
        """
        Generuje i wykonuje komendę bash.
        
        Args:
            text: Opis operacji w języku naturalnym
            
        Returns:
            Wynik wykonania
        """
        try:
            # Parse intent
            intent = self.parse_intent(text)
            command = self.generate_command(intent)
            
            # Walidacja bezpieczeństwa
            if self.safe_mode and not self.validate_command(command):
                return ConversionResult(
                    success=False,
                    command=command,
                    error="Komenda odrzucona przez walidację bezpieczeństwa"
                )
            
            # Dry run
            if self.dry_run:
                logger.info(f"[DRY RUN] {command}")
                return ConversionResult(
                    success=True,
                    command=command,
                    output=f"[DRY RUN] Would execute: {command}"
                )
            
            # Wykonaj komendę
            logger.info(f"Executing: {command}")
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            success = result.returncode == 0
            output = result.stdout if success else result.stderr
            
            conv_result = ConversionResult(
                success=success,
                command=command,
                output=output.strip(),
                error=None if success else f"Exit code: {result.returncode}",
                metadata={
                    "description": intent["description"],
                    "returncode": result.returncode,
                    "matched_pattern": intent.get("matched_pattern")
                }
            )
            
            self.log_execution(text, conv_result)
            return conv_result
            
        except subprocess.TimeoutExpired:
            return ConversionResult(
                success=False,
                command=command,
                error=f"Timeout po {self.timeout} sekundach"
            )
        except Exception as e:
            logger.error(f"Błąd wykonania: {e}")
            return ConversionResult(
                success=False,
                error=str(e),
                metadata={"input": text}
            )
    
    def generate_script(
        self,
        text: str,
        shebang: str = "#!/bin/bash"
    ) -> str:
        """
        Generuje pełny skrypt bash (bez wykonywania).
        
        Args:
            text: Opis skryptu
            shebang: Shebang line
            
        Returns:
            Pełny skrypt bash
        """
        intent = self.parse_intent(text)
        command = self.generate_command(intent)
        
        script = f"""{shebang}
# Generated by NLP2CMD
# Description: {intent['description']}

set -e  # Exit on error

{command}
"""
        return script
    
    def validate_command(self, command: str) -> bool:
        """
        Rozszerzona walidacja dla bash.
        
        Sprawdza:
        - Podstawowe niebezpieczne patterny (z BaseConverter)
        - Bash-specific niebezpieczne konstrukcje
        """
        # Podstawowa walidacja
        if not super().validate_command(command):
            return False
        
        # Bash-specific dangerous patterns
        bash_dangerous = [
            "> /dev/sd",  # Nadpisywanie dysków
            "chmod 777",  # Niebezpieczne uprawnienia
            "chmod -R 777",
            "curl ... | sh",  # Pipe do shell
            "wget ... | bash",
            "eval",  # Wykonywanie dynamicznego kodu
        ]
        
        if not self.allow_dangerous:
            for pattern in bash_dangerous:
                if pattern in command.lower():
                    logger.warning(f"Wykryto niebezpieczny pattern bash: {pattern}")
                    return False
        
        return True
