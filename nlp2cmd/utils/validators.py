"""
Walidatory bezpieczeństwa dla NLP2CMD.
"""

import re
from typing import List, Optional, Callable
import logging

logger = logging.getLogger(__name__)


class SecurityValidator:
    """
    Bazowy walidator bezpieczeństwa.
    
    Sprawdza czy komendy nie zawierają niebezpiecznych patternów.
    """
    
    # Globalne niebezpieczne patterny
    DANGEROUS_PATTERNS = [
        # System destruction
        r"rm\s+-rf\s+/",
        r"rm\s+-rf\s+\*",
        r":\(\)\{\s*:\|:\&\s*\}",  # fork bomb
        r"dd\s+if=/dev/zero",
        r"mkfs\.",
        r">/dev/sd[a-z]",
        
        # Privilege escalation
        r"sudo\s+su",
        r"chmod\s+777",
        r"chmod\s+-R\s+777",
        
        # Remote execution
        r"curl.*\|\s*sh",
        r"wget.*\|\s*bash",
        r"nc\s+.*-e",
        
        # Dangerous eval
        r"eval\s*\(",
        r"exec\s*\(",
    ]
    
    def __init__(
        self,
        custom_patterns: Optional[List[str]] = None,
        whitelist: Optional[List[str]] = None
    ):
        """
        Inicjalizacja walidatora.
        
        Args:
            custom_patterns: Dodatkowe niebezpieczne patterny
            whitelist: Lista dozwolonych komend (nadpisuje blacklist)
        """
        self.patterns = self.DANGEROUS_PATTERNS.copy()
        if custom_patterns:
            self.patterns.extend(custom_patterns)
        
        self.whitelist = whitelist or []
    
    def validate(self, command: str) -> bool:
        """
        Waliduje komendę.
        
        Args:
            command: Komenda do sprawdzenia
            
        Returns:
            True jeśli komenda jest bezpieczna
        """
        # Sprawdź whitelist
        if self.whitelist:
            for allowed in self.whitelist:
                if command.startswith(allowed):
                    return True
            # Jeśli nie pasuje do whitelist, odrzuć
            logger.warning(f"Komenda nie na whitelist: {command}")
            return False
        
        # Sprawdź blacklist
        for pattern in self.patterns:
            if re.search(pattern, command, re.IGNORECASE):
                logger.warning(f"Wykryto niebezpieczny pattern: {pattern}")
                return False
        
        return True
    
    def add_pattern(self, pattern: str):
        """Dodaje niebezpieczny pattern"""
        self.patterns.append(pattern)
    
    def remove_pattern(self, pattern: str):
        """Usuwa pattern z listy"""
        if pattern in self.patterns:
            self.patterns.remove(pattern)


class BashValidator(SecurityValidator):
    """Walidator specyficzny dla komend bash"""
    
    BASH_DANGEROUS = [
        # File operations
        r"rm\s+-rf",
        r"shred",
        
        # Process manipulation
        r"kill\s+-9\s+1",  # Kill init
        r"killall\s+-9",
        
        # Network
        r"iptables\s+.*-F",  # Flush firewall
        
        # Dangerous redirects
        r">\s*/dev/sd[a-z]",
        r">\s*/dev/null",  # Może być OK w niektórych przypadkach
    ]
    
    def __init__(self, **kwargs):
        super().__init__(custom_patterns=self.BASH_DANGEROUS, **kwargs)


class DockerValidator(SecurityValidator):
    """Walidator dla komend Docker"""
    
    DOCKER_DANGEROUS = [
        # Privileged mode
        r"--privileged",
        
        # Host network
        r"--network\s+host",
        
        # Bind mounts of sensitive directories
        r"-v\s+/:/",
        r"-v\s+/etc:/",
        r"-v\s+/var/run/docker.sock",
        
        # Run as root
        r"--user\s+root",
        r"--user\s+0",
    ]
    
    def __init__(self, allow_privileged: bool = False, **kwargs):
        patterns = self.DOCKER_DANGEROUS.copy()
        
        # Jeśli allow_privileged, usuń te patterny
        if allow_privileged:
            patterns = [p for p in patterns if "privileged" not in p]
        
        super().__init__(custom_patterns=patterns, **kwargs)


