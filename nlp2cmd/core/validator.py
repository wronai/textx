"""
Validation System for Generated Artifacts

Waliduje wygenerowane artefakty pod kątem:
- Poprawności składniowej
- Best practices
- Security issues
- Compatibility
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import re
import yaml
import logging

logger = logging.getLogger(__name__)


@dataclass
class ValidationIssue:
    """Reprezentacja problemu walidacji"""
    level: str  # error, warning, info
    message: str
    line: Optional[int] = None
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Wynik walidacji"""
    success: bool
    errors: List[ValidationIssue]
    warnings: List[ValidationIssue]
    info: List[ValidationIssue]
    score: float  # 0.0 - 1.0
    
    def has_errors(self) -> bool:
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0
    
    def to_dict(self) -> Dict:
        return {
            "success": self.success,
            "score": self.score,
            "errors": [{"message": e.message, "line": e.line} for e in self.errors],
            "warnings": [{"message": w.message, "line": w.line} for w in self.warnings],
            "info": [{"message": i.message, "line": i.line} for i in self.info]
        }


class BaseValidator:
    """Base class dla wszystkich validatorów"""
    
    def validate(self, content: str) -> ValidationResult:
        """Waliduje zawartość"""
        raise NotImplementedError
    
    def _create_result(
        self,
        errors: List[ValidationIssue] = None,
        warnings: List[ValidationIssue] = None,
        info: List[ValidationIssue] = None
    ) -> ValidationResult:
        """Helper do tworzenia wyniku"""
        
        errors = errors or []
        warnings = warnings or []
        info = info or []
        
        # Calculate score
        error_penalty = len(errors) * 0.2
        warning_penalty = len(warnings) * 0.05
        score = max(0.0, 1.0 - error_penalty - warning_penalty)
        
        return ValidationResult(
            success=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            info=info,
            score=score
        )


class PythonValidator(BaseValidator):
    """Validator dla kodu Python"""
    
    def validate(self, content: str) -> ValidationResult:
        """Waliduje kod Python"""
        
        errors = []
        warnings = []
        info = []
        
        # 1. Syntax check
        try:
            import ast
            ast.parse(content)
            info.append(ValidationIssue("info", "Python syntax is valid"))
        except SyntaxError as e:
            errors.append(ValidationIssue(
                "error",
                f"Syntax error: {e.msg}",
                line=e.lineno,
                suggestion="Check Python syntax"
            ))
        
        # 2. Check imports
        if "import *" in content:
            warnings.append(ValidationIssue(
                "warning",
                "Wildcard imports (import *) are discouraged",
                suggestion="Use explicit imports"
            ))
        
        # 3. Check for hardcoded credentials
        patterns = [
            (r'password\s*=\s*["\'][\w]+["\']', "Hardcoded password detected"),
            (r'api_key\s*=\s*["\'][\w]+["\']', "Hardcoded API key detected"),
            (r'secret\s*=\s*["\'][\w]+["\']', "Hardcoded secret detected"),
        ]
        
        for pattern, message in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                errors.append(ValidationIssue(
                    "error",
                    message,
                    suggestion="Use environment variables"
                ))
        
        # 4. Check for print statements (should use logging)
        if re.search(r'\bprint\(', content):
            warnings.append(ValidationIssue(
                "warning",
                "Using print() instead of logging",
                suggestion="Use logging module for production code"
            ))
        
        # 5. Check docstrings for functions
        if 'def ' in content:
            functions = re.findall(r'def\s+(\w+)\s*\(', content)
            if functions:
                info.append(ValidationIssue(
                    "info",
                    f"Found {len(functions)} functions"
                ))
        
        return self._create_result(errors, warnings, info)


