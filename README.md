## KoBE

This repository **restores an already-instantiated Neo4j database** from a `.dump` file, then runs the KoBE pipeline.

### What you need
- **Neo4j desktop 2.0.5**
- **Python 3.10+**

### Project structure
- `neo4j/`: the database dump file (`battery-kg.dump`)
- `configs/`: Neo4j and LLM configs (examples are provided)
- `configs/prompts/`: retrieval/generation prompts and Cypher examples
- `src/`: core Python modules (ontology, retrieval/generation modules, LLM client)
- `scripts/`: pipeline scripts + Neo4j utilities

### Setup (steps)

#### 1) Create a Python environment

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

#### 2) Configure Neo4j and LLM
- Copy `configs/neo4j.yaml.example` → `configs/neo4j.yaml` and fill in credentials/database name.
- Copy `configs/llm_baseline.yaml.example` → `configs/llm_baseline.yaml` and fill in provider keys.

#### 3) Restore the Neo4j database from dump
Stop Neo4j, then run (from this repo root):

```powershell
neo4j-admin database load battery-kg --from-path .\neo4j --overwrite-destination=true
```

Or use the helper:

```powershell
.\scripts\restore_neo4j_dump.ps1 -Database battery-kg -DumpDir .\neo4j
```

Start Neo4j again after restoring.

#### 4) Run the KoBE pipeline

```powershell
python scripts/run_kg_prompting_pipeline.py `
  --user-query "Estimate SOC for this 30-point (V, I, T) sequence: ..." `
  --neo4j-config configs/neo4j.yaml `
  --llm-config configs/llm_baseline.yaml `
  --value-dict configs/kg_value_dict_min.json `
  --output-dir outputs/kg_prompting
```