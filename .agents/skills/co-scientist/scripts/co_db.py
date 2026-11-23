#!/usr/bin/env python3
"""SQLite state store for the Co-Scientist multi-agent workflow.

Manages runs, research goals, hypotheses (with evolutionary lineage), peer reviews,
proximity graph edges/clusters, Elo tournament matches, and round meta-reviews.
Uses Python stdlib only (sqlite3 + WAL mode for safe concurrent access).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sqlite3
import sys
import uuid
from typing import Any


DEFAULT_ELO = 1200.0


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def connect_db(db_path: str | pathlib.Path) -> sqlite3.Connection:
    path = pathlib.Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS run_meta (
    run_id TEXT PRIMARY KEY,
    goal TEXT NOT NULL,
    constraints TEXT DEFAULT '',
    domain TEXT DEFAULT 'general',
    current_round INTEGER DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS hypotheses (
    id TEXT PRIMARY KEY,
    round_created INTEGER NOT NULL,
    strategy TEXT NOT NULL DEFAULT 'initial',
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    mechanism TEXT NOT NULL,
    experimental_plan TEXT NOT NULL,
    novelty_claim TEXT DEFAULT '',
    citations_json TEXT DEFAULT '[]',
    parent_ids_json TEXT DEFAULT '[]',
    elo REAL NOT NULL DEFAULT 1200.0,
    matches_played INTEGER NOT NULL DEFAULT 0,
    wins INTEGER NOT NULL DEFAULT 0,
    losses INTEGER NOT NULL DEFAULT 0,
    draws INTEGER NOT NULL DEFAULT 0,
    cluster_id INTEGER DEFAULT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    merged_into TEXT DEFAULT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hypothesis_id TEXT NOT NULL REFERENCES hypotheses(id),
    round INTEGER NOT NULL,
    reviewer_role TEXT DEFAULT 'cs-reflector',
    novelty_score REAL NOT NULL,
    soundness_score REAL NOT NULL,
    feasibility_score REAL NOT NULL,
    testability_score REAL NOT NULL,
    overall_score REAL NOT NULL,
    decision TEXT NOT NULL DEFAULT 'keep',
    strengths_json TEXT DEFAULT '[]',
    weaknesses_json TEXT DEFAULT '[]',
    assumptions_json TEXT DEFAULT '[]',
    citation_checks_json TEXT DEFAULT '[]',
    suggested_improvements TEXT DEFAULT '',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS proximity_edges (
    round INTEGER NOT NULL,
    hyp_a TEXT NOT NULL REFERENCES hypotheses(id),
    hyp_b TEXT NOT NULL REFERENCES hypotheses(id),
    similarity REAL NOT NULL,
    shared_terms_json TEXT DEFAULT '[]',
    PRIMARY KEY (round, hyp_a, hyp_b)
);

CREATE TABLE IF NOT EXISTS matches (
    id TEXT PRIMARY KEY,
    round INTEGER NOT NULL,
    hyp_a TEXT NOT NULL REFERENCES hypotheses(id),
    hyp_b TEXT NOT NULL REFERENCES hypotheses(id),
    match_type TEXT DEFAULT 'swiss',
    winner TEXT NOT NULL,
    confidence REAL DEFAULT 0.7,
    elo_a_before REAL NOT NULL,
    elo_b_before REAL NOT NULL,
    elo_a_after REAL NOT NULL,
    elo_b_after REAL NOT NULL,
    debate_summary TEXT NOT NULL,
    key_differentiator TEXT DEFAULT '',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS meta_reviews (
    round INTEGER PRIMARY KEY,
    recurring_weaknesses_json TEXT DEFAULT '[]',
    promising_themes_json TEXT DEFAULT '[]',
    unexplored_directions_json TEXT DEFAULT '[]',
    evolution_guidance TEXT NOT NULL,
    research_overview TEXT DEFAULT '',
    created_at TEXT NOT NULL
);
"""