class DockerfileValidator(BaseValidator):
    """Validator dla Dockerfile"""
    
    def validate(self, content: str) -> ValidationResult:
        """Waliduje Dockerfile"""
        
        errors = []
        warnings = []
        info = []
        
        lines = content.split('\n')
        
        # 1. Check FROM statement
        from_lines = [l for l in lines if l.strip().startswith('FROM')]
        if not from_lines:
            errors.append(ValidationIssue(
                "error",
                "Missing FROM statement",
                suggestion="Every Dockerfile must start with FROM"
            ))
        elif from_lines[0].strip().endswith(':latest'):
            warnings.append(ValidationIssue(
                "warning",
                "Using :latest tag",
                suggestion="Pin specific version for reproducibility"
            ))
        
        # 2. Check for USER statement (security)
        if not any(l.strip().startswith('USER') for l in lines):
            warnings.append(ValidationIssue(
                "warning",
                "No USER statement found",
                suggestion="Run as non-root user for security"
            ))
        
        # 3. Check for HEALTHCHECK
        if not any(l.strip().startswith('HEALTHCHECK') for l in lines):
            info.append(ValidationIssue(
                "info",
                "No HEALTHCHECK defined",
                suggestion="Add HEALTHCHECK for better monitoring"
            ))
        
        # 4. Check for proper WORKDIR
        if not any(l.strip().startswith('WORKDIR') for l in lines):
            warnings.append(ValidationIssue(
                "warning",
                "No WORKDIR defined",
                suggestion="Define WORKDIR for clarity"
            ))
        
        # 5. Check layer optimization
        run_count = len([l for l in lines if l.strip().startswith('RUN')])
        if run_count > 5:
            warnings.append(ValidationIssue(
                "warning",
                f"{run_count} RUN statements found",
                suggestion="Consider combining RUN statements to reduce layers"
            ))
        
        # 6. Check for apt-get without cleanup
        for i, line in enumerate(lines, 1):
            if 'apt-get install' in line and 'rm -rf /var/lib/apt/lists' not in content:
                warnings.append(ValidationIssue(
                    "warning",
                    "apt-get without cleanup",
                    line=i,
                    suggestion="Clean up apt cache to reduce image size"
                ))
        
        return self._create_result(errors, warnings, info)


class KubernetesValidator(BaseValidator):
    """Validator dla manifestów Kubernetes"""
    
    def validate(self, content: str) -> ValidationResult:
        """Waliduje manifest K8s"""
        
        errors = []
        warnings = []
        info = []
        
        try:
            # Parse YAML
            manifest = yaml.safe_load(content)
            
            # 1. Check required fields
            if 'apiVersion' not in manifest:
                errors.append(ValidationIssue(
                    "error",
                    "Missing apiVersion",
                    suggestion="Add apiVersion field"
                ))
            
            if 'kind' not in manifest:
                errors.append(ValidationIssue(
                    "error",
                    "Missing kind",
                    suggestion="Add kind field"
                ))
            
            if 'metadata' not in manifest:
                errors.append(ValidationIssue(
                    "error",
                    "Missing metadata",
                    suggestion="Add metadata section"
                ))
            
            # 2. Check specific kinds
            kind = manifest.get('kind', '')
            
            if kind == 'Deployment':
                self._validate_deployment(manifest, errors, warnings, info)
            elif kind == 'Service':
                self._validate_service(manifest, errors, warnings, info)
            
            # 3. Check labels
            if 'metadata' in manifest and 'labels' not in manifest['metadata']:
                warnings.append(ValidationIssue(
                    "warning",
                    "No labels defined",
                    suggestion="Add labels for better organization"
                ))
            
        except yaml.YAMLError as e:
            errors.append(ValidationIssue(
                "error",
                f"Invalid YAML: {str(e)}",
                suggestion="Fix YAML syntax"
            ))
        
        return self._create_result(errors, warnings, info)
    
    def _validate_deployment(
        self,
        manifest: Dict,
        errors: List,
        warnings: List,
        info: List
    ):
        """Waliduje Deployment"""
        
        spec = manifest.get('spec', {})
        
        # Check replicas
        replicas = spec.get('replicas', 1)
        if replicas < 2:
            warnings.append(ValidationIssue(
                "warning",
                f"Only {replicas} replica(s)",
                suggestion="Use 2+ replicas for high availability"
            ))
        
        # Check resource limits
        template = spec.get('template', {})
        pod_spec = template.get('spec', {})
        containers = pod_spec.get('containers', [])
        
        for i, container in enumerate(containers):
            if 'resources' not in container:
                warnings.append(ValidationIssue(
                    "warning",
                    f"No resource limits for container {i}",
                    suggestion="Define resource requests and limits"
                ))
            
            # Check health probes
            if 'livenessProbe' not in container:
                warnings.append(ValidationIssue(
                    "warning",
                    f"No livenessProbe for container {i}",
                    suggestion="Add liveness probe for better reliability"
                ))
            
            if 'readinessProbe' not in container:
                warnings.append(ValidationIssue(
                    "warning",
                    f"No readinessProbe for container {i}",
                    suggestion="Add readiness probe for better traffic management"
                ))
    
    def _validate_service(
        self,
        manifest: Dict,
        errors: List,
        warnings: List,
        info: List
    ):
        """Waliduje Service"""
        
        spec = manifest.get('spec', {})
        
        # Check selector
        if 'selector' not in spec:
            errors.append(ValidationIssue(
                "error",
                "Missing selector",
                suggestion="Add selector to match pods"
            ))
        
        # Check ports
        if 'ports' not in spec:
            errors.append(ValidationIssue(
                "error",
                "Missing ports",
                suggestion="Define at least one port"
            ))


