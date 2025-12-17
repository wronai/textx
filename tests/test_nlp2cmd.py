"""
Testy jednostkowe dla NLP2CMD.
"""

import pytest
import tempfile
from pathlib import Path
from nlp2cmd import Text2Env, Text2Bash, Text2Makefile, Text2Docker, Pipeline
from nlp2cmd.core.base import ConversionResult


class TestText2Env:
    """Testy dla Text2Env"""
    
    def setup_method(self):
        """Setup dla każdego testu"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False)
        self.temp_file.close()
        self.env = Text2Env(env_file=self.temp_file.name, dry_run=True)
    
    def teardown_method(self):
        """Cleanup po teście"""
        Path(self.temp_file.name).unlink(missing_ok=True)
    
    def test_parse_set_command(self):
        """Test parsowania komendy set"""
        intent = self.env.parse_intent("ustaw PORT na 8080")
        assert intent["action"] == "set"
        assert intent["key"] == "PORT"
        assert intent["value"] == "8080"
    
    def test_parse_add_command(self):
        """Test parsowania komendy add"""
        intent = self.env.parse_intent("dodaj API_KEY z wartością xyz123")
        assert intent["action"] == "add"
        assert intent["key"] == "API_KEY"
        assert intent["value"] == "xyz123"
    
    def test_parse_delete_command(self):
        """Test parsowania komendy delete"""
        intent = self.env.parse_intent("usuń DEBUG")
        assert intent["action"] == "delete"
        assert intent["key"] == "DEBUG"
    
    def test_execute_set(self):
        """Test wykonania set"""
        result = self.env.execute("ustaw PORT na 8080")
        assert result.success
        assert "PORT" in result.command


class TestText2Bash:
    """Testy dla Text2Bash"""
    
    def setup_method(self):
        self.bash = Text2Bash(dry_run=True)
    
    def test_parse_list_files(self):
        """Test parsowania listowania plików"""
        intent = self.bash.parse_intent("pokaż pliki")
        assert intent["command"] == "ls -lh"
    
    def test_parse_find_files(self):
        """Test parsowania wyszukiwania"""
        intent = self.bash.parse_intent("znajdź readme")
        assert "find" in intent["command"]
        assert "readme" in intent["command"]
    
    def test_execute_safe_command(self):
        """Test wykonania bezpiecznej komendy"""
        result = self.bash.execute("pokaż pliki")
        assert result.success
    
    def test_validate_dangerous_command(self):
        """Test walidacji niebezpiecznej komendy"""
        # W safe_mode powinno odrzucić
        self.bash.safe_mode = True
        assert not self.bash.validate_command("rm -rf /")
        
        # Bez safe_mode powinno przejść przez BaseConverter
        self.bash.safe_mode = False
        assert not self.bash.validate_command("rm -rf /")  # Nadal złapie BaseConverter


class TestText2Docker:
    """Testy dla Text2Docker"""
    
    def setup_method(self):
        self.docker = Text2Docker(dry_run=True)
    
    def test_parse_run_postgres(self):
        """Test parsowania uruchomienia postgres"""
        intent = self.docker.parse_intent("uruchom postgres")
        assert intent["action"] == "run"
        assert intent["service"] == "postgres"
    
    def test_parse_stop_container(self):
        """Test parsowania zatrzymania kontenera"""
        intent = self.docker.parse_intent("zatrzymaj redis")
        assert intent["action"] == "stop"
        assert intent["service"] == "redis"
    
    def test_generate_run_command(self):
        """Test generowania komendy run"""
        intent = {
            "action": "run",
            "service": "postgres",
            "options": {"port": "5432"}
        }
        command = self.docker.generate_command(intent)
        assert "docker run" in command
        assert "postgres" in command
        assert "5432" in command


class TestPipeline:
    """Testy dla Pipeline"""
    
    def setup_method(self):
        self.pipeline = Pipeline()
        self.pipeline.add_module("bash", Text2Bash(dry_run=True))
        self.pipeline.add_module("docker", Text2Docker(dry_run=True))
    
    def test_add_module(self):
        """Test dodawania modułu"""
        assert "bash" in self.pipeline.modules
        assert "docker" in self.pipeline.modules
    
    def test_execute_steps(self):
        """Test wykonania kroków"""
        steps = [
            ("bash", "pokaż pliki"),
            ("docker", "uruchom postgres"),
        ]
        
        results = self.pipeline.execute(steps)
        assert len(results) == 2
        assert all(r.success for r in results)
    
    def test_stop_on_error(self):
        """Test zatrzymania przy błędzie"""
        self.pipeline.stop_on_error = True
        
        steps = [
            ("bash", "pokaż pliki"),
            ("nonexistent", "błędna komenda"),
            ("bash", "to nie powinno się wykonać"),
        ]
        
        results = self.pipeline.execute(steps)
        assert len(results) == 2  # Powinno zatrzymać po błędzie
        assert not results[1].success
    
    def test_get_summary(self):
        """Test podsumowania"""
        steps = [
            ("bash", "pokaż pliki"),
            ("bash", "znajdź readme"),
        ]
        
        self.pipeline.execute(steps)
        summary = self.pipeline.get_summary()
        
        assert summary["total_executions"] == 2
        assert summary["successful"] == 2
        assert summary["failed"] == 0
        assert summary["success_rate"] == 1.0


class TestValidators:
    """Testy dla walidatorów"""
    
    def test_security_validator(self):
        """Test SecurityValidator"""
        from nlp2cmd.utils.validators import SecurityValidator
        
        validator = SecurityValidator()
        
        # Bezpieczne komendy
        assert validator.validate("ls -la")
        assert validator.validate("cat file.txt")
        
        # Niebezpieczne komendy
        assert not validator.validate("rm -rf /")
        assert not validator.validate(":(){ :|:& };:")
    
    def test_input_sanitizer(self):
        """Test InputSanitizer"""
        from nlp2cmd.utils.validators import InputSanitizer
        
        # Sanitize shell input
        dirty = "ls -la; rm -rf /"
        clean = InputSanitizer.sanitize_shell_input(dirty)
        assert ";" not in clean
        
        # Sanitize path
        dirty_path = "../../../etc/passwd"
        clean_path = InputSanitizer.sanitize_path(dirty_path)
        assert ".." not in clean_path


class TestParsers:
    """Testy dla parserów"""
    
    def test_env_parser(self):
        """Test EnvParser"""
        from nlp2cmd.utils.parsers import EnvParser
        
        content = """
