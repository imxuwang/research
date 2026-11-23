---
name: co-scientist
description: >-
  Multi-agent scientific research partner inspired by Google DeepMind's AI Co-Scientist.
  Use this skill when the user wants to generate, critique, rank, and evolve novel scientific
  research hypotheses, design experimental protocols, run an Elo idea tournament, or invoke
  co-scientist on a research question.
---

# Co-Scientist Multi-Agent Orchestrator

You act as the **Supervisor Agent** coordinating specialized subagents and deterministic Python scripts to iteratively generate, peer-review, cluster, debate (Elo tournament), and evolve scientific hypotheses.

## Architecture Overview

- **Supervisor (You):** Parses the research goal, defines/dispatches subagents in parallel batches, and runs Python scripts to maintain SQLite state (`runs/<run_id>/co_scientist.db`).
- **Subagents:** Defined via `define_subagent` using the exact specifications in [references/subagent_prompts.md](./references/subagent_prompts.md):
  1. `cs-generator` — Literature search + diverse hypothesis generation
  2. `cs-reflector` — Unbiased peer review + citation verification
  3. `cs-judge` — Head-to-head 3-round scientific debate judge
  4. `cs-evolver` — Critique refinement, cross-cluster crossover, simplification, and divergent mutation
  5. `cs-meta-reviewer` — Cross-round synthesis of recurring pitfalls and research overview
- **Python Scripts (`./scripts/`):**
  - [co_db.py](./scripts/co_db.py) — SQLite state store for hypotheses, lineage, reviews, and meta-reviews
  - [literature.py](./scripts/literature.py) — Zero-key search & ID verification across arXiv, PubMed, OpenAlex, and Semantic Scholar
  - [proximity.py](./scripts/proximity.py) — TF-IDF similarity graph, clustering, duplicate merging, and crossover pairing
  - [tournament.py](./scripts/tournament.py) — Swiss + cluster-aware matchmaking and exact Elo rating updates
  - [report.py](./scripts/report.py) — Renders the final Markdown report with leaderboard, Mermaid lineage graph, and top dossiers

---

## Execution Modes (Scale to User Intent)

| Mode | Initial Seeds | Rounds | Matches / Hyp / Round | Evolved / Round | When to Use |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Standard** (Default) | 6 (3 subagents × 2) | 2 | 2 | 3 | Normal interactive or `agy -p` session |
| **Quick** | 4 (2 subagents × 2) | 1 | 2 | 0 (skip evolution) | User asks for a fast/quick run |
| **Deep** (`/goal`) | 8–9 (3 subagents × 3) | 3–4 | 3 | 4 | User runs `/goal` or asks for thorough exploration |

---

## Step-by-Step Supervisor Workflow

### Phase 0: Setup & Subagent Registration
1. If key constraints (e.g., wet-lab vs. computational-only, target organism/system) are genuinely ambiguous, ask briefly; otherwise proceed immediately.
2. Read [references/subagent_prompts.md](./references/subagent_prompts.md) and register the 5 subagents (`cs-generator`, `cs-reflector`, `cs-judge`, `cs-evolver`, `cs-meta-reviewer`) via `define_subagent` (`EnableWriteTools: true`).
3. Initialize the run database:
   ```bash
   python3 .agents/skills/co-scientist/scripts/co_db.py init \
     --goal "<research goal>" \
     --constraints "<constraints>" \
     --domain "<general|biomed|ml|physics>"
   ```
   Save `run_dir` and `db_path` from the JSON output, and set Round 1:
   ```bash
   python3 .agents/skills/co-scientist/scripts/co_db.py set-round --db "<db_path>" --round 1
   ```

### Phase 1: Parallel Hypothesis Generation (Round 1)
1. Dispatch **3 `cs-generator` subagents in parallel** in a single turn via `invoke_subagent`, assigning each a distinct angle and output file so they explore orthogonal regions of literature:
   - Generator 1 (`literature_synthesis`): `output_path = <run_dir>/inbox/gen_r1_lit.json`
   - Generator 2 (`simulated_debate`): `output_path = <run_dir>/inbox/gen_r1_debate.json`
   - Generator 3 (`cross_domain`): `output_path = <run_dir>/inbox/gen_r1_xdomain.json`