class SecurityValidator(BaseValidator):
    """Validator dla security issues"""
    
    def validate(self, content: str) -> ValidationResult:
        """Waliduje security aspects"""
        
        errors = []
        warnings = []
        info = []
        
        # Check for common vulnerabilities
        security_patterns = [
            (r'eval\(', "Use of eval() is dangerous", "error"),
            (r'exec\(', "Use of exec() is dangerous", "error"),
            (r'shell=True', "shell=True in subprocess is risky", "warning"),
            (r'verify=False', "SSL verification disabled", "error"),
            (r'DEBUG\s*=\s*True', "Debug mode enabled", "warning"),
            (r'http://', "Using HTTP instead of HTTPS", "warning"),
        ]
        
        for pattern, message, level in security_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                
                issue = ValidationIssue(
                    level,
                    message,
                    line=line_num,
                    suggestion="Review security implications"
                )
                
                if level == "error":
                    errors.append(issue)
                else:
                    warnings.append(issue)
        
        return self._create_result(errors, warnings, info)


class ArtifactValidator:
    """
    Main validator that coordinates all specific validators.
    """
    
    def __init__(self):
        self.validators = {
            "python": PythonValidator(),
            "dockerfile": DockerfileValidator(),
            "kubernetes": KubernetesValidator(),
            "security": SecurityValidator(),
        }
    
    def validate(
        self,
        content: str,
        artifact_type: str,
        check_security: bool = True
    ) -> ValidationResult:
        """
        Waliduje artefakt.
        
        Args:
            content: Zawartość do walidacji
            artifact_type: Typ artefaktu
            check_security: Czy sprawdzać security
            
        Returns:
            Wynik walidacji
        """
        logger.info(f"Validating {artifact_type} artifact")
        
        validator = self.validators.get(artifact_type)
        
        if not validator:
            # Unknown type - return success
            return ValidationResult(
                success=True,
                errors=[],
                warnings=[],
                info=[ValidationIssue("info", f"No validator for {artifact_type}")],
                score=1.0
            )
        
        # Primary validation
        result = validator.validate(content)
        
        # Security validation
        if check_security and artifact_type != "security":
            security_result = self.validators["security"].validate(content)
            
            # Merge results
            result.errors.extend(security_result.errors)
            result.warnings.extend(security_result.warnings)
            result.info.extend(security_result.info)
            
            # Recalculate
            result.success = len(result.errors) == 0
            error_penalty = len(result.errors) * 0.2
            warning_penalty = len(result.warnings) * 0.05
            result.score = max(0.0, 1.0 - error_penalty - warning_penalty)
        
        logger.info(f"Validation complete: score={result.score:.2f}")
        
        return result
    
    def validate_multiple(
        self,
        artifacts: Dict[str, str]
    ) -> Dict[str, ValidationResult]:
        """
        Waliduje wiele artefaktów.
        
        Args:
            artifacts: Dict {artifact_type: content}
            
        Returns:
            Dict {artifact_type: ValidationResult}
        """
        results = {}
        
        for artifact_type, content in artifacts.items():
            results[artifact_type] = self.validate(content, artifact_type)
        
        return results
    
    def get_summary(
        self,
        results: Dict[str, ValidationResult]
    ) -> Dict[str, Any]:
        """Podsumowanie walidacji"""
        
        total_errors = sum(len(r.errors) for r in results.values())
        total_warnings = sum(len(r.warnings) for r in results.values())
        avg_score = sum(r.score for r in results.values()) / len(results) if results else 0
        
        return {
            "total_artifacts": len(results),
            "passed": sum(1 for r in results.values() if r.success),
            "failed": sum(1 for r in results.values() if not r.success),
            "total_errors": total_errors,
            "total_warnings": total_warnings,
            "average_score": avg_score,
            "grade": self._calculate_grade(avg_score)
        }
    
    def _calculate_grade(self, score: float) -> str:
        """Oblicza ocenę literową"""
        if score >= 0.95:
            return "A+"
        elif score >= 0.90:
            return "A"
        elif score >= 0.85:
            return "B+"
        elif score >= 0.80:
            return "B"
        elif score >= 0.75:
            return "C+"
        elif score >= 0.70:
            return "C"
        else:
            return "D"
