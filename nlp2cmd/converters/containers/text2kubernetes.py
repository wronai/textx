"""
Text2Kubernetes - Query i zarządzanie klastrem Kubernetes.

Ten konwerter umożliwia zarządzanie zasobami K8s przez naturalne komendy.
"""

import subprocess
import json
from typing import Dict, Any, Optional, List
from nlp2cmd.core.base import BaseConverter, ConversionResult
import logging

logger = logging.getLogger(__name__)


class Text2Kubernetes(BaseConverter):
    """
    Konwerter dla operacji na klastrze Kubernetes.
    
    Obsługuje:
    - Query zasobów (get, describe, logs)
    - Zarządzanie deployments
    - Scaling
    - Rollouts
    - Port-forwarding
    - Namespace operations
    """
    
    # Mapowanie akcji
    ACTION_PATTERNS = {
        "get": [
            r"pokaż|show|list|wyświetl|get",
        ],
        "describe": [
            r"opisz|describe|details|szczegóły",
        ],
        "logs": [
            r"logi|logs",
        ],
        "scale": [
            r"skaluj|scale",
        ],
        "restart": [
            r"restart|zrestartuj",
        ],
        "delete": [
            r"usuń|delete|remove",
        ],
        "port-forward": [
            r"port-forward|przekieruj port",
        ],
        "exec": [
            r"wykonaj|exec|uruchom w",
        ]
    }
    
    # Typy zasobów
    RESOURCE_TYPES = {
        "pod": ["pod", "pody", "pods", "po"],
        "deployment": ["deployment", "deploymenty", "deployments", "deploy"],
        "service": ["service", "serwis", "services", "svc"],
        "ingress": ["ingress", "ing"],
        "configmap": ["configmap", "cm"],
        "secret": ["secret", "secrets"],
        "node": ["node", "nodes", "węzeł"],
        "namespace": ["namespace", "ns", "namespaces"],
        "pvc": ["pvc", "persistentvolumeclaim"],
        "statefulset": ["statefulset", "sts"],
        "daemonset": ["daemonset", "ds"],
    }
    
    def __init__(
        self,
        context: Optional[str] = None,
        namespace: str = "default",
        timeout: int = 30,
        **kwargs
    ):
        """
        Inicjalizacja Text2Kubernetes.
        
        Args:
            context: Kubernetes context
            namespace: Domyślny namespace
            timeout: Timeout dla komend
        """
        super().__init__(**kwargs)
        self.context = context
        self.namespace = namespace
        self.timeout = timeout
        
        # Sprawdź kubectl
        if not self._check_kubectl():
            logger.warning("kubectl nie jest dostępny")
    
    def _check_kubectl(self) -> bool:
        """Sprawdza czy kubectl jest dostępny"""
        try:
            result = subprocess.run(
                ["kubectl", "version", "--client"],
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
                "action": str,          # get, describe, logs, etc.
                "resource_type": str,   # pod, deployment, etc.
                "resource_name": str | None,
                "namespace": str,
                "options": Dict
            }
        """
        text = text.strip().lower()
        
        # Wykryj akcję
        action = "get"  # default
        for act, patterns in self.ACTION_PATTERNS.items():
            for pattern in patterns:
                if pattern in text:
                    action = act
                    break
            if action != "get":
                break
        
        # Wykryj typ zasobu
        resource_type = "pod"  # default
        for rtype, keywords in self.RESOURCE_TYPES.items():
            if any(kw in text for kw in keywords):
                resource_type = rtype
                break
        
        # Wykryj nazwę zasobu (uproszczone)
        resource_name = None
        words = text.split()
        for i, word in enumerate(words):
            if word in sum(self.RESOURCE_TYPES.values(), []):
                if i + 1 < len(words):
                    next_word = words[i + 1]
                    if next_word not in ["w", "na", "in", "all", "wszystkie"]:
                        resource_name = next_word
                break
        
        # Wykryj namespace
        namespace = self.namespace
        if "namespace" in text or "ns" in text:
            for i, word in enumerate(words):
                if word in ["namespace", "ns"] and i + 1 < len(words):
                    namespace = words[i + 1]
                    break
        elif " w " in text:
            idx = text.find(" w ")
            after = text[idx+3:].split()[0]
            if after not in ["klastrze", "cluster"]:
                namespace = after
        
        # Opcje
        options = {}
        
        if "all" in text or "wszystkie" in text:
            options["all_namespaces"] = True
        
        if "watch" in text or "obserwuj" in text:
            options["watch"] = True
        
        if "wide" in text or "szczegółowe" in text:
            options["wide"] = True
        
        if "json" in text:
            options["output"] = "json"
        elif "yaml" in text:
            options["output"] = "yaml"
        
        return {
            "action": action,
            "resource_type": resource_type,
            "resource_name": resource_name,
            "namespace": namespace,
            "options": options,
            "description": text
        }
    
    def generate_command(self, intent: Dict[str, Any]) -> str:
        """
        Generuje komendę kubectl.
        
        Returns:
            Komenda kubectl
        """
        parts = ["kubectl"]
        
        # Context
        if self.context:
            parts.extend(["--context", self.context])
        
        # Action
        parts.append(intent["action"])
        
        # Resource type
        parts.append(intent["resource_type"])
        
        # Resource name
        if intent["resource_name"]:
            parts.append(intent["resource_name"])
        
        # Namespace
        if intent["options"].get("all_namespaces"):
            parts.append("--all-namespaces")
        elif intent["namespace"] != "default" or not intent["resource_name"]:
            parts.extend(["-n", intent["namespace"]])
        
        # Output format
        if "output" in intent["options"]:
            parts.extend(["-o", intent["options"]["output"]])
        elif intent["options"].get("wide"):
            parts.extend(["-o", "wide"])
        
        # Watch
        if intent["options"].get("watch"):
            parts.append("--watch")
        
        return " ".join(parts)
    
    def execute(self, text: str) -> ConversionResult:
        """
        Wykonuje operację Kubernetes.
        
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
            
            # Execute
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
                    "action": intent["action"],
                    "resource_type": intent["resource_type"],
                    "namespace": intent["namespace"]
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
    
    def get_pods(self, namespace: Optional[str] = None) -> List[Dict[str, str]]:
        """Zwraca listę podów"""
        ns = namespace or self.namespace
        
        try:
            result = subprocess.run(
                f"kubectl get pods -n {ns} -o json",
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                pods = []
                for item in data.get("items", []):
                    pods.append({
                        "name": item["metadata"]["name"],
                        "status": item["status"]["phase"],
                        "namespace": item["metadata"]["namespace"]
                    })
                return pods
            
        except Exception as e:
            logger.error(f"Błąd pobierania podów: {e}")
        
        return []
    
    def get_namespaces(self) -> List[str]:
        """Zwraca listę namespaces"""
        try:
            result = subprocess.run(
                "kubectl get namespaces -o json",
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return [item["metadata"]["name"] for item in data.get("items", [])]
        
        except Exception as e:
            logger.error(f"Błąd pobierania namespaces: {e}")
        
        return []
    
    def scale_deployment(
        self,
        deployment: str,
        replicas: int,
        namespace: Optional[str] = None
    ) -> bool:
        """Skaluje deployment"""
        ns = namespace or self.namespace
        
        try:
            result = subprocess.run(
                f"kubectl scale deployment {deployment} --replicas={replicas} -n {ns}",
                shell=True,
                capture_output=True,
                timeout=30
            )
            
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"Błąd skalowania: {e}")
            return False
