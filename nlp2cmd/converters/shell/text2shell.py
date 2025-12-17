"""
Text2Shell - Interaktywne sesje shell z wieloetapowym wykonywaniem komend.

Ten konwerter umożliwia:
- Wieloetapowe wykonywanie komend
- Interaktywne sesje (np. ssh, ftp)
- Zachowanie kontekstu między komendami
- Obsługa promptów i interakcji
"""

import subprocess
import pexpect
from typing import Dict, Any, Optional, List
from nlp2cmd.core.base import BaseConverter, ConversionResult
import logging
import time

logger = logging.getLogger(__name__)


class Text2Shell(BaseConverter):
    """
    Konwerter dla interaktywnych sesji shell.
    
    Obsługuje:
    - Wieloetapowe komendy: "połącz się z serwerem, przejdź do /var/log, pokaż ostatnie logi"
    - Interaktywne programy: ssh, ftp, mysql, psql
    - Zachowanie stanu sesji
    - Obsługa promptów i uwierzytelniania
    """
    
    def __init__(
        self,
        timeout: int = 30,
        encoding: str = 'utf-8',
        keep_session: bool = True,
        **kwargs
    ):
        """
        Inicjalizacja Text2Shell.
        
        Args:
            timeout: Timeout dla komend (sekundy)
            encoding: Encoding dla I/O
            keep_session: Czy zachowywać sesję między komendami
        """
        super().__init__(**kwargs)
        self.timeout = timeout
        self.encoding = encoding
        self.keep_session = keep_session
        self.session = None
        self.session_history = []
    
    def parse_intent(self, text: str) -> Dict[str, Any]:
        """
        Parsuje intencję z tekstu.
        
        Returns:
            {
                "commands": List[str],  # Lista komend do wykonania
                "interactive": bool,     # Czy wymaga interaktywnej sesji
                "program": str | None,   # Program interaktywny (ssh, ftp, etc.)
                "connection": Dict       # Parametry połączenia jeśli potrzebne
            }
        """
        text = text.strip().lower()
        
        # Wykryj czy to połączenie
        connection_keywords = {
            "ssh": ["połącz się z", "ssh do", "zaloguj się na"],
            "ftp": ["ftp do", "połącz ftp"],
            "mysql": ["mysql na", "połącz się z mysql"],
            "psql": ["psql do", "postgresql na"],
        }
        
        program = None
        connection = {}
        
        for prog, keywords in connection_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    program = prog
                    # Extract host
                    words = text.split()
                    for i, word in enumerate(words):
                        if keyword.split()[0] in word and i + 1 < len(words):
                            connection["host"] = words[i + 1]
                            break
                    break
            if program:
                break
        
        # Rozdziel na komendy (przecinek, "i", "potem", "następnie")
        separators = [",", " i ", " potem ", " następnie ", " a potem "]
        commands = [text]
        
        for sep in separators:
            if sep in text:
                commands = [cmd.strip() for cmd in text.split(sep)]
                break
        
        # Czy wymaga interaktywnej sesji
        interactive = program is not None or len(commands) > 1
        
        return {
            "commands": commands,
            "interactive": interactive,
            "program": program,
            "connection": connection,
            "description": text
        }
    
    def generate_command(self, intent: Dict[str, Any]) -> str:
        """
        Generuje komendę lub sekwencję komend.
        
        Returns:
            Komenda lub opis sekwencji
        """
        commands = intent["commands"]
        
        if len(commands) == 1:
            return commands[0]
        else:
            return " && ".join(commands)
    
    def execute(self, text: str) -> ConversionResult:
        """
        Wykonuje komendę shell lub interaktywną sesję.
        
        Args:
            text: Opis operacji w języku naturalnym
            
        Returns:
            Wynik wykonania
        """
        try:
            intent = self.parse_intent(text)
            
            if intent["interactive"] and intent["program"]:
                return self._execute_interactive(intent)
            elif len(intent["commands"]) > 1:
                return self._execute_sequence(intent)
            else:
                return self._execute_single(intent)
                
        except Exception as e:
            logger.error(f"Błąd wykonania: {e}")
            return ConversionResult(
                success=False,
                error=str(e),
                metadata={"input": text}
            )
    
    def _execute_single(self, intent: Dict[str, Any]) -> ConversionResult:
        """Wykonuje pojedynczą komendę"""
        command = intent["commands"][0]
        
        if self.dry_run:
            return ConversionResult(
                success=True,
                command=command,
                output=f"[DRY RUN] Would execute: {command}"
            )
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            return ConversionResult(
                success=result.returncode == 0,
                command=command,
                output=result.stdout.strip(),
                error=result.stderr.strip() if result.returncode != 0 else None
            )
        except subprocess.TimeoutExpired:
            return ConversionResult(
                success=False,
                command=command,
                error=f"Timeout po {self.timeout} sekundach"
            )
    
    def _execute_sequence(self, intent: Dict[str, Any]) -> ConversionResult:
        """Wykonuje sekwencję komend"""
        commands = intent["commands"]
        outputs = []
        
        if self.dry_run:
            commands_str = "\n".join(f"{i+1}. {cmd}" for i, cmd in enumerate(commands))
            return ConversionResult(
                success=True,
                command=f"Sequence of {len(commands)} commands",
                output=f"[DRY RUN] Would execute:\n{commands_str}"
            )
        
        for i, command in enumerate(commands, 1):
            logger.info(f"Executing step {i}/{len(commands)}: {command}")
            
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout
                )
                
                outputs.append(f"[{i}] {command}\n{result.stdout.strip()}")
                
                if result.returncode != 0:
                    return ConversionResult(
                        success=False,
                        command=f"Sequence (failed at step {i})",
                        output="\n\n".join(outputs),
                        error=f"Step {i} failed: {result.stderr.strip()}"
                    )
                    
            except subprocess.TimeoutExpired:
                return ConversionResult(
                    success=False,
                    command=f"Sequence (timeout at step {i})",
                    output="\n\n".join(outputs),
                    error=f"Step {i} timeout"
                )
        
        return ConversionResult(
            success=True,
            command=f"Sequence of {len(commands)} commands",
            output="\n\n".join(outputs)
        )
    
    def _execute_interactive(self, intent: Dict[str, Any]) -> ConversionResult:
        """Wykonuje interaktywną sesję"""
        program = intent["program"]
        connection = intent["connection"]
        
        if self.dry_run:
            return ConversionResult(
                success=True,
                command=f"Interactive {program} session",
                output=f"[DRY RUN] Would start {program} to {connection.get('host', 'unknown')}"
            )
        
        # Dla interaktywnych sesji używamy pexpect
        try:
            if program == "ssh":
                return self._ssh_session(connection, intent["commands"])
            elif program == "ftp":
                return self._ftp_session(connection, intent["commands"])
            else:
                return ConversionResult(
                    success=False,
                    error=f"Nieobsługiwany program interaktywny: {program}"
                )
        except Exception as e:
            return ConversionResult(
                success=False,
                error=f"Interactive session error: {str(e)}"
            )
    
    def _ssh_session(
        self,
        connection: Dict[str, Any],
        commands: List[str]
    ) -> ConversionResult:
        """Obsługuje sesję SSH"""
        host = connection.get("host", "")
        
        try:
            # Spawn SSH
            child = pexpect.spawn(f"ssh {host}", timeout=self.timeout, encoding=self.encoding)
            
            # Obsłuż prompt hasła (opcjonalnie)
            patterns = [
                pexpect.EOF,
                pexpect.TIMEOUT,
                "password:",
                "yes/no",
                r"[\$#] ",  # Shell prompt
            ]
            
            outputs = []
            
            for command in commands[1:]:  # Skip first command (connect)
                child.sendline(command)
                index = child.expect(patterns)
                
                if index in [0, 1]:  # EOF or TIMEOUT
                    break
                
                outputs.append(child.before)
            
            child.close()
            
            return ConversionResult(
                success=True,
                command=f"SSH session to {host}",
                output="\n".join(outputs)
            )
            
        except Exception as e:
            return ConversionResult(
                success=False,
                command=f"SSH to {host}",
                error=str(e)
            )
    
    def _ftp_session(
        self,
        connection: Dict[str, Any],
        commands: List[str]
    ) -> ConversionResult:
        """Obsługuje sesję FTP"""
        host = connection.get("host", "")
        
        try:
            child = pexpect.spawn(f"ftp {host}", timeout=self.timeout, encoding=self.encoding)
            
            outputs = []
            
            for command in commands[1:]:
                child.sendline(command)
                child.expect("ftp>")
                outputs.append(child.before)
            
            child.sendline("quit")
            child.close()
            
            return ConversionResult(
                success=True,
                command=f"FTP session to {host}",
                output="\n".join(outputs)
            )
            
        except Exception as e:
            return ConversionResult(
                success=False,
                command=f"FTP to {host}",
                error=str(e)
            )
    
    def create_session(self, session_type: str = "bash") -> bool:
        """
        Tworzy trwałą sesję shell.
        
        Args:
            session_type: Typ sesji ('bash', 'zsh', etc.)
            
        Returns:
            True jeśli sukces
        """
        try:
            self.session = pexpect.spawn(session_type, encoding=self.encoding)
            self.session.expect(r"[\$#] ")
            return True
        except Exception as e:
            logger.error(f"Błąd tworzenia sesji: {e}")
            return False
    
    def close_session(self):
        """Zamyka sesję shell"""
        if self.session:
            self.session.close()
            self.session = None
            self.session_history = []
