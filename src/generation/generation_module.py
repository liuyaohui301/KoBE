from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

from src.config import LLMConfig, load_yaml_config
from src.llm_client import LLMClient, LLMRequest


@dataclass
class GenerationResult:
    enhanced_prompt: str
    raw: str


class GenerationModule:
    def __init__(
        self,
        llm_config: LLMConfig,
        system_prompt_path: Path,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
    ) -> None:
        self.llm_config = llm_config
        self.system_prompt_path = system_prompt_path
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = LLMClient(
            api_base=llm_config.api_base,
            api_key=llm_config.api_key,
            max_retries=llm_config.max_retries,
            retry_backoff=llm_config.retry_backoff,
        )

    def build_prompt(self, user_query: str, kg_triplets: str) -> str:
        template = self.system_prompt_path.read_text(encoding="utf-8")
        return template.format(
            kg_triplets=kg_triplets,
            user_query=user_query,
        )

    def build_enhanced_prompt(self, user_query: str, kg_triplets: str) -> GenerationResult:
        prompt = self.build_prompt(user_query, kg_triplets)
        request = LLMRequest(
            model=self.llm_config.model,
            messages=[{"role": "system", "content": prompt}],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        response = self.client.chat(request)
        raw = self.client.extract_text(response).strip()
        return GenerationResult(enhanced_prompt=raw, raw=raw)


def load_generation_module(
    llm_config_path: Path = Path("configs/llm_baseline.yaml"),
    system_prompt_path: Path = Path("configs/prompts/generation_system_prompt.txt"),
    temperature: float = 0.0,
    max_tokens: Optional[int] = None,
) -> GenerationModule:
    llm_dict = load_yaml_config(llm_config_path)
    llm_config = LLMConfig(**llm_dict)
    return GenerationModule(
        llm_config=llm_config,
        system_prompt_path=system_prompt_path,
        temperature=temperature,
        max_tokens=max_tokens,
    )

