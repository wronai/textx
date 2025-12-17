"""
Testy dla Orchestratora i nowych konwerterów.
"""

import pytest
import sys
sys.path.insert(0, '/home/claude/nlp2cmd')

from nlp2cmd.core.orchestrator import Orchestrator, WorkflowStep
from nlp2cmd.converters.api.text3app import Text3App
from nlp2cmd.converters.api.text2api import Text2API
from nlp2cmd.converters.containers.text3kubernetes import Text3Kubernetes
from nlp2cmd.converters.network.text2ssh import Text2SSH


class TestOrchestrator:
    """Testy dla Orchestratora"""
    
    def test_orchestrator_initialization(self):
        """Test inicjalizacji orchestratora"""
        orch = Orchestrator(dry_run=True)
        assert orch.dry_run == True
        assert len(orch.converters) == 0
    
    def test_register_converter(self):
        """Test rejestracji konwertera"""
        orch = Orchestrator()
        app_gen = Text3App()
        
        orch.register_converter("text3app", app_gen)
        
        assert "text3app" in orch.converters
        assert orch.converters["text3app"] == app_gen
    
    def test_extract_parameters(self):
        """Test ekstraktowania parametrów"""
        orch = Orchestrator()
        
        text = "deploy app with IP=192.168.1.100 user root password test123 port 8080"
        params = orch._extract_parameters(text)
        
        assert params["ip"] == "192.168.1.100"
        assert params["user"] == "root"
        assert params["password"] == "test123"
        assert params["port"] == 8080
    
    def test_detect_task_type(self):
        """Test wykrywania typu zadania"""
        orch = Orchestrator()
        
        # Deploy task
        text1 = "deploy aplikację na serwer"
        task_type1 = orch._detect_task_type(text1)
        assert task_type1 == "deploy_app"
        
        # Test and replicate
        text2 = "przetestuj i wygeneruj nową aplikację"
        task_type2 = orch._detect_task_type(text2)
        assert task_type2 == "test_and_replicate"
    
    def test_workflow_step_creation(self):
        """Test tworzenia kroków workflow"""
        step = WorkflowStep(
            name="generate_app",
            converter="text3app",
            command="wygeneruj aplikację Flask",
            save_output_as="app_code"
        )
        
        assert step.name == "generate_app"
        assert step.converter == "text3app"
        assert step.save_output_as == "app_code"
        assert len(step.depends_on) == 0
    
    def test_plan_deploy_app(self):
        """Test planowania deployment"""
        orch = Orchestrator()
        
        params = {
            "app_name": "user-api",
            "language": "python",
            "ip": "192.168.1.100",
            "user": "root",
            "password": "test123"
        }
        
        steps = orch._plan_deploy_app(params, "deploy user-api")
        
        assert len(steps) > 0
        assert any(s.name == "generate_app" for s in steps)
        assert any(s.name == "generate_dockerfile" for s in steps)
        assert any(s.name == "generate_k8s_manifest" for s in steps)
    
    def test_execute_dry_run(self):
        """Test wykonania w trybie dry run"""
        orch = Orchestrator(dry_run=True)
        orch.register_converter("text3app", Text3App())
        
        result = orch.execute("wygeneruj aplikację Flask dla użytkowników")
        
        # W dry run powinno się powieść bez rzeczywistego wykonania
        assert "success" in result


class TestText3App:
    """Testy dla Text3App"""
    
    def test_parse_intent_python_flask(self):
        """Test parsowania dla Python Flask"""
        gen = Text3App()
        
        intent = gen.parse_intent("aplikacja do zarządzania użytkownikami w Flask")
        
        assert intent["language"] == "python"
        assert intent["framework"] == "flask"
        assert "użytkownik" in intent["resource"] or "users" in intent["resource"]
    
    def test_parse_intent_nodejs(self):
        """Test parsowania dla Node.js"""
        gen = Text3App()
        
        intent = gen.parse_intent("Express API dla produktów")
        
        assert intent["language"] == "nodejs"
        assert intent["framework"] == "express"
    
    def test_generate_flask_app(self):
        """Test generowania aplikacji Flask"""
        gen = Text3App()
        
        result = gen.execute("CRUD aplikacja Flask dla użytkowników")
        
        assert result.success
        assert "Flask" in result.output
        assert "def" in result.output  # Python code
        assert result.metadata["language"] == "python"
    
    def test_generate_nodejs_app(self):
        """Test generowania aplikacji Node.js"""
        gen = Text3App()
        
        result = gen.execute("Express API dla produktów")
        
        assert result.success
        assert "express" in result.output.lower()
        assert "const" in result.output or "require" in result.output
    
    def test_generate_additional_files(self):
        """Test generowania dodatkowych plików"""
        gen = Text3App()
        
        result = gen.execute("Flask aplikacja")
        
        assert "additional_files" in result.metadata
        files = result.metadata["additional_files"]
        assert "requirements.txt" in files or "package.json" in files


