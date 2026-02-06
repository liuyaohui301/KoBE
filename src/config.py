from dataclasses import dataclass
from dataclasses import field
from pathlib import Path


@dataclass
class Neo4jConfig:
    uri: str
    user: str
    password: str
    database: str = "neo4j"
    max_connection_lifetime: int = 3600
    max_connection_pool_size: int = 50
    connection_acquisition_timeout: int = 30
    read_tx_timeout: int = 60
    default_limit: int = 100


@dataclass
class LLMConfig:
    provider: str
    api_base: str
    api_key: str
    model: str
    max_retries: int = 3
    retry_backoff: float = 2.0


@dataclass
class PathsConfig:
    data_root: Path = Path("data")
    samples_dir: Path = Path("data/samples")


@dataclass
class AppConfig:
    neo4j: Neo4jConfig
    llm: LLMConfig
    paths: PathsConfig = field(default_factory=PathsConfig)


def load_yaml_config(path: Path) -> dict:
    import yaml

    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_app_config(
    neo4j_path: Path = Path("configs/neo4j.yaml"),
    llm_path: Path = Path("configs/llm_baseline.yaml"),
) -> AppConfig:
    neo4j_dict = load_yaml_config(neo4j_path)
    llm_dict = load_yaml_config(llm_path)
    return AppConfig(neo4j=Neo4jConfig(**neo4j_dict), llm=LLMConfig(**llm_dict))
