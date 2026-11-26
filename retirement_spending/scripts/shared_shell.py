#!/usr/bin/env python3
"""Shared self-contained HTML/CSS/JS shell and dataset loader for the Pfau retirement-spending suite."""

import csv
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(ROOT, "data")
OUT_DIR = os.path.join(ROOT, "docs", "retirement-spending")

# (slug, full_en, full_zh, nav_en, nav_zh, ch_tag_en, ch_tag_zh)
CHAPTER_NAV = [
    ("", "Retirement Spending Strategies (Pfau)", "退休支出策略分析（Pfau）", "Suite Overview & Ch. 1", "全书总览与第1章", "Ch. 1", "第1章"),
    ("fixed-returns-longevity", "Fixed Returns & Longevity Risk", "固定收益与长寿风险", "Ch. 2 · Fixed Returns & Longevity", "第2章 · 固定收益与长寿风险", "Ch. 2", "第2章"),
    ("sequence-of-returns-risk", "Sequence-of-Returns Risk", "收益率顺序风险", "Ch. 3 · Sequence-of-Returns Risk", "第3章 · 收益率顺序风险", "Ch. 3", "第3章"),
    ("safe-withdrawal-rates", "Safe Withdrawal Rates & Trinity Study", "安全提取率与 Trinity 研究", "Ch. 4 · Safe Withdrawal Rates", "第4章 · 安全提取率", "Ch. 4", "第4章"),
    ("valuations-and-savings", "Valuations, Safe Savings & Drag", "市场估值、安全储蓄率与损耗", "Ch. 5A · Valuations & Safe Savings", "第5章上 · 估值与安全储蓄率", "Ch. 5A", "第5章上"),
    ("spending-smiles-glidepaths", "Spending Smiles & Bond Tents", "支出微笑曲线与动态股债滑道", "Ch. 5B · Smiles & Bond Tents", "第5章下 · 支出微笑与滑道", "Ch. 5B", "第5章下"),
    ("variable-spending", "Variable Spending & PAY Rule™", "可变支出策略与 PAY 准则", "Ch. 6 · Variable Spending & PAY", "第6章 · 可变支出与 PAY 准则", "Ch. 6", "第6章"),
    ("bonds-and-buckets", "Bond Ladders & Time Segmentation", "债券阶梯与时间分段策略", "Ch. 7 · Bond Ladders & Buckets", "第7章 · 债券阶梯与时间分段", "Ch. 7", "第7章"),
    ("funded-ratio-and-gamma", "Funded Ratio, CARE & Advisor Gamma", "资金充足率、CARE 与规划 Gamma", "Ch. 8–9 · Funded Ratio & Gamma", "第8–9章 · 充足率与 Gamma", "Ch. 8–9", "第8–9章"),
]


def load_csv_records(filename: str) -> list[dict]:
    path = os.path.join(DATA_DIR, filename)
    out = []
    with open(path, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            parsed = {}
            for k, v in row.items():
                if v == "" or v is None:
                    parsed[k] = None
                else:
                    try:
                        if "." not in v and "e" not in v.lower() and (v.isdigit() or (v.startswith("-") and v[1:].isdigit())):
                            parsed[k] = int(v)
                        else:
                            parsed[k] = float(v)
                    except ValueError:
                        parsed[k] = v
            out.append(parsed)
    return out


def dump_json_inline(obj) -> str:
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False)


