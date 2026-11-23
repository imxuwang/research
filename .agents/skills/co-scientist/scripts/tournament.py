#!/usr/bin/env python3
"""Ranking & Elo Tournament Engine for Co-Scientist.

Generates Swiss-system + cluster-aware pairwise debate packets (`pair`) and updates
exact Elo ratings from `cs-judge` subagent verdicts (`record`).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import uuid
from typing import Any

from co_db import connect_db, load_json_input, row_to_hypothesis_dict, utc_now


def expected_score(elo_a: float, elo_b: float) -> float:
    return 1.0 / (1.0 + 10.0 ** ((elo_b - elo_a) / 400.0))


def k_factor(matches_played: int) -> float:
    return 32.0 if matches_played < 4 else 24.0


def canonical_pair(a: str, b: str) -> tuple[str, str]:
    return (a, b) if a < b else (b, a)


def deterministic_swap(round_num: int, a: str, b: str) -> tuple[str, str]:
    """Deterministically pseudo-randomize A/B presentation order to mitigate LLM position bias."""
    digest = hashlib.sha256(f"{round_num}:{a}:{b}".encode("utf-8")).digest()
    return (a, b) if (digest[0] % 2 == 0) else (b, a)


def cmd_pair(args: argparse.Namespace) -> None:
    conn = connect_db(args.db)
    meta = dict(conn.execute("SELECT * FROM run_meta LIMIT 1").fetchone())
    rnd = args.round if args.round is not None else meta["current_round"]

    rows = conn.execute(
        "SELECT * FROM hypotheses WHERE status = 'active' ORDER BY elo DESC, matches_played ASC, id ASC"
    ).fetchall()
    active = [row_to_hypothesis_dict(conn, r, include_details=True) for r in rows]

    if len(active) < 2:
        conn.close()
        print(json.dumps({"ok": True, "round": rnd, "match_count": 0, "matches": []}))
        return

    past_rows = conn.execute("SELECT hyp_a, hyp_b FROM matches").fetchall()
    played_pairs = {canonical_pair(r["hyp_a"], r["hyp_b"]) for r in past_rows}

    by_id = {h["id"]: h for h in active}
    ids = [h["id"] for h in active]
    scheduled_counts = {hid: 0 for hid in ids}
    selected_matches: list[dict[str, Any]] = []
    this_round_pairs: set[tuple[str, str]] = set()

    # 1. Schedule top-contender championship debates between top distinct clusters
    top_ids = ids[: min(4, len(ids))]
    for i in range(len(top_ids)):
        for j in range(i + 1, len(top_ids)):
            a, b = top_ids[i], top_ids[j]
            cp = canonical_pair(a, b)
            if cp in played_pairs or cp in this_round_pairs:
                continue
            if scheduled_counts[a] >= args.matches_per_hyp or scheduled_counts[b] >= args.matches_per_hyp:
                continue
            if by_id[a].get("cluster_id") != by_id[b].get("cluster_id") or len(ids) <= 4:
                pres_a, pres_b = deterministic_swap(rnd, a, b)
                selected_matches.append({"hyp_a": pres_a, "hyp_b": pres_b, "match_type": "top_debate"})
                this_round_pairs.add(cp)
                scheduled_counts[a] += 1
                scheduled_counts[b] += 1
                if len(selected_matches) >= args.max_matches:
                    break
        if len(selected_matches) >= args.max_matches:
            break

    # 2. Fill remaining quota via Swiss pairing (prioritize under-tested hypotheses & close Elo)
    while len(selected_matches) < args.max_matches:
        candidates = [
            hid
            for hid in ids
            if scheduled_counts[hid] < args.matches_per_hyp
        ]
        if len(candidates) < 2:
            break
        # Pick the hypothesis with fewest total + scheduled matches, then highest Elo
        candidates.sort(key=lambda hid: (scheduled_counts[hid] + by_id[hid]["matches_played"], -by_id[hid]["elo"]))
        anchor = candidates[0]

        best_opp: str | None = None
        best_cost = float("inf")
        for opp in candidates[1:]:
            cp = canonical_pair(anchor, opp)
            if cp in this_round_pairs:
                continue
            rematch_penalty = 500.0 if cp in played_pairs else 0.0
            elo_gap = abs(by_id[anchor]["elo"] - by_id[opp]["elo"])
            # Slight bonus for intra-cluster comparison if neither has played yet
            same_cluster = by_id[anchor].get("cluster_id") and (
                by_id[anchor].get("cluster_id") == by_id[opp].get("cluster_id")
            )
            cluster_adj = -35.0 if (same_cluster and by_id[anchor]["matches_played"] == 0) else 0.0
            cost = rematch_penalty + elo_gap + cluster_adj
            if cost < best_cost:
                best_cost = cost
                best_opp = opp

        if best_opp is None:
            # Anchor cannot pair with anyone remaining; mark saturated for this pass
            scheduled_counts[anchor] = args.matches_per_hyp
            continue

        cp = canonical_pair(anchor, best_opp)
        pres_a, pres_b = deterministic_swap(rnd, anchor, best_opp)
        mtype = (
            "intra_cluster"
            if by_id[anchor].get("cluster_id") == by_id[best_opp].get("cluster_id")
            else "swiss"
        )
        selected_matches.append({"hyp_a": pres_a, "hyp_b": pres_b, "match_type": mtype})
        this_round_pairs.add(cp)
        scheduled_counts[anchor] += 1
        scheduled_counts[best_opp] += 1

    packets_dir = pathlib.Path(args.db).parent / "packets"
    packets_dir.mkdir(parents=True, exist_ok=True)

    detailed_packets = []
    for idx, m in enumerate(selected_matches, start=1):
        ha = by_id[m["hyp_a"]]
        hb = by_id[m["hyp_b"]]
        match_id = f"M_R{rnd}_{idx:02d}_{uuid.uuid4().hex[:4]}"

        def compact_card(h: dict[str, Any]) -> dict[str, Any]:
            latest_rev = h["reviews"][0] if h.get("reviews") else None
            return {
                "id": h["id"],
                "title": h["title"],
                "summary": h["summary"],
                "mechanism": h["mechanism"],
                "experimental_plan": h["experimental_plan"],
                "novelty_claim": h["novelty_claim"],
                "citations": h["citations"],
                "peer_review_summary": {
                    "overall_score": latest_rev["overall_score"],
                    "strengths": latest_rev["strengths"],
                    "weaknesses": latest_rev["weaknesses"],
                }
                if latest_rev
                else None,
            }

        packet = {
            "match_id": match_id,
            "round": rnd,
            "match_type": m["match_type"],
            "goal": meta["goal"],
            "constraints": meta["constraints"],
            "hypothesis_A": compact_card(ha),
            "hypothesis_B": compact_card(hb),
        }
        packet_file = packets_dir / f"round_{rnd}_match_{idx:02d}_{ha['id']}_vs_{hb['id']}.json"
        packet_file.write_text(json.dumps(packet, indent=2), encoding="utf-8")
        detailed_packets.append(
            {
                "match_id": match_id,
                "match_type": m["match_type"],
                "hyp_a": ha["id"],
                "hyp_b": hb["id"],
                "title_a": ha["title"],
                "title_b": hb["title"],
                "packet_file": str(packet_file.resolve()),
            }
        )

    conn.close()
    print(
        json.dumps(
            {
                "ok": True,
                "round": rnd,
                "match_count": len(detailed_packets),
                "matches": detailed_packets,
            },
            indent=2,
        )
    )


def cmd_record(args: argparse.Namespace) -> None:
    payload = load_json_input(args.json_file, args.json)
    items = payload["results"] if isinstance(payload, dict) and "results" in payload else payload
    if isinstance(items, dict):
        items = [items]

    conn = connect_db(args.db)
    meta = conn.execute("SELECT current_round FROM run_meta LIMIT 1").fetchone()
    default_round = args.round if args.round is not None else (meta["current_round"] if meta else 1)

    updates_log = []
    with conn:
        now = utc_now()
        for item in items:
            ha_id = item["hyp_a"]
            hb_id = item["hyp_b"]
            raw_winner = str(item["winner"]).strip().upper()
            if raw_winner in ("A", ha_id.upper()):
                score_a, winner_label = 1.0, ha_id
            elif raw_winner in ("B", hb_id.upper()):
                score_a, winner_label = 0.0, hb_id
            elif raw_winner in ("DRAW", "TIE", "0.5"):
                score_a, winner_label = 0.5, "draw"
            else:
                raise ValueError(f"Invalid winner '{item['winner']}'; expected 'A', 'B', '{ha_id}', '{hb_id}', or 'draw'.")

            ra_row = conn.execute("SELECT elo, matches_played, wins, losses, draws FROM hypotheses WHERE id = ?", (ha_id,)).fetchone()
            rb_row = conn.execute("SELECT elo, matches_played, wins, losses, draws FROM hypotheses WHERE id = ?", (hb_id,)).fetchone()
            if not ra_row or not rb_row:
                raise ValueError(f"Unknown hypothesis ID in match ({ha_id} vs {hb_id})")

            elo_a, mp_a = float(ra_row["elo"]), int(ra_row["matches_played"])
            elo_b, mp_b = float(rb_row["elo"]), int(rb_row["matches_played"])
            exp_a = expected_score(elo_a, elo_b)
            exp_b = 1.0 - exp_a
            score_b = 1.0 - score_a

            conf = max(0.5, min(1.0, float(item.get("confidence", 0.8))))
            # Scale K slightly by judge confidence (0.75x at 0.5 conf -> 1.0x at 1.0 conf)
            scale = 0.5 + 0.5 * conf
            new_elo_a = round(elo_a + k_factor(mp_a) * scale * (score_a - exp_a), 2)
            new_elo_b = round(elo_b + k_factor(mp_b) * scale * (score_b - exp_b), 2)

            wa, la, da = int(ra_row["wins"]), int(ra_row["losses"]), int(ra_row["draws"])
            wb, lb, db_cnt = int(rb_row["wins"]), int(rb_row["losses"]), int(rb_row["draws"])
            if score_a == 1.0:
                wa += 1
                lb += 1
            elif score_a == 0.0:
                la += 1
                wb += 1
            else:
                da += 1
                db_cnt += 1

            conn.execute(
                "UPDATE hypotheses SET elo = ?, matches_played = ?, wins = ?, losses = ?, draws = ? WHERE id = ?",
                (new_elo_a, mp_a + 1, wa, la, da, ha_id),
            )
            conn.execute(
                "UPDATE hypotheses SET elo = ?, matches_played = ?, wins = ?, losses = ?, draws = ? WHERE id = ?",
                (new_elo_b, mp_b + 1, wb, lb, db_cnt, hb_id),
            )

            mid = item.get("match_id") or f"M_{uuid.uuid4().hex[:8]}"
            conn.execute(
                """
                INSERT OR REPLACE INTO matches
                (id, round, hyp_a, hyp_b, match_type, winner, confidence,
                 elo_a_before, elo_b_before, elo_a_after, elo_b_after,
                 debate_summary, key_differentiator, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    mid,
                    int(item.get("round", default_round)),
                    ha_id,
                    hb_id,
                    str(item.get("match_type", "swiss")),
                    winner_label,
                    conf,
                    elo_a,
                    elo_b,
                    new_elo_a,
                    new_elo_b,
                    str(item.get("debate_summary", "")),
                    str(item.get("key_differentiator", "")),
                    now,
                ),
            )
            updates_log.append(
                {
                    "match_id": mid,
                    "hyp_a": ha_id,
                    "hyp_b": hb_id,
                    "winner": winner_label,
                    "elo_a": f"{elo_a:.1f} -> {new_elo_a:.1f}",
                    "elo_b": f"{elo_b:.1f} -> {new_elo_b:.1f}",
                }
            )
        conn.execute("UPDATE run_meta SET updated_at = ?", (now,))

    leaderboard = [
        dict(r)
        for r in conn.execute(
            """
            SELECT id, title, ROUND(elo, 1) AS elo, matches_played, wins, losses, draws, cluster_id, strategy
            FROM hypotheses WHERE status = 'active' ORDER BY elo DESC
            """
        ).fetchall()
    ]
    conn.close()
    print(json.dumps({"ok": True, "recorded": updates_log, "leaderboard": leaderboard}, indent=2))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Co-Scientist Elo Tournament manager")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_pair = sub.add_parser("pair", help="Generate Swiss + cluster-aware debate packets")
    p_pair.add_argument("--db", required=True)
    p_pair.add_argument("--round", type=int, default=None)
    p_pair.add_argument("--matches-per-hyp", type=int, default=2, help="Target matches per hypothesis per round")
    p_pair.add_argument("--max-matches", type=int, default=8, help="Cap total matches in this round")
    p_pair.set_defaults(func=cmd_pair)

    p_rec = sub.add_parser("record", help="Record tournament debate verdicts and update Elo")
    p_rec.add_argument("--db", required=True)
    p_rec.add_argument("--round", type=int, default=None)
    p_rec.add_argument("--json-file", default=None)
    p_rec.add_argument("--json", default=None)
    p_rec.set_defaults(func=cmd_record)

    return p


if __name__ == "__main__":
    parser = build_parser()
    parsed = parser.parse_args()
    parsed.func(parsed)
