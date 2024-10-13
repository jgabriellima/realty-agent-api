import os
from functools import lru_cache
from typing import Optional

import yaml
from pydantic_settings import BaseSettings

try:
    from langfuse import Langfuse

    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False


class PromptManagerSettings(BaseSettings):
    LANGFUSE_PUBLIC_KEY: Optional[str] = None
    LANGFUSE_SECRET_KEY: Optional[str] = None
    LANGFUSE_HOST: Optional[str] = "https://cloud.langfuse.com"
    USE_LANGFUSE: bool = False
    PROMPTS_DIR: str = "api_template/prompts/"

    class Config:
        env_file = ".env"


class PromptManager:
    def __init__(self):
        self.settings = PromptManagerSettings()
        self.langfuse_client = None
        if self.settings.USE_LANGFUSE:
            if not LANGFUSE_AVAILABLE:
                raise ImportError(
                    "Langfuse is not installed. Please install it with 'pip install langfuse'"
                )
            if not self.settings.LANGFUSE_PUBLIC_KEY or not self.settings.LANGFUSE_SECRET_KEY:
                raise ValueError("Langfuse keys are not set in the environment variables")
            self.langfuse_client = Langfuse(
                public_key=self.settings.LANGFUSE_PUBLIC_KEY,
                secret_key=self.settings.LANGFUSE_SECRET_KEY,
                host=self.settings.LANGFUSE_HOST,
            )

    @lru_cache(maxsize=100)
    def get_prompt(self, name: str) -> str:
        if self.settings.USE_LANGFUSE:
            return self._get_prompt_from_langfuse(name)
        else:
            return self._get_prompt_from_file(name)

    def _get_prompt_from_langfuse(self, name: str) -> str:
        try:
            prompt = self.langfuse_client.get_prompt(name)
            return prompt.text
        except Exception as e:
            raise ValueError(f"Failed to retrieve prompt '{name}' from Langfuse: {str(e)}")

    def _get_prompt_from_file(self, name: str) -> str:
        # directory path relative to the current file
        path_relative = os.path.dirname(os.path.realpath(__file__))
        prompt_path = os.path.join(path_relative, f"{name}/prompt.yaml")
        if not os.path.exists(prompt_path):
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

        with open(prompt_path, "r") as file:
            prompt_data = yaml.safe_load(file)

        if not isinstance(prompt_data, dict) or "text" not in prompt_data:
            raise ValueError(f"Invalid prompt file format for '{name}'")

        return prompt_data["text"]

    def compile_prompt(self, name: str, **kwargs) -> str:
        prompt_template = self.get_prompt(name)
        try:
            return prompt_template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing variable in prompt '{name}': {str(e)}")


# Singleton instance
prompt_manager = PromptManager()