SHARED_CSS = """
    :root {
      --bg: #f7f7f5;
      --bg-subtle: #fafaf8;
      --panel: #ffffff;
      --panel-alt: #f3f3ef;
      --seg-bg: #efefeb;
      --seg-active: #ffffff;
      --seg-shadow: 0 1px 2px rgba(24, 24, 27, 0.08);
      --thumb-shadow: 0 1px 3px rgba(24, 24, 27, 0.22);
      --switch-knob: #ffffff;
      --switch-knob-shadow: 0 1px 2px rgba(24, 24, 27, 0.22);
      --input-bg: #ffffff;
      --canvas-bg: transparent;
      --thead-bg: #fafaf8;
      --tooltip-bg: rgba(255, 255, 255, 0.98);
      --border: rgba(24, 24, 27, 0.09);
      --border-strong: rgba(24, 24, 27, 0.18);
      --border-hover: rgba(24, 24, 27, 0.32);
      --tip-shadow: 0 8px 24px rgba(24, 24, 27, 0.10), 0 1px 3px rgba(24, 24, 27, 0.06);
      --text: #18181b;
      --text-soft: #3f3f46;
      --muted: #52525b;
      --grid: rgba(24, 24, 27, 0.07);
      --zero-line: rgba(24, 24, 27, 0.24);
      --crosshair: rgba(24, 24, 27, 0.30);
      --accent: #1d4ed8;
      --accent-soft: rgba(29, 78, 216, 0.10);
      --accent-border: rgba(29, 78, 216, 0.24);
      --equity: #4338ca;
      --bond: #047857;
      --port: #b45309;
      --port-fill-top: rgba(180, 83, 9, 0.12);
      --port-fill-bot: rgba(180, 83, 9, 0.00);
      --expense: #9a3412;
      --inflation: #7e22ce;
      --danger: #be123c;
      --success: #047857;
      --warn-bg: rgba(180, 83, 9, 0.08);
      --warn-border: rgba(180, 83, 9, 0.24);
      --mc-outer-band: rgba(29, 78, 216, 0.08);
      --mc-inner-band: rgba(29, 78, 216, 0.18);
      --exp-outer-band: rgba(180, 83, 9, 0.10);
      --exp-inner-band: rgba(180, 83, 9, 0.22);
      --dd-band: rgba(190, 18, 60, 0.12);
      --pill-bg: #f3f3ef;
      --pill-text: #3f3f46;
      --row-alt: rgba(24, 24, 27, 0.018);
      --row-hover: rgba(29, 78, 216, 0.045);
      --font: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", system-ui, sans-serif;
      --mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      color-scheme: light;
    }

    html[data-theme="dark"] {
      --bg: #0c0d0f;
      --bg-subtle: #111316;
      --panel: #15171b;
      --panel-alt: #1d2026;
      --seg-bg: #111316;
      --seg-active: #262a32;
      --seg-shadow: 0 1px 2px rgba(0, 0, 0, 0.35);
      --thumb-shadow: 0 1px 3px rgba(0, 0, 0, 0.45);
      --switch-knob: #f4f4f5;
      --switch-knob-shadow: 0 1px 2px rgba(0, 0, 0, 0.40);
      --input-bg: #101215;
      --canvas-bg: transparent;
      --thead-bg: #191c21;
      --tooltip-bg: rgba(21, 23, 27, 0.97);
      --border: rgba(244, 244, 245, 0.09);
      --border-strong: rgba(244, 244, 245, 0.19);
      --border-hover: rgba(244, 244, 245, 0.30);
      --tip-shadow: 0 12px 28px rgba(0, 0, 0, 0.50);
      --text: #f4f4f5;
      --text-soft: #d4d4d8;
      --muted: #a1a1aa;
      --grid: rgba(244, 244, 245, 0.08);
      --zero-line: rgba(244, 244, 245, 0.24);
      --crosshair: rgba(244, 244, 245, 0.32);
      --accent: #60a5fa;
      --accent-soft: rgba(96, 165, 250, 0.16);
      --accent-border: rgba(96, 165, 250, 0.30);
      --equity: #818cf8;
      --bond: #34d399;
      --port: #f59e0b;
      --port-fill-top: rgba(245, 158, 11, 0.18);
      --port-fill-bot: rgba(245, 158, 11, 0.00);
      --expense: #fbbf24;
      --inflation: #c084fc;
      --danger: #fb7185;
      --success: #34d399;
      --warn-bg: rgba(245, 158, 11, 0.12);
      --warn-border: rgba(245, 158, 11, 0.30);
      --mc-outer-band: rgba(96, 165, 250, 0.10);
      --mc-inner-band: rgba(96, 165, 250, 0.22);
      --exp-outer-band: rgba(251, 191, 36, 0.11);
      --exp-inner-band: rgba(251, 191, 36, 0.24);
      --dd-band: rgba(251, 113, 133, 0.15);
      --pill-bg: #22262d;
      --pill-text: #d4d4d8;
      --row-alt: rgba(255, 255, 255, 0.02);
      --row-hover: rgba(96, 165, 250, 0.07);
      color-scheme: dark;
    }

    * {
      box-sizing: border-box;
      scrollbar-width: thin;
      scrollbar-color: var(--border-strong) transparent;
    }
    *::-webkit-scrollbar { width: 6px; height: 6px; }
    *::-webkit-scrollbar-track { background: transparent; }
    *::-webkit-scrollbar-thumb { background: var(--border-strong); border-radius: 999px; }
    *::-webkit-scrollbar-thumb:hover { background: var(--muted); }
    ::selection { background: var(--accent-soft); color: var(--text); }

    body {
      margin: 0;
      font-family: var(--font);
      background: var(--bg);
      color: var(--text);
      caret-color: var(--accent);
      line-height: 1.48;
      font-size: 13.5px;
      -webkit-font-smoothing: antialiased;
    }

    a:focus-visible, button:focus-visible, summary:focus-visible,
    input:focus-visible, select:focus-visible, [tabindex]:focus-visible {
      outline: 2px solid var(--accent);
      outline-offset: 2px;
    }

    .tabular { font-variant-numeric: tabular-nums; }
    .mono { font-family: var(--mono); font-variant-numeric: tabular-nums; }
    .pos { color: var(--success); }
    .neg { color: var(--danger); }
    .muted { color: var(--muted); }
    .exp-col { color: var(--expense); }
    .inf-col { color: var(--inflation); font-weight: 600; }

    /* HEADER */
    header {
      border-bottom: 1px solid var(--border);
      background: var(--panel);
      padding: 8px 22px;
      min-height: 52px;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 10px 14px;
      z-index: 30;
      flex-shrink: 0;
    }
    .hdr-left { display: flex; align-items: center; min-width: 0; }
    .hdr-title-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; min-width: 0; }
    .hdr-home-link {
      color: var(--muted);
      text-decoration: none;
      font-size: 13px;
      font-weight: 500;
      padding: 4px 2px;
      min-height: 28px;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      transition: color 0.12s;
      white-space: nowrap;
    }
    .hdr-home-link:hover { color: var(--text); }
    .hdr-sep { color: var(--border-strong); font-size: 13px; user-select: none; }
    header h1 {
      margin: 0;
      font-size: 16.5px;
      font-weight: 620;
      letter-spacing: -0.02em;
      text-wrap: balance;
    }
    .hdr-right { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
    .chapter-jump {
      width: auto;
      max-width: 255px;
      background: var(--input-bg);
      color: var(--text);
      border: 1px solid var(--border-strong);
      border-radius: 6px;
      padding: 4px 8px;
      min-height: 32px;
      font-size: 12px;
      font-weight: 500;
      font-family: var(--font);
    }

    /* APP-SHELL SPLIT LAYOUT */
    .layout {
      width: 100%;
      display: grid;
      grid-template-columns: 356px minmax(0, 1fr);
    }
    .sidebar {
      padding: 0 0 28px;
      border-right: 1px solid var(--border);
      background: var(--panel);
      display: flex;
      flex-direction: column;
    }
    .workspace {
      padding: 18px 24px 36px;
      min-width: 0;
    }
    @media (min-width: 1100px) {
      body.app-shell {
        height: 100vh;
        display: flex;
        flex-direction: column;
        overflow: hidden;
      }
      body.app-shell .layout { flex: 1; overflow: hidden; }
      body.app-shell .sidebar, body.app-shell .workspace { height: 100%; overflow-y: auto; }
    }
    @media (max-width: 1099px) {
      .layout { grid-template-columns: 1fr; }
      .sidebar { border-right: none; border-bottom: 1px solid var(--border); }
      .workspace { padding: 14px 14px 28px; }
    }
    @media (max-width: 720px) {
      header { padding: 8px 12px; gap: 6px 10px; }
    }

    /* SIDEBAR SECTIONS */
    .side-section {
      border-bottom: 1px solid var(--border);
      padding: 16px 20px;
    }
    .side-section:last-of-type { border-bottom: none; }
    .sec-head-static {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      margin-bottom: 12px;
    }
    .sec-title {
      margin: 0;
      font-size: 13px;
      font-weight: 620;
      letter-spacing: -0.01em;
      color: var(--text);
      text-wrap: balance;
    }
    details.side-section > summary {
      list-style: none;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      min-height: 28px;
      user-select: none;
    }
    details.side-section > summary::-webkit-details-marker { display: none; }
    details.side-section[open] > summary { margin-bottom: 12px; }
    .sec-text { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
    .sec-summary {
      font-size: 12px;
      color: var(--muted);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    details[open] > summary .sec-summary { display: none; }
    .chev { color: var(--muted); font-size: 12px; transition: transform 0.15s; flex-shrink: 0; }
    details[open] > summary .chev { transform: rotate(90deg); }
    details.side-section > summary:hover .sec-title { color: var(--accent); }

    .control-group { margin-bottom: 13px; }
    .control-group:last-child { margin-bottom: 0; }
    label, .label-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 12px;
      font-weight: 500;
      color: var(--text-soft);
      margin-bottom: 5px;
      gap: 6px;
    }
    .label-row label { margin-bottom: 0; justify-content: flex-start; }
    .label-lead { display: inline-flex; align-items: center; gap: 5px; min-width: 0; }
    .label-hint {
      font-size: 12px;
      font-weight: 500;
      color: var(--muted);
      font-variant-numeric: tabular-nums;
      white-space: nowrap;
    }

    input[type="number"], input[type="text"], select {
      width: 100%;
      background: var(--input-bg);
      color: var(--text);
      border: 1px solid var(--border-strong);
      border-radius: 6px;
      padding: 6px 9px;
      min-height: 32px;
      font-size: 13px;
      font-family: var(--font);
      transition: border-color 0.12s, box-shadow 0.12s;
    }
    input[type="number"]:focus, input[type="text"]:focus, select:focus {
      border-color: var(--accent);
      box-shadow: 0 0 0 2px var(--accent-soft);
      outline: 2px solid transparent;
    }
    .row-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
    .row-3 { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; }

    /* CURRENCY FIELD */
    .currency-field {
      display: flex;
      align-items: center;
      background: var(--input-bg);
      border: 1px solid var(--border-strong);
      border-radius: 6px;
      padding: 0 9px;
      transition: border-color 0.12s, box-shadow 0.12s;
    }
    .currency-field:focus-within {
      border-color: var(--accent);
      box-shadow: 0 0 0 2px var(--accent-soft);
    }
    .currency-prefix {
      color: var(--muted);
      font-family: var(--mono);
      font-weight: 500;
      font-size: 13px;
      margin-right: 6px;
      user-select: none;
    }
    .currency-field input {
      border: none;
      background: transparent;
      padding: 6px 0;
      font-family: var(--mono);
      font-variant-numeric: tabular-nums;
      font-weight: 600;
      font-size: 13px;
      box-shadow: none !important;
      outline: none;
    }

    /* CHIPS, SEGMENTED CONTROLS & SLIDERS */
    .chips { display: flex; gap: 4px; margin-top: 6px; flex-wrap: wrap; }
    .chips .chip {
      flex: 1 1 0;
      text-align: center;
      background: transparent;
      border: 1px solid var(--border);
      color: var(--muted);
      font-size: 12px;
      font-weight: 500;
      font-family: var(--font);
      padding: 4px 6px;
      min-height: 28px;
      border-radius: 5px;
      cursor: pointer;
      white-space: nowrap;
      transition: border-color 0.12s, color 0.12s, background 0.12s;
    }
    .chip:hover:not(:disabled) { border-color: var(--border-strong); color: var(--text); }
    .chip.active {
      background: var(--panel-alt);
      border-color: var(--border-strong);
      color: var(--text);
      font-weight: 600;
    }

    .seg-group {
      display: inline-flex;
      background: var(--seg-bg);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 3px;
      gap: 2px;
      flex-wrap: wrap;
    }
    .scale-btn {
      background: transparent;
      border: none;
      color: var(--muted);
      padding: 4px 8px;
      min-height: 26px;
      border-radius: 4px;
      font-size: 12px;
      font-weight: 500;
      font-family: var(--font);
      cursor: pointer;
      white-space: nowrap;
      transition: color 0.12s, background 0.12s;
    }
    .scale-btn:hover { color: var(--text); }
    .scale-btn.active {
      background: var(--seg-active);
      color: var(--text);
      font-weight: 600;
      box-shadow: var(--seg-shadow);
    }

    .seg-ctl {
      display: flex;
      background: var(--seg-bg);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 3px;
      gap: 2px;
    }
    .seg-ctl button {
      flex: 1 1 0;
      background: transparent;
      border: none;
      color: var(--muted);
      padding: 5px 8px;
      min-height: 28px;
      border-radius: 4px;
      font-size: 12px;
      font-weight: 500;
      cursor: pointer;
      white-space: nowrap;
      font-family: var(--font);
      transition: color 0.12s, background 0.12s;
    }
    .seg-ctl button:hover { color: var(--text); }
    .seg-ctl button.active {
      background: var(--seg-active);
      color: var(--text);
      font-weight: 600;
      box-shadow: var(--seg-shadow);
    }

    .ratio-slider {
      -webkit-appearance: none;
      appearance: none;
      width: 100%;
      height: 26px;
      margin: 2px 0;
      background: transparent;
      cursor: pointer;
    }
    .ratio-slider::-webkit-slider-runnable-track {
      height: 6px;
      border-radius: 999px;
      background: linear-gradient(to right, var(--equity) 0 var(--pct, 50%), var(--bond) var(--pct, 50%) 100%);
    }
    .ratio-slider::-moz-range-track {
      height: 6px;
      border-radius: 999px;
      background: linear-gradient(to right, var(--equity) 0 var(--pct, 50%), var(--bond) var(--pct, 50%) 100%);
    }
    .ratio-slider::-webkit-slider-thumb {
      -webkit-appearance: none;
      width: 18px; height: 18px; margin-top: -6px;
      border-radius: 50%;
      background: var(--panel);
      border: 2px solid var(--text);
      box-shadow: var(--thumb-shadow);
    }
    .ratio-slider::-moz-range-thumb {
      width: 16px; height: 16px; border-radius: 50%;
      background: var(--panel); border: 2px solid var(--text);
    }
    .ratio-labels {
      display: flex; justify-content: space-between;
      font-size: 12px; font-family: var(--mono);
      margin-top: 2px; color: var(--text-soft); font-weight: 500;
    }

    .range-slider {
      -webkit-appearance: none;
      appearance: none;
      width: 100%;
      height: 24px;
      margin: 2px 0;
      background: transparent;
      cursor: pointer;
    }
    .range-slider::-webkit-slider-runnable-track {
      height: 5px; border-radius: 999px; background: var(--border-strong);
    }
    .range-slider::-moz-range-track {
      height: 5px; border-radius: 999px; background: var(--border-strong);
    }
    .range-slider::-webkit-slider-thumb {
      -webkit-appearance: none;
      width: 16px; height: 16px; margin-top: -5.5px;
      border-radius: 50%; background: var(--accent);
      border: 2px solid var(--panel); box-shadow: var(--thumb-shadow);
    }
    .range-slider::-moz-range-thumb {
      width: 15px; height: 15px; border-radius: 50%;
      background: var(--accent); border: 2px solid var(--panel);
    }

    .switch-row {
      display: flex; align-items: center; justify-content: space-between; gap: 8px;
    }
    .switch-row label { margin-bottom: 0; cursor: pointer; }
    .switch {
      -webkit-appearance: none; appearance: none;
      width: 38px; height: 24px; padding: 2px;
      border-radius: 999px; background: var(--border-strong);
      position: relative; cursor: pointer; flex-shrink: 0;
      transition: background 0.15s; margin: 0;
    }
    .switch::after {
      content: ""; position: absolute; top: 3px; left: 3px;
      width: 18px; height: 18px; border-radius: 50%;
      background: var(--switch-knob); box-shadow: var(--switch-knob-shadow);
      transition: transform 0.15s;
    }
    .switch:checked { background: var(--accent); }
    .switch:checked::after { transform: translateX(14px); }

    /* BUTTONS & POPOVERS */
    .btn {
      background: transparent;
      border: 1px solid var(--border-strong);
      color: var(--text-soft);
      padding: 5px 10px;
      min-height: 32px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 500;
      font-family: var(--font);
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 5px;
      white-space: nowrap;
      transition: border-color 0.12s, background 0.12s, color 0.12s;
    }
    .btn:hover:not(:disabled) { background: var(--panel-alt); color: var(--text); }
    .btn:disabled { opacity: 0.52; cursor: not-allowed; }
    .btn-accent { background: var(--accent-soft); border-color: var(--accent-border); color: var(--accent); font-weight: 600; }
    .link-btn {
      background: none; border: none; color: var(--accent);
      font-size: 12px; font-weight: 500; font-family: var(--font);
      cursor: pointer; padding: 3px 4px; min-height: 24px;
      display: inline-flex; align-items: center; border-radius: 4px;
    }
    .link-btn:hover { text-decoration: underline; text-underline-offset: 2px; }

    .info-btn {
      width: 20px; height: 20px; border-radius: 50%;
      border: 1px solid var(--border-strong); background: transparent;
      color: var(--muted); font-size: 11px; font-weight: 600;
      font-family: var(--font); cursor: pointer;
      display: inline-flex; align-items: center; justify-content: center;
      padding: 0; flex-shrink: 0;
      transition: border-color 0.12s, color 0.12s, background 0.12s;
    }
    .info-btn:hover, .info-btn[aria-expanded="true"] {
      border-color: var(--text-soft); color: var(--text); background: var(--panel-alt);
    }
    .info-popover {
      margin: 0;
      width: min(330px, calc(100vw - 24px));
      background: var(--tooltip-bg);
      border: 1px solid var(--border-strong);
      border-radius: 8px;
      padding: 11px 13px;
      box-shadow: var(--tip-shadow);
      font-size: 12px;
      line-height: 1.48;
      color: var(--text-soft);
      text-wrap: pretty;
    }
    .info-popover:not([popover]) { display: none; position: fixed; z-index: 60; }
    .info-popover.open { display: block; }

    /* NOTICES & BOOK PRESETS */
    .notice {
      font-size: 12px;
      background: var(--panel-alt);
      border: 1px solid var(--border);
      color: var(--text-soft);
      padding: 8px 10px;
      border-radius: 6px;
      margin-top: 8px;
      text-wrap: pretty;
    }
    .notice.warn { background: var(--warn-bg); border-color: var(--warn-border); color: var(--port); }
    .preset-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 5px; }
    .preset-btn {
      background: transparent;
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 6px 8px;
      text-align: left;
      cursor: pointer;
      font-family: var(--font);
      color: var(--text-soft);
      transition: border-color 0.12s, background 0.12s, color 0.12s;
    }
    .preset-btn:hover { border-color: var(--border-strong); background: var(--panel-alt); color: var(--text); }
    .preset-btn.active { background: var(--accent-soft); border-color: var(--accent-border); color: var(--text); }
    .preset-btn .p-title { display: block; font-size: 12px; font-weight: 600; line-height: 1.25; }
    .preset-btn .p-meta { display: block; font-size: 11px; color: var(--muted); margin-top: 2px; line-height: 1.2; }

    /* RESULTS SHELL, TABS & KPIs */
    .results-shell {
      --body-px: 20px;
      --body-py: 18px;
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 8px;
      overflow: visible;
    }
    @media (max-width: 680px) {
      .results-shell { --body-px: 14px; --body-py: 14px; }
    }
    .tabs-bar {
      display: flex; gap: 8px; padding: 10px var(--body-px);
      border-bottom: 1px solid var(--border);
      flex-wrap: wrap; align-items: center; justify-content: space-between;
    }
    .tab-strip { display: flex; gap: 6px; flex-wrap: wrap; }
    .tab-btn {
      background: transparent; border: 1px solid transparent; border-radius: 6px;
      color: var(--muted); padding: 7px 11px;
      font-size: 12.5px; font-weight: 500; font-family: var(--font);
      cursor: pointer; display: inline-flex; align-items: center; gap: 6px; white-space: nowrap;
      transition: color 0.12s, border-color 0.12s, background 0.12s;
    }
    .tab-btn:hover { color: var(--text); background: var(--panel-alt); }
    .tab-btn.active { background: var(--accent-soft); border-color: var(--accent-border); color: var(--text); font-weight: 620; }
    .tabs-controls { display: flex; gap: 6px; align-items: center; flex-wrap: wrap; padding: 6px 0; margin-left: auto; }
    .results-body { padding: var(--body-py) var(--body-px) 20px; }
    .tab-pane > .panel-block {
      padding: 18px 0;
      border-bottom: 1px solid var(--border);
    }
    .tab-pane > .panel-block:first-child { padding-top: 0; }
    .tab-pane > .panel-block:last-child { padding-bottom: 0; border-bottom: none; }
    .card-title {
      font-size: 13.5px; font-weight: 620; letter-spacing: -0.01em; color: var(--text);
      margin: 0 0 10px 0; display: flex; align-items: center; justify-content: space-between;
      gap: 10px; flex-wrap: wrap; text-wrap: balance;
    }
    .subhead { color: var(--muted); font-size: 12px; text-wrap: pretty; }

    .kpis {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 1px;
      background: var(--border);
      border-top: 1px solid var(--border);
      border-bottom: 1px solid var(--border);
      overflow: hidden;
      margin: 0 calc(var(--body-px, 20px) * -1);
    }
    .kpis.kpis-flush-top { margin-top: calc(var(--body-py, 18px) * -1); border-top: none; }
    .kpis.kpis-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
    .kpis.kpis-5 { grid-template-columns: repeat(5, minmax(0, 1fr)); }
    .kpis.kpis-6 { grid-template-columns: repeat(6, minmax(0, 1fr)); }
    @media (max-width: 1280px) {
      .kpis.kpis-6, .kpis.kpis-5 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
    }
    @media (max-width: 720px) {
      .kpis, .kpis.kpis-3, .kpis.kpis-4, .kpis.kpis-5, .kpis.kpis-6 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }
    .kpi { background: var(--bg-subtle); padding: 12px 14px; min-width: 0; }
    .kpi-label { font-size: 12px; color: var(--muted); font-weight: 500; line-height: 1.3; }
    .kpi-val {
      font-size: clamp(14.5px, 1.25vw, 18.5px); font-weight: 650;
      font-family: var(--mono); font-variant-numeric: tabular-nums;
      letter-spacing: -0.02em; margin-top: 4px; line-height: 1.25; white-space: nowrap;
    }
    .kpi-sub { font-size: 12px; color: var(--muted); margin-top: 4px; line-height: 1.35; font-variant-numeric: tabular-nums; }

    /* CHARTS & TOOLTIPS */
    .chart-wrap { position: relative; width: 100%; }
    canvas { width: 100%; display: block; background: var(--canvas-bg); touch-action: pan-y; }
    .legend {
      display: flex; flex-wrap: wrap; gap: 10px 14px; font-size: 12px;
      color: var(--text-soft); margin-bottom: 10px; align-items: center; justify-content: space-between;
    }
    .legend-items { display: flex; gap: 14px; flex-wrap: wrap; align-items: center; }
    .legend-item { display: inline-flex; align-items: center; gap: 6px; }
    .swatch { width: 11px; height: 3px; border-radius: 1px; display: inline-block; }
    .tooltip {
      position: absolute; pointer-events: none; background: var(--tooltip-bg);
      border: 1px solid var(--border-strong); border-radius: 6px; padding: 8px 10px;
      font-size: 12px; font-family: var(--mono); font-variant-numeric: tabular-nums;
      color: var(--text); box-shadow: var(--tip-shadow); display: none; z-index: 15;
      min-width: min(220px, calc(100% - 16px)); max-width: calc(100% - 16px);
    }
    .tip-row { display: flex; justify-content: space-between; gap: 14px; line-height: 1.5; }

    /* 2-COL GRID INSIDE RESULTS */
    .split-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 1px;
      background: var(--border);
      border-bottom: 1px solid var(--border);
      margin: 0 calc(var(--body-px, 20px) * -1);
    }
    .split-grid > .grid-cell { background: var(--panel); padding: 16px var(--body-px, 20px); min-width: 0; }
    @media (max-width: 960px) { .split-grid { grid-template-columns: 1fr; } }

    /* TABLES */
    .table-container {
      max-height: 460px; overflow: auto;
    }
    table {
      width: 100%; border-collapse: collapse; font-size: 12px;
      font-family: var(--mono); font-variant-numeric: tabular-nums;
    }
    th, td { padding: 7px 10px; text-align: right; border-bottom: 1px solid var(--border); white-space: nowrap; }
    th:first-child, td:first-child { text-align: left; }
    th {
      position: sticky; top: 0; background: var(--thead-bg); color: var(--muted);
      border-top: 1px solid var(--border);
      font-family: var(--font); font-size: 12px; font-weight: 600; z-index: 2;
    }
    tbody tr:nth-child(even) td { background: var(--row-alt); }
    tbody tr:hover td { background: var(--row-hover); }
    tr.highlight-row td { background: var(--accent-soft) !important; font-weight: 600; }
    .year-pill {
      display: inline-block; padding: 1px 6px; border-radius: 4px;
      background: var(--pill-bg); color: var(--pill-text); font-size: 11px; font-weight: 500;
    }
    .hm-cell { text-align: center !important; font-weight: 500; }

    /* PROSE NOTES BLOCK */
    .method-note {
      font-size: 12.5px; color: var(--text-soft); line-height: 1.55; max-width: 74ch; text-wrap: pretty;
    }
    .method-note strong { color: var(--text); }

    @media (pointer: coarse) {
      .hdr-home-link { min-height: 40px; }
      .btn { min-height: 40px; padding: 8px 12px; font-size: 13px; }
      .tab-btn { min-height: 44px; padding: 12px 2px 10px; font-size: 13px; }
      .scale-btn, .seg-ctl button, .chips .chip { min-height: 38px; padding: 7px 10px; font-size: 12.5px; }
      input[type="number"], input[type="text"], select { font-size: 16px; min-height: 40px; }
    }
    @media (prefers-reduced-motion: reduce) {
      * { transition: none !important; animation: none !important; }
    }
"""