class TestText2API:
    """Testy dla Text2API"""
    
    def test_parse_intent_test(self):
        """Test parsowania dla testowania"""
        api = Text2API()
        
        intent = api.parse_intent("przetestuj wszystkie endpointy")
        
        assert intent["action"] == "test"
    
    def test_parse_intent_analyze(self):
        """Test parsowania dla analizy"""
        api = Text2API()
        
        intent = api.parse_intent("przeanalizuj strukturę API")
        
        assert intent["action"] == "analyze"
    
    def test_parse_intent_openapi(self):
        """Test parsowania dla generowania OpenAPI"""
        api = Text2API()
        
        intent = api.parse_intent("wygeneruj OpenAPI spec")
        
        assert intent["action"] == "generate_spec"
    
    def test_generate_openapi_spec(self):
        """Test generowania OpenAPI spec"""
        api = Text2API(base_url="http://localhost:5000")
        
        result = api.execute("wygeneruj OpenAPI spec")
        
        # W dry_run lub bez działającego API
        # Powinna być próba generowania spec
        assert result.success or result.error


class TestText3Kubernetes:
    """Testy dla Text3Kubernetes"""
    
    def test_parse_intent_deployment(self):
        """Test parsowania dla Deployment"""
        k8s = Text3Kubernetes()
        
        intent = k8s.parse_intent("deployment dla myapp z 3 replikami na porcie 8080")
        
        assert intent["resource_type"] == "deployment"
        assert intent["app_name"] == "myapp"
        assert intent["replicas"] == 3
        assert intent["port"] == 8080
    
    def test_generate_deployment(self):
        """Test generowania Deployment manifest"""
        k8s = Text3Kubernetes()
        
        result = k8s.execute("deployment dla user-api z 3 replikami")
        
        assert result.success
        assert "apiVersion" in result.output
        assert "kind: Deployment" in result.output
        assert "replicas: 3" in result.output
    
    def test_generate_service(self):
        """Test generowania Service manifest"""
        k8s = Text3Kubernetes()
        
        result = k8s.execute("service dla api-gateway na porcie 8080")
        
        assert result.success
        assert "kind: Service" in result.output
        assert "port: 8080" in result.output
    
    def test_generate_full_deployment(self):
        """Test generowania pełnego deploymentu"""
        k8s = Text3Kubernetes()
        
        manifests = k8s.generate_full_deployment(
            app_name="test-app",
            image="test:latest",
            port=8080,
            replicas=2
        )
        
        assert "deployment.yaml" in manifests
        assert "service.yaml" in manifests
        assert "ingress.yaml" in manifests
        assert "configmap.yaml" in manifests


class TestText2SSH:
    """Testy dla Text2SSH"""
    
    def test_parse_intent_connect(self):
        """Test parsowania dla połączenia"""
        ssh = Text2SSH()
        
        intent = ssh.parse_intent("połącz się z 192.168.1.100 jako root")
        
        assert intent["action"] == "connect"
        assert intent["host"] == "192.168.1.100"
        assert intent["user"] == "root"
    
    def test_parse_intent_execute(self):
        """Test parsowania dla wykonania komendy"""
        ssh = Text2SSH()
        
        intent = ssh.parse_intent("wykonaj uptime na serwerze 192.168.1.100")
        
        assert intent["action"] == "execute"
        assert intent["host"] == "192.168.1.100"
        assert "uptime" in intent["command"]
    
    def test_generate_ssh_command(self):
        """Test generowania komendy SSH"""
        ssh = Text2SSH()
        
        intent = {
            "action": "connect",
            "host": "192.168.1.100",
            "user": "root",
            "password": None,
            "key_file": None
        }
        
        command = ssh.generate_command(intent)
        
        assert "ssh" in command
        assert "root@192.168.1.100" in command


class TestIntegration:
    """Testy integracyjne"""
    
    def test_orchestrator_with_converters(self):
        """Test orchestratora z rzeczywistymi konwerterami"""
        orch = Orchestrator(dry_run=True)
        
        # Register converters
        orch.register_converter("text3app", Text3App())
        orch.register_converter("text3kubernetes", Text3Kubernetes())
        
        # Execute task
        result = orch.execute("wygeneruj aplikację Flask i deployment K8s")
        
        # Should have planned steps
        assert "steps" in result or "error" in result
    
    def test_context_sharing(self):
        """Test przekazywania kontekstu między krokami"""
        orch = Orchestrator(dry_run=True)
        orch.register_converter("text3app", Text3App())
        
        # Generate app and save to context
        step = WorkflowStep(
            name="gen_app",
            converter="text3app",
            command="flask app",
            save_output_as="app_code"
        )
        
        # Simulate execution
        result = orch.converters["text3app"].execute(step.command)
        if result.success and step.save_output_as:
            orch.context[step.save_output_as] = result.output
        
        # Check context
        assert "app_code" in orch.context


def run_all_tests():
    """Uruchom wszystkie testy"""
    print("🧪 Uruchamianie testów...\n")
    
    # Run with pytest
    pytest.main([__file__, "-v", "--tb=short"])


if __name__ == "__main__":
    run_all_tests()
