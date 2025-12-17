"""
Text2SSH - Operacje SSH i zarządzanie zdalnymi serwerami.

Ten konwerter umożliwia połączenia SSH i wykonywanie komend zdalnych.
"""

import subprocess
from typing import Dict, Any, Optional, List
from nlp2cmd.core.base import BaseConverter, ConversionResult
import logging

logger = logging.getLogger(__name__)


class Text2SSH(BaseConverter):
    """
    Konwerter dla operacji SSH.
    
    Obsługuje:
    - Połączenia SSH
    - Wykonywanie komend zdalnych
    - Transfer plików (SCP)
    - SSH config management
    """
    
    def __init__(self, timeout: int = 30, **kwargs):
        super().__init__(**kwargs)
        self.timeout = timeout
        self.active_connections = {}
    
    def parse_intent(self, text: str) -> Dict[str, Any]:
        """
        Parsuje intencję z tekstu.
        
        Returns:
            {
                "action": str,      # connect, execute, copy
                "host": str,
                "user": str,
                "password": str | None,
                "key_file": str | None,
                "command": str | None
            }
        """
        text = text.strip().lower()
        
        # Action
        action = "connect"
        if "wykonaj" in text or "uruchom" in text or "execute" in text:
            action = "execute"
        elif "skopiuj" in text or "copy" in text or "transfer" in text:
            action = "copy"
        
        # Extract parameters
        import re
        
        # Host/IP
        host_match = re.search(r'(?:IP|host)[=:]?\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|\S+)', text)
        if not host_match:
            host_match = re.search(r'(?:do|z|na)\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|\w+\.[\w\.]+)', text)
        host = host_match.group(1) if host_match else None
        
        # User
        user_match = re.search(r'(?:user|jako)[=:]?\s*(\w+)', text)
        user = user_match.group(1) if user_match else "root"
        
        # Password
        pass_match = re.search(r'(?:hasło|password)[=:]?\s*(\S+)', text)
        password = pass_match.group(1) if pass_match else None
        
        # Key file
        key_match = re.search(r'(?:key|klucz)[=:]?\s*(\S+)', text)
        key_file = key_match.group(1) if key_match else None
        
        # Command (for execute)
        command = None
        if action == "execute":
            # Extract command after "wykonaj" or similar
            cmd_match = re.search(r'(?:wykonaj|uruchom|execute)\s+(.+)', text)
            if cmd_match:
                command = cmd_match.group(1)
        
        return {
            "action": action,
            "host": host,
            "user": user,
            "password": password,
            "key_file": key_file,
            "command": command,
            "description": text
        }
    
    def generate_command(self, intent: Dict[str, Any]) -> str:
        """Generuje komendę SSH"""
        
        host = intent["host"]
        user = intent["user"]
        action = intent["action"]
        
        if action == "connect":
            cmd = f"ssh {user}@{host}"
            if intent.get("key_file"):
                cmd += f" -i {intent['key_file']}"
            return cmd
        
        elif action == "execute":
            command = intent.get("command", "echo 'Hello'")
            cmd = f"ssh {user}@{host}"
            if intent.get("key_file"):
                cmd += f" -i {intent['key_file']}"
            cmd += f" '{command}'"
            return cmd
        
        return f"ssh {user}@{host}"
    
    def execute(self, text: str) -> ConversionResult:
        """
        Wykonuje operację SSH.
        
        Args:
            text: Komenda w języku naturalnym
            
        Returns:
            Wynik operacji
        """
        try:
            intent = self.parse_intent(text)
            command = self.generate_command(intent)
            
            if not intent["host"]:
                return ConversionResult(
                    success=False,
                    error="No host specified"
                )
            
            if self.dry_run:
                return ConversionResult(
                    success=True,
                    command=command,
                    output=f"[DRY RUN] Would execute: {command}"
                )
            
            # Execute SSH command
            if intent["action"] == "execute":
                return self._execute_remote_command(intent, command)
            else:
                return ConversionResult(
                    success=True,
                    command=command,
                    output="SSH connection command generated. Use interactive mode for actual connection."
                )
            
        except Exception as e:
            logger.error(f"Błąd SSH: {e}")
            return ConversionResult(
                success=False,
                error=str(e),
                metadata={"input": text}
            )
    
    def _execute_remote_command(
        self,
        intent: Dict[str, Any],
        ssh_command: str
    ) -> ConversionResult:
        """Wykonuje komendę na zdalnym serwerze"""
        
        try:
            # For password authentication, we'd need sshpass or pexpect
            # For now, use key-based or no auth
            
            result = subprocess.run(
                ssh_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            success = result.returncode == 0
            
            return ConversionResult(
                success=success,
                command=ssh_command,
                output=result.stdout.strip() if success else result.stderr.strip(),
                error=None if success else f"Exit code: {result.returncode}",
                metadata={
                    "host": intent["host"],
                    "user": intent["user"],
                    "command": intent.get("command")
                }
            )
            
        except subprocess.TimeoutExpired:
            return ConversionResult(
                success=False,
                command=ssh_command,
                error=f"Timeout po {self.timeout} sekundach"
            )
        except Exception as e:
            return ConversionResult(
                success=False,
                command=ssh_command,
                error=str(e)
            )
    
    def copy_file(
        self,
        local_path: str,
        remote_path: str,
        host: str,
        user: str = "root",
        direction: str = "upload"
    ) -> ConversionResult:
        """
        Kopiuje plik przez SCP.
        
        Args:
            local_path: Ścieżka lokalna
            remote_path: Ścieżka zdalna
            host: Host docelowy
            user: User
            direction: 'upload' lub 'download'
            
        Returns:
            Wynik operacji
        """
        
        if direction == "upload":
            command = f"scp {local_path} {user}@{host}:{remote_path}"
        else:
            command = f"scp {user}@{host}:{remote_path} {local_path}"
        
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
                output=result.stdout or result.stderr
            )
            
        except Exception as e:
            return ConversionResult(
                success=False,
                command=command,
                error=str(e)
            )