def load_json_input(json_file: str | None, json_str: str | None) -> Any:
    if json_file:
        if json_file == "-":
            return json.loads(sys.stdin.read())
        return json.loads(pathlib.Path(json_file).read_text(encoding="utf-8"))
    if json_str:
        return json.loads(json_str)
    raise ValueError("Provide either --json-file <path|-> or --json '<string>'.")


def next_hypothesis_id(conn: sqlite3.Connection) -> str:
    row = conn.execute("SELECT COUNT(*) AS cnt FROM hypotheses").fetchone()
    idx = (row["cnt"] if row else 0) + 1
    while True:
        candidate = f"H{idx:03d}"
        exists = conn.execute("SELECT 1 FROM hypotheses WHERE id = ?", (candidate,)).fetchone()
        if not exists:
            return candidate
        idx += 1


def row_to_hypothesis_dict(conn: sqlite3.Connection, row: sqlite3.Row, include_details: bool = False) -> dict[str, Any]:
    d = dict(row)
    d["citations"] = json.loads(d.pop("citations_json") or "[]")
    d["parent_ids"] = json.loads(d.pop("parent_ids_json") or "[]")
    rev_row = conn.execute(
        """
        SELECT ROUND(AVG(overall_score), 2) AS avg_score,
               ROUND(AVG(novelty_score), 2) AS avg_novelty,
               ROUND(AVG(soundness_score), 2) AS avg_soundness,
               ROUND(AVG(feasibility_score), 2) AS avg_feasibility,
               COUNT(*) AS review_count
        FROM reviews WHERE hypothesis_id = ?
        """,
        (d["id"],),
    ).fetchone()
    d["review_summary"] = dict(rev_row) if rev_row else {}

    if include_details:
        revs = conn.execute(
            "SELECT * FROM reviews WHERE hypothesis_id = ? ORDER BY id DESC",
            (d["id"],),
        ).fetchall()
        parsed_revs = []
        for r in revs:
            rd = dict(r)
            for k in ("strengths", "weaknesses", "assumptions", "citation_checks"):
                rd[k] = json.loads(rd.pop(f"{k}_json") or "[]")
            parsed_revs.append(rd)
        d["reviews"] = parsed_revs

        matches = conn.execute(
            "SELECT * FROM matches WHERE hyp_a = ? OR hyp_b = ? ORDER BY created_at DESC",
            (d["id"], d["id"]),
        ).fetchall()
        d["matches"] = [dict(m) for m in matches]

    return d


def cmd_init(args: argparse.Namespace) -> None:
    ts = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_id = args.run_id or f"run_{ts}_{uuid.uuid4().hex[:6]}"
    base_dir = pathlib.Path(args.runs_dir) / run_id
    base_dir.mkdir(parents=True, exist_ok=True)
    (base_dir / "inbox").mkdir(exist_ok=True)
    (base_dir / "packets").mkdir(exist_ok=True)

    db_path = base_dir / "co_scientist.db"
    conn = connect_db(db_path)
    with conn:
        conn.executescript(SCHEMA_SQL)
        now = utc_now()
        conn.execute(
            """
            INSERT OR REPLACE INTO run_meta
            (run_id, goal, constraints, domain, current_round, created_at, updated_at)
            VALUES (?, ?, ?, ?, 0, ?, ?)
            """,
            (run_id, args.goal, args.constraints or "", args.domain or "general", now, now),
        )
    conn.close()
    print(
        json.dumps(
            {
                "ok": True,
                "run_id": run_id,
                "run_dir": str(base_dir.resolve()),
                "db_path": str(db_path.resolve()),
                "goal": args.goal,
            },
            indent=2,
        )
    )


def cmd_set_round(args: argparse.Namespace) -> None:
    conn = connect_db(args.db)
    with conn:
        conn.execute(
            "UPDATE run_meta SET current_round = ?, updated_at = ?",
            (args.round, utc_now()),
        )
    conn.close()
    print(json.dumps({"ok": True, "current_round": args.round}))


