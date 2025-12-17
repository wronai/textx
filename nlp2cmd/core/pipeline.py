"""
Pipeline do łączenia wielu konwerterów NLP2CMD.
"""

from typing import List, Tuple, Dict, Any, Optional
from nlp2cmd.core.base import BaseConverter, ConversionResult
import logging

logger = logging.getLogger(__name__)


class Pipeline:
    """
    Pipeline do sekwencyjnego wykonywania wielu konwerterów.
    
    Umożliwia łączenie różnych modułów (text2env, text2bash, text2docker)
    w jeden workflow.
    """
    
    def __init__(self, stop_on_error: bool = True):
        """
        Inicjalizacja pipeline'u.
        
        Args:
            stop_on_error: Czy zatrzymać pipeline przy pierwszym błędzie
        """
        self.modules: Dict[str, BaseConverter] = {}
        self.stop_on_error = stop_on_error
        self.history: List[ConversionResult] = []
    
    def add_module(self, name: str, converter: BaseConverter) -> 'Pipeline':
        """
        Dodaje moduł do pipeline'u.
        
        Args:
            name: Nazwa modułu (alias)
            converter: Instancja konwertera
            
        Returns:
            Self dla chain calling
        """
        self.modules[name] = converter
        logger.info(f"Dodano moduł: {name} ({converter.__class__.__name__})")
        return self
    
    def remove_module(self, name: str) -> 'Pipeline':
        """Usuwa moduł z pipeline'u"""
        if name in self.modules:
            del self.modules[name]
            logger.info(f"Usunięto moduł: {name}")
        return self
    
    def execute(
        self,
        steps: List[Tuple[str, str]]
    ) -> List[ConversionResult]:
        """
        Wykonuje sekwencję kroków.
        
        Args:
            steps: Lista kroków jako (module_name, command)
            
        Returns:
            Lista wyników dla każdego kroku
            
        Example:
            pipeline.execute([
                ("env", "ustaw PORT na 8080"),
                ("docker", "uruchom postgres"),
                ("bash", "sprawdź czy postgres działa")
            ])
        """
        results = []
        
        logger.info(f"Rozpoczęcie pipeline'u z {len(steps)} krokami")
        
        for i, (module_name, command) in enumerate(steps, 1):
            logger.info(f"Krok {i}/{len(steps)}: {module_name} - '{command}'")
            
            if module_name not in self.modules:
                error_msg = f"Nieznany moduł: {module_name}"
                logger.error(error_msg)
                result = ConversionResult(
                    success=False,
                    error=error_msg,
                    metadata={"step": i, "module": module_name}
                )
                results.append(result)
                
                if self.stop_on_error:
                    logger.error("Zatrzymanie pipeline'u z powodu błędu")
                    break
                continue
            
            try:
                converter = self.modules[module_name]
                result = converter.execute(command)
                result.metadata.update({"step": i, "module": module_name})
                results.append(result)
                
                if not result.success and self.stop_on_error:
                    logger.error(f"Błąd w kroku {i}, zatrzymanie pipeline'u")
                    break
                    
            except Exception as e:
                error_msg = f"Wyjątek w module {module_name}: {str(e)}"
                logger.error(error_msg)
                result = ConversionResult(
                    success=False,
                    error=error_msg,
                    metadata={"step": i, "module": module_name}
                )
                results.append(result)
                
                if self.stop_on_error:
                    break
        
        self.history.extend(results)
        logger.info(f"Pipeline zakończony. Sukces: {sum(r.success for r in results)}/{len(results)}")
        
        return results
    
    def execute_parallel(
        self,
        tasks: List[Tuple[str, str]]
    ) -> List[ConversionResult]:
        """
        Wykonuje zadania równolegle (wszystkie niezależnie).
        
        Args:
            tasks: Lista zadań jako (module_name, command)
            
        Returns:
            Lista wyników
        """
        results = []
        
        logger.info(f"Rozpoczęcie równoległego wykonania {len(tasks)} zadań")
        
        for module_name, command in tasks:
            if module_name not in self.modules:
                results.append(ConversionResult(
                    success=False,
                    error=f"Nieznany moduł: {module_name}",
                    metadata={"module": module_name}
                ))
                continue
            
            try:
                converter = self.modules[module_name]
                result = converter.execute(command)
                result.metadata["module"] = module_name
                results.append(result)
            except Exception as e:
                results.append(ConversionResult(
                    success=False,
                    error=str(e),
                    metadata={"module": module_name}
                ))
        
        self.history.extend(results)
        return results
    
    def get_history(self) -> List[ConversionResult]:
        """Zwraca historię wykonań"""
        return self.history
    
    def clear_history(self):
        """Czyści historię wykonań"""
        self.history = []
        logger.info("Historia pipeline'u wyczyszczona")
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Zwraca podsumowanie pipeline'u.
        
        Returns:
            Dict z statystykami
        """
        total = len(self.history)
        success = sum(r.success for r in self.history)
        failed = total - success
        
        modules_used = {}
        for result in self.history:
            module = result.metadata.get("module", "unknown")
            if module not in modules_used:
                modules_used[module] = {"total": 0, "success": 0, "failed": 0}
            
            modules_used[module]["total"] += 1
            if result.success:
                modules_used[module]["success"] += 1
            else:
                modules_used[module]["failed"] += 1
        
        return {
            "total_executions": total,
            "successful": success,
            "failed": failed,
            "success_rate": success / total if total > 0 else 0,
            "modules": modules_used,
            "available_modules": list(self.modules.keys())
        }
    
    def __repr__(self) -> str:
        return f"Pipeline(modules={list(self.modules.keys())}, history={len(self.history)})"