PORT=8080
DEBUG=true
DATABASE_URL="postgres://localhost/db"
"""
        
        parsed = EnvParser.parse(content)
        assert parsed["PORT"] == "8080"
        assert parsed["DEBUG"] == "true"
        assert parsed["DATABASE_URL"] == "postgres://localhost/db"
    
    def test_command_parser(self):
        """Test CommandParser"""
        from nlp2cmd.utils.parsers import CommandParser
        
        # Parse pipeline
        pipeline = "cat file.txt | grep error | wc -l"
        commands = CommandParser.parse_pipeline(pipeline)
        assert len(commands) == 3
        assert commands[0] == "cat file.txt"
        
        # Extract arguments
        command = "ls -la --color=auto /home"
        parsed = CommandParser.extract_arguments(command)
        assert parsed["command"] == "ls"
        assert "-la" in parsed["flags"]
        assert "/home" in parsed["args"]


# Fixtures
@pytest.fixture
def temp_env_file():
    """Tymczasowy plik .env"""
    temp = tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False)
    temp.write("PORT=8080\nDEBUG=false\n")
    temp.close()
    yield temp.name
    Path(temp.name).unlink(missing_ok=True)


@pytest.fixture
def temp_makefile():
    """Tymczasowy Makefile"""
    temp = tempfile.NamedTemporaryFile(mode='w', suffix='', delete=False)
    temp.write("""
.PHONY: build test clean

build:
\techo "Building..."

test:
\techo "Testing..."

clean:
\techo "Cleaning..."
""")
    temp.close()
    yield temp.name
    Path(temp.name).unlink(missing_ok=True)


# Testy integracyjne
class TestIntegration:
    """Testy integracyjne"""
    
    def test_full_workflow(self, temp_env_file):
        """Test pełnego workflow"""
        # Stwórz pipeline z różnymi modułami
        pipeline = Pipeline()
        pipeline.add_module("env", Text2Env(env_file=temp_env_file, dry_run=True))
        pipeline.add_module("bash", Text2Bash(dry_run=True))
        
        # Wykonaj sekwencję operacji
        steps = [
            ("env", "ustaw PORT na 9000"),
            ("bash", "pokaż pliki"),
            ("env", "dodaj NEW_VAR z wartością test"),
        ]
        
        results = pipeline.execute(steps)
        
        # Sprawdź wyniki
        assert len(results) == 3
        assert all(r.success for r in results)
        
        # Sprawdź podsumowanie
        summary = pipeline.get_summary()
        assert summary["successful"] == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