def cmd_add_hypothesis(args: argparse.Namespace) -> None:
    payload = load_json_input(args.json_file, args.json)
    items = payload["hypotheses"] if isinstance(payload, dict) and "hypotheses" in payload else payload
    if isinstance(items, dict):
        items = [items]

    conn = connect_db(args.db)
    added_ids: list[str] = []
    with conn:
        meta = conn.execute("SELECT current_round FROM run_meta LIMIT 1").fetchone()
        default_round = args.round if args.round is not None else (meta["current_round"] if meta else 1)
        now = utc_now()

        for item in items:
            hid = item.get("id") or next_hypothesis_id(conn)
            parent_ids = item.get("parent_ids", [])
            start_elo = DEFAULT_ELO
            # Evolved children inherit the average Elo of parents (slightly regressed toward 1200)
            if parent_ids:
                placeholders = ",".join("?" for _ in parent_ids)
                prows = conn.execute(
                    f"SELECT AVG(elo) AS avg_elo FROM hypotheses WHERE id IN ({placeholders})",
                    parent_ids,
                ).fetchall()
                if prows and prows[0]["avg_elo"] is not None:
                    start_elo = round(0.5 * DEFAULT_ELO + 0.5 * float(prows[0]["avg_elo"]), 2)

            conn.execute(
                """
                INSERT INTO hypotheses
                (id, round_created, strategy, title, summary, mechanism, experimental_plan,
                 novelty_claim, citations_json, parent_ids_json, elo, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', ?)
                """,
                (
                    hid,
                    int(item.get("round", default_round)),
                    str(item.get("strategy", "initial")),
                    str(item["title"]).strip(),
                    str(item["summary"]).strip(),
                    str(item["mechanism"]).strip(),
                    str(item["experimental_plan"]).strip(),
                    str(item.get("novelty_claim", "")).strip(),
                    json.dumps(item.get("citations", [])),
                    json.dumps(parent_ids),
                    start_elo,
                    now,
                ),
            )
            added_ids.append(hid)
        conn.execute("UPDATE run_meta SET updated_at = ?", (now,))
    conn.close()
    print(json.dumps({"ok": True, "added_count": len(added_ids), "hypothesis_ids": added_ids}, indent=2))


def cmd_add_review(args: argparse.Namespace) -> None:
    payload = load_json_input(args.json_file, args.json)
    items = payload["reviews"] if isinstance(payload, dict) and "reviews" in payload else payload
    if isinstance(items, dict):
        items = [items]

    conn = connect_db(args.db)
    recorded = []
    with conn:
        meta = conn.execute("SELECT current_round FROM run_meta LIMIT 1").fetchone()
        default_round = args.round if args.round is not None else (meta["current_round"] if meta else 1)
        now = utc_now()

        for item in items:
            hid = item["hypothesis_id"]
            novelty = float(item.get("novelty_score", 5.0))
            soundness = float(item.get("soundness_score", 5.0))
            feasibility = float(item.get("feasibility_score", 5.0))
            testability = float(item.get("testability_score", 5.0))
            overall = float(
                item.get(
                    "overall_score",
                    round((0.30 * novelty + 0.35 * soundness + 0.20 * feasibility + 0.15 * testability), 2),
                )
            )
            decision = str(item.get("decision", "keep")).lower()

            conn.execute(
                """
                INSERT INTO reviews
                (hypothesis_id, round, reviewer_role, novelty_score, soundness_score,
                 feasibility_score, testability_score, overall_score, decision,
                 strengths_json, weaknesses_json, assumptions_json, citation_checks_json,
                 suggested_improvements, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    hid,
                    int(item.get("round", default_round)),
                    str(item.get("reviewer_role", "cs-reflector")),
                    novelty,
                    soundness,
                    feasibility,
                    testability,
                    overall,
                    decision,
                    json.dumps(item.get("strengths", [])),
                    json.dumps(item.get("weaknesses", [])),
                    json.dumps(item.get("assumptions", [])),
                    json.dumps(item.get("citation_checks", [])),
                    str(item.get("suggested_improvements", "")),
                    now,
                ),
            )
            if decision == "reject" and args.auto_prune:
                conn.execute("UPDATE hypotheses SET status = 'rejected' WHERE id = ?", (hid,))
            recorded.append({"hypothesis_id": hid, "overall_score": overall, "decision": decision})
        conn.execute("UPDATE run_meta SET updated_at = ?", (now,))
    conn.close()
    print(json.dumps({"ok": True, "reviews_recorded": recorded}, indent=2))


def cmd_add_meta_review(args: argparse.Namespace) -> None:
    item = load_json_input(args.json_file, args.json)
    conn = connect_db(args.db)
    with conn:
        meta = conn.execute("SELECT current_round FROM run_meta LIMIT 1").fetchone()
        rnd = args.round if args.round is not None else (meta["current_round"] if meta else 1)
        now = utc_now()
        conn.execute(
            """
            INSERT OR REPLACE INTO meta_reviews
            (round, recurring_weaknesses_json, promising_themes_json,
             unexplored_directions_json, evolution_guidance, research_overview, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                int(rnd),
                json.dumps(item.get("recurring_weaknesses", [])),
                json.dumps(item.get("promising_themes", [])),
                json.dumps(item.get("unexplored_directions", [])),
                str(item.get("evolution_guidance", "")),
                str(item.get("research_overview", "")),
                now,
            ),
        )
        conn.execute("UPDATE run_meta SET updated_at = ?", (now,))
    conn.close()
    print(json.dumps({"ok": True, "round": rnd}, indent=2))