class EnvValidator:
    """Walidator dla plików .env"""
    
    SENSITIVE_KEYS = [
        "PASSWORD",
        "SECRET",
        "API_KEY",
        "TOKEN",
        "PRIVATE_KEY",
        "AWS_SECRET",
    ]
    
    @staticmethod
    def validate_key(key: str) -> bool:
        """
        Sprawdza czy klucz jest poprawny.
        
        Args:
            key: Nazwa klucza
            
        Returns:
            True jeśli klucz jest poprawny
        """
        # Klucze powinny być uppercase z underscores
        if not re.match(r'^[A-Z_][A-Z0-9_]*$', key):
            logger.warning(f"Niepoprawny format klucza: {key}")
            return False
        
        return True
    
    @staticmethod
    def is_sensitive(key: str) -> bool:
        """
        Sprawdza czy klucz zawiera wrażliwe dane.
        
        Args:
            key: Nazwa klucza
            
        Returns:
            True jeśli klucz jest wrażliwy
        """
        key_upper = key.upper()
        return any(sensitive in key_upper for sensitive in EnvValidator.SENSITIVE_KEYS)
    
    @staticmethod
    def validate_value(value: str, key: str) -> bool:
        """
        Waliduje wartość dla danego klucza.
        
        Args:
            value: Wartość
            key: Nazwa klucza
            
        Returns:
            True jeśli wartość jest poprawna
        """
        # Sprawdź czy wartość nie jest pusta dla wrażliwych kluczy
        if EnvValidator.is_sensitive(key) and not value:
            logger.warning(f"Pusta wartość dla wrażliwego klucza: {key}")
            return False
        
        # Sprawdź czy wartość nie zawiera niebezpiecznych znaków
        if re.search(r'[;\n\r]', value):
            logger.warning(f"Wartość zawiera niebezpieczne znaki: {value}")
            return False
        
        return True


class InputSanitizer:
    """Sanitizer dla danych wejściowych"""
    
    @staticmethod
    def sanitize_shell_input(text: str) -> str:
        """
        Sanitize input dla shell commands.
        
        Args:
            text: Tekst do oczyszczenia
            
        Returns:
            Oczyszczony tekst
        """
        # Usuń niebezpieczne znaki
        dangerous_chars = [';', '&', '|', '`', '$', '(', ')', '<', '>', '\n', '\r']
        
        for char in dangerous_chars:
            text = text.replace(char, '')
        
        return text.strip()
    
    @staticmethod
    def sanitize_path(path: str) -> str:
        """
        Sanitize ścieżki pliku.
        
        Args:
            path: Ścieżka do oczyszczenia
            
        Returns:
            Oczyszczona ścieżka
        """
        # Usuń próby directory traversal
        path = path.replace('..', '')
        path = path.replace('//', '/')
        
        # Usuń leading/trailing whitespace
        path = path.strip()
        
        return path
    
    @staticmethod
    def escape_quotes(text: str) -> str:
        """
        Escapuje cudzysłowy.
        
        Args:
            text: Tekst do escapowania
            
        Returns:
            Tekst z escapowanymi cudzysłowami
        """
        text = text.replace('"', '\\"')
        text = text.replace("'", "\\'")
        return text


class ValidationChain:
    """
    Łańcuch walidatorów.
    
    Umożliwia sekwencyjne stosowanie wielu walidatorów.
    """
    
    def __init__(self):
        self.validators: List[Callable[[str], bool]] = []
    
    def add(self, validator: Callable[[str], bool]) -> 'ValidationChain':
        """Dodaje walidator do łańcucha"""
        self.validators.append(validator)
        return self
    
    def validate(self, command: str) -> bool:
        """
        Waliduje komendę przez wszystkie walidatory.
        
        Returns:
            True jeśli wszystkie walidatory przeszły
        """
        for validator in self.validators:
            if not validator(command):
                return False
        return True
    
    def validate_with_details(self, command: str) -> tuple:
        """
        Waliduje i zwraca szczegóły.
        
        Returns:
            (success: bool, failed_at: int | None)
        """
        for i, validator in enumerate(self.validators):
            if not validator(command):
                return False, i
        return True, None
