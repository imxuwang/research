#!/usr/bin/env python3
"""Proximity Agent engine: TF-IDF similarity graph, clustering, deduplication, and crossover pairing.

Computes pairwise semantic/lexical similarity across active hypotheses using weighted
scientific unigrams, bigrams, and character n-grams (zero external dependencies).
Updates `proximity_edges` and `hypotheses.cluster_id` in SQLite.
"""

from __future__ import annotations

import argparse
import collections
import json
import math
import re
from typing import Any

from co_db import connect_db, utc_now


STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "could", "data",
    "do", "does", "effect", "effects", "experiments", "experimental", "for",
    "from", "has", "have", "how", "hypothesis", "if", "in", "into", "is", "it",
    "its", "may", "mechanism", "method", "model", "more", "most", "new", "no",
    "not", "novel", "of", "on", "or", "our", "over", "propose", "proposed",
    "research", "results", "role", "should", "show", "specific", "study", "such",
    "system", "test", "than", "that", "the", "their", "them", "then", "there",
    "these", "this", "through", "to", "under", "use", "used", "using", "via",
    "was", "we", "were", "which", "while", "will", "with", "within", "would",
}


def extract_features(row: dict[str, Any]) -> tuple[collections.Counter[str], set[str]]:
    sections = [
        (row.get("title", ""), 2.5),
        (row.get("summary", ""), 1.5),
        (row.get("mechanism", ""), 2.0),
        (row.get("experimental_plan", ""), 1.0),
    ]
    counts: collections.Counter[str] = collections.Counter()
    readable_terms: set[str] = set()

    for text, weight in sections:
        raw_tokens = re.findall(r"[a-z0-9][a-z0-9\-_/+]{1,}", text.lower())
        tokens = [t.strip("-_/+") for t in raw_tokens if len(t) >= 3 and t not in STOPWORDS]
        for tok in tokens:
            counts[f"w:{tok}"] += weight
            readable_terms.add(tok)
            if len(tok) >= 5:
                for i in range(len(tok) - 3):
                    counts[f"c4:{tok[i:i+4]}"] += 0.25 * weight
        for i in range(len(tokens) - 1):
            bg = f"{tokens[i]}_{tokens[i+1]}"
            counts[f"b:{bg}"] += 1.2 * weight

    return counts, readable_terms


def build_tfidf_vectors(docs: list[dict[str, Any]]) -> tuple[dict[str, dict[str, float]], dict[str, set[str]]]:
    n_docs = len(docs)
    doc_counts: dict[str, collections.Counter[str]] = {}
    doc_terms: dict[str, set[str]] = {}
    df: collections.Counter[str] = collections.Counter()

    for d in docs:
        hid = d["id"]
        cnts, terms = extract_features(d)
        doc_counts[hid] = cnts
        doc_terms[hid] = terms
        for feat in cnts:
            df[feat] += 1

    vectors: dict[str, dict[str, float]] = {}
    for hid, cnts in doc_counts.items():
        vec: dict[str, float] = {}
        norm_sq = 0.0
        for feat, tf in cnts.items():
            # Smooth IDF so small corpora (4-12 hypotheses) stay well-behaved
            idf = math.log((1.0 + n_docs) / (1.0 + df[feat])) + 1.0
            val = (1.0 + math.log(tf)) * idf if tf > 0 else 0.0
            vec[feat] = val
            norm_sq += val * val
        norm = math.sqrt(norm_sq) or 1.0
        vectors[hid] = {k: v / norm for k, v in vec.items()}

    return vectors, doc_terms


def cosine_sim(v1: dict[str, float], v2: dict[str, float]) -> float:
    if len(v1) > len(v2):
        v1, v2 = v2, v1
    return sum(val * v2.get(k, 0.0) for k, val in v1.items())


def cluster_hypotheses(ids: list[str], sim_matrix: dict[tuple[str, str], float], threshold: float) -> dict[str, int]:
    # Average-linkage agglomerative clustering so chains don't collapse unrelated clusters
    clusters: list[list[str]] = [[hid] for hid in ids]

    def avg_sim(c1: list[str], c2: list[str]) -> float:
        total = 0.0
        for a in c1:
            for b in c2:
                key = (a, b) if a < b else (b, a)
                total += sim_matrix.get(key, 0.0)
        return total / (len(c1) * len(c2))

    while len(clusters) > 1:
        best_pair: tuple[int, int] | None = None
        best_score = -1.0
        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                s = avg_sim(clusters[i], clusters[j])
                if s > best_score:
                    best_score = s
                    best_pair = (i, j)
        if best_pair is None or best_score < threshold:
            break
        i, j = best_pair
        clusters[i] = clusters[i] + clusters[j]
        clusters.pop(j)

    # Sort clusters by size descending, then first ID
    clusters.sort(key=lambda c: (-len(c), sorted(c)[0]))
    assignment: dict[str, int] = {}
    for cid, members in enumerate(clusters, start=1):
        for m in members:
            assignment[m] = cid
    return assignment


