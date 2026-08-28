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
        # Set by generate_stream so callers can tell a complete answer from one
        # the context window cut short. "stop" = model finished, "length" = hit
        # the cap. Mirrors llama.cpp's finish_reason.
        self.last_finish_reason: Optional[str] = None
        self.last_prompt_tokens: int = 0
        self.last_completion_tokens: int = 0
    
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
                f16_kv=True,
                n_batch=128,
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
        """Generate a response from the model (synchronous)."""
        full_text = ""
        for chunk in self.generate_stream(prompt, max_tokens, temperature, stop):
            full_text += chunk
        return full_text

    def count_tokens(self, text: str) -> int:
        """Token count for a raw string, using the model's own tokenizer."""
        if not self.is_loaded:
            self.load_model()
        return len(self._model.tokenize(text.encode("utf-8"), add_bos=True))

    def prompt_tokens(self, user_input: str) -> int:
        """Token count of the full prompt that user_input would produce."""
        return self.count_tokens(self._build_prompt(user_input))

    def answer_budget(self, user_input: str) -> int:
        """
        Tokens left inside n_ctx for the answer once the prompt is in place.

        Callers use this to shrink the data context *before* generating, which
        is the only fix that yields a complete answer rather than a shorter
        truncated one.
        """
        remaining = (
            model_config.n_ctx
            - self.prompt_tokens(user_input)
            - model_config.context_safety_margin
        )
        return max(0, remaining)

    def generate_stream(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stop: Optional[list] = None
    ):
        """Generate a response from the model (streaming)."""
        if not self.is_loaded:
            self.load_model()
        
        full_prompt = self._build_prompt(prompt)
        
        # Clamp the request to what actually fits. Asking for max_tokens=500
        # behind a 608-token prompt in a 768-token window does not produce a
        # 500-token answer -- it produces 160 tokens and a mid-word cut.
        requested = max_tokens or model_config.max_tokens
        prompt_tokens = self.count_tokens(full_prompt)
        budget = max(
            0,
            model_config.n_ctx - prompt_tokens - model_config.context_safety_margin,
        )
        effective_max = min(requested, budget)
        
        self.last_finish_reason = None
        self.last_prompt_tokens = prompt_tokens
        self.last_completion_tokens = 0
        
        if effective_max <= 0:
            # The prompt alone fills the window; nothing can be generated.
            logger.error(
                f"Prompt of {prompt_tokens} tokens leaves no room in n_ctx="
                f"{model_config.n_ctx}; refusing to generate"
            )
            self.last_finish_reason = "length"
            return
        
        if effective_max < requested:
            logger.info(
                f"PROFILING: capping max_tokens {requested} -> {effective_max} "
                f"(prompt {prompt_tokens} tokens, n_ctx {model_config.n_ctx})"
            )
        
        stream = self._model(
            full_prompt,
            max_tokens=effective_max,
            temperature=temperature or model_config.temperature,
            top_p=model_config.top_p,
            top_k=model_config.top_k,
            repeat_penalty=model_config.repeat_penalty,
            stop=stop or ["### Instruction:", "### Input:", "</s>", "[/INST]"],
            stream=True
        )
        
        for chunk in stream:
            choice = chunk["choices"][0]
            text = choice["text"]
            # The final chunk carries finish_reason; earlier ones carry None.
            if choice.get("finish_reason"):
                self.last_finish_reason = choice["finish_reason"]
            if text:
                self.last_completion_tokens += 1
                yield text
    
    def _build_prompt(self, user_input: str) -> str:
        """Skeletal system prompt for maximum speed."""
        system_instruction = "Senior Analyst. Provide concise analysis using data provided."

        return f"""Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{system_instruction}

### Input:
{user_input}

### Response:
"""


# Global instance
model_loader = ModelLoader()