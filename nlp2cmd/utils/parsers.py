"""
Parsery dla różnych formatów używanych w NLP2CMD.
"""

import re
from typing import Dict, List, Any, Optional
import yaml
import json


class EnvParser:
    """Parser dla plików .env"""
    
    @staticmethod
    def parse(content: str) -> Dict[str, str]:
        """
        Parsuje zawartość pliku .env.
        
        Args:
            content: Zawartość pliku
            
        Returns:
            Dict z kluczami i wartościami
        """
        env_vars = {}
        for line in content.split('\n'):
            line = line.strip()
            
            # Ignoruj puste linie i komentarze
            if not line or line.startswith('#'):
                continue
            
            # Parsuj KEY=VALUE
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Usuń cudzysłowy
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                
                env_vars[key] = value
        
        return env_vars
    
    @staticmethod
    def format(env_vars: Dict[str, str]) -> str:
        """
        Formatuje dict do formatu .env.
        
        Args:
            env_vars: Dict z kluczami i wartościami
            
        Returns:
            Sformatowana zawartość pliku
        """
        lines = []
        for key, value in sorted(env_vars.items()):
            # Dodaj cudzysłowy jeśli wartość zawiera spacje
            if ' ' in value:
                value = f'"{value}"'
            lines.append(f"{key}={value}")
        
        return '\n'.join(lines)


class MakefileParser:
    """Parser dla Makefile"""
    
    @staticmethod
    def parse_targets(content: str) -> List[Dict[str, Any]]:
        """
        Parsuje target'y z Makefile.
        
        Args:
            content: Zawartość Makefile
            
        Returns:
            Lista dict'ów z informacjami o target'ach
        """
        targets = []
        current_target = None
        
        for line in content.split('\n'):
            # Target definition
            if line and not line.startswith('\t') and ':' in line:
                match = re.match(r'^([a-zA-Z0-9_-]+):\s*(.*)', line)
                if match:
                    target_name = match.group(1)
                    dependencies = match.group(2).strip().split() if match.group(2) else []
                    
                    current_target = {
                        "name": target_name,
                        "dependencies": dependencies,
                        "commands": [],
                        "description": None
                    }
                    targets.append(current_target)
            
            # Command for current target
            elif line.startswith('\t') and current_target:
                command = line.strip()
                if command:
                    current_target["commands"].append(command)
            
            # Comment before target (description)
            elif line.startswith('#') and targets:
                comment = line[1:].strip()
                if not targets[-1]["description"]:
                    targets[-1]["description"] = comment
        
        return targets
    
    @staticmethod
    def extract_variables(content: str) -> Dict[str, str]:
        """
        Ekstraktuje zmienne z Makefile.
        
        Args:
            content: Zawartość Makefile
            
        Returns:
            Dict ze zmiennymi
        """
        variables = {}
        
        for line in content.split('\n'):
            # Variable assignment
            match = re.match(r'^([A-Z_]+)\s*=\s*(.*)', line)
            if match:
                var_name = match.group(1)
                var_value = match.group(2).strip()
                variables[var_name] = var_value
        
        return variables


class DockerfileParser:
    """Parser dla Dockerfile"""
    
    @staticmethod
    def parse_instructions(content: str) -> List[Dict[str, str]]:
        """
        Parsuje instrukcje z Dockerfile.
        
        Args:
            content: Zawartość Dockerfile
            
        Returns:
            Lista instrukcji
        """
        instructions = []
        
        for line in content.split('\n'):
            line = line.strip()
            
            # Ignoruj puste linie i komentarze
            if not line or line.startswith('#'):
                continue
            
            # Parsuj instrukcję
            match = re.match(r'^(\w+)\s+(.*)', line)
            if match:
                instruction = match.group(1).upper()
                args = match.group(2)
                
                instructions.append({
                    "instruction": instruction,
                    "args": args
                })
        
        return instructions
    
    @staticmethod
    def extract_base_image(content: str) -> Optional[str]:
        """
        Ekstraktuje obraz bazowy (FROM).
        
        Args:
            content: Zawartość Dockerfile
            
        Returns:
            Nazwa obrazu bazowego lub None
        """
        for line in content.split('\n'):
            if line.strip().startswith('FROM'):
                return line.split()[1]
        return None


class ConfigParser:
    """Parser dla plików konfiguracyjnych (YAML, JSON)"""
    
    @staticmethod
    def parse(content: str, format: str = "yaml") -> Dict[str, Any]:
        """
        Parsuje plik konfiguracyjny.
        
        Args:
            content: Zawartość pliku
            format: Format ('yaml' lub 'json')
            
        Returns:
            Sparsowana konfiguracja
        """
        if format == "yaml":
            return yaml.safe_load(content)
        elif format == "json":
            return json.loads(content)
        else:
            raise ValueError(f"Nieobsługiwany format: {format}")
    
    @staticmethod
    def format(data: Dict[str, Any], format: str = "yaml") -> str:
        """
        Formatuje dict do pliku konfiguracyjnego.
        
        Args:
            data: Dane do sformatowania
            format: Format wyjściowy
            
        Returns:
            Sformatowana zawartość
        """
        if format == "yaml":
            return yaml.dump(data, default_flow_style=False, allow_unicode=True)
        elif format == "json":
            return json.dumps(data, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"Nieobsługiwany format: {format}")


class CommandParser:
    """Parser dla komend bash/shell"""
    
    @staticmethod
    def parse_pipeline(command: str) -> List[str]:
        """
        Parsuje pipeline bash (komendy połączone |).
        
        Args:
            command: Komenda bash
            
        Returns:
            Lista poszczególnych komend
        """
        return [cmd.strip() for cmd in command.split('|')]
    
    @staticmethod
    def extract_arguments(command: str) -> Dict[str, Any]:
        """
        Ekstraktuje argumenty z komendy.
        
        Args:
            command: Komenda z argumentami
            
        Returns:
            Dict z argumentami
        """
        parts = command.split()
        
        result = {
            "command": parts[0] if parts else None,
            "args": [],
            "flags": {},
        }
        
        i = 1
        while i < len(parts):
            part = parts[i]
            
            # Flag with value
            if part.startswith('-') and i + 1 < len(parts) and not parts[i + 1].startswith('-'):
                result["flags"][part] = parts[i + 1]
                i += 2
            # Boolean flag
            elif part.startswith('-'):
                result["flags"][part] = True
                i += 1
            # Positional argument
            else:
                result["args"].append(part)
                i += 1
        
        return result
