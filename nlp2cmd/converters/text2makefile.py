"""
Text2Makefile - Konwersja języka naturalnego na komendy make
"""

import subprocess
import re
from typing import Dict, Any, Optional, List
from pathlib import Path
from nlp2cmd.core.base import BaseConverter, ConversionResult
import logging

logger = logging.getLogger(__name__)


class Text2Makefile(BaseConverter):
    """
    Konwerter dla uruchamiania target'ów z Makefile.
    
    Obsługuje:
    - Uruchamianie target'ów: "zbuduj aplikację" -> "make build"
    - Target'y z parametrami: "uruchom testy z coverage" -> "make test COVERAGE=1"
    - Listowanie target'ów: "pokaż dostępne komendy"
    - Uruchamianie wielu target'ów: "zbuduj i uruchom"
    """
    
    # Mapowanie fraz na target'y Makefile
    TARGET_MAPPINGS = {
        # Build
        r"zbuduj|build|kompiluj|compile": "build",
        r"rebuild|przebuduj": "rebuild",
        r"clean|wyczyść": "clean",
        
        # Test
        r"testy|tests|testuj": "test",
        r"testy jednostkowe|unit tests": "test-unit",
        r"testy integracyjne|integration tests": "test-integration",
        
        # Run
        r"uruchom|run|start|wystartuj": "run",
        r"zatrzymaj|stop": "stop",
        r"restart|zrestartuj": "restart",
        
        # Deploy
        r"wdróż|deploy": "deploy",
        r"deploy production|wdróż na produkcję": "deploy-prod",
        r"deploy staging|wdróż na staging": "deploy-staging",
        
        # Docker
        r"zbuduj obraz|build image|docker build": "docker-build",
        r"uruchom docker|docker up": "docker-up",
        r"zatrzymaj docker|docker down": "docker-down",
        
        # Dependencies
        r"zainstaluj zależności|install dependencies": "install",
        r"update|zaktualizuj": "update",
        
        # Documentation
        r"dokumentacja|docs|generate docs": "docs",
        
        # Lint/Format
        r"lint|sprawdź kod": "lint",
        r"format|formatuj": "format",
        
        # Database
        r"migracje|migrations": "migrate",
        r"seed database|wypełnij bazę": "seed",
    }
    
    def __init__(
        self,
        makefile: str = "Makefile",
        working_dir: Optional[str] = None,
        timeout: int = 300,
        **kwargs
    ):
        """
        Inicjalizacja Text2Makefile.
        
        Args:
            makefile: Ścieżka do Makefile
            working_dir: Katalog roboczy (domyślnie gdzie jest Makefile)
            timeout: Maksymalny czas wykonania (sekundy)
        """
        super().__init__(**kwargs)
        self.makefile = Path(makefile)
        self.working_dir = Path(working_dir) if working_dir else self.makefile.parent
        self.timeout = timeout
        
        if not self.makefile.exists():
            logger.warning(f"Makefile nie istnieje: {self.makefile}")
    
    def _parse_makefile(self) -> List[str]:
        """
        Parsuje Makefile i zwraca listę dostępnych target'ów.
        
        Returns:
            Lista nazw target'ów
        """
        if not self.makefile.exists():
            return []
        
        targets = []
        with open(self.makefile, 'r') as f:
            for line in f:
                # Szukaj linii definiujących target'y (linia zaczyna się od słowa: )
                match = re.match(r'^([a-zA-Z0-9_-]+):', line)
                if match:
                    target = match.group(1)
                    # Ignoruj specjalne target'y
                    if not target.startswith('.'):
                        targets.append(target)
        
        return targets
    
    def parse_intent(self, text: str) -> Dict[str, Any]:
        """
        Parsuje intencję z tekstu.
        
        Returns:
            {
                "targets": List[str],  # Lista target'ów do uruchomienia
                "params": Dict[str, str],  # Parametry dla make
                "description": str
            }
        """
        text = text.strip().lower()
        
        # Lista target'ów
        targets = []
        params = {}
        
        # Specjalne komendy
        if "pokaż" in text or "list" in text or "dostępne" in text:
            return {
                "targets": ["list"],
                "params": {},
                "description": "List available targets"
            }
        
        # Szukaj dopasowań do znanych target'ów
        available_targets = self._parse_makefile()
        
        for pattern, target in self.TARGET_MAPPINGS.items():
            if re.search(pattern, text, re.IGNORECASE):
                # Sprawdź czy target istnieje w Makefile
                if target in available_targets or target in ["list"]:
                    targets.append(target)
                else:
                    logger.warning(f"Target '{target}' nie istnieje w Makefile")
        
        # Jeśli nic nie znaleziono, spróbuj z modelem
        if not targets and self.model:
            return self._parse_with_model(text, available_targets)
        
        # Jeśli nadal nic, spróbuj znaleźć bezpośrednie dopasowanie
        if not targets:
            for target in available_targets:
                if target in text:
                    targets.append(target)
        
        # Parsuj parametry (format: "z PARAM=value")
        param_pattern = r"z\s+(\w+)=(\S+)|with\s+(\w+)=(\S+)"
        for match in re.finditer(param_pattern, text):
            groups = match.groups()
            if groups[0]:  # Polish version
                params[groups[0]] = groups[1]
            else:  # English version
                params[groups[2]] = groups[3]
        
        # Specjalne parametry
        if "coverage" in text or "pokrycie" in text:
            params["COVERAGE"] = "1"
        if "verbose" in text or "szczegółowo" in text:
            params["VERBOSE"] = "1"
        if "debug" in text:
            params["DEBUG"] = "1"
        
        return {
            "targets": targets or ["help"],  # Fallback to help
            "params": params,
            "description": text
        }
    
    def _parse_with_model(
        self,
        text: str,
        available_targets: List[str]
    ) -> Dict[str, Any]:
        """Parsuje używając modelu LLM"""
        system_prompt = f"""Jesteś parserem komend make. 
Dostępne target'y w Makefile: {', '.join(available_targets)}

Zadanie: Przekonwertuj komendę na listę target'ów make.
Format wyjściowy: lista target'ów oddzielona przecinkami

Jeśli nie jesteś pewien, zwróć: help"""
        
        examples = [
            {
                "input": "zbuduj aplikację",
                "output": "build"
            },
            {
                "input": "uruchom testy i zbuduj",
                "output": "test,build"
            }
        ]
        
        output = self.model.extract_command(text, system_prompt, examples)
        targets = [t.strip() for t in output.split(',')]
        
        return {
            "targets": targets,
            "params": {},
            "description": text
        }
    
    def generate_command(self, intent: Dict[str, Any]) -> str:
        """
        Generuje komendę make.
        
        Returns:
            Pełna komenda make z parametrami
        """
        targets = intent["targets"]
        params = intent["params"]
        
        # Specjalne: listowanie
        if "list" in targets:
            return f"make -f {self.makefile} -qp | grep -E '^[a-z]'"
        
        # Buduj komendę
        parts = ["make", f"-f {self.makefile}"]
        
        # Dodaj target'y
        parts.extend(targets)
        
        # Dodaj parametry
        for key, value in params.items():
            parts.append(f"{key}={value}")
        
        return " ".join(parts)
    
    def execute(self, text: str) -> ConversionResult:
        """
        Wykonuje target make.
        
        Args:
            text: Komenda w języku naturalnym
            
        Returns:
            Wynik wykonania
        """
        try:
            # Parse intent
            intent = self.parse_intent(text)
            command = self.generate_command(intent)
            
            # Dry run
            if self.dry_run:
                logger.info(f"[DRY RUN] {command}")
                return ConversionResult(
                    success=True,
                    command=command,
                    output=f"[DRY RUN] Would execute: {command}"
                )
            
            # Specjalna obsługa listowania
            if "list" in intent["targets"]:
                targets = self._parse_makefile()
                output = "Dostępne target'y:\n" + "\n".join(f"  - {t}" for t in targets)
                return ConversionResult(
                    success=True,
                    command="list targets",
                    output=output,
                    metadata={"targets": targets}
                )
            
            # Wykonaj make
            logger.info(f"Executing: {command}")
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=str(self.working_dir)
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
                    "targets": intent["targets"],
                    "params": intent["params"],
                    "returncode": result.returncode
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
    
    def list_targets(self) -> List[str]:
        """Zwraca listę dostępnych target'ów"""
        return self._parse_makefile()
