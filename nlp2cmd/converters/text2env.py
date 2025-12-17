"""
Text2Env - Konwersja języka naturalnego na operacje na plikach .env
"""

import os
import re
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import dotenv_values, set_key, unset_key
from nlp2cmd.core.base import BaseConverter, ConversionResult
import logging
import shutil

logger = logging.getLogger(__name__)


class Text2Env(BaseConverter):
    """
    Konwerter dla operacji na plikach .env.
    
    Obsługuje operacje:
    - Ustawianie wartości: "ustaw PORT na 8080"
    - Zmiana wartości: "zmień DATABASE na production_db"
    - Usuwanie: "usuń DEBUG"
    - Dodawanie: "dodaj API_KEY z wartością xyz"
    """
    
    # Wzorce dla różnych operacji
    PATTERNS = {
        "set": [
            r"ustaw\s+(\w+)\s+na\s+(.+)",
            r"zmień\s+(\w+)\s+na\s+(.+)",
            r"set\s+(\w+)\s+to\s+(.+)",
        ],
        "add": [
            r"dodaj\s+(\w+)\s+z wartością\s+(.+)",
            r"add\s+(\w+)\s+with value\s+(.+)",
        ],
        "delete": [
            r"usuń\s+(\w+)",
            r"delete\s+(\w+)",
            r"remove\s+(\w+)",
        ],
        "get": [
            r"pokaż\s+(\w+)",
            r"get\s+(\w+)",
            r"jaka\s+jest\s+wartość\s+(\w+)",
        ]
    }
    
    def __init__(
        self,
        env_file: str = ".env",
        backup: bool = True,
        create_if_missing: bool = True,
        **kwargs
    ):
        """
        Inicjalizacja Text2Env.
        
        Args:
            env_file: Ścieżka do pliku .env
            backup: Czy tworzyć backup przed zmianami
            create_if_missing: Czy tworzyć plik jeśli nie istnieje
        """
        super().__init__(**kwargs)
        self.env_file = Path(env_file)
        self.backup = backup
        self.create_if_missing = create_if_missing
        
        # Utwórz plik jeśli nie istnieje
        if create_if_missing and not self.env_file.exists():
            self.env_file.touch()
            logger.info(f"Utworzono plik: {self.env_file}")
    
    def _create_backup(self):
        """Tworzy backup pliku .env"""
        if not self.env_file.exists():
            return
        
        backup_path = self.env_file.with_suffix(".env.backup")
        shutil.copy2(self.env_file, backup_path)
        logger.info(f"Utworzono backup: {backup_path}")
    
    def parse_intent(self, text: str) -> Dict[str, Any]:
        """
        Parsuje intencję z tekstu.
        
        Returns:
            {
                "action": "set" | "add" | "delete" | "get",
                "key": str,
                "value": str | None
            }
        """
        text = text.strip().lower()
        
        # Sprawdź każdy pattern
        for action, patterns in self.PATTERNS.items():
            for pattern in patterns:
                match = re.match(pattern, text, re.IGNORECASE)
                if match:
                    groups = match.groups()
                    
                    result = {
                        "action": action,
                        "key": groups[0].upper(),
                        "value": groups[1] if len(groups) > 1 else None
                    }
                    
                    logger.debug(f"Parsed intent: {result}")
                    return result
        
        # Jeśli nie dopasowano, użyj modelu
        if self.model:
            return self._parse_with_model(text)
        
        raise ValueError(f"Nie można sparsować komendy: {text}")
    
    def _parse_with_model(self, text: str) -> Dict[str, Any]:
        """Parsuje intencję używając modelu LLM"""
        system_prompt = """Jesteś parserem komend dla plików .env.
Zadanie: Przekonwertuj komendę w języku naturalnym na strukturę JSON.

Format wyjściowy:
{"action": "set|add|delete|get", "key": "NAZWA_ZMIENNEJ", "value": "wartość"}

Akcje:
- set/add: ustawienie/dodanie zmiennej
- delete: usunięcie zmiennej
- get: odczyt zmiennej
"""
        
        examples = [
            {
                "input": "ustaw PORT na 8080",
                "output": '{"action": "set", "key": "PORT", "value": "8080"}'
            },
            {
                "input": "usuń DEBUG",
                "output": '{"action": "delete", "key": "DEBUG", "value": null}'
            }
        ]
        
        output = self.model.extract_command(text, system_prompt, examples)
        
        # Parse JSON
        import json
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            raise ValueError(f"Model zwrócił nieprawidłowy JSON: {output}")
    
    def generate_command(self, intent: Dict[str, Any]) -> str:
        """
        Generuje operację na pliku .env.
        
        Returns:
            Opis operacji (dla logowania)
        """
        action = intent["action"]
        key = intent["key"]
        value = intent.get("value")
        
        if action in ["set", "add"]:
            return f"set_key('{self.env_file}', '{key}', '{value}')"
        elif action == "delete":
            return f"unset_key('{self.env_file}', '{key}')"
        elif action == "get":
            return f"get_value('{key}')"
        
        raise ValueError(f"Nieznana akcja: {action}")
    
    def execute(self, text: str) -> ConversionResult:
        """
        Wykonuje operację na pliku .env.
        
        Args:
            text: Komenda w języku naturalnym
            
        Returns:
            Wynik operacji
        """
        try:
            # Parse intent
            intent = self.parse_intent(text)
            action = intent["action"]
            key = intent["key"]
            value = intent.get("value")
            
            # Generate command description
            command = self.generate_command(intent)
            
            # Dry run mode
            if self.dry_run:
                logger.info(f"[DRY RUN] {command}")
                return ConversionResult(
                    success=True,
                    command=command,
                    output=f"[DRY RUN] Would execute: {command}"
                )
            
            # Create backup
            if self.backup and action in ["set", "add", "delete"]:
                self._create_backup()
            
            # Execute action
            if action in ["set", "add"]:
                set_key(str(self.env_file), key, value)
                output = f"Ustawiono {key}={value}"
                
            elif action == "delete":
                unset_key(str(self.env_file), key)
                output = f"Usunięto {key}"
                
            elif action == "get":
                env_values = dotenv_values(str(self.env_file))
                value = env_values.get(key)
                output = f"{key}={value}" if value else f"{key} nie istnieje"
            
            result = ConversionResult(
                success=True,
                command=command,
                output=output,
                metadata={
                    "action": action,
                    "key": key,
                    "value": value,
                    "env_file": str(self.env_file)
                }
            )
            
            self.log_execution(text, result)
            return result
            
        except Exception as e:
            logger.error(f"Błąd wykonania: {e}")
            return ConversionResult(
                success=False,
                error=str(e),
                metadata={"input": text}
            )
    
    def get_all_values(self) -> Dict[str, str]:
        """Zwraca wszystkie wartości z pliku .env"""
        return dotenv_values(str(self.env_file))
    
    def list_keys(self) -> list:
        """Zwraca listę kluczy w pliku .env"""
        return list(self.get_all_values().keys())