SHARED_JS_HEAD = """
    const LANG_STORAGE_KEY = "site_lang_v1";
    const THEME_STORAGE_KEY = "site_theme_v1";
    const CANVAS_FONT = '11px ui-monospace, SFMono-Regular, Menlo, Consolas, "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif';
    const CANVAS_LABEL_FONT = '600 11px -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", system-ui, sans-serif';

    const SHARED_I18N = {
      nav_home: { "en-UK": "Home", "zh-CN": "首页" },
      nav_suite: { "en-UK": "Retirement Spending", "zh-CN": "退休支出策略" },
      theme_dark: { "en-UK": "Dark", "zh-CN": "深色" },
      theme_light: { "en-UK": "Light", "zh-CN": "浅色" },
      theme_title: { "en-UK": "Toggle Dark / Light Theme", "zh-CN": "切换深色 / 浅色主题" },
      btn_export_csv: { "en-UK": "Export CSV", "zh-CN": "导出 CSV" },
      btn_reset: { "en-UK": "Reset", "zh-CN": "重置" },
      aria_lang: { "en-UK": "Language", "zh-CN": "语言切换" },
      aria_jump: { "en-UK": "Jump to chapter lab", "zh-CN": "跳转至章节实验室" },
      aria_sidebar: { "en-UK": "Simulation parameters", "zh-CN": "模拟参数设置" },
      aria_workspace: { "en-UK": "Simulation outputs", "zh-CN": "模拟结果输出" },
      lbl_presets: { "en-UK": "Book exhibit presets", "zh-CN": "全书图表预设" },
      yr_prefix: { "en-UK": "Yr ", "zh-CN": "第" },
      yr_suffix: { "en-UK": "", "zh-CN": "年" },
      age_lbl: { "en-UK": "Age {a}", "zh-CN": "{a} 岁" }
    };
"""

