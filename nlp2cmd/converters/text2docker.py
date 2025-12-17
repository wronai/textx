"""
Text2Docker - Konwersja języka naturalnego na komendy Docker
"""

import subprocess
import re
from typing import Dict, Any, Optional, List
from nlp2cmd.core.base import BaseConverter, ConversionResult
import logging

logger = logging.getLogger(__name__)


class Text2Docker(BaseConverter):
    """
    Konwerter dla zarządzania kontenerami Docker.
    
    Obsługuje:
    - Uruchamianie kontenerów: "uruchom postgres"
    - Zatrzymywanie: "zatrzymaj redis"
    - Budowanie obrazów: "zbuduj obraz z Dockerfile"
    - Zarządzanie: "pokaż działające kontenery"
    """
    
    # Popularne obrazy Docker i ich konfiguracje
    COMMON_SERVICES = {
        "postgres": {
            "image": "postgres:latest",
            "env": ["POSTGRES_PASSWORD=postgres"],
            "port": "5432:5432"
        },
        "postgresql": {
            "image": "postgres:latest",
            "env": ["POSTGRES_PASSWORD=postgres"],
            "port": "5432:5432"
        },
        "mysql": {
            "image": "mysql:latest",
            "env": ["MYSQL_ROOT_PASSWORD=root"],
            "port": "3306:3306"
        },
        "redis": {
            "image": "redis:latest",
            "port": "6379:6379"
        },
        "mongodb": {
            "image": "mongo:latest",
            "port": "27017:27017"
        },
        "nginx": {
            "image": "nginx:latest",
            "port": "80:80"
        },
        "elasticsearch": {
            "image": "elasticsearch:8.11.0",
            "env": ["discovery.type=single-node"],
            "port": "9200:9200"
        },
        "rabbitmq": {
            "image": "rabbitmq:management",
            "port": "5672:5672,15672:15672"
        },
    }
    
    # Akcje Docker
    ACTION_PATTERNS = {
        "run": [
            r"uruchom|run|start|wystartuj",
            r"stwórz kontener|create container"
        ],
        "stop": [
            r"zatrzymaj|stop",
        ],
        "restart": [
            r"zrestartuj|restart",
        ],
        "remove": [
            r"usuń|remove|delete",
        ],
        "list": [
            r"pokaż|list|wyświetl",
            r"jakie kontenery|what containers"
        ],
        "build": [
            r"zbuduj obraz|build image",
        ],
        "logs": [
            r"logi|logs",
        ],
        "exec": [
            r"wykonaj|exec|uruchom komendę",
        ]
    }
    
    def __init__(
        self,
        docker_host: Optional[str] = None,
        timeout: int = 60,
        auto_pull: bool = True,
        **kwargs
    ):
        """
        Inicjalizacja Text2Docker.
        
        Args:
            docker_host: Docker host (domyślnie local socket)
            timeout: Maksymalny czas wykonania (sekundy)
            auto_pull: Czy automatycznie pobierać obrazy
        """
        super().__init__(**kwargs)
        self.docker_host = docker_host
        self.timeout = timeout
        self.auto_pull = auto_pull
        
        # Sprawdź czy Docker jest dostępny
        if not self._check_docker():
            logger.warning("Docker nie jest dostępny lub nie działa")
    
    def _check_docker(self) -> bool:
        """Sprawdza czy Docker jest dostępny"""
        try:
            result = subprocess.run(
                ["docker", "version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def parse_intent(self, text: str) -> Dict[str, Any]:
        """
        Parsuje intencję z tekstu.
        
        Returns:
            {
                "action": str,  # run, stop, restart, etc.
                "service": str | None,  # Nazwa usługi
                "options": Dict[str, Any]  # Dodatkowe opcje
            }
        """
        text = text.strip().lower()
        
        # Wykryj akcję
        action = None
        for act, patterns in self.ACTION_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    action = act
                    break
            if action:
                break
        
        if not action and self.model:
            return self._parse_with_model(text)
        
        # Wykryj usługę
        service = None
        for svc in self.COMMON_SERVICES.keys():
            if svc in text:
                service = svc
                break
        
        # Opcje
        options = {}
        
        # Port
        port_match = re.search(r"port(?:cie)?\s+(\d+)", text)
        if port_match:
            options["port"] = port_match.group(1)
        
        # Nazwa kontenera
        name_match = re.search(r"nazwa\s+(\w+)|name\s+(\w+)", text)
        if name_match:
            options["name"] = name_match.group(1) or name_match.group(2)
        
        # Detached mode
        if "w tle" in text or "detached" in text:
            options["detached"] = True
        
        # Volumes
        volume_match = re.search(r"volume\s+([^\s]+)", text)
        if volume_match:
            options["volume"] = volume_match.group(1)
        
        # Environment
        env_match = re.findall(r"env\s+(\w+)=(\S+)", text)
        if env_match:
            options["env"] = {k: v for k, v in env_match}
        
        return {
            "action": action or "list",
            "service": service,
            "options": options,
            "description": text
        }
    
    def _parse_with_model(self, text: str) -> Dict[str, Any]:
        """Parsuje używając modelu LLM"""
        system_prompt = f"""Jesteś parserem komend Docker.
Dostępne usługi: {', '.join(self.COMMON_SERVICES.keys())}

Zadanie: Przekonwertuj komendę na strukturę JSON.
Format: {{"action": "run|stop|list|build", "service": "nazwa_usługi", "options": {{}}}}
"""
        
        examples = [
            {
                "input": "uruchom postgres na porcie 5432",
                "output": '{"action": "run", "service": "postgres", "options": {"port": "5432"}}'
            },
            {
                "input": "zatrzymaj redis",
                "output": '{"action": "stop", "service": "redis", "options": {}}'
            }
        ]
        
        output = self.model.extract_command(text, system_prompt, examples)
        
        import json
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            raise ValueError(f"Model zwrócił nieprawidłowy JSON: {output}")
    
    def generate_command(self, intent: Dict[str, Any]) -> str:
        """
        Generuje komendę docker.
        
        Returns:
            Komenda docker
        """
        action = intent["action"]
        service = intent.get("service")
        options = intent.get("options", {})
        
        if action == "run":
            return self._generate_run_command(service, options)
        elif action == "stop":
            return f"docker stop {options.get('name', service)}"
        elif action == "restart":
            return f"docker restart {options.get('name', service)}"
        elif action == "remove":
            return f"docker rm {options.get('name', service)}"
        elif action == "list":
            filter_type = "running" if "działające" in intent.get("description", "") else "all"
            return "docker ps" if filter_type == "running" else "docker ps -a"
        elif action == "build":
            tag = options.get("tag", "myimage")
            return f"docker build -t {tag} ."
        elif action == "logs":
            return f"docker logs {options.get('name', service)}"
        elif action == "exec":
            cmd = options.get("command", "/bin/bash")
            return f"docker exec -it {options.get('name', service)} {cmd}"
        
        raise ValueError(f"Nieznana akcja: {action}")
    
    def _generate_run_command(
        self,
        service: Optional[str],
        options: Dict[str, Any]
    ) -> str:
        """Generuje komendę docker run"""
        parts = ["docker run"]
        
        # Detached mode (domyślnie dla usług)
        if options.get("detached", True):
            parts.append("-d")
        
        # Nazwa kontenera
        name = options.get("name", service)
        if name:
            parts.append(f"--name {name}")
        
        # Automatyczne usuwanie
        if options.get("rm", False):
            parts.append("--rm")
        
        # Service configuration
        if service and service in self.COMMON_SERVICES:
            config = self.COMMON_SERVICES[service]
            
            # Port
            port = options.get("port", config.get("port"))
            if port:
                parts.append(f"-p {port}")
            
            # Environment
            env_vars = config.get("env", [])
            for env in env_vars:
                parts.append(f"-e {env}")
            
            # Custom env from options
            if "env" in options:
                for key, value in options["env"].items():
                    parts.append(f"-e {key}={value}")
            
            # Volume
            if "volume" in options:
                parts.append(f"-v {options['volume']}")
            
            # Image
            parts.append(config["image"])
        else:
            # Custom image
            image = options.get("image", service)
            if not image:
                raise ValueError("Nie podano obrazu Docker")
            parts.append(image)
        
        return " ".join(parts)
    
    def execute(self, text: str) -> ConversionResult:
        """
        Wykonuje operację Docker.
        
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
                    "description": intent.get("description", ""),
                    "action": intent["action"],
                    "service": intent.get("service"),
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
    
    def list_running_containers(self) -> List[Dict[str, str]]:
        """Zwraca listę działających kontenerów"""
        try:
            result = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}}|{{.Image}}|{{.Status}}"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            containers = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    name, image, status = line.split('|')
                    containers.append({
                        "name": name,
                        "image": image,
                        "status": status
                    })
            
            return containers
        except Exception as e:
            logger.error(f"Błąd listowania kontenerów: {e}")
            return []
