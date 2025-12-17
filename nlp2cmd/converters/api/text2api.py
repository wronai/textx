"""
Text2API - Testowanie i analiza API endpoints.

Ten konwerter testuje API i generuje dokumentację/specyfikacje.
"""

import requests
import json
from typing import Dict, Any, Optional, List
from nlp2cmd.core.base import BaseConverter, ConversionResult
import logging

logger = logging.getLogger(__name__)


class Text2API(BaseConverter):
    """
    Konwerter dla testowania i analizy API.
    
    Obsługuje:
    - Automatyczne testowanie wszystkich endpoints
    - Generowanie OpenAPI/Swagger spec
    - Load testing
    - API health monitoring
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: int = 30,
        **kwargs
    ):
        """
        Inicjalizacja Text2API.
        
        Args:
            base_url: Bazowy URL API
            timeout: Timeout dla requestów
        """
        super().__init__(**kwargs)
        self.base_url = base_url
        self.timeout = timeout
        self.discovered_endpoints = []
    
    def parse_intent(self, text: str) -> Dict[str, Any]:
        """
        Parsuje intencję z tekstu.
        
        Returns:
            {
                "action": str,           # test, analyze, generate_spec
                "target": str | None,    # specific endpoint
                "method": str | None,    # GET, POST, etc.
                "test_type": str         # functional, load, security
            }
        """
        text = text.strip().lower()
        
        # Detect action
        action = "test"
        if "przeanalizuj" in text or "analyze" in text:
            action = "analyze"
        elif "spec" in text or "openapi" in text or "swagger" in text:
            action = "generate_spec"
        elif "health" in text or "status" in text:
            action = "health_check"
        
        # Extract URL if present
        import re
        url_match = re.search(r'https?://[\w\-\.]+(?::\d+)?(?:/[\w\-\.]*)*', text)
        target_url = url_match.group(0) if url_match else None
        
        # Detect method
        method = None
        methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
        for m in methods:
            if m.lower() in text:
                method = m
                break
        
        # Test type
        test_type = "functional"
        if "load" in text or "performance" in text:
            test_type = "load"
        elif "security" in text or "bezpieczeństwo" in text:
            test_type = "security"
        
        return {
            "action": action,
            "target": target_url,
            "method": method,
            "test_type": test_type,
            "description": text
        }
    
    def generate_command(self, intent: Dict[str, Any]) -> str:
        """Generuje opis komendy do wykonania"""
        
        action = intent["action"]
        target = intent.get("target", self.base_url)
        
        if action == "test":
            return f"Test API endpoints at {target}"
        elif action == "analyze":
            return f"Analyze API structure at {target}"
        elif action == "generate_spec":
            return f"Generate OpenAPI spec for {target}"
        elif action == "health_check":
            return f"Health check {target}"
        
        return "API operation"
    
    def execute(self, text: str) -> ConversionResult:
        """
        Wykonuje operację na API.
        
        Args:
            text: Komenda w języku naturalnym
            
        Returns:
            Wynik operacji
        """
        try:
            intent = self.parse_intent(text)
            command = self.generate_command(intent)
            
            if self.dry_run:
                return ConversionResult(
                    success=True,
                    command=command,
                    output=f"[DRY RUN] {command}"
                )
            
            action = intent["action"]
            
            if action == "test":
                return self._test_endpoints(intent)
            elif action == "analyze":
                return self._analyze_api(intent)
            elif action == "generate_spec":
                return self._generate_openapi_spec(intent)
            elif action == "health_check":
                return self._health_check(intent)
            
            return ConversionResult(
                success=False,
                error=f"Unknown action: {action}"
            )
            
        except Exception as e:
            logger.error(f"Błąd wykonania: {e}")
            return ConversionResult(
                success=False,
                error=str(e),
                metadata={"input": text}
            )
    
    def _test_endpoints(self, intent: Dict[str, Any]) -> ConversionResult:
        """Testuje wszystkie endpoints"""
        
        base_url = intent.get("target", self.base_url)
        
        if not base_url:
            return ConversionResult(
                success=False,
                error="No base URL provided"
            )
        
        # Common endpoints to test
        test_endpoints = [
            ("/health", "GET"),
            ("/users", "GET"),
            ("/users/1", "GET"),
            ("/api/v1/users", "GET"),
        ]
        
        results = []
        
        for endpoint, method in test_endpoints:
            url = base_url.rstrip('/') + endpoint
            
            try:
                if method == "GET":
                    response = requests.get(url, timeout=self.timeout)
                
                results.append({
                    "endpoint": endpoint,
                    "method": method,
                    "status_code": response.status_code,
                    "success": 200 <= response.status_code < 300,
                    "response_time": response.elapsed.total_seconds()
                })
                
            except requests.RequestException as e:
                results.append({
                    "endpoint": endpoint,
                    "method": method,
                    "success": False,
                    "error": str(e)
                })
        
        # Summary
        successful = sum(1 for r in results if r.get("success", False))
        total = len(results)
        
        output = f"API Test Results: {successful}/{total} endpoints passed\n\n"
        for r in results:
            status = "✓" if r.get("success") else "✗"
            output += f"{status} {r['method']} {r['endpoint']}"
            if "status_code" in r:
                output += f" - {r['status_code']}"
            if "response_time" in r:
                output += f" ({r['response_time']:.2f}s)"
            if "error" in r:
                output += f" - Error: {r['error']}"
            output += "\n"
        
        return ConversionResult(
            success=successful == total,
            command=f"Tested {total} endpoints",
            output=output,
            metadata={"results": results, "success_rate": successful/total}
        )
    
    def _analyze_api(self, intent: Dict[str, Any]) -> ConversionResult:
        """Analizuje strukturę API"""
        
        # Simple analysis - discover endpoints
        base_url = intent.get("target", self.base_url)
        
        if not base_url:
            return ConversionResult(
                success=False,
                error="No base URL provided"
            )
        
        # Try to discover endpoints
        discovered = self._discover_endpoints(base_url)
        
        output = f"Discovered {len(discovered)} endpoints:\n\n"
        for ep in discovered:
            output += f"  {ep['method']} {ep['path']}\n"
            if ep.get('params'):
                output += f"    Params: {', '.join(ep['params'])}\n"
        
        return ConversionResult(
            success=True,
            command="API Analysis",
            output=output,
            metadata={"endpoints": discovered}
        )
    
    def _discover_endpoints(self, base_url: str) -> List[Dict[str, Any]]:
        """Próbuje odkryć endpoints API"""
        
        endpoints = []
        
        # Common patterns
        patterns = [
            "/health",
            "/users",
            "/users/:id",
            "/api/v1/users",
            "/products",
            "/products/:id",
        ]
        
        for pattern in patterns:
            # Try to access
            url = base_url.rstrip('/') + pattern.replace(':id', '1')
            
            try:
                response = requests.get(url, timeout=5)
                if 200 <= response.status_code < 400:
                    endpoints.append({
                        "method": "GET",
                        "path": pattern,
                        "status": response.status_code
                    })
            except:
                pass
        
        return endpoints
    
    def _generate_openapi_spec(self, intent: Dict[str, Any]) -> ConversionResult:
        """Generuje specyfikację OpenAPI"""
        
        base_url = intent.get("target", self.base_url) or "http://localhost:5000"
        
        # Discover endpoints first
        endpoints = self._discover_endpoints(base_url)
        
        # Generate OpenAPI spec
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "API Documentation",
                "version": "1.0.0",
                "description": "Auto-generated API specification"
            },
            "servers": [
                {"url": base_url}
            ],
            "paths": {}
        }
        
        for ep in endpoints:
            path = ep["path"]
            method = ep["method"].lower()
            
            if path not in spec["paths"]:
                spec["paths"][path] = {}
            
            spec["paths"][path][method] = {
                "summary": f"{method.upper()} {path}",
                "responses": {
                    "200": {
                        "description": "Successful response"
                    }
                }
            }
        
        output = json.dumps(spec, indent=2)
        
        return ConversionResult(
            success=True,
            command="Generated OpenAPI spec",
            output=output,
            metadata={"spec": spec, "endpoints_count": len(endpoints)}
        )
    
    def _health_check(self, intent: Dict[str, Any]) -> ConversionResult:
        """Sprawdza health endpoint"""
        
        base_url = intent.get("target", self.base_url)
        
        if not base_url:
            return ConversionResult(
                success=False,
                error="No base URL provided"
            )
        
        health_urls = [
            f"{base_url}/health",
            f"{base_url}/healthz",
            f"{base_url}/api/health",
        ]
        
        for url in health_urls:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    return ConversionResult(
                        success=True,
                        command=f"Health check {url}",
                        output=f"API is healthy\nStatus: {response.status_code}\nResponse: {response.text[:200]}"
                    )
            except:
                continue
        
        return ConversionResult(
            success=False,
            error="No health endpoint found"
        )