def cmd_compute(args: argparse.Namespace) -> None:
    conn = connect_db(args.db)
    meta = conn.execute("SELECT current_round FROM run_meta LIMIT 1").fetchone()
    rnd = args.round if args.round is not None else (meta["current_round"] if meta else 1)

    rows = conn.execute(
        """
        SELECT h.*, COALESCE(AVG(r.overall_score), 5.0) AS avg_review
        FROM hypotheses h
        LEFT JOIN reviews r ON r.hypothesis_id = h.id
        WHERE h.status = 'active'
        GROUP BY h.id
        ORDER BY h.elo DESC, avg_review DESC, h.id ASC
        """
    ).fetchall()
    docs = [dict(r) for r in rows]

    if len(docs) == 0:
        conn.close()
        print(json.dumps({"ok": True, "active_count": 0, "clusters": [], "merged": []}))
        return

    vectors, doc_terms = build_tfidf_vectors(docs)
    ids = [d["id"] for d in docs]
    by_id = {d["id"]: d for d in docs}

    sim_matrix: dict[tuple[str, str], float] = {}
    shared_map: dict[tuple[str, str], list[str]] = {}
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            a, b = ids[i], ids[j]
            key = (a, b) if a < b else (b, a)
            sim = round(cosine_sim(vectors[a], vectors[b]), 4)
            sim_matrix[key] = sim
            common = sorted(doc_terms[a] & doc_terms[b], key=lambda t: (-len(t), t))[:8]
            shared_map[key] = common

    merged_events: list[dict[str, Any]] = []
    surviving_ids = list(ids)

    if args.dedup:
        # `ids` is already ordered by highest Elo, then highest avg_review
        dropped: set[str] = set()
        for i, keeper in enumerate(ids):
            if keeper in dropped:
                continue
            for dup in ids[i + 1 :]:
                if dup in dropped:
                    continue
                key = (keeper, dup) if keeper < dup else (dup, keeper)
                sim = sim_matrix[key]
                if sim >= args.dedup_threshold:
                    dropped.add(dup)
                    merged_events.append(
                        {
                            "merged_id": dup,
                            "kept_id": keeper,
                            "similarity": sim,
                            "shared_terms": shared_map[key],
                        }
                    )
        surviving_ids = [hid for hid in ids if hid not in dropped]

    cluster_map = cluster_hypotheses(surviving_ids, sim_matrix, args.cluster_threshold)

    with conn:
        conn.execute("DELETE FROM proximity_edges WHERE round = ?", (rnd,))
        for (a, b), sim in sim_matrix.items():
            conn.execute(
                """
                INSERT INTO proximity_edges (round, hyp_a, hyp_b, similarity, shared_terms_json)
                VALUES (?, ?, ?, ?, ?)
                """,
                (rnd, a, b, sim, json.dumps(shared_map[(a, b)])),
            )
        for ev in merged_events:
            conn.execute(
                "UPDATE hypotheses SET status = 'merged', merged_into = ? WHERE id = ?",
                (ev["kept_id"], ev["merged_id"]),
            )
        for hid, cid in cluster_map.items():
            conn.execute("UPDATE hypotheses SET cluster_id = ? WHERE id = ?", (cid, hid))
        conn.execute("UPDATE run_meta SET updated_at = ?", (utc_now(),))

    conn.close()

    # Summarize clusters and recommend cross-cluster recombination pairs
    clusters_summary: dict[int, list[dict[str, Any]]] = collections.defaultdict(list)
    for hid in surviving_ids:
        d = by_id[hid]
        clusters_summary[cluster_map[hid]].append(
            {
                "id": hid,
                "title": d["title"],
                "elo": round(d["elo"], 1),
                "avg_review": round(d["avg_review"], 2),
            }
        )

    crossover_candidates = []
    cluster_leaders = [members[0] for _, members in sorted(clusters_summary.items())]
    for i in range(len(cluster_leaders)):
        for j in range(i + 1, len(cluster_leaders)):
            a_id, b_id = cluster_leaders[i]["id"], cluster_leaders[j]["id"]
            key = (a_id, b_id) if a_id < b_id else (b_id, a_id)
            sim = sim_matrix.get(key, 0.0)
            combined_strength = (
                by_id[a_id]["elo"] + by_id[b_id]["elo"] + 25.0 * (by_id[a_id]["avg_review"] + by_id[b_id]["avg_review"])
            )
            crossover_candidates.append(
                {
                    "parent_a": a_id,
                    "parent_b": b_id,
                    "similarity": sim,
                    "shared_bridge_terms": shared_map.get(key, [])[:5],
                    "score": round(combined_strength, 1),
                }
            )
    crossover_candidates.sort(key=lambda x: (-x["score"], x["similarity"]))

    output = {
        "ok": True,
        "round": rnd,
        "active_count": len(surviving_ids),
        "cluster_count": len(clusters_summary),
        "merged_duplicates": merged_events,
        "clusters": [
            {"cluster_id": cid, "size": len(members), "members": members}
            for cid, members in sorted(clusters_summary.items())
        ],
        "recommended_crossover_pairs": crossover_candidates[:4],
    }
    print(json.dumps(output, indent=2))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Proximity graph, clustering, and deduplication")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_c = sub.add_parser("compute", help="Compute proximity graph and update clusters")
    p_c.add_argument("--db", required=True)
    p_c.add_argument("--round", type=int, default=None)
    p_c.add_argument(
        "--cluster-threshold",
        type=float,
        default=0.22,
        help="Average-linkage cosine similarity threshold to group into same cluster (default: 0.22)",
    )
    p_c.add_argument("--dedup", action="store_true", help="Mark near-duplicate hypotheses as merged")
    p_c.add_argument(
        "--dedup-threshold",
        type=float,
        default=0.78,
        help="Cosine similarity threshold for duplicate merging (default: 0.78)",
    )
    p_c.set_defaults(func=cmd_compute)

    return p


if __name__ == "__main__":
    parser = build_parser()
    parsed = parser.parse_args()
    parsed.func(parsed)
