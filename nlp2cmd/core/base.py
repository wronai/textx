"""
Bazowa klasa dla wszystkich konwerterów NLP2CMD.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConversionResult(BaseModel):
    """Wynik konwersji"""
    success: bool
    command: Optional[str] = None
    output: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BaseConverter(ABC):
    """
    Bazowa klasa dla wszystkich konwerterów.
    
    Każdy konwerter musi implementować:
    - parse_intent() - analiza intencji użytkownika
    - generate_command() - generowanie komendy
    - execute() - wykonanie komendy
    """
    
    def __init__(
        self,
        model_name: Optional[str] = None,
        device: str = "cpu",
        safe_mode: bool = True,
        dry_run: bool = False,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Inicjalizacja konwertera.
        
        Args:
            model_name: Nazwa modelu HuggingFace (opcjonalne)
            device: Urządzenie do obliczeń ('cpu' lub 'cuda')
            safe_mode: Czy włączyć walidację bezpieczeństwa
            dry_run: Czy tylko symulować wykonanie
            config: Dodatkowa konfiguracja
        """
        self.model_name = model_name
        self.device = device
        self.safe_mode = safe_mode
        self.dry_run = dry_run
        self.config = config or {}
        self.model = None
        
        # Lazy loading modelu
        if model_name:
            self._load_model()
    
    def _load_model(self):
        """Ładuje model LLM (lazy loading)"""
        if self.model is None:
            from nlp2cmd.core.model import ModelWrapper
            self.model = ModelWrapper(
                model_name=self.model_name,
                device=self.device
            )
            logger.info(f"Załadowano model: {self.model_name}")
    
    @abstractmethod
    def parse_intent(self, text: str) -> Dict[str, Any]:
        """
        Parsuje intencję użytkownika z tekstu.
        
        Args:
            text: Komenda w języku naturalnym
            
        Returns:
            Dict z rozparsowaną intencją
        """
        pass
    
    @abstractmethod
    def generate_command(self, intent: Dict[str, Any]) -> str:
        """
        Generuje komendę na podstawie intencji.
        
        Args:
            intent: Rozparsowana intencja
            
        Returns:
            Wygenerowana komenda
        """
        pass
    
    @abstractmethod
    def execute(self, text: str) -> ConversionResult:
        """
        Wykonuje pełny proces konwersji i wykonania.
        
        Args:
            text: Komenda w języku naturalnym
            
        Returns:
            Wynik konwersji
        """
        pass
    
    def validate_command(self, command: str) -> bool:
        """
        Waliduje bezpieczeństwo komendy.
        
        Args:
            command: Komenda do walidacji
            
        Returns:
            True jeśli komenda jest bezpieczna
        """
        if not self.safe_mode:
            return True
        
        # Podstawowa walidacja - można rozszerzyć
        dangerous_patterns = [
            "rm -rf /",
            ":(){ :|:& };:",  # fork bomb
            "dd if=/dev/zero",
            "> /dev/sda",
        ]
        
        for pattern in dangerous_patterns:
            if pattern in command.lower():
                logger.warning(f"Wykryto niebezpieczny pattern: {pattern}")
                return False
        
        return True
    
    def log_execution(self, text: str, result: ConversionResult):
        """Loguje wykonanie komendy"""
        logger.info(f"Input: {text}")
        logger.info(f"Command: {result.command}")
        logger.info(f"Success: {result.success}")
        if result.error:
            logger.error(f"Error: {result.error}")