def cmd_list(args: argparse.Namespace) -> None:
    conn = connect_db(args.db)
    query = "SELECT * FROM hypotheses"
    params: list[Any] = []
    if args.status != "all":
        query += " WHERE status = ?"
        params.append(args.status)
    query += " ORDER BY elo DESC, id ASC"

    rows = conn.execute(query, params).fetchall()
    results = [row_to_hypothesis_dict(conn, r, include_details=args.details) for r in rows]

    if args.diverse_clusters:
        seen_clusters: set[int] = set()
        diverse: list[dict[str, Any]] = []
        overflow: list[dict[str, Any]] = []
        for item in results:
            cid = item.get("cluster_id")
            if cid is None or cid not in seen_clusters:
                diverse.append(item)
                if cid is not None:
                    seen_clusters.add(cid)
            else:
                overflow.append(item)
        results = diverse + overflow

    if args.top:
        results = results[: args.top]

    conn.close()
    print(json.dumps({"count": len(results), "hypotheses": results}, indent=2))


def cmd_show(args: argparse.Namespace) -> None:
    conn = connect_db(args.db)
    row = conn.execute("SELECT * FROM hypotheses WHERE id = ?", (args.id,)).fetchone()
    if not row:
        conn.close()
        sys.exit(f"Hypothesis {args.id} not found.")
    result = row_to_hypothesis_dict(conn, row, include_details=True)
    conn.close()
    print(json.dumps(result, indent=2))