SHARED_JS_UTILS = """
    function detectInitialLang() {
      try {
        const saved = localStorage.getItem(LANG_STORAGE_KEY);
        if (saved === "en-UK" || saved === "zh-CN") return saved;
      } catch (_) {}
      const nav = (navigator.language || "").toLowerCase();
      return nav.startsWith("zh") ? "zh-CN" : "en-UK";
    }

    function detectInitialTheme() {
      try {
        const t = localStorage.getItem(THEME_STORAGE_KEY);
        if (t === "dark" || t === "light") return t;
      } catch (_) {}
      if (document.documentElement.dataset.theme === "dark" || document.documentElement.dataset.theme === "light") {
        return document.documentElement.dataset.theme;
      }
      return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    }

    let currentLang = detectInitialLang();
    const I18N = Object.assign({}, SHARED_I18N, typeof PAGE_I18N !== "undefined" ? PAGE_I18N : {});

    function t(key, vars) {
      const entry = I18N[key];
      let str = entry ? (entry[currentLang] !== undefined ? entry[currentLang] : entry["en-UK"]) : key;
      if (vars && typeof vars === "object") {
        for (const k of Object.keys(vars)) {
          str = str.replace(new RegExp("\\\\{" + k + "\\\\}", "g"), vars[k]);
        }
      }
      return str;
    }

    function setBtnActive(btn, active) {
      btn.classList.toggle("active", !!active);
      btn.setAttribute("aria-pressed", active ? "true" : "false");
    }

    function syncThemeBtn() {
      const btn = document.getElementById("btnThemeToggle");
      if (!btn) return;
      const isDark = document.documentElement.dataset.theme === "dark";
      const lbl = btn.querySelector(".theme-lbl");
      const sun = btn.querySelector(".icon-sun");
      const moon = btn.querySelector(".icon-moon");
      if (lbl) lbl.textContent = isDark ? t("theme_light") : t("theme_dark");
      if (sun) sun.style.display = isDark ? "inline" : "none";
      if (moon) moon.style.display = isDark ? "none" : "inline";
      btn.setAttribute("title", t("theme_title"));
      btn.setAttribute("aria-pressed", isDark ? "true" : "false");
    }

    function applyTheme(next) {
      const th = next === "dark" ? "dark" : "light";
      document.documentElement.dataset.theme = th;
      syncThemeBtn();
      try { localStorage.setItem(THEME_STORAGE_KEY, th); } catch (_) {}
      if (typeof onThemeOrLangChange === "function") onThemeOrLangChange();
    }

    function applyStaticI18n() {
      document.documentElement.lang = currentLang === "zh-CN" ? "zh-CN" : "en-GB";
      document.title = t("page_title");
      document.querySelectorAll("[data-i18n]").forEach(el => {
        el.textContent = t(el.dataset.i18n);
      });
      document.querySelectorAll("[data-i18n-title]").forEach(el => {
        el.setAttribute("title", t(el.dataset.i18nTitle));
      });
      document.querySelectorAll("[data-i18n-aria-label]").forEach(el => {
        el.setAttribute("aria-label", t(el.dataset.i18nAriaLabel));
      });
      document.querySelectorAll("[data-i18n-html]").forEach(el => {
        el.innerHTML = t(el.dataset.i18nHtml);
      });
      document.querySelectorAll("#langSwitch button[data-lang]").forEach(btn => {
        setBtnActive(btn, btn.dataset.lang === currentLang);
      });
      const sel = document.getElementById("chapterJump");
      if (sel) {
        Array.from(sel.options).forEach(opt => {
          const txt = currentLang === "zh-CN" ? opt.dataset.zh : opt.dataset.en;
          if (txt) opt.textContent = txt;
        });
      }
      syncThemeBtn();
    }

    function parseMoney(el) {
      const n = parseFloat(String(el.value).replace(/[^0-9.-]/g, ""));
      return isFinite(n) ? n : 0;
    }
    function formatMoneyEl(el, val) {
      el.value = Math.max(0, Math.round(val)).toLocaleString("en-US");
    }
    function fmtCompactMoney(v) {
      if (!isFinite(v)) return "—";
      const abs = Math.abs(v), s = v < 0 ? "-" : "";
      if (abs >= 1e9) return s + "$" + (abs / 1e9).toFixed(2) + "B";
      if (abs >= 1e6) {
        const m = abs / 1e6;
        return s + "$" + (Math.abs(m - Math.round(m)) < 0.005 ? Math.round(m) : m.toFixed(2)) + "M";
      }
      if (abs >= 1e3) {
        const k = abs / 1e3;
        return s + "$" + (Math.abs(k - Math.round(k)) < 0.05 ? Math.round(k) : k.toFixed(1)) + "k";
      }
      return s + "$" + Math.round(abs).toLocaleString("en-US");
    }
    function fmtExactMoney(v) {
      if (!isFinite(v)) return "—";
      const abs = Math.abs(v), s = v < 0 ? "-" : "";
      return s + "$" + Math.round(abs).toLocaleString("en-US");
    }
    function fmtPct(v, d = 2, plus = true) {
      if (v === null || v === undefined || !isFinite(v)) return "—";
      const s = v > 0 && plus ? "+" : "";
      return s + v.toFixed(d) + "%";
    }

    function getThemeColors() {
      const cs = getComputedStyle(document.documentElement);
      const g = k => cs.getPropertyValue(k).trim();
      return {
        panel: g("--panel"), bgSubtle: g("--bg-subtle"), text: g("--text"), textSoft: g("--text-soft"),
        muted: g("--muted"), grid: g("--grid"), zeroLine: g("--zero-line"), crosshair: g("--crosshair"),
        accent: g("--accent"), accentSoft: g("--accent-soft"), equity: g("--equity"), bond: g("--bond"),
        port: g("--port"), portFillTop: g("--port-fill-top"), portFillBot: g("--port-fill-bot"),
        expense: g("--expense"), inflation: g("--inflation"), danger: g("--danger"), success: g("--success"),
        mcOuterBand: g("--mc-outer-band"), mcInnerBand: g("--mc-inner-band"),
        expOuterBand: g("--exp-outer-band"), expInnerBand: g("--exp-inner-band"), ddBand: g("--dd-band")
      };
    }

    function setupCanvas(canvas) {
      const dpr = window.devicePixelRatio || 1;
      if (!canvas.dataset.baseHeight) {
        canvas.dataset.baseHeight = canvas.getAttribute("height") || "290";
      }
      const h = parseInt(canvas.dataset.baseHeight, 10);
      canvas.style.height = h + "px";
      const rect = canvas.getBoundingClientRect();
      if (rect.width < 20) return null;
      const w = rect.width;
      canvas.width = Math.round(w * dpr);
      canvas.height = Math.round(h * dpr);
      const ctx = canvas.getContext("2d");
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      return { ctx, w, h };
    }

    function computeNiceLinearTicks(minVal, maxVal, targetCount = 5) {
      if (!isFinite(minVal) || !isFinite(maxVal)) return [0, 1];
      if (maxVal <= minVal) maxVal = minVal + 1;
      const rawStep = (maxVal - minVal) / Math.max(1, targetCount);
      const mag = Math.pow(10, Math.floor(Math.log10(rawStep)));
      const frac = rawStep / mag;
      const nice = frac <= 1 ? 1 : frac <= 2 ? 2 : frac <= 2.5 ? 2.5 : frac <= 5 ? 5 : 10;
      const step = nice * mag;
      const tickMin = Math.floor(minVal / step) * step;
      const tickMax = Math.ceil(maxVal / step) * step;
      const ticks = [];
      const cnt = Math.round((tickMax - tickMin) / step);
      for (let i = 0; i <= cnt; i++) {
        const v = tickMin + i * step;
        ticks.push(Math.abs(v) < step * 1e-9 ? 0 : Number(v.toPrecision(10)));
      }
      return ticks;
    }

    function mulberry32(a) {
      let s = a >>> 0;
      return function () {
        s = (s + 0x6D2B79F5) >>> 0;
        let r = Math.imul(s ^ (s >>> 15), 1 | s);
        r = (r + Math.imul(r ^ (r >>> 7), 61 | r)) ^ r;
        return ((r ^ (r >>> 14)) >>> 0) / 4294967296;
      };
    }

    function randNormal(rng) {
      let u = 0, v = 0;
      while (u === 0) u = rng();
      while (v === 0) v = rng();
      return Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
    }

    function quantileSorted(sorted, q) {
      if (!sorted || !sorted.length) return 0;
      if (sorted.length === 1) return sorted[0];
      const pos = (sorted.length - 1) * q;
      const b = Math.floor(pos), r = pos - b;
      return b + 1 < sorted.length ? sorted[b] + r * (sorted[b + 1] - sorted[b]) : sorted[b];
    }

    function meanArr(arr) {
      if (!arr || !arr.length) return 0;
      let s = 0;
      for (let i = 0; i < arr.length; i++) s += arr[i];
      return s / arr.length;
    }

    function placeTooltip(tipEl, canvas, clientX, clientY) {
      const wrap = canvas.parentElement.getBoundingClientRect();
      const x = clientX - wrap.left, y = clientY - wrap.top;
      tipEl.style.display = "block";
      const tw = tipEl.offsetWidth || 210, th = tipEl.offsetHeight || 90;
      let left = x + 14;
      if (left + tw > wrap.width - 8) left = Math.max(8, x - tw - 14);
      let top = Math.max(8, Math.min(wrap.height - th - 8, y - th * 0.4));
      tipEl.style.left = Math.round(left) + "px";
      tipEl.style.top = Math.round(top) + "px";
    }

    function attachCanvasHover(canvas, tipEl, onHover) {
      if (!canvas) return;
      canvas.addEventListener("mousemove", e => onHover(e, canvas, tipEl));
      canvas.addEventListener("mouseleave", () => {
        tipEl.style.display = "none";
        onHover(null, canvas, tipEl);
      });
    }

    function downloadCsv(filename, headers, rows) {
      const esc = v => {
        const s = v === null || v === undefined ? "" : String(v);
        return /[",\\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
      };
      const lines = [headers.map(esc).join(",")];
      for (const r of rows) lines.push(r.map(esc).join(","));
      const blob = new Blob([lines.join("\\n")], { type: "text/csv;charset=utf-8;" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url; a.download = filename; a.click();
      URL.revokeObjectURL(url);
    }

    function initSharedControls() {
      const langSwitch = document.getElementById("langSwitch");
      if (langSwitch) {
        langSwitch.querySelectorAll("button[data-lang]").forEach(btn => {
          btn.addEventListener("click", () => {
            const next = btn.dataset.lang === "zh-CN" ? "zh-CN" : "en-UK";
            if (currentLang === next) return;
            currentLang = next;
            try { localStorage.setItem(LANG_STORAGE_KEY, currentLang); } catch (_) {}
            applyStaticI18n();
            if (typeof onThemeOrLangChange === "function") onThemeOrLangChange();
          });
        });
      }
      const themeBtn = document.getElementById("btnThemeToggle");
      if (themeBtn) {
        themeBtn.addEventListener("click", () => {
          applyTheme(document.documentElement.dataset.theme === "dark" ? "light" : "dark");
        });
      }
      const jump = document.getElementById("chapterJump");
      if (jump) {
        jump.addEventListener("change", () => {
          const slug = jump.value;
          const isHub = jump.dataset.isHub === "1";
          const prefix = isHub ? "./" : "../";
          window.location.href = slug ? (prefix + slug + "/") : (isHub ? "./" : "../");
        });
      }
      // Top-layer accessible popovers
      const pop = document.getElementById("infoPopover");
      const supportsPop = typeof HTMLElement !== "undefined" && typeof HTMLElement.prototype.showPopover === "function";
      let activeBtn = null;
      if (pop) {
        document.querySelectorAll(".info-btn[data-info-key]").forEach(btn => {
          btn.addEventListener("click", e => {
            e.preventDefault(); e.stopPropagation();
            const isOpen = supportsPop ? pop.matches(":popover-open") : pop.classList.contains("open");
            if (isOpen && activeBtn === btn) {
              if (supportsPop) pop.hidePopover(); else pop.classList.remove("open");
              btn.setAttribute("aria-expanded", "false"); activeBtn = null; return;
            }
            document.querySelectorAll(".info-btn").forEach(b => b.setAttribute("aria-expanded", "false"));
            pop.innerHTML = t(btn.dataset.infoKey);
            activeBtn = btn;
            if (supportsPop) { if (!pop.matches(":popover-open")) pop.showPopover(); }
            else pop.classList.add("open");
            const a = btn.getBoundingClientRect();
            const pw = Math.min(330, window.innerWidth - 24);
            const left = Math.max(12, Math.min(window.innerWidth - pw - 12, a.left - pw * 0.4));
            const top = (a.bottom + 140 > window.innerHeight) ? Math.max(12, a.top - 120) : a.bottom + 8;
            pop.style.left = Math.round(left) + "px"; pop.style.top = Math.round(top) + "px";
            btn.setAttribute("aria-expanded", "true");
          });
        });
        if (!supportsPop) {
          document.addEventListener("click", e => {
            if (pop.classList.contains("open") && !pop.contains(e.target) && !e.target.closest(".info-btn")) {
              pop.classList.remove("open");
              document.querySelectorAll(".info-btn").forEach(b => b.setAttribute("aria-expanded", "false"));
            }
          });
        }
      }
    }
"""


