#!/usr/bin/env python3
"""Render a structured Markdown Co-Scientist Research Report from SQLite state."""

from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any

from co_db import connect_db, row_to_hypothesis_dict


def safe_mermaid_label(text: str, max_len: int = 38) -> str:
    cleaned = text.replace('"', "'").replace("\n", " ").strip()
    if len(cleaned) > max_len:
        cleaned = cleaned[: max_len - 1] + "…"
    return cleaned


def generate_markdown(db_path: str, top_k: int = 3) -> str:
    conn = connect_db(db_path)
    meta = dict(conn.execute("SELECT * FROM run_meta LIMIT 1").fetchone())

    all_rows = conn.execute("SELECT * FROM hypotheses ORDER BY elo DESC, id ASC").fetchall()
    all_hyps = [row_to_hypothesis_dict(conn, r, include_details=True) for r in all_rows]
    active_hyps = [h for h in all_hyps if h["status"] == "active"]
    archived_hyps = [h for h in all_hyps if h["status"] != "active"]

    meta_revs = conn.execute("SELECT * FROM meta_reviews ORDER BY round DESC").fetchall()
    match_cnt = conn.execute("SELECT COUNT(*) AS cnt FROM matches").fetchone()["cnt"]
    rev_cnt = conn.execute("SELECT COUNT(*) AS cnt FROM reviews").fetchone()["cnt"]
    conn.close()

    lines: list[str] = []
    lines.append("# Co-Scientist Research Report")
    lines.append("")
    lines.append(f"**Run ID:** `{meta['run_id']}` | **Rounds Completed:** {meta['current_round']} | **Peer Reviews:** {rev_cnt} | **Tournament Debates:** {match_cnt}")
    lines.append("")
    lines.append("## 1. Research Goal & Constraints")
    lines.append(f"- **Goal:** {meta['goal']}")
    if meta.get("constraints"):
        lines.append(f"- **Constraints:** {meta['constraints']}")
    lines.append("")

    # Latest Meta-Review Overview
    if meta_revs:
        latest_mr = dict(meta_revs[0])
        lines.append("## 2. Meta-Review Synthesis")
        if latest_mr.get("research_overview"):
            lines.append(latest_mr["research_overview"])
            lines.append("")
        themes = json.loads(latest_mr.get("promising_themes_json") or "[]")
        weaknesses = json.loads(latest_mr.get("recurring_weaknesses_json") or "[]")
        unexplored = json.loads(latest_mr.get("unexplored_directions_json") or "[]")
        if themes:
            lines.append("**Promising Mechanistic Themes:**")
            for t in themes:
                lines.append(f"- {t}")
            lines.append("")
        if weaknesses:
            lines.append("**Key Pitfalls Filtered During Peer Review:**")
            for w in weaknesses:
                lines.append(f"- {w}")
            lines.append("")
        if unexplored:
            lines.append("**Recommended Follow-Up Directions:**")
            for u in unexplored:
                lines.append(f"- {u}")
            lines.append("")

    # Leaderboard
    lines.append("## 3. Elo Tournament Leaderboard (Active Hypotheses)")
    lines.append("")
    lines.append("| Rank | ID | Hypothesis | Elo | W-L-D | Review (1-10) | Cluster | Origin |")
    lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
    for idx, h in enumerate(active_hyps, start=1):
        rs = h.get("review_summary") or {}
        avg_sc = rs.get("avg_score")
        sc_str = f"{avg_sc:.1f}" if avg_sc is not None else "—"
        wld = f"{h['wins']}-{h['losses']}-{h['draws']}"
        parents = ",".join(h["parent_ids"]) if h["parent_ids"] else "seed"
        origin = f"R{h['round_created']} {h['strategy']} ({parents})"
        lines.append(
            f"| {idx} | `{h['id']}` | {h['title']} | **{h['elo']:.1f}** | {wld} | {sc_str} | C{h['cluster_id'] or '?'} | {origin} |"
        )
    lines.append("")

    # Evolutionary Lineage Diagram (if any parents exist)
    has_lineage = any(h["parent_ids"] for h in all_hyps)
    if has_lineage:
        lines.append("## 4. Evolutionary Lineage")
        lines.append("")
        lines.append("```mermaid")
        lines.append("flowchart TD")
        by_id = {h["id"]: h for h in all_hyps}
        for h in all_hyps:
            lbl = safe_mermaid_label(f"{h['id']} ({h['elo']:.0f}): {h['title']}")
            lines.append(f'    {h["id"]}["{lbl}"]')
            for pid in h["parent_ids"]:
                if pid in by_id:
                    lines.append(f'    {pid} -->|"{h["strategy"]}"| {h["id"]}')
        lines.append("```")
        lines.append("")

    # Top-K Detailed Dossiers
    lines.append(f"## 5. Top {min(top_k, len(active_hyps))} Research Proposals (Detailed Dossiers)")
    lines.append("")
    for rank, h in enumerate(active_hyps[:top_k], start=1):
        lines.append(f"### Proposal #{rank}: [{h['id']}] {h['title']}")
        lines.append(f"- **Elo Rating:** `{h['elo']:.1f}` ({h['wins']}W / {h['losses']}L / {h['draws']}D) | **Cluster:** `C{h['cluster_id'] or '?'}` | **Strategy:** `{h['strategy']}`")
        if h["parent_ids"]:
            lines.append(f"- **Evolved From:** {', '.join(f'`{p}`' for p in h['parent_ids'])}")
        lines.append("")
        lines.append(f"**Executive Summary:** {h['summary']}")
        lines.append("")
        if h.get("novelty_claim"):
            lines.append(f"**Novelty Claim:** {h['novelty_claim']}")
            lines.append("")
        lines.append("#### Proposed Mechanism")
        lines.append(h["mechanism"])
        lines.append("")
        lines.append("#### Experimental Validation Plan")
        lines.append(h["experimental_plan"])
        lines.append("")

        if h.get("citations"):
            lines.append("#### Grounding Literature")
            for c in h["citations"]:
                if isinstance(c, dict):
                    cid = c.get("id", "")
                    ctitle = c.get("title", "")
                    curl = c.get("url", "")
                    cnote = c.get("relevance", "")
                    link = f"[{ctitle}]({curl})" if curl and ctitle else (ctitle or cid)
                    suffix = f" — *{cnote}*" if cnote else ""
                    lines.append(f"- `{cid}` {link}{suffix}")
                else:
                    lines.append(f"- {c}")
            lines.append("")

        if h.get("reviews"):
            rev = h["reviews"][0]
            lines.append(
                f"#### Peer Review Assessment (Overall: {rev['overall_score']}/10 | "
                f"Novelty: {rev['novelty_score']} | Soundness: {rev['soundness_score']} | "
                f"Feasibility: {rev['feasibility_score']} | Testability: {rev['testability_score']})"
            )
            if rev.get("strengths"):
                lines.append("- **Strengths:** " + "; ".join(rev["strengths"]))
            if rev.get("weaknesses"):
                lines.append("- **Residual Risks / Open Questions:** " + "; ".join(rev["weaknesses"]))
            lines.append("")

        if h.get("matches"):
            lines.append("#### Key Tournament Debate Takeaways")
            for m in h["matches"][:3]:
                opp = m["hyp_b"] if m["hyp_a"] == h["id"] else m["hyp_a"]
                outcome = "Won" if m["winner"] == h["id"] else ("Drew" if m["winner"] == "draw" else "Lost")
                diff = m.get("key_differentiator") or m.get("debate_summary")
                lines.append(f"- **{outcome} vs `{opp}`:** {diff}")
            lines.append("")

    if archived_hyps:
        lines.append("## 6. Audit Trail: Merged & Rejected Hypotheses")
        lines.append("")
        for h in archived_hyps:
            note = f"merged into `{h['merged_into']}`" if h["status"] == "merged" else "pruned in peer review"
            lines.append(f"- **`{h['id']}` ({h['status']} — {note}):** {h['title']}")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser(description="Render Markdown report for a Co-Scientist run")
    p.add_argument("--db", required=True, help="Path to co_scientist.db")
    p.add_argument("--top", type=int, default=3, help="Number of top proposals to expand in full detail")
    p.add_argument("--out", default=None, help="Output markdown path (defaults to <run_dir>/final_report.md)")
    args = p.parse_args()

    out_path = pathlib.Path(args.out) if args.out else (pathlib.Path(args.db).parent / "final_report.md")
    md = generate_markdown(args.db, top_k=args.top)
    out_path.write_text(md, encoding="utf-8")
    print(json.dumps({"ok": True, "report_path": str(out_path.resolve()), "chars": len(md)}, indent=2))


if __name__ == "__main__":
    main()
