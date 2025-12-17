"""
Text3Docker - Generowanie Dockerfiles na podstawie opisów w języku naturalnym.

Ten konwerter generuje optymalne Dockerfiles dla różnych technologii.
"""

from typing import Dict, Any, Optional, List
from nlp2cmd.core.base import BaseConverter, ConversionResult
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class Text3Docker(BaseConverter):
    """
    Generator Dockerfiles z języka naturalnego.
    
    Obsługuje:
    - Różne języki i frameworki (Python, Node.js, Go, Java, etc.)
    - Multi-stage builds
    - Best practices Docker
    - Optymalizacja warstw
    - Security hardening
    """
    
    # Bazowe obrazy dla różnych technologii
    BASE_IMAGES = {
        "python": {
            "default": "python:3.11-slim",
            "alpine": "python:3.11-alpine",
            "full": "python:3.11"
        },
        "node": {
            "default": "node:20-slim",
            "alpine": "node:20-alpine",
            "full": "node:20"
        },
        "go": {
            "default": "golang:1.21-alpine",
            "builder": "golang:1.21-alpine",
            "runtime": "alpine:3.18"
        },
        "java": {
            "default": "eclipse-temurin:21-jre-alpine",
            "builder": "maven:3.9-eclipse-temurin-21",
            "runtime": "eclipse-temurin:21-jre-alpine"
        },
        "php": {
            "default": "php:8.3-fpm-alpine",
            "apache": "php:8.3-apache",
            "nginx": "php:8.3-fpm-alpine"
        },
        "ruby": {
            "default": "ruby:3.3-alpine",
            "full": "ruby:3.3"
        }
    }
    
    def __init__(
        self,
        multi_stage: bool = True,
        optimize_layers: bool = True,
        include_healthcheck: bool = True,
        **kwargs
    ):
        """
        Inicjalizacja Text3Docker.
        
        Args:
            multi_stage: Czy używać multi-stage builds
            optimize_layers: Czy optymalizować warstwy
            include_healthcheck: Czy dodawać HEALTHCHECK
        """
        super().__init__(**kwargs)
        self.multi_stage = multi_stage
        self.optimize_layers = optimize_layers
        self.include_healthcheck = include_healthcheck
    
    def parse_intent(self, text: str) -> Dict[str, Any]:
        """
        Parsuje intencję z tekstu.
        
        Returns:
            {
                "language": str,        # python, node, go, etc.
                "framework": str | None, # flask, django, express, etc.
                "image_variant": str,   # slim, alpine, full
                "port": int,           # Exposed port
                "features": List[str]  # Dodatkowe funkcje
            }
        """
        text = text.strip().lower()
        
        # Wykryj język
        language = None
        for lang in self.BASE_IMAGES:
            if lang in text:
                language = lang
                break
        
        if not language:
            # Domyślnie Python
            language = "python"
        
        # Wykryj framework
        framework = None
        frameworks = {
            "python": ["flask", "django", "fastapi", "streamlit"],
            "node": ["express", "nest", "next", "react"],
            "java": ["spring", "quarkus"],
            "php": ["laravel", "symfony", "wordpress"],
        }
        
        if language in frameworks:
            for fw in frameworks[language]:
                if fw in text:
                    framework = fw
                    break
        
        # Wykryj wariant obrazu
        image_variant = "default"
        if "alpine" in text:
            image_variant = "alpine"
        elif "slim" in text:
            image_variant = "slim"
        elif "full" in text or "complete" in text:
            image_variant = "full"
        
        # Wykryj port
        port = 8080
        if "port" in text or "porcie" in text:
            import re
            port_match = re.search(r'\d{4,5}', text)
            if port_match:
                port = int(port_match.group())
        elif framework == "flask":
            port = 5000
        elif framework == "express":
            port = 3000
        elif framework == "nginx":
            port = 80
        
        # Dodatkowe funkcje
        features = []
        if "nginx" in text:
            features.append("nginx")
        if "redis" in text:
            features.append("redis")
        if "postgres" in text or "postgresql" in text:
            features.append("postgres")
        if "mysql" in text:
            features.append("mysql")
        
        return {
            "language": language,
            "framework": framework,
            "image_variant": image_variant,
            "port": port,
            "features": features,
            "description": text
        }
    
    def generate_command(self, intent: Dict[str, Any]) -> str:
        """
        Generuje Dockerfile.
        
        Returns:
            Kompletny Dockerfile
        """
        language = intent["language"]
        
        if self.multi_stage and language in ["go", "java"]:
            return self._generate_multistage(intent)
        else:
            return self._generate_single_stage(intent)
    
    def _generate_single_stage(self, intent: Dict[str, Any]) -> str:
        """Generuje single-stage Dockerfile"""
        parts = []
        
        # 1. Header & Base image
        parts.append(self._generate_header(intent))
        parts.append(self._generate_base_image(intent))
        
        # 2. Metadata
        parts.append(self._generate_metadata(intent))
        
        # 3. Working directory
        parts.append("WORKDIR /app")
        
        # 4. Dependencies
        parts.append(self._generate_dependencies(intent))
        
        # 5. Copy application
        parts.append(self._generate_copy_app(intent))
        
        # 6. Expose port
        parts.append(f"\nEXPOSE {intent['port']}")
        
        # 7. Healthcheck
        if self.include_healthcheck:
            parts.append(self._generate_healthcheck(intent))
        
        # 8. User (security)
        parts.append(self._generate_user())
        
        # 9. CMD
        parts.append(self._generate_cmd(intent))
        
        return "\n\n".join(parts)
    
    def _generate_multistage(self, intent: Dict[str, Any]) -> str:
        """Generuje multi-stage Dockerfile"""
        parts = []
        
        # Stage 1: Builder
        parts.append(self._generate_header(intent))
        parts.append("# Build stage")
        parts.append(self._generate_builder_stage(intent))
        
        # Stage 2: Runtime
        parts.append("\n# Runtime stage")
        parts.append(self._generate_runtime_stage(intent))
        
        return "\n\n".join(parts)
    
    def _generate_header(self, intent: Dict[str, Any]) -> str:
        """Generuje header Dockerfile"""
        return f"""# Generated by NLP2CMD
# Language: {intent['language']}
# Framework: {intent.get('framework', 'N/A')}
# Description: {intent['description']}"""
    
    def _generate_base_image(self, intent: Dict[str, Any]) -> str:
        """Generuje FROM directive"""
        lang = intent["language"]
        variant = intent["image_variant"]
        
        base = self.BASE_IMAGES[lang].get(variant, self.BASE_IMAGES[lang]["default"])
        
        return f"FROM {base}"
    
    def _generate_metadata(self, intent: Dict[str, Any]) -> str:
        """Generuje LABEL directives"""
        return """LABEL maintainer="your-email@example.com"
LABEL version="1.0"
LABEL description="Application container\""""
    
    def _generate_dependencies(self, intent: Dict[str, Any]) -> str:
        """Generuje instalację dependencies"""
        lang = intent["language"]
        
        if lang == "python":
            return """# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt"""
        
        elif lang == "node":
            return """# Install dependencies
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force"""
        
        elif lang == "go":
            return """# Download dependencies
COPY go.mod go.sum ./
RUN go mod download"""
        
        elif lang == "java":
            return """# Copy and build
COPY pom.xml .
COPY src ./src
RUN mvn clean package -DskipTests"""
        
        elif lang == "php":
            if "composer" in intent.get("features", []):
                return """# Install dependencies
COPY composer.json composer.lock ./
RUN composer install --no-dev --optimize-autoloader"""
            return ""
        
        return ""
    
    def _generate_copy_app(self, intent: Dict[str, Any]) -> str:
        """Generuje COPY directive dla aplikacji"""
        lang = intent["language"]
        
        if lang == "python":
            return """# Copy application
COPY . ."""
        
        elif lang == "node":
            return """# Copy application
COPY . ."""
        
        elif lang == "go":
            return """# Copy source
COPY . .

# Build
RUN go build -o app ."""
        
        return "COPY . ."
    
    def _generate_healthcheck(self, intent: Dict[str, Any]) -> str:
        """Generuje HEALTHCHECK"""
        port = intent["port"]
        
        return f"""HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
  CMD curl -f http://localhost:{port}/health || exit 1"""
    
    def _generate_user(self) -> str:
        """Generuje USER directive (security)"""
        return """# Run as non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser"""
    
    def _generate_cmd(self, intent: Dict[str, Any]) -> str:
        """Generuje CMD directive"""
        lang = intent["language"]
        framework = intent.get("framework")
        
        if lang == "python":
            if framework == "flask":
                return 'CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]'
            elif framework == "django":
                return 'CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]'
            elif framework == "fastapi":
                return 'CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]'
            else:
                return 'CMD ["python", "app.py"]'
        
        elif lang == "node":
            return 'CMD ["node", "server.js"]'
        
        elif lang == "go":
            return 'CMD ["./app"]'
        
        elif lang == "java":
            return 'CMD ["java", "-jar", "target/app.jar"]'
        
        return 'CMD ["./start.sh"]'
    
    def _generate_builder_stage(self, intent: Dict[str, Any]) -> str:
        """Generuje builder stage dla multi-stage"""
        lang = intent["language"]
        
        if lang == "go":
            builder = self.BASE_IMAGES["go"]["builder"]
            return f"""FROM {builder} AS builder
WORKDIR /build
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o app ."""
        
        elif lang == "java":
            builder = self.BASE_IMAGES["java"]["builder"]
            return f"""FROM {builder} AS builder
WORKDIR /build
COPY pom.xml .
COPY src ./src
RUN mvn clean package -DskipTests"""
        
        return ""
    
    def _generate_runtime_stage(self, intent: Dict[str, Any]) -> str:
        """Generuje runtime stage dla multi-stage"""
        lang = intent["language"]
        port = intent["port"]
        
        if lang == "go":
            runtime = self.BASE_IMAGES["go"]["runtime"]
            return f"""FROM {runtime}
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /build/app .
EXPOSE {port}
CMD ["./app"]"""
        
        elif lang == "java":
            runtime = self.BASE_IMAGES["java"]["runtime"]
            return f"""FROM {runtime}
WORKDIR /app
COPY --from=builder /build/target/*.jar app.jar
EXPOSE {port}
CMD ["java", "-jar", "app.jar"]"""
        
        return ""
    
    def execute(self, text: str) -> ConversionResult:
        """
        Generuje Dockerfile.
        
        Args:
            text: Opis aplikacji w języku naturalnym
            
        Returns:
            Wynik z wygenerowanym Dockerfile
        """
        try:
            # Parse intent
            intent = self.parse_intent(text)
            
            # Generate Dockerfile
            dockerfile = self.generate_command(intent)
            
            return ConversionResult(
                success=True,
                command="Generated Dockerfile",
                output=dockerfile,
                metadata={
                    "language": intent["language"],
                    "framework": intent.get("framework"),
                    "port": intent["port"],
                    "multi_stage": self.multi_stage
                }
            )
            
        except Exception as e:
            logger.error(f"Błąd generowania: {e}")
            return ConversionResult(
                success=False,
                error=str(e),
                metadata={"input": text}
            )
    
    def save_dockerfile(
        self,
        dockerfile: str,
        directory: str = ".",
        filename: str = "Dockerfile"
    ) -> bool:
        """
        Zapisuje Dockerfile do pliku.
        
        Args:
            dockerfile: Zawartość Dockerfile
            directory: Katalog docelowy
            filename: Nazwa pliku
            
        Returns:
            True jeśli sukces
        """
        try:
            path = Path(directory) / filename
            path.write_text(dockerfile)
            logger.info(f"Zapisano Dockerfile: {path}")
            return True
        except Exception as e:
            logger.error(f"Błąd zapisu: {e}")
            return False