def build_header_html(slug: str, show_csv: bool = True) -> str:
    is_hub = (slug == "")
    home_href = "../" if is_hub else "../../"
    suite_href = "./" if is_hub else "../"
    current = next(x for x in CHAPTER_NAV if x[0] == slug)
    options_html = []
    for s, _, _, nav_en, nav_zh, _, _ in CHAPTER_NAV:
        sel = " selected" if s == slug else ""
        options_html.append(f'<option value="{s}" data-en="{nav_en}" data-zh="{nav_zh}"{sel}>{nav_en}</option>')

    breadcrumb = (
        f'<a href="{home_href}" class="hdr-home-link">'
        f'<svg width="13" height="13" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M10 3L5 8l5 5"/></svg>'
        f'<span data-i18n="nav_home">Home</span></a>'
        f'<span class="hdr-sep" aria-hidden="true">/</span>'
    )
    if is_hub:
        breadcrumb += f'<h1 data-i18n="app_title">{current[1]}</h1>'
    else:
        breadcrumb += (
            f'<a href="{suite_href}" class="hdr-home-link" data-i18n="nav_suite">Retirement Spending</a>'
            f'<span class="hdr-sep" aria-hidden="true">/</span>'
            f'<h1 data-i18n="app_title">{current[1]}</h1>'
        )

    csv_btn = (
        '<button type="button" class="btn" id="btnExportCsv" data-i18n="btn_export_csv">Export CSV</button>'
        if show_csv else ""
    )

    return f"""  <header>
    <div class="hdr-left">
      <div class="hdr-title-row">{breadcrumb}</div>
    </div>
    <div class="hdr-right">
      <select id="chapterJump" class="chapter-jump" data-is-hub="{1 if is_hub else 0}" aria-label="Jump to chapter lab" data-i18n-aria-label="aria_jump">
        {''.join(options_html)}
      </select>
      <div class="seg-group" id="langSwitch" role="group" aria-label="Language" data-i18n-aria-label="aria_lang">
        <button type="button" class="scale-btn active" data-lang="en-UK" aria-pressed="true">EN</button>
        <button type="button" class="scale-btn" data-lang="zh-CN" aria-pressed="false">中文</button>
      </div>
      <button type="button" class="btn" id="btnThemeToggle" aria-pressed="false" data-i18n-title="theme_title" title="Toggle Dark / Light Theme">
        <svg class="icon-moon" width="13" height="13" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M13.5 9.8A5.8 5.8 0 016.2 2.5a5.8 5.8 0 107.3 7.3z"/></svg>
        <svg class="icon-sun" width="13" height="13" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" style="display:none;" aria-hidden="true"><circle cx="8" cy="8" r="3"/><path d="M8 1.5v1.5M8 13v1.5M1.5 8H3M13 8h1.5M3.4 3.4l1.1 1.1M11.5 11.5l1.1 1.1M12.6 3.4l-1.1 1.1M4.5 11.5l-1.1 1.1"/></svg>
        <span class="theme-lbl" data-i18n="theme_dark">Dark</span>
      </button>
      {csv_btn}
    </div>
  </header>"""


