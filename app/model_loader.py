"""
Model Loader
============
Loads and manages the QLoRA fine-tuned GGUF model.
"""

import logging
import os
from pathlib import Path
from typing import Optional

from huggingface_hub import hf_hub_download

from config import model_config

logger = logging.getLogger(__name__)


class ModelLoader:
    """Singleton class for loading and managing the LLM model."""
    
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.model_path: Optional[str] = None
        self.is_loaded: bool = False
    
    def download_model(self) -> str:
        """Download model from HuggingFace Hub if not present locally."""
        local_dir = Path(model_config.local_model_dir)
        local_dir.mkdir(parents=True, exist_ok=True)
        local_path = Path(model_config.local_model_path)
        
        if local_path.exists():
            logger.info(f"Model found locally: {local_path}")
            return str(local_path)
        
        logger.info(f"Downloading model from {model_config.hf_repo_id}...")
        
        try:
            downloaded_path = hf_hub_download(
                repo_id=model_config.hf_repo_id,
                filename=model_config.hf_filename,
                local_dir=str(local_dir),
                local_dir_use_symlinks=False,
            )
            
            # Rename if necessary
            if downloaded_path != str(local_path):
                os.rename(downloaded_path, str(local_path))
            
            logger.info(f"Model downloaded: {local_path}")
            return str(local_path)
            
        except Exception as e:
            logger.error(f"Failed to download model: {e}")
            raise
    
    def load_model(self):
        """Load the model into memory."""
        if self._model is not None and self.is_loaded:
            logger.info("Model already loaded")
            return self._model
        
        # Import here to avoid import errors if llama-cpp-python not installed
        try:
            from llama_cpp import Llama
        except ImportError:
            raise ImportError(
                "llama-cpp-python is required. "
                "Install with: pip install llama-cpp-python"
            )
        
        self.model_path = self.download_model()
        
        logger.info("Loading model into memory...")
        
        try:
            self._model = Llama(
                model_path=self.model_path,
                n_ctx=model_config.n_ctx,
                n_threads=model_config.n_threads,
                n_gpu_layers=model_config.n_gpu_layers,
                verbose=False,
            )
            self.is_loaded = True
            logger.info("Model loaded successfully")
            return self._model
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def unload_model(self):
        """Unload the model from memory."""
        if self._model is not None:
            del self._model
            self._model = None
            self.is_loaded = False
            logger.info("Model unloaded")
    
    def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stop: Optional[list] = None
    ) -> str:
        """Generate a response from the model."""
        if not self.is_loaded:
            self.load_model()
        
        full_prompt = self._build_prompt(prompt)
        
        response = self._model(
            full_prompt,
            max_tokens=max_tokens or model_config.max_tokens,
            temperature=temperature or model_config.temperature,
            top_p=model_config.top_p,
            top_k=model_config.top_k,
            repeat_penalty=model_config.repeat_penalty,
            stop=stop or ["### Instruction:", "### Input:", "</s>", "[/INST]"],
        )
        
        return response["choices"][0]["text"].strip()
    
    def _build_prompt(self, user_input: str) -> str:
        """Build the full prompt with system instruction."""
        system_instruction = """You are a senior financial analyst providing comprehensive macroeconomic analysis for 80+ countries worldwide. Your analysis must:

1. Present data from multiple authoritative sources (FRED, World Bank, OECD)
2. Calculate and present consensus values from triangulated data
3. Assess confidence levels based on source agreement
4. Provide risk or quality assessments appropriate to each indicator
5. Contextualize findings within regional and income-level frameworks

You analyze 12 key macroeconomic indicators: GDP Growth, Inflation, Unemployment, Interest Rate, GDP Per Capita, Current Account, Government Debt, FDI Inflows, Exchange Rate Change, Industrial Production, Consumer Confidence, and Trade Balance."""

        return f"""Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{system_instruction}

### Input:
{user_input}

### Response:
"""


# Global instance
model_loader = ModelLoader()