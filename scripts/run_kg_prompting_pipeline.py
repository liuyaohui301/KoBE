"""
End-to-end prompting pipeline: user_query -> Cypher -> Neo4j -> enhanced prompt.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from neo4j import GraphDatabase

from src.config import LLMConfig, load_yaml_config
from src.generation import GenerationModule
from src.retrieval import RetrievalModule


def load_neo4j_config(path: Path) -> Dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def format_value_dict(value_dict: Dict[str, Any], max_keys: int) -> str:
    focus_keys = [
        "component.chemistry",
        "component.ratedCapacity_Ah",
        "context.temperature_C",
        "context.lifeStage",
        "context.operatingSubphase",
        "state.SOC.stateType",
        "state.SOH.stateType",
        "measurement.summary.voltage_v.start",
        "measurement.summary.voltage_v.end",
        "measurement.summary.voltage_v.mean",
        "measurement.summary.current_a.start",
        "measurement.summary.current_a.end",
        "measurement.summary.current_a.mean",
        "measurement.summary.temperature_c.start",
        "measurement.summary.temperature_c.end",
        "measurement.summary.temperature_c.mean",
    ]
    if max_keys > 0:
        focus_keys = focus_keys[:max_keys]

    def format_entry(entry: Dict[str, Any]) -> str:
        parts = [f"type={entry.get('type')}"]
        examples = entry.get("examples") or []
        if examples:
            parts.append(f"examples={examples}")
        if entry.get("min") is not None or entry.get("max") is not None:
            parts.append(f"range=[{entry.get('min')}, {entry.get('max')}]")
        return ", ".join(parts)

    lines: List[str] = ["Focused KG value dictionary:"]
    for key in focus_keys:
        entry = value_dict.get(key)
        if not entry:
            continue
        lines.append(f"- {key}: {format_entry(entry)}")
    return "\n".join(lines)


def execute_cypher_neo4j(driver, cypher: str) -> List[Dict[str, Any]]:
    with driver.session() as session:
        result = session.run(cypher)
        return [record.data() for record in result]


def format_triplets(rows: List[Dict[str, Any]], max_rows: int) -> str:
    lines = []
    for row in rows[:max_rows]:
        parts = [f"{key}={value}" for key, value in row.items()]
        lines.append("; ".join(parts))
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run KG prompting pipeline.")
    parser.add_argument("--user-query", default=None)
    parser.add_argument("--user-query-file", default=None)
    parser.add_argument("--neo4j-config", default="configs/neo4j.yaml")
    parser.add_argument("--llm-config", default="configs/llm_baseline.yaml")
    parser.add_argument("--value-dict", default="configs/kg_value_dict_min.json")
    parser.add_argument("--schema-file", default="configs/prompts/kg_schema.txt")
    parser.add_argument("--cypher-example-file", default="configs/prompts/cypher_example.cypher")
    parser.add_argument("--output-dir", default="outputs/kg_prompting")
    parser.add_argument("--value-dict-max-keys", type=int, default=80)
    parser.add_argument("--triplets-max-rows", type=int, default=50)
    args = parser.parse_args()

    if not args.user_query and not args.user_query_file:
        raise RuntimeError("Provide --user-query or --user-query-file.")
    user_query = args.user_query
    if args.user_query_file:
        user_query = Path(args.user_query_file).read_text(encoding="utf-8").strip()

    schema_text = Path(args.schema_file).read_text(encoding="utf-8").strip()

    cypher_example = Path(args.cypher_example_file).read_text(encoding="utf-8").strip()

    value_dict_path = Path(args.value_dict)
    value_dict_raw = json.loads(value_dict_path.read_text(encoding="utf-8"))
    value_dict_text = format_value_dict(value_dict_raw, args.value_dict_max_keys)

    llm_cfg = LLMConfig(**load_yaml_config(Path(args.llm_config)))
    retrieval = RetrievalModule(llm_cfg, Path("configs/prompts/retrieval_system_prompt.txt"))
    generation = GenerationModule(llm_cfg, Path("configs/prompts/generation_system_prompt.txt"))

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    retrieval_prompt = retrieval.build_prompt(
        user_query=user_query,
        kg_schema=schema_text,
        value_dict=value_dict_text,
        cypher_example=cypher_example,
    )
    (output_dir / "retrieval_prompt.txt").write_text(retrieval_prompt, encoding="utf-8")

    retrieval_result = retrieval.generate_cypher(
        user_query=user_query,
        kg_schema=schema_text,
        value_dict=value_dict_text,
        cypher_example=cypher_example,
    )
    (output_dir / "retrieval_response.txt").write_text(retrieval_result.raw, encoding="utf-8")
    (output_dir / "cypher.txt").write_text(retrieval_result.sparql, encoding="utf-8")

    neo4j_cfg = load_neo4j_config(Path(args.neo4j_config))
    driver = GraphDatabase.driver(
        neo4j_cfg["uri"], auth=(neo4j_cfg["user"], neo4j_cfg["password"])
    )
    try:
        rows = execute_cypher_neo4j(driver, retrieval_result.sparql)
    finally:
        driver.close()

    (output_dir / "kg_results.json").write_text(
        json.dumps(rows, ensure_ascii=True, indent=2), encoding="utf-8"
    )
    triplets_text = format_triplets(rows, args.triplets_max_rows)
    (output_dir / "kg_triplets.txt").write_text(triplets_text, encoding="utf-8")

    enhanced = generation.build_enhanced_prompt(user_query=user_query, kg_triplets=triplets_text)
    (output_dir / "enhanced_prompt.txt").write_text(enhanced.enhanced_prompt, encoding="utf-8")

    print(f"Wrote outputs to {output_dir}")


if __name__ == "__main__":
    main()
