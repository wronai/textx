"""
Text3Kubernetes - Generowanie manifestów Kubernetes.

Ten konwerter generuje YAML manifesty dla różnych zasobów K8s.
"""

from typing import Dict, Any, Optional, List
from nlp2cmd.core.base import BaseConverter, ConversionResult
from pathlib import Path
import yaml
import logging

logger = logging.getLogger(__name__)


class Text3Kubernetes(BaseConverter):
    """
    Generator manifestów Kubernetes.
    
    Obsługuje:
    - Deployment
    - Service
    - Ingress
    - ConfigMap
    - Secret
    - StatefulSet
    - DaemonSet
    """
    
    def __init__(self, namespace: str = "default", **kwargs):
        super().__init__(**kwargs)
        self.namespace = namespace
    
    def parse_intent(self, text: str) -> Dict[str, Any]:
        """
        Parsuje intencję z tekstu.
        
        Returns:
            {
                "resource_type": str,  # deployment, service, etc.
                "app_name": str,
                "image": str,
                "replicas": int,
                "port": int,
                "namespace": str
            }
        """
        text = text.strip().lower()
        
        # Resource type
        resource_type = "deployment"
        if "service" in text or "serwis" in text:
            resource_type = "service"
        elif "ingress" in text:
            resource_type = "ingress"
        elif "configmap" in text:
            resource_type = "configmap"
        elif "secret" in text:
            resource_type = "secret"
        
        # App name
        import re
        app_match = re.search(r'(?:dla|for)\s+(\w+(?:-\w+)*)', text)
        app_name = app_match.group(1) if app_match else "myapp"
        
        # Image
        image_match = re.search(r'image[=:]?\s*([\w\-\./:]+)', text)
        image = image_match.group(1) if image_match else f"{app_name}:latest"
        
        # Replicas
        replicas_match = re.search(r'(\d+)\s+(?:replik|replicas?)', text)
        replicas = int(replicas_match.group(1)) if replicas_match else 3
        
        # Port
        port_match = re.search(r'port(?:cie)?\s+(\d+)', text)
        port = int(port_match.group(1)) if port_match else 8080
        
        # Namespace
        ns_match = re.search(r'namespace[=:]?\s*(\w+)', text)
        namespace = ns_match.group(1) if ns_match else self.namespace
        
        return {
            "resource_type": resource_type,
            "app_name": app_name,
            "image": image,
            "replicas": replicas,
            "port": port,
            "namespace": namespace,
            "description": text
        }
    
    def generate_command(self, intent: Dict[str, Any]) -> str:
        """Generuje manifest K8s"""
        
        resource_type = intent["resource_type"]
        
        if resource_type == "deployment":
            return self._generate_deployment(intent)
        elif resource_type == "service":
            return self._generate_service(intent)
        elif resource_type == "ingress":
            return self._generate_ingress(intent)
        elif resource_type == "configmap":
            return self._generate_configmap(intent)
        
        return "# Kubernetes manifest"
    
    def _generate_deployment(self, intent: Dict[str, Any]) -> str:
        """Generuje Deployment manifest"""
        
        manifest = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": intent["app_name"],
                "namespace": intent["namespace"],
                "labels": {
                    "app": intent["app_name"]
                }
            },
            "spec": {
                "replicas": intent["replicas"],
                "selector": {
                    "matchLabels": {
                        "app": intent["app_name"]
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": intent["app_name"]
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": intent["app_name"],
                            "image": intent["image"],
                            "ports": [{
                                "containerPort": intent["port"],
                                "name": "http"
                            }],
                            "resources": {
                                "requests": {
                                    "memory": "256Mi",
                                    "cpu": "100m"
                                },
                                "limits": {
                                    "memory": "512Mi",
                                    "cpu": "500m"
                                }
                            },
                            "livenessProbe": {
                                "httpGet": {
                                    "path": "/health",
                                    "port": intent["port"]
                                },
                                "initialDelaySeconds": 30,
                                "periodSeconds": 10
                            },
                            "readinessProbe": {
                                "httpGet": {
                                    "path": "/health",
                                    "port": intent["port"]
                                },
                                "initialDelaySeconds": 5,
                                "periodSeconds": 5
                            }
                        }]
                    }
                }
            }
        }
        
        return yaml.dump(manifest, default_flow_style=False, sort_keys=False)
    
    def _generate_service(self, intent: Dict[str, Any]) -> str:
        """Generuje Service manifest"""
        
        manifest = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": intent["app_name"],
                "namespace": intent["namespace"],
                "labels": {
                    "app": intent["app_name"]
                }
            },
            "spec": {
                "type": "ClusterIP",
                "selector": {
                    "app": intent["app_name"]
                },
                "ports": [{
                    "port": intent["port"],
                    "targetPort": intent["port"],
                    "protocol": "TCP",
                    "name": "http"
                }]
            }
        }
        
        return yaml.dump(manifest, default_flow_style=False, sort_keys=False)
    
    def _generate_ingress(self, intent: Dict[str, Any]) -> str:
        """Generuje Ingress manifest"""
        
        manifest = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "Ingress",
            "metadata": {
                "name": intent["app_name"],
                "namespace": intent["namespace"],
                "annotations": {
                    "kubernetes.io/ingress.class": "nginx"
                }
            },
            "spec": {
                "rules": [{
                    "host": f"{intent['app_name']}.example.com",
                    "http": {
                        "paths": [{
                            "path": "/",
                            "pathType": "Prefix",
                            "backend": {
                                "service": {
                                    "name": intent["app_name"],
                                    "port": {
                                        "number": intent["port"]
                                    }
                                }
                            }
                        }]
                    }
                }]
            }
        }
        
        return yaml.dump(manifest, default_flow_style=False, sort_keys=False)
    
    def _generate_configmap(self, intent: Dict[str, Any]) -> str:
        """Generuje ConfigMap manifest"""
        
        manifest = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": f"{intent['app_name']}-config",
                "namespace": intent["namespace"]
            },
            "data": {
                "APP_NAME": intent["app_name"],
                "PORT": str(intent["port"]),
                "LOG_LEVEL": "info"
            }
        }
        
        return yaml.dump(manifest, default_flow_style=False, sort_keys=False)
    
    def execute(self, text: str) -> ConversionResult:
        """
        Generuje manifest Kubernetes.
        
        Args:
            text: Opis zasobu w języku naturalnym
            
        Returns:
            Wynik z wygenerowanym manifestem
        """
        try:
            intent = self.parse_intent(text)
            manifest = self.generate_command(intent)
            
            return ConversionResult(
                success=True,
                command=f"Generated {intent['resource_type']} manifest",
                output=manifest,
                metadata={
                    "resource_type": intent["resource_type"],
                    "app_name": intent["app_name"],
                    "namespace": intent["namespace"]
                }
            )
            
        except Exception as e:
            logger.error(f"Błąd generowania: {e}")
            return ConversionResult(
                success=False,
                error=str(e),
                metadata={"input": text}
            )
    
    def generate_full_deployment(
        self,
        app_name: str,
        image: str,
        port: int = 8080,
        replicas: int = 3,
        namespace: str = "default"
    ) -> Dict[str, str]:
        """
        Generuje komplet manifestów (Deployment + Service + Ingress).
        
        Returns:
            Dict z manifestami
        """
        intent = {
            "app_name": app_name,
            "image": image,
            "port": port,
            "replicas": replicas,
            "namespace": namespace
        }
        
        manifests = {
            "deployment.yaml": self._generate_deployment(intent),
            "service.yaml": self._generate_service(intent),
            "ingress.yaml": self._generate_ingress(intent),
            "configmap.yaml": self._generate_configmap(intent)
        }
        
        return manifests
    
    def save_manifests(
        self,
        manifests: Dict[str, str],
        directory: str = "k8s"
    ) -> bool:
        """Zapisuje manifesty do plików"""
        try:
            path = Path(directory)
            path.mkdir(parents=True, exist_ok=True)
            
            for filename, content in manifests.items():
                file_path = path / filename
                file_path.write_text(content)
            
            logger.info(f"Zapisano manifesty w: {directory}")
            return True
            
        except Exception as e:
            logger.error(f"Błąd zapisu: {e}")
            return False