def render_page(
    slug: str,
    title_en: str,
    extra_css: str,
    body_html: str,
    embedded_data_js: str,
    page_i18n: dict,
    page_js: str,
    is_app_shell: bool = True,
    show_csv: bool = True,
) -> str:
    body_cls = ' class="app-shell"' if is_app_shell else ""
    out_path = os.path.join(OUT_DIR, slug, "index.html") if slug else os.path.join(OUT_DIR, "index.html")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    header = build_header_html(slug, show_csv=show_csv)
    i18n_json = dump_json_inline(page_i18n)
    html = f"""<!DOCTYPE html>
<html lang="en-GB" data-theme="light">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title_en}</title>
  <script>
    (function () {{
      try {{
        var t = localStorage.getItem("site_theme_v1");
        if (t !== "dark" && t !== "light") {{
          t = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
        }}
        document.documentElement.dataset.theme = t;
      }} catch (_) {{}}
    }})();
  </script>
  <style>{SHARED_CSS}
{extra_css}
  </style>
</head>
<body{body_cls}>
{header}
{body_html}
  <div id="infoPopover" class="info-popover" popover="auto" role="note"></div>
  <script>
{SHARED_JS_HEAD}
    const PAGE_I18N = {i18n_json};
{SHARED_JS_UTILS}
{embedded_data_js}
{page_js}
  </script>
</body>
</html>
"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Wrote {os.path.relpath(out_path, ROOT)} ({len(html)//1024} KB)")
    return out_path
