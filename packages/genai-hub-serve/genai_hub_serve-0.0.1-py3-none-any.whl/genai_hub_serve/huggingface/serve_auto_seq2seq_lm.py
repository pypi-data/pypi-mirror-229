import os
from abc import ABC, abstractmethod
from typing import Dict, Optional
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from genai_hub_serve import SemantixTorchKserve

class ServeAutoSeq2SeqLM(SemantixTorchKserve):

    def __init__(self, checkpoint: str, name: Optional[str] = None, base_cache_dir: Optional[str] = None,
                 force_local_load: Optional[bool] = False):
        super().__init__(checkpoint, name, base_cache_dir, force_local_load)

    def load(self, checkpoint: str, base_cache_dir: str, force_local_load: bool):
        if not force_local_load:
            tokenizer_path = checkpoint
            model_path = checkpoint
        else :
            base_cache_dir = os.getenv("BASE_CACHE_DIR", "/mnt/models")
            base_cache_dir = os.path.join(base_cache_dir, self._transform_checkpoint_name(checkpoint))
            tokenizer_path = os.path.join(base_cache_dir, "tokenizer")
            model_path = os.path.join(base_cache_dir, "model")
        
        self._tokenizer = AutoTokenizer.from_pretrained(tokenizer_path, local_files_only=force_local_load, device_map={"": self.device})
        self._model = AutoModelForSeq2SeqLM.from_pretrained(model_path, local_files_only=force_local_load, device_map={"": self.device})
        self.ready = True

    def _transform_checkpoint_name(self, checkpoint: str):
        """
        Modifies a checkpoint name in the huggingface format (e.g. 'facebook/bart-large-cnn') to a format that can be used as a model name in the Semantix GenAI model registry (e.g. 'models--facebook--bart-large-cnn'

        Args:
            checkpoint (str): The checkpoint name following the huggingface format
        """
        # Replace all '/' characters with '--'
        transformed = checkpoint.replace('/', '--')
        
        # Prepend 'models--' to the transformed string
        return "models--" + transformed

    
    def predict(self, payload: Dict, headers: Dict[str, str] = None) -> Dict:
        responses = []
        prompts = []
        for instance in payload["instances"]:
            prompts.append(instance["prompt"])
        
        # check the other params necessary on _inference() are in payload and add them to a kwargs object to be passed to the _inference() method
        kwargs = {}
        for arg, value in payload.items():
            if arg == "instances":
                continue
            kwargs[arg] = value

        response = self._inference(prompts, **kwargs)
        responses.append(response)
        return {"responses": responses}
    
    @abstractmethod
    def _inference(self, prompts, **kwargs):
        pass