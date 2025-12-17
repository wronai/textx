"""
Orchestrator - Inteligentny system orchestracji dla złożonych workflow.

Ten moduł rozłożi złożone zadanie na kroki używając odpowiednich konwerterów.
"""

from typing import Dict, Any, List, Optional, Tuple
from nlp2cmd.core.base import BaseConverter, ConversionResult
from nlp2cmd.core.pipeline import Pipeline
import logging
import re

logger = logging.getLogger(__name__)


class WorkflowStep:
    """Reprezentacja pojedynczego kroku w workflow"""
    
    def __init__(
        self,
        name: str,
        converter: str,
        command: str,
        depends_on: Optional[List[str]] = None,
        save_output_as: Optional[str] = None
    ):
        self.name = name
        self.converter = converter
        self.command = command
        self.depends_on = depends_on or []
        self.save_output_as = save_output_as
        self.result: Optional[ConversionResult] = None
    
    def __repr__(self):
        return f"WorkflowStep(name={self.name}, converter={self.converter})"


class Orchestrator:
    """
    Inteligentny orchestrator do zarządzania złożonymi workflow.
    
    Funkcje:
    - Automatyczne planowanie kroków
    - Dependency resolution
    - Parallel execution (gdzie możliwe)
    - Error recovery
    - State management
    - Context passing między krokami
    """
    
    # Wzorce dla różnych typów zadań
    TASK_PATTERNS = {
        "deploy_app": {
            "keywords": ["deploy", "wdróż", "zainstaluj aplikację", "uruchom aplikację"],
            "steps": [
                "generate_app",
                "generate_dockerfile", 
                "generate_k8s_manifest",
                "ssh_connect",
                "deploy_to_k8s"
            ]
        },
        "test_and_replicate": {
            "keywords": ["przetestuj i wygeneruj", "test and generate", "replicate"],
            "steps": [
                "test_api",
                "analyze_endpoints",
                "generate_app",
                "generate_tests"
            ]
        },
        "full_stack_setup": {
            "keywords": ["kompletny setup", "full stack", "cały stack"],
            "steps": [
                "generate_backend",
                "generate_frontend",
                "generate_database",
                "generate_docker_compose",
                "deploy_all"
            ]
        },
        "infrastructure_setup": {
            "keywords": ["infrastruktura", "infrastructure", "provision"],
            "steps": [
                "generate_terraform",
                "apply_terraform",
                "configure_k8s",
                "deploy_monitoring"
            ]
        }
    }
    
    def __init__(self, dry_run: bool = False):
        """
        Inicjalizacja orchestratora.
        
        Args:
            dry_run: Czy tylko symulować wykonanie
        """
        self.dry_run = dry_run
        self.converters = {}
        self.context = {}  # Shared context między krokami
        self.workflow_history = []
        
        # Initialize converters lazily
        self._initialize_converters()
    
    def _initialize_converters(self):
        """Lazy initialization konwerterów"""
        # Importy będą dodawane dynamicznie
        pass
    
    def register_converter(self, name: str, converter: BaseConverter):
        """Rejestruje konwerter w orchestratorze"""
        self.converters[name] = converter
        logger.info(f"Zarejestrowano konwerter: {name}")
    
    def parse_complex_task(self, task_description: str) -> List[WorkflowStep]:
        """
        Parsuje złożone zadanie i rozkłada na kroki.
        
        Args:
            task_description: Opis zadania w języku naturalnym
            
        Returns:
            Lista kroków do wykonania
        """
        task_lower = task_description.lower()
        
        # Wykryj typ zadania
        task_type = self._detect_task_type(task_lower)
        
        # Ekstraktuj parametry
        params = self._extract_parameters(task_description)
        
        # Wygeneruj plan
        if task_type:
            return self._generate_plan(task_type, params, task_description)
        else:
            # Użyj LLM do planowania
            return self._generate_plan_with_llm(task_description, params)
    
    def _detect_task_type(self, text: str) -> Optional[str]:
        """Wykrywa typ zadania na podstawie keywords"""
        for task_type, config in self.TASK_PATTERNS.items():
            if any(kw in text for kw in config["keywords"]):
                return task_type
        return None
    
    def _extract_parameters(self, text: str) -> Dict[str, Any]:
        """
        Ekstraktuje parametry z opisu zadania.
        
        Returns:
            Dict z parametrami (IP, user, password, port, etc.)
        """
        params = {}
        
        # IP address
        ip_match = re.search(r'IP[=:]?\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', text)
        if ip_match:
            params['ip'] = ip_match.group(1)
        
        # User
        user_match = re.search(r'user[=:]?\s*(\w+)', text, re.IGNORECASE)
        if user_match:
            params['user'] = user_match.group(1)
        
        # Password
        pass_match = re.search(r'(hasło|password)[=:]?\s*(\S+)', text, re.IGNORECASE)
        if pass_match:
            params['password'] = pass_match.group(2)
        
        # Port
        port_match = re.search(r'port[=:]?\s*(\d+)', text, re.IGNORECASE)
        if port_match:
            params['port'] = int(port_match.group(1))
        
        # App name
        app_match = re.search(r'aplikacj[ęa]\s+(?:do\s+)?(\w+(?:\s+\w+)*)', text, re.IGNORECASE)
        if app_match:
            params['app_name'] = app_match.group(1)
        
        # Language
        languages = ['python', 'nodejs', 'node.js', 'go', 'java', 'php', 'ruby']
        for lang in languages:
            if lang in text.lower():
                params['language'] = lang
                break
        
        # Namespace (K8s)
        ns_match = re.search(r'namespace[=:]?\s*(\w+)', text, re.IGNORECASE)
        if ns_match:
            params['namespace'] = ns_match.group(1)
        
        return params
    
    def _generate_plan(
        self,
        task_type: str,
        params: Dict[str, Any],
        original_task: str
    ) -> List[WorkflowStep]:
        """Generuje plan kroków dla danego typu zadania"""
        
        if task_type == "deploy_app":
            return self._plan_deploy_app(params, original_task)
        elif task_type == "test_and_replicate":
            return self._plan_test_and_replicate(params, original_task)
        elif task_type == "full_stack_setup":
            return self._plan_full_stack_setup(params, original_task)
        elif task_type == "infrastructure_setup":
            return self._plan_infrastructure_setup(params, original_task)
        
        return []
    
    def _plan_deploy_app(
        self,
        params: Dict[str, Any],
        task: str
    ) -> List[WorkflowStep]:
        """Plan dla deployment aplikacji"""
        
        app_name = params.get('app_name', 'myapp')
        language = params.get('language', 'python')
        ip = params.get('ip')
        user = params.get('user', 'root')
        password = params.get('password')
        namespace = params.get('namespace', 'default')
        
        steps = []
        
        # 1. Generate application
        steps.append(WorkflowStep(
            name="generate_app",
            converter="text3app",
            command=f"wygeneruj aplikację {app_name} w {language}",
            save_output_as="app_code"
        ))
        
        # 2. Generate Dockerfile
        steps.append(WorkflowStep(
            name="generate_dockerfile",
            converter="text3docker",
            command=f"dockerfile dla {language} aplikacji",
            depends_on=["generate_app"],
            save_output_as="dockerfile"
        ))
        
        # 3. Generate K8s manifests
        steps.append(WorkflowStep(
            name="generate_k8s_manifest",
            converter="text3kubernetes",
            command=f"deployment manifest dla {app_name} w namespace {namespace}",
            depends_on=["generate_dockerfile"],
            save_output_as="k8s_manifest"
        ))
        
        # 4. Connect via SSH (if IP provided)
        if ip and password:
            steps.append(WorkflowStep(
                name="ssh_connect",
                converter="text2ssh",
                command=f"połącz się z {ip} jako {user} hasło {password}",
                save_output_as="ssh_connection"
            ))
            
            # 5. Deploy to K8s
            steps.append(WorkflowStep(
                name="deploy_to_k8s",
                converter="text2kubernetes",
                command=f"apply manifest dla {app_name}",
                depends_on=["generate_k8s_manifest", "ssh_connect"],
            ))
        
        return steps
    
    def _plan_test_and_replicate(
        self,
        params: Dict[str, Any],
        task: str
    ) -> List[WorkflowStep]:
        """Plan dla testowania i replikacji API"""
        
        target_lang = params.get('language', 'nodejs')
        
        steps = []
        
        # 1. Test API endpoints
        steps.append(WorkflowStep(
            name="test_api",
            converter="text2api",
            command="przetestuj wszystkie endpointy",
            save_output_as="api_tests"
        ))
        
        # 2. Analyze API structure
        steps.append(WorkflowStep(
            name="analyze_api",
            converter="text2api",
            command="przeanalizuj strukturę API i wyeksportuj OpenAPI spec",
            depends_on=["test_api"],
            save_output_as="openapi_spec"
        ))
        
        # 3. Generate new app
        steps.append(WorkflowStep(
            name="generate_app",
            converter="text3app",
            command=f"wygeneruj aplikację w {target_lang} na podstawie OpenAPI spec",
            depends_on=["analyze_api"],
            save_output_as="new_app"
        ))
        
        # 4. Generate tests for new app
        steps.append(WorkflowStep(
            name="generate_tests",
            converter="text3app",
            command=f"wygeneruj testy dla nowej aplikacji w {target_lang}",
            depends_on=["generate_app"],
            save_output_as="tests"
        ))
        
        return steps
    
    def _plan_full_stack_setup(
        self,
        params: Dict[str, Any],
        task: str
    ) -> List[WorkflowStep]:
        """Plan dla full-stack setup"""
        
        steps = []
        
        # Backend
        steps.append(WorkflowStep(
            name="generate_backend",
            converter="text3app",
            command="wygeneruj backend API",
            save_output_as="backend"
        ))
        
        # Frontend
        steps.append(WorkflowStep(
            name="generate_frontend",
            converter="text3app",
            command="wygeneruj frontend React",
            save_output_as="frontend"
        ))
        
        # Database
        steps.append(WorkflowStep(
            name="generate_database",
            converter="text3database",
            command="wygeneruj schemat bazy danych",
            save_output_as="database_schema"
        ))
        
        # Docker Compose
        steps.append(WorkflowStep(
            name="generate_compose",
            converter="text3compose",
            command="docker-compose dla full-stack",
            depends_on=["generate_backend", "generate_frontend", "generate_database"],
            save_output_as="docker_compose"
        ))
        
        return steps
    
    def _plan_infrastructure_setup(
        self,
        params: Dict[str, Any],
        task: str
    ) -> List[WorkflowStep]:
        """Plan dla infrastructure setup"""
        
        steps = []
        
        # Terraform
        steps.append(WorkflowStep(
            name="generate_terraform",
            converter="text3terraform",
            command="wygeneruj konfigurację Terraform dla K8s cluster",
            save_output_as="terraform_config"
        ))
        
        # Apply Terraform
        steps.append(WorkflowStep(
            name="apply_terraform",
            converter="text2terraform",
            command="apply terraform config",
            depends_on=["generate_terraform"]
        ))
        
        # Configure K8s
        steps.append(WorkflowStep(
            name="configure_k8s",
            converter="text2kubernetes",
            command="skonfiguruj klaster",
            depends_on=["apply_terraform"]
        ))
        
        return steps
    
    def _generate_plan_with_llm(
        self,
        task: str,
        params: Dict[str, Any]
    ) -> List[WorkflowStep]:
        """Używa LLM do wygenerowania planu dla custom zadania"""
        
        # TODO: Implementacja z użyciem LLM
        # Na razie zwróć pusty plan
        logger.warning("LLM planning not yet implemented")
        return []
    
    def execute(self, task_description: str) -> Dict[str, Any]:
        """
        Wykonuje złożone zadanie.
        
        Args:
            task_description: Opis zadania w języku naturalnym
            
        Returns:
            Dict z wynikami wszystkich kroków
        """
        logger.info(f"Rozpoczynam orchestrację: {task_description}")
        
        # 1. Wygeneruj plan
        steps = self.parse_complex_task(task_description)
        
        if not steps:
            return {
                "success": False,
                "error": "Nie można wygenerować planu dla tego zadania",
                "task": task_description
            }
        
        logger.info(f"Wygenerowano plan z {len(steps)} krokami")
        for i, step in enumerate(steps, 1):
            logger.info(f"  {i}. {step.name} ({step.converter})")
        
        # 2. Wykonaj kroki
        results = {}
        
        for step in steps:
            # Check dependencies
            if not self._check_dependencies(step, results):
                return {
                    "success": False,
                    "error": f"Dependency failed for step: {step.name}",
                    "completed_steps": results
                }
            
            # Execute step
            logger.info(f"Executing: {step.name}")
            
            if self.dry_run:
                result = ConversionResult(
                    success=True,
                    command=step.command,
                    output=f"[DRY RUN] Would execute {step.converter}: {step.command}"
                )
            else:
                # Get converter
                if step.converter not in self.converters:
                    result = ConversionResult(
                        success=False,
                        error=f"Converter not available: {step.converter}"
                    )
                else:
                    converter = self.converters[step.converter]
                    result = converter.execute(step.command)
            
            step.result = result
            results[step.name] = result
            
            # Save to context if requested
            if step.save_output_as:
                self.context[step.save_output_as] = result.output
            
            # Stop on error
            if not result.success:
                return {
                    "success": False,
                    "error": f"Step '{step.name}' failed: {result.error}",
                    "completed_steps": results,
                    "failed_step": step.name
                }
        
        # 3. Return results
        return {
            "success": True,
            "task": task_description,
            "steps": [s.name for s in steps],
            "results": results,
            "context": self.context
        }
    
    def _check_dependencies(
        self,
        step: WorkflowStep,
        completed: Dict[str, ConversionResult]
    ) -> bool:
        """Sprawdza czy wszystkie zależności zostały wykonane pomyślnie"""
        for dep in step.depends_on:
            if dep not in completed:
                logger.error(f"Missing dependency: {dep}")
                return False
            if not completed[dep].success:
                logger.error(f"Dependency failed: {dep}")
                return False
        return True
    
    def get_workflow_summary(self) -> Dict[str, Any]:
        """Zwraca podsumowanie workflow"""
        return {
            "registered_converters": list(self.converters.keys()),
            "context_keys": list(self.context.keys()),
            "history": self.workflow_history
        }
