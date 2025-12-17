"""
Wrapper dla modeli LLM z optymalizacją dla małych modeli (do 3B).
"""

from typing import Optional, Dict, Any, List
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    pipeline,
    GenerationConfig
)
import logging

logger = logging.getLogger(__name__)


class ModelWrapper:
    """
    Wrapper dla modeli Hugging Face z optymalizacją dla małych modeli.
    
    Domyślnie używa modeli do 3B parametrów dla wydajności.
    """
    
    RECOMMENDED_MODELS = {
        "phi-2": "microsoft/phi-2",  # 2.7B
        "tinyllama": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",  # 1.1B
        "bielik": "speakleash/Bielik-7B-v0.1",  # 7B - Polski model
        "phi-1.5": "microsoft/phi-1_5",  # 1.3B
    }
    
    def __init__(
        self,
        model_name: Optional[str] = None,
        device: str = "cpu",
        use_8bit: bool = False,
        max_length: int = 512,
        temperature: float = 0.3,
    ):
        """
        Inicjalizacja wrappera modelu.
        
        Args:
            model_name: Nazwa modelu HF lub alias z RECOMMENDED_MODELS
            device: 'cpu' lub 'cuda'
            use_8bit: Czy używać 8-bit quantization (dla większych modeli)
            max_length: Maksymalna długość generacji
            temperature: Temperatura generacji (0-1)
        """
        # Resolve model name from alias
        if model_name in self.RECOMMENDED_MODELS:
            model_name = self.RECOMMENDED_MODELS[model_name]
        
        self.model_name = model_name or self.RECOMMENDED_MODELS["phi-2"]
        self.device = device
        self.use_8bit = use_8bit
        self.max_length = max_length
        self.temperature = temperature
        
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        
        self._load()
    
    def _load(self):
        """Ładuje model i tokenizer"""
        try:
            logger.info(f"Ładowanie modelu: {self.model_name}")
            
            # Tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            
            # Model configuration
            model_kwargs = {
                "trust_remote_code": True,
                "torch_dtype": torch.float16 if self.device == "cuda" else torch.float32,
            }
            
            if self.use_8bit and self.device == "cuda":
                model_kwargs["load_in_8bit"] = True
            
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                **model_kwargs
            )
            
            if not self.use_8bit:
                self.model = self.model.to(self.device)
            
            self.model.eval()
            
            logger.info(f"Model załadowany pomyślnie na {self.device}")
            
        except Exception as e:
            logger.error(f"Błąd ładowania modelu: {e}")
            raise
    
    def generate(
        self,
        prompt: str,
        max_new_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        do_sample: bool = True,
        top_p: float = 0.9,
        top_k: int = 50,
    ) -> str:
        """
        Generuje tekst na podstawie promptu.
        
        Args:
            prompt: Prompt wejściowy
            max_new_tokens: Maksymalna liczba nowych tokenów
            temperature: Temperatura (override domyślnej)
            do_sample: Czy używać samplingu
            top_p: Nucleus sampling
            top_k: Top-k sampling
            
        Returns:
            Wygenerowany tekst
        """
        if not self.model or not self.tokenizer:
            raise RuntimeError("Model nie został załadowany")
        
        # Tokenize
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=self.max_length
        ).to(self.device)
        
        # Generation config
        gen_config = GenerationConfig(
            max_new_tokens=max_new_tokens or 256,
            temperature=temperature or self.temperature,
            do_sample=do_sample,
            top_p=top_p,
            top_k=top_k,
            pad_token_id=self.tokenizer.eos_token_id,
        )
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                generation_config=gen_config
            )
        
        # Decode
        generated_text = self.tokenizer.decode(
            outputs[0],
            skip_special_tokens=True
        )
        
        # Remove prompt from output
        if generated_text.startswith(prompt):
            generated_text = generated_text[len(prompt):].strip()
        
        return generated_text
    
    def extract_command(
        self,
        natural_language: str,
        system_prompt: str,
        examples: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Ekstraktuje komendę z języka naturalnego.
        
        Args:
            natural_language: Komenda w języku naturalnym
            system_prompt: Prompt systemowy definiujący zadanie
            examples: Lista przykładów (input/output)
            
        Returns:
            Wyekstraktowana komenda
        """
        # Build prompt with examples
        prompt_parts = [system_prompt, ""]
        
        if examples:
            prompt_parts.append("Przykłady:")
            for ex in examples:
                prompt_parts.append(f"Input: {ex['input']}")
                prompt_parts.append(f"Output: {ex['output']}")
                prompt_parts.append("")
        
        prompt_parts.append(f"Input: {natural_language}")
        prompt_parts.append("Output:")
        
        full_prompt = "\n".join(prompt_parts)
        
        # Generate
        output = self.generate(
            prompt=full_prompt,
            max_new_tokens=128,
            temperature=0.2,  # Lower for more deterministic output
        )
        
        # Clean output
        output = output.strip()
        
        # Extract first line (usually the command)
        if '\n' in output:
            output = output.split('\n')[0]
        
        return output
    
    def get_model_info(self) -> Dict[str, Any]:
        """Zwraca informacje o załadowanym modelu"""
        if not self.model:
            return {}
        
        num_params = sum(p.numel() for p in self.model.parameters())
        
        return {
            "model_name": self.model_name,
            "device": self.device,
            "num_parameters": num_params,
            "num_parameters_millions": num_params / 1e6,
            "dtype": str(self.model.dtype),
            "use_8bit": self.use_8bit,
        }