def cmd_status(args: argparse.Namespace) -> None:
    conn = connect_db(args.db)
    meta = dict(conn.execute("SELECT * FROM run_meta LIMIT 1").fetchone())
    status_counts = {
        r["status"]: r["cnt"]
        for r in conn.execute("SELECT status, COUNT(*) AS cnt FROM hypotheses GROUP BY status").fetchall()
    }
    rev_cnt = conn.execute("SELECT COUNT(*) AS cnt FROM reviews").fetchone()["cnt"]
    match_cnt = conn.execute("SELECT COUNT(*) AS cnt FROM matches").fetchone()["cnt"]
    cluster_cnt = conn.execute(
        "SELECT COUNT(DISTINCT cluster_id) AS cnt FROM hypotheses WHERE status = 'active' AND cluster_id IS NOT NULL"
    ).fetchone()["cnt"]
    top_rows = conn.execute(
        "SELECT id, title, ROUND(elo, 1) AS elo, matches_played, cluster_id, strategy FROM hypotheses WHERE status = 'active' ORDER BY elo DESC LIMIT 5"
    ).fetchall()
    latest_meta = conn.execute("SELECT * FROM meta_reviews ORDER BY round DESC LIMIT 1").fetchone()
    conn.close()

    out = {
        "meta": meta,
        "hypothesis_counts": status_counts,
        "total_reviews": rev_cnt,
        "total_matches": match_cnt,
        "active_clusters": cluster_cnt,
        "top_5_active": [dict(r) for r in top_rows],
        "latest_meta_review_round": latest_meta["round"] if latest_meta else None,
    }
    print(json.dumps(out, indent=2))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Co-Scientist SQLite state manager")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="Initialize a new Co-Scientist run")
    p_init.add_argument("--goal", required=True, help="Natural language research goal")
    p_init.add_argument("--constraints", default="", help="Experimental, budget, or domain constraints")
    p_init.add_argument("--domain", default="general", help="Domain tag (e.g., biomed, ml, physics, general)")
    p_init.add_argument("--runs-dir", default="runs", help="Base directory for runs (default: runs)")
    p_init.add_argument("--run-id", default=None, help="Optional custom run ID")
    p_init.set_defaults(func=cmd_init)

    p_round = sub.add_parser("set-round", help="Update current round counter")
    p_round.add_argument("--db", required=True)
    p_round.add_argument("--round", type=int, required=True)
    p_round.set_defaults(func=cmd_set_round)

    p_add_h = sub.add_parser("add-hypothesis", help="Add one or more hypotheses from JSON")
    p_add_h.add_argument("--db", required=True)
    p_add_h.add_argument("--round", type=int, default=None)
    p_add_h.add_argument("--json-file", default=None)
    p_add_h.add_argument("--json", default=None)
    p_add_h.set_defaults(func=cmd_add_hypothesis)

    p_add_r = sub.add_parser("add-review", help="Record one or more peer reviews from JSON")
    p_add_r.add_argument("--db", required=True)
    p_add_r.add_argument("--round", type=int, default=None)
    p_add_r.add_argument("--json-file", default=None)
    p_add_r.add_argument("--json", default=None)
    p_add_r.add_argument("--auto-prune", action="store_true", help="Mark decision=='reject' hypotheses as rejected")
    p_add_r.set_defaults(func=cmd_add_review)

    p_add_m = sub.add_parser("add-meta-review", help="Record meta-review synthesis for a round")
    p_add_m.add_argument("--db", required=True)
    p_add_m.add_argument("--round", type=int, default=None)
    p_add_m.add_argument("--json-file", default=None)
    p_add_m.add_argument("--json", default=None)
    p_add_m.set_defaults(func=cmd_add_meta_review)

    p_list = sub.add_parser("list", help="List hypotheses ordered by Elo")
    p_list.add_argument("--db", required=True)
    p_list.add_argument("--status", default="active", choices=["active", "rejected", "merged", "all"])
    p_list.add_argument("--top", type=int, default=None)
    p_list.add_argument("--diverse-clusters", action="store_true", help="Rank one representative per cluster first")
    p_list.add_argument("--details", action="store_true", help="Include full reviews and matches")
    p_list.set_defaults(func=cmd_list)

    p_show = sub.add_parser("show", help="Show full dossier for a single hypothesis")
    p_show.add_argument("--db", required=True)
    p_show.add_argument("--id", required=True)
    p_show.set_defaults(func=cmd_show)

    p_stat = sub.add_parser("status", help="Show compact run status summary")
    p_stat.add_argument("--db", required=True)
    p_stat.set_defaults(func=cmd_status)

    return p


if __name__ == "__main__":
    parser = build_parser()
    parsed = parser.parse_args()
    parsed.func(parsed)