2. End your turn and wait reactively for all 3 subagents to finish (do **not** poll).
3. Ingest each generated JSON file into SQLite:
   ```bash
   python3 .agents/skills/co-scientist/scripts/co_db.py add-hypothesis --db "<db_path>" --round 1 --json-file "<run_dir>/inbox/gen_r1_lit.json"
   ```

### Phase 2: Proximity Clustering & Deduplication
1. Compute the proximity graph and merge near-duplicates before spending review/debate tokens:
   ```bash
   python3 .agents/skills/co-scientist/scripts/proximity.py compute --db "<db_path>" --round <R> --dedup
   ```

### Phase 3: Parallel Peer Review (`cs-reflector`)
1. List active unreviewed hypotheses (`co_db.py list --db "<db_path>" --status active`).
2. Dispatch `cs-reflector` subagents **in parallel** (1–2 hypotheses per subagent so each reviewer stays sharp and unbiased), instructing each to write `<run_dir>/inbox/rev_r<R>_<tag>.json`.
3. Once all reviewers reply, record the reviews (with `--auto-prune` to filter fatally flawed ideas):
   ```bash
   python3 .agents/skills/co-scientist/scripts/co_db.py add-review --db "<db_path>" --round <R> --auto-prune --json-file "<run_dir>/inbox/rev_r<R>_<tag>.json"
   ```

### Phase 4: Elo Tournament Ranking (`tournament.py` + `cs-judge`)
1. Generate Swiss + top-cluster debate packets:
   ```bash
   python3 .agents/skills/co-scientist/scripts/tournament.py pair --db "<db_path>" --round <R> --matches-per-hyp 2
   ```
2. Dispatch `cs-judge` subagents **in parallel** (1–2 matchup packet files per judge), instructing each judge to write `<run_dir>/inbox/<match_id>.json`.
3. When all judges complete, update Elo ratings:
   ```bash
   python3 .agents/skills/co-scientist/scripts/tournament.py record --db "<db_path>" --round <R> --json-file "<run_dir>/inbox/<match_id>.json"
   ```

### Phase 5: Meta-Review Synthesis (`cs-meta-reviewer`)
1. Export full active hypothesis dossiers (`co_db.py list --db "<db_path>" --details > "<run_dir>/packets/round_<R>_state.json"`).
2. Invoke `cs-meta-reviewer` on `round_<R>_state.json`, writing `<run_dir>/inbox/meta_round_<R>.json`, then commit:
   ```bash
   python3 .agents/skills/co-scientist/scripts/co_db.py add-meta-review --db "<db_path>" --round <R> --json-file "<run_dir>/inbox/meta_round_<R>.json"
   ```

### Phase 6: Evolution Loop (For Rounds $2 \dots N$)
If another round remains:
1. Advance round (`co_db.py set-round --db "<db_path>" --round <R+1>`) and inspect top hypotheses + `proximity.py compute` crossover pairs + `meta_round_<R>.json` guidance.
2. Dispatch **2–3 `cs-evolver` subagents in parallel**:
   - **Critique Refinement:** Fix peer-review weaknesses of the #1 Elo hypothesis.
   - **Cross-Cluster Crossover:** Recombine the top `recommended_crossover_pairs` from `proximity.py`.
   - **Divergent / Simplification:** Explore an `unexplored_directions` gap from the Meta-Review or simplify an overly complex contender.
3. Ingest evolved hypotheses (`co_db.py add-hypothesis`), then repeat **Phases 2 → 5** so new children are clustered, peer-reviewed, and tested head-to-head against incumbent leaders in the Elo tournament!

### Phase 7: Final Report & Validation
1. Render the final report:
   ```bash
   python3 .agents/skills/co-scientist/scripts/report.py --db "<db_path>" --top 3
   ```
2. Verify `co_db.py status --db "<db_path>"` confirms reviews, matches, and meta-review are recorded, and verify `<run_dir>/final_report.md` exists and is non-empty.
3. Present a concise executive summary to the user with clickable file links to `<run_dir>/final_report.md` and `<db_path>`.
