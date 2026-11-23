# Co-Scientist for Antigravity CLI (`agy`)

A workspace-scoped multi-agent scientific research skill inspired by [Google DeepMind's AI Co-Scientist](https://deepmind.google/blog/co-scientist-a-multi-agent-ai-partner-to-accelerate-research/), built with **Antigravity Skills**, **Subagents**, and **zero-dependency Python 3.12 scripts**.

## Architecture

```text
.agents/skills/co-scientist/
├── SKILL.md                        # Supervisor workflow & round-by-round state machine
├── references/
│   └── subagent_prompts.md         # Prompts & JSON contracts for the 5 subagent roles
└── scripts/
    ├── co_db.py                    # SQLite state store (hypotheses, lineage, reviews, matches)
    ├── literature.py               # Zero-key search & ID verification (arXiv, PubMed, OpenAlex, S2)
    ├── proximity.py                # TF-IDF similarity graph, clustering, dedup & crossover pairs
    ├── tournament.py               # Swiss + cluster-aware matchmaking & exact Elo updates
    └── report.py                   # Renders final Markdown report + Mermaid lineage diagram
```

### Multi-Agent Roles
1. **Supervisor (`SKILL.md`)** — Coordinates rounds, dispatches parallel subagents, and commits state via Python scripts.
2. **`cs-generator`** — Explores literature (`search_web` + `literature.py`) using literature synthesis, simulated scientific debate, and cross-domain transfer.
3. **`cs-reflector`** — Independent peer reviewer that verifies cited IDs/DOIs/PMIDs, checks assumptions, and prunes fatally flawed hypotheses.
4. **Proximity (`proximity.py`)** — Computes TF-IDF cosine similarity across hypotheses, merges near-duplicates, assigns clusters, and proposes cross-cluster crossover pairs.
5. **`cs-judge` + `tournament.py`** — Runs 3-round head-to-head scientific debates and updates **Elo ratings**.
6. **`cs-evolver`** — Refines top hypotheses against peer critiques, recombines top cross-cluster parents, or explores meta-review gaps.
7. **`cs-meta-reviewer`** — Synthesizes recurring failure modes and promising themes across each round and writes the research overview.

---

## Running in Antigravity CLI (`agy`)

From `/home/xwang/projects/research`:

### 1. Interactive TUI (Standard 2-Round Run)
```bash
agy
```
Then prompt:
```text
Use co-scientist to propose novel, testable hypotheses for <your research question>. Constraints: <wet-lab / compute / dataset constraints>.
```

### 2. Deep Multi-Round Exploration (`/goal`)
Inside `agy`, use `/goal` so the Supervisor runs 3–4 full tournament + evolution rounds autonomously until Elo ratings stabilize:
```text
/goal Run a deep 3-round co-scientist tournament on: <your research question>
```

### 3. Headless / Non-Interactive CLI (`agy -p`)
```bash
agy -p --mode auto "Use co-scientist (quick mode) to generate and rank hypotheses for: <your research question>"
```

---

## Output Artifacts

Each run writes an isolated audit directory under `runs/<run_id>/`:
- `runs/<run_id>/co_scientist.db` — Full SQLite database (hypotheses, reviews, proximity edges, Elo match history, meta-reviews)
- `runs/<run_id>/final_report.md` — Ranked research proposals, Elo leaderboard, Mermaid evolutionary lineage graph, and experimental validation plans
