"""
LLM-Powered Planning System

Inteligentne planowanie workflow używając modelu językowego.
"""

from typing import Dict, Any, List, Optional
from nlp2cmd.core.base import ConversionResult
import json
import logging

logger = logging.getLogger(__name__)


class LLMPlanner:
    """
    Planner wykorzystujący LLM do inteligentnego planowania kroków.
    
    Zamiast pattern matching, używa LLM do analizy zadania
    i generowania optymalnego planu.
    """
    
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        """
        Inicjalizacja LLM Planner.
        
        Args:
            model_name: Nazwa modelu LLM
        """
        self.model_name = model_name
        self.available_converters = {}
    
    def register_converter(self, name: str, description: str, capabilities: List[str]):
        """
        Rejestruje konwerter w plannerze.
        
        Args:
            name: Nazwa konwertera
            description: Opis funkcjonalności
            capabilities: Lista możliwości
        """
        self.available_converters[name] = {
            "description": description,
            "capabilities": capabilities
        }
    
    def plan(self, task: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Planuje workflow dla zadania używając LLM.
        
        Args:
            task: Opis zadania w języku naturalnym
            context: Opcjonalny kontekst (poprzednie kroki, dane)
            
        Returns:
            Plan workflow jako Dict
        """
        logger.info(f"Planning workflow for: {task}")
        
        # Przygotuj prompt dla LLM
        prompt = self._create_planning_prompt(task, context)
        
        # W produkcji: wywołaj prawdziwy LLM
        # plan_json = self._call_llm(prompt)
        
        # Na razie: symuluj inteligentne planowanie
        plan = self._simulate_llm_planning(task, context)
        
        logger.info(f"Generated plan with {len(plan['steps'])} steps")
        return plan
    
    def _create_planning_prompt(self, task: str, context: Optional[Dict]) -> str:
        """Tworzy prompt dla LLM"""
        
        converters_desc = "\n".join([
            f"- {name}: {info['description']}"
            for name, info in self.available_converters.items()
        ])
        
        prompt = f"""You are an expert DevOps engineer. Analyze this task and create a step-by-step workflow.

Task: {task}

Available converters:
{converters_desc}

Context: {json.dumps(context or {}, indent=2)}

Create a workflow plan as JSON with this structure:
{{
  "steps": [
    {{
      "name": "step_name",
      "converter": "converter_name",
      "command": "natural language command",
      "depends_on": ["previous_step_name"],
      "save_output_as": "variable_name"
    }}
  ],
  "reasoning": "explanation of the plan"
}}

Important:
1. Break down complex tasks into simple steps
2. Respect dependencies between steps
3. Pass data between steps using save_output_as
4. Use the most appropriate converter for each step
5. Keep steps atomic and focused

Generate the plan:"""
        
        return prompt
    
    def _simulate_llm_planning(self, task: str, context: Optional[Dict]) -> Dict[str, Any]:
        """
        Symuluje inteligentne planowanie LLM.
        
        W rzeczywistości to byłby wywołanie do OpenAI/Anthropic API.
        """
        task_lower = task.lower()
        
        # Zaawansowana analiza zadania
        steps = []
        
        # Detect multiple services
        if "microservices" in task_lower or "services" in task_lower:
            steps.extend(self._plan_microservices(task))
        
        # Detect deployment
        elif "deploy" in task_lower or "wdróż" in task_lower:
            steps.extend(self._plan_deployment(task))
        
        # Detect testing
        elif "test" in task_lower or "przetestuj" in task_lower:
            steps.extend(self._plan_testing(task))
        
        # Detect infrastructure
        elif "infrastructure" in task_lower or "infrastruktura" in task_lower:
            steps.extend(self._plan_infrastructure(task))
        
        # Single application
        elif "aplikacja" in task_lower or "application" in task_lower:
            steps.extend(self._plan_application(task))
        
        else:
            # Generic planning
            steps.extend(self._plan_generic(task))
        
        return {
            "steps": steps,
            "reasoning": f"Analyzed task and determined {len(steps)} steps needed",
            "complexity": self._estimate_complexity(steps),
            "estimated_duration": len(steps) * 2  # seconds
        }
    
    def _plan_application(self, task: str) -> List[Dict]:
        """Plan dla generowania aplikacji"""
        
        steps = []
        
        # Extract details
        needs_docker = "docker" in task.lower()
        needs_k8s = "kubernetes" in task.lower() or "k8s" in task.lower()
        needs_tests = "test" in task.lower()
        
        # Step 1: Generate app
        steps.append({
            "name": "generate_application",
            "converter": "text3app",
            "command": task,
            "depends_on": [],
            "save_output_as": "app_code"
        })
        
        # Step 2: Tests if needed
        if needs_tests:
            steps.append({
                "name": "generate_tests",
                "converter": "text3app",
                "command": "generate tests for application",
                "depends_on": ["generate_application"],
                "save_output_as": "test_code"
            })
        
        # Step 3: Dockerfile if needed
        if needs_docker or needs_k8s:
            steps.append({
                "name": "generate_dockerfile",
                "converter": "text3docker",
                "command": "generate dockerfile for application",
                "depends_on": ["generate_application"],
                "save_output_as": "dockerfile"
            })
        
        # Step 4: K8s manifests if needed
        if needs_k8s:
            steps.append({
                "name": "generate_k8s_manifests",
                "converter": "text3kubernetes",
                "command": "generate kubernetes manifests",
                "depends_on": ["generate_dockerfile"],
                "save_output_as": "k8s_manifests"
            })
        
        return steps
    
    def _plan_deployment(self, task: str) -> List[Dict]:
        """Plan dla deployment"""
        
        return [
            {
                "name": "generate_app",
                "converter": "text3app",
                "command": task,
                "depends_on": [],
                "save_output_as": "app_code"
            },
            {
                "name": "generate_dockerfile",
                "converter": "text3docker",
                "command": "dockerfile for application",
                "depends_on": ["generate_app"],
                "save_output_as": "dockerfile"
            },
            {
                "name": "generate_k8s_deployment",
                "converter": "text3kubernetes",
                "command": "kubernetes deployment",
                "depends_on": ["generate_dockerfile"],
                "save_output_as": "k8s_deployment"
            },
            {
                "name": "generate_k8s_service",
                "converter": "text3kubernetes",
                "command": "kubernetes service",
                "depends_on": ["generate_k8s_deployment"],
                "save_output_as": "k8s_service"
            }
        ]
    
    def _plan_microservices(self, task: str) -> List[Dict]:
        """Plan dla architektury microservices"""
        
        # Extract number of services (simplified)
        import re
        num_match = re.search(r'(\d+)\s+(?:services?|serwis)', task.lower())
        num_services = int(num_match.group(1)) if num_match else 3
        
        steps = []
        
        service_names = ["gateway", "users", "products", "orders", "payments"][:num_services]
        
        for service in service_names:
            # Generate each service
            steps.append({
                "name": f"generate_{service}_service",
                "converter": "text3app",
                "command": f"generate {service} service",
                "depends_on": [],
                "save_output_as": f"{service}_code"
            })
            
            # Dockerfile for each
            steps.append({
                "name": f"generate_{service}_dockerfile",
                "converter": "text3docker",
                "command": f"dockerfile for {service}",
                "depends_on": [f"generate_{service}_service"],
                "save_output_as": f"{service}_dockerfile"
            })
            
            # K8s manifests for each
            steps.append({
                "name": f"generate_{service}_k8s",
                "converter": "text3kubernetes",
                "command": f"kubernetes manifests for {service}",
                "depends_on": [f"generate_{service}_dockerfile"],
                "save_output_as": f"{service}_k8s"
            })
        
        return steps
    
    def _plan_testing(self, task: str) -> List[Dict]:
        """Plan dla testowania"""
        
        return [
            {
                "name": "test_api_endpoints",
                "converter": "text2api",
                "command": task,
                "depends_on": [],
                "save_output_as": "test_results"
            },
            {
                "name": "analyze_api_structure",
                "converter": "text2api",
                "command": "analyze api structure",
                "depends_on": ["test_api_endpoints"],
                "save_output_as": "api_structure"
            },
            {
                "name": "generate_openapi_spec",
                "converter": "text2api",
                "command": "generate openapi spec",
                "depends_on": ["analyze_api_structure"],
                "save_output_as": "openapi_spec"
            }
        ]
    
    def _plan_infrastructure(self, task: str) -> List[Dict]:
        """Plan dla infrastruktury"""
        
        return [
            {
                "name": "generate_terraform",
                "converter": "text3terraform",
                "command": task,
                "depends_on": [],
                "save_output_as": "terraform_config"
            },
            {
                "name": "validate_terraform",
                "converter": "text2terraform",
                "command": "validate terraform config",
                "depends_on": ["generate_terraform"],
                "save_output_as": "validation_result"
            }
        ]
    
    def _plan_generic(self, task: str) -> List[Dict]:
        """Generic planning fallback"""
        
        return [
            {
                "name": "execute_task",
                "converter": "text3app",  # Default converter
                "command": task,
                "depends_on": [],
                "save_output_as": "result"
            }
        ]
    
    def _estimate_complexity(self, steps: List[Dict]) -> str:
        """Szacuje złożoność workflow"""
        
        num_steps = len(steps)
        
        if num_steps <= 2:
            return "simple"
        elif num_steps <= 5:
            return "medium"
        elif num_steps <= 10:
            return "complex"
        else:
            return "very_complex"
    
    def optimize_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optymalizuje plan workflow.
        
        - Usuwa redundantne kroki
        - Identyfikuje równoległe wykonanie
        - Optymalizuje zależności
        """
        steps = plan["steps"]
        optimized = []
        seen_commands = set()
        
        for step in steps:
            # Remove duplicates
            cmd_signature = f"{step['converter']}:{step['command']}"
            
            if cmd_signature not in seen_commands:
                optimized.append(step)
                seen_commands.add(cmd_signature)
        
        # Identify parallel opportunities
        parallel_groups = self._identify_parallel_steps(optimized)
        
        return {
            **plan,
            "steps": optimized,
            "parallel_groups": parallel_groups,
            "optimizations_applied": len(steps) - len(optimized)
        }
    
    def _identify_parallel_steps(self, steps: List[Dict]) -> List[List[str]]:
        """Identyfikuje kroki, które mogą być wykonane równolegle"""
        
        groups = []
        current_group = []
        
        for step in steps:
            if not step["depends_on"]:
                # Independent step - can run in parallel
                current_group.append(step["name"])
            else:
                # Has dependencies - new group
                if current_group:
                    groups.append(current_group)
                    current_group = []
                current_group.append(step["name"])
        
        if current_group:
            groups.append(current_group)
        
        # Return only groups with >1 step
        return [g for g in groups if len(g) > 1]
    
    def explain_plan(self, plan: Dict[str, Any]) -> str:
        """
        Generuje ludzko-czytelne wyjaśnienie planu.
        """
        steps = plan["steps"]
        complexity = plan.get("complexity", "unknown")
        
        explanation = f"Workflow Analysis:\n\n"
        explanation += f"Complexity: {complexity}\n"
        explanation += f"Total Steps: {len(steps)}\n"
        explanation += f"Estimated Duration: {plan.get('estimated_duration', 'unknown')}s\n\n"
        
        explanation += "Execution Plan:\n"
        
        for i, step in enumerate(steps, 1):
            explanation += f"\n{i}. {step['name']}\n"
            explanation += f"   Converter: {step['converter']}\n"
            explanation += f"   Command: {step['command']}\n"
            
            if step['depends_on']:
                explanation += f"   Depends on: {', '.join(step['depends_on'])}\n"
            
            if step.get('save_output_as'):
                explanation += f"   Saves as: {step['save_output_as']}\n"
        
        if "parallel_groups" in plan and plan["parallel_groups"]:
            explanation += "\n\nParallel Execution Opportunities:\n"
            for i, group in enumerate(plan["parallel_groups"], 1):
                explanation += f"{i}. {', '.join(group)}\n"
        
        return explanation
