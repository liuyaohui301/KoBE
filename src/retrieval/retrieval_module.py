from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from src.config import LLMConfig, load_yaml_config
from src.llm_client import LLMClient, LLMRequest


@dataclass
class RetrievalResult:
    sparql: str
    rationale: Optional[str]
    raw: str


class RetrievalModule:
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

    def build_prompt(
        self,
        user_query: str,
        kg_schema: str,
        value_dict: str,
        cypher_example: str,
    ) -> str:
        template = self.system_prompt_path.read_text(encoding="utf-8")
        return template.format(
            kg_schema=kg_schema,
            kg_value_dict=value_dict,
            cypher_example=cypher_example,
            user_query=user_query,
        )

    def generate_cypher(
        self,
        user_query: str,
        kg_schema: str,
        value_dict: str,
        cypher_example: str,
    ) -> RetrievalResult:
        prompt = self.build_prompt(user_query, kg_schema, value_dict, cypher_example)
        request = LLMRequest(
            model=self.llm_config.model,
            messages=[{"role": "system", "content": prompt}],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        response = self.client.chat(request)
        raw = self.client.extract_text(response).strip()
        sparql = raw
        rationale = None
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                sparql = parsed.get("cypher", raw).strip()
                rationale = parsed.get("rationale")
        except json.JSONDecodeError:
            pass
        return RetrievalResult(sparql=sparql, rationale=rationale, raw=raw)


def load_retrieval_module(
    llm_config_path: Path = Path("configs/llm_baseline.yaml"),
    system_prompt_path: Path = Path("configs/prompts/retrieval_system_prompt.txt"),
    temperature: float = 0.0,
    max_tokens: Optional[int] = None,
) -> RetrievalModule:
    llm_dict = load_yaml_config(llm_config_path)
    llm_config = LLMConfig(**llm_dict)
    return RetrievalModule(
        llm_config=llm_config,
        system_prompt_path=system_prompt_path,
        temperature=temperature,
        max_tokens=max_tokens,
    )
