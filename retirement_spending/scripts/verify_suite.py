#!/usr/bin/env python3
"""Comprehensive offline verification: HTML/JS syntax, i18n completeness, zero external runtime dependencies, and quantitative parity with Pfau's book exhibits."""

import json
import os
import re
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DOCS_DIR = os.path.join(ROOT, "docs")

PAGES = [
    os.path.join(DOCS_DIR, "index.html"),
    os.path.join(DOCS_DIR, "retirement-spending", "index.html"),
    os.path.join(DOCS_DIR, "retirement-spending", "fixed-returns-longevity", "index.html"),
    os.path.join(DOCS_DIR, "retirement-spending", "sequence-of-returns-risk", "index.html"),
    os.path.join(DOCS_DIR, "retirement-spending", "safe-withdrawal-rates", "index.html"),
    os.path.join(DOCS_DIR, "retirement-spending", "valuations-and-savings", "index.html"),
    os.path.join(DOCS_DIR, "retirement-spending", "spending-smiles-glidepaths", "index.html"),
    os.path.join(DOCS_DIR, "retirement-spending", "variable-spending", "index.html"),
    os.path.join(DOCS_DIR, "retirement-spending", "bonds-and-buckets", "index.html"),
    os.path.join(DOCS_DIR, "retirement-spending", "funded-ratio-and-gamma", "index.html"),
]


def extract_scripts(html: str) -> list[str]:
    return re.findall(r"<script[^>]*>([\s\S]*?)</script>", html, flags=re.I)


def extract_styles(html: str) -> list[str]:
    return re.findall(r"<style[^>]*>([\s\S]*?)</style>", html, flags=re.I)


def check_page(path: str) -> list[str]:
    errors = []
    rel = os.path.relpath(path, ROOT)
    if not os.path.isfile(path):
        return [f"Missing file: {rel}"]

    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Zero external assets / runtime network requests
    if re.search(r"<script[^>]+src\s*=", html, flags=re.I):
        errors.append(f"{rel}: external <script src=...> found")
    if re.search(r'<link[^>]+rel\s*=\s*["\']stylesheet', html, flags=re.I):
        errors.append(f"{rel}: external <link rel=stylesheet> found")
    for st in extract_styles(html):
        if "@import" in st or re.search(r"https?://", st):
            errors.append(f"{rel}: external URL/@import inside <style>")

    scripts = extract_scripts(html)
    if not scripts:
        errors.append(f"{rel}: no inline <script> found")
        return errors

    for sc in scripts:
        if re.search(r"\bfetch\s*\(|XMLHttpRequest|https?://", sc):
            errors.append(f"{rel}: network call or http(s) URL inside <script>")

    # 2. JS Syntax check using Node vm.Script on every inline script
    node_syntax = """
const fs = require("fs");
const vm = require("vm");
const html = fs.readFileSync(process.argv[1], "utf8");
const re = /<script[^>]*>([\\s\\S]*?)<\\/script>/gi;
let m, idx = 0;
while ((m = re.exec(html)) !== null) {
  idx++;
  new vm.Script(m[1], { filename: process.argv[1] + "#script" + idx });
}
"""
    res = subprocess.run(["node", "-e", node_syntax, path], capture_output=True, text=True)
    if res.returncode != 0:
        errors.append(f"{rel}: JS syntax error:\n{res.stderr.strip()}")

    # 3. Complete i18n coverage check (scan <body> HTML markup + page script)
    body_start = html.find("<body")
    body_end = html.rfind("<script>")
    body_part = html[body_start:body_end] if body_start >= 0 and body_end > body_start else html
    keys_used = set(re.findall(r'data-i18n(?:-[a-z-]+)?="([^"]+)"', body_part))
    keys_used.update(re.findall(r'data-info-key="([^"]+)"', body_part))
    main_script = scripts[-1]
    if "retirement-spending" in rel:
        # Only inspect page-specific JS after PAGE_I18N to extract page calls to t("...")
        page_js_idx = main_script.find("const PAGE_I18N")
        if page_js_idx >= 0:
            for k in re.findall(r'\bt\(\s*"([a-zA-Z0-9_]+)"', main_script[page_js_idx:]):
                keys_used.add(k)
        node_i18n = r"""
const fs = require("fs");
const vm = require("vm");
const html = fs.readFileSync(process.argv[1], "utf8");
const mS = html.match(/const SHARED_I18N = (\{[\s\S]*?\n    \});/);
const mP = html.match(/const PAGE_I18N = (\{[\s\S]*?\});\r?\n/);
if (!mS || !mP) { console.error("NO_I18N_DICT", !!mS, !!mP); process.exit(2); }
const ctx = vm.createContext({});
vm.runInContext("var S = " + mS[1] + ";", ctx);
const P = JSON.parse(mP[1]);
console.log(JSON.stringify(Object.assign({}, ctx.S, P)));
"""
        r2 = subprocess.run(["node", "-e", node_i18n, path], capture_output=True, text=True)
        if r2.returncode != 0:
            errors.append(f"{rel}: failed to extract SHARED_I18N / PAGE_I18N: {r2.stderr.strip()}")
        else:
            i18n = json.loads(r2.stdout)
            for k in sorted(keys_used):
                if k not in i18n:
                    errors.append(f"{rel}: missing i18n key '{k}'")
                else:
                    if not str(i18n[k].get("en-UK", "")).strip():
                        errors.append(f"{rel}: empty en-UK for key '{k}'")
                    if not str(i18n[k].get("zh-CN", "")).strip():
                        errors.append(f"{rel}: empty zh-CN for key '{k}'")
    else:
        # Root docs/index.html check
        for k in sorted(keys_used):
            if f"{k}:" not in main_script:
                errors.append(f"{rel}: missing root I18N key '{k}'")

    print(f"CHECKED {rel}: {len(html)//1024} KB, {len(keys_used)} i18n keys verified.")
    return errors


def check_quantitative_benchmarks() -> list[str]:
    """Execute actual embedded simulation engines from generated HTML files in Node."""
    errs = []

    def run_node_on_page(slug: str, harness_js: str):
        p = os.path.join(DOCS_DIR, "retirement-spending", slug, "index.html")
        with open(p, "r", encoding="utf-8") as f:
            html = f.read()
        script = extract_scripts(html)[-1]
        # Slice out everything before `const state` or `initSharedControls` so we execute the exact embedded data + helpers without DOM
        cut_markers = ["const state =", "function updateAll(", "initSharedControls();"]
        cut_idx = len(script)
        for cm in cut_markers:
            pos = script.find(cm)
            if pos > 0:
                cut_idx = min(cut_idx, pos)
        lib_code = script[:cut_idx]
        # Provide minimal window/localStorage/navigator stubs for top-level utils
        preamble = """
const window = { matchMedia: () => ({ matches: false }), addEventListener: () => {} };
const document = { documentElement: { dataset: {} }, getElementById: () => null, querySelectorAll: () => [] };
const navigator = { language: "en-US" };
const localStorage = { getItem: () => null, setItem: () => {} };
"""
        full_code = preamble + lib_code + "\n" + harness_js
        res = subprocess.run(["node", "-"], input=full_code, capture_output=True, text=True)
        if res.returncode != 0:
            errs.append(f"Quantitative Node harness failed for {slug}:\n{res.stderr.strip()}\n{res.stdout.strip()}")
            return None
        return json.loads(res.stdout)

    # 1. Ch. 2: PMT & SOA Survival
    out2 = run_node_on_page(
        "fixed-returns-longevity",
        """
const pmt = -calcPMT(0.0133, 30, 1000000, 0, 1);
const nper = calcNPER(0.0133, -pmt, 1000000, 0, 1);
const sM = buildSurvivalCurve(MORT_DATA, { table: "soa_2017", startAge: 65, household: "male" });
const sF = buildSurvivalCurve(MORT_DATA, { table: "soa_2017", startAge: 65, household: "female" });
const sC = buildSurvivalCurve(MORT_DATA, { table: "soa_2017", startAge: 65, household: "couple" });
console.log(JSON.stringify({ pmt, nper, mMean: sM.meanAge, fMean: sF.meanAge, cMean: sC.meanAge }));
""",
    )
    assert out2 is not None, f"Ch.2 harness error: {errs}"
    if out2:
        assert abs(out2["pmt"] - 40109) < 10, f"Ch2 PMT mismatch: {out2}"
        assert abs(out2["nper"] - 30.0) < 0.05, f"Ch2 NPER mismatch: {out2}"
        assert 86.5 <= out2["mMean"] <= 89.0, f"Ch2 Male meanAge mismatch: {out2}"
        assert 88.0 <= out2["fMean"] <= 91.0, f"Ch2 Female meanAge mismatch: {out2}"
        assert 92.5 <= out2["cMean"] <= 95.5, f"Ch2 Couple meanAge mismatch: {out2}"
        print(f"QUANT PASS Ch.2: PMT=${out2['pmt']:.2f}, SOA 2017 Mean Ages M={out2['mMean']:.1f}, F={out2['fMean']:.1f}, C={out2['cMean']:.1f}")

    # 2. Ch. 4: 1966 50/50 MWR (NYU & Shiller)
    out4 = run_node_on_page(
        "safe-withdrawal-rates",
        """
const idxN66 = NYU_DATA.findIndex(r => r.Year === 1966);
const mwrNyu = computeCohortMWR(
  NYU_DATA.map(r => r.NYU_SP500_pct / 100), NYU_DATA.map(r => r.NYU_US_10Y_TBond_pct / 100), NYU_DATA.map(r => r.NYU_US_CPI_Inflation_pct / 100),
  idxN66, 30, 0.50, { timing: "start" }
);
const mwrNyuEnd = computeCohortMWR(
  NYU_DATA.map(r => r.NYU_SP500_pct / 100), NYU_DATA.map(r => r.NYU_US_10Y_TBond_pct / 100), NYU_DATA.map(r => r.NYU_US_CPI_Inflation_pct / 100),
  idxN66, 30, 0.50, { timing: "end" }
);
const idxS66 = SHILLER_DATA.findIndex(r => r.Year === 1966);
const mwrSh = computeCohortMWR(
  SHILLER_DATA.map(r => r.Shiller_SP500_TR_pct / 100), SHILLER_DATA.map(r => r.Shiller_10Y_TBond_pct / 100), SHILLER_DATA.map(r => r.Shiller_US_CPI_pct / 100),
  idxS66, 30, 0.50, { timing: "start" }
);
console.log(JSON.stringify({ mwrNyu, mwrNyuEnd, mwrSh }));
""",
    )
    if out4:
        assert abs(out4["mwrNyu"] - out4["mwrSh"]) < 0.15, f"Ch4 NYU vs Shiller 1966 MWR divergence: {out4}"
        assert abs(out4["mwrSh"] - 3.69) < 0.10, f"Ch4 Shiller 1966 SAFEMAX mismatch: {out4}"
        assert out4["mwrNyuEnd"] > out4["mwrNyu"], f"Ch4 end timing should exceed start timing: {out4}"
        print(f"QUANT PASS Ch.4: NYU 1966 Start={out4['mwrNyu']:.2f}% / End={out4['mwrNyuEnd']:.2f}%, Shiller 1966 SAFEMAX={out4['mwrSh']:.2f}%")

    # 3. Ch. 5 & 6: Markowitz QP & Zolt / 10 Ch.6 Strategies (from variable-spending page)
    out6 = run_node_on_page(
        "variable-spending",
        """
const eff = solveEfficientFrontier([0.10, 0.05], [0.20, 0.08], [[1, 0.2], [0.2, 1]], 11);
const zolt = computeZoltGlidePath(100, 0.04, 45, 0.03);
let zPk = 0, zYr = 0;
zolt.path.forEach((v, i) => { if (v > zPk) { zPk = v; zYr = i; } });
const nyuEq = NYU.map(r => r.NYU_SP500_pct / 100), nyuBd = NYU.map(r => r.NYU_US_10Y_TBond_pct / 100), nyuInf = NYU.map(r => r.NYU_US_CPI_Inflation_pct / 100);
const idx66 = NYU.findIndex(r => r.Year === 1966);
const eq66 = nyuEq.slice(idx66, idx66 + 30), bd66 = nyuBd.slice(idx66, idx66 + 30), inf66 = nyuInf.slice(idx66, idx66 + 30);
const ends = [];
for (let sid = 1; sid <= 10; sid++) {
  const res = simulateCh6Strategy(sid, 0.04, eq66, bd66, inf66, { V0: 100000, eqWeight: 0.5, horizon: 30, startAge: 65, rmdByAge: RMD_PRE });
  ends.push({ sid, s1: res.spendReal[0], s30: res.spendReal[29], end: res.endWealthReal, dsv: res.dsvPct });
}
const cal = calibrateCh3AEngine(SHILLER);
const rng = mulberry32(42);
const mcPaths = Array.from({ length: 400 }, () => simulateCh3APath(cal, 30, rng));
const payW0 = calibratePayRuleW0(8, mcPaths, 10, 15000, 30, { V0: 100000, eqWeight: 0.5, rmdByAge: RMD_PRE });
console.log(JSON.stringify({ effLen: eff.length, zReq: zolt.rReq * 100, zPk, zYr, ends, payW0: payW0 * 100 }));
""",
    )
    assert out6 is not None, f"Ch.6 harness error: {errs}"
    if out6:
        assert out6["effLen"] >= 3, f"Markowitz frontier too short: {out6['effLen']}"
        assert abs(out6["zReq"] - 6.152) < 0.05, f"Zolt rReq mismatch: {out6}"
        assert abs(out6["zPk"] - 129.0) < 1.0 and 21 <= out6["zYr"] <= 25, f"Zolt peak mismatch: {out6}"
        assert all(abs(e["s1"] - 4000) < 1e-3 for e in out6["ends"]), f"Yr1 spend != $4000: {out6['ends']}"
        assert out6["ends"][1]["end"] > 0, "Fixed % strategy should never hit zero wealth"
        assert 2.0 <= out6["payW0"] <= 8.0, f"PAY Rule w0 out of bounds: {out6['payW0']}"
        print(f"QUANT PASS Ch.6: Zolt rReq={out6['zReq']:.3f}%, Peak=${out6['zPk']:.2f} @ Yr {out6['zYr']}, PAY w0(G-K)={out6['payW0']:.2f}%")

    # 4. Ch. 7: WSJ STRIPS + TIPS Backward Induction + Ex 7.2 Bond Pricing
    out7 = run_node_on_page(
        "bonds-and-buckets",
        """
function interpCurve(knots, t) {
  if (t <= knots[0][0]) return knots[0][1];
  if (t >= knots[knots.length - 1][0]) return knots[knots.length - 1][1];
  for (let i = 0; i < knots.length - 1; i++) {
    const [x0, y0] = knots[i], [x1, y1] = knots[i + 1];
    if (t >= x0 && t <= x1) return y0 + ((t - x0) / (x1 - x0)) * (y1 - y0);
  }
  return knots[0][1];
}
// Evaluate solveLadder & bondAnalytics by slicing from script directly? Even simpler: evaluate page helper block!
console.log(JSON.stringify({ qLen: QUOTES_2017.length, cLen: CURVES.length }));
""",
    )
    # Better: extract solveLadder & bondAnalytics right out of bonds-and-buckets HTML!
    with open(os.path.join(DOCS_DIR, "retirement-spending", "bonds-and-buckets", "index.html"), "r", encoding="utf-8") as f:
        ch7_html = f.read()
    sc7 = extract_scripts(ch7_html)[-1]
    cut7 = sc7.find("function updateAll(")
    lib7 = sc7[:cut7].replace('const sel = document.getElementById("curveSel");', 'const sel = { appendChild: () => {}, value: "" };')
    lib7 = lib7.replace('const opt = document.createElement("option");', 'const opt = {};').replace('const o1 = document.createElement("option");', 'const o1 = {};')
    ch7_harness = """
const window = { matchMedia: () => ({ matches: false }), addEventListener: () => {} };
const document = { documentElement: { dataset: {} }, getElementById: () => ({ appendChild: () => {}, value: "" }), querySelectorAll: () => [], createElement: () => ({}) };
const navigator = { language: "en-US" };
const localStorage = { getItem: () => null, setItem: () => {} };
""" + lib7 + """
const lad = solveLadder("wsj2017", 40000, 30, 2.0, 1000000);
const bBase = bondAnalytics(1000, 2.0, 30, 2.0);
const bUp = bondAnalytics(1000, 2.0, 30, 1.0);
const bDn = bondAnalytics(1000, 2.0, 30, 3.0);
console.log(JSON.stringify({
  stripsTotal: lad.stripsTotal, tipsTotal: lad.tipsTotal, yr1Cash: lad.yr1TipsCash,
  stripsIrr: lad.stripsIrr, tipsIrr: lad.tipsIrr, beInf: lad.beInf,
  pctUp: ((bUp.px - bBase.px) / bBase.px) * 100,
  pctDn: ((bDn.px - bBase.px) / bBase.px) * 100,
  crossReal: crossCache.crossReal
}));
"""
    res7 = subprocess.run(["node", "-"], input=ch7_harness, capture_output=True, text=True)
    if res7.returncode != 0:
        errs.append(f"Ch.7 quantitative harness failed:\n{res7.stderr.strip()}")
    else:
        o7 = json.loads(res7.stdout)
        assert abs(o7["stripsTotal"] - 1044685) < 50, f"STRIPS cost mismatch: {o7}"
        assert abs(o7["tipsTotal"] - 1069231) < 500, f"TIPS cost mismatch: {o7}"
        assert abs(o7["yr1Cash"] - 22266) < 35, f"Yr-1 Cash mismatch: {o7}"
        assert abs(o7["pctUp"] - 25.8) < 0.25 and abs(o7["pctDn"] - (-19.6)) < 0.25, f"Bond duration mismatch: {o7}"
        print(f"QUANT PASS Ch.7: STRIPS=${o7['stripsTotal']:.0f}, TIPS=${o7['tipsTotal']:.0f}, Yr1Cash=${o7['yr1Cash']:.0f}, BE={o7['beInf']:.2f}%, 30Y +/-1% = +{o7['pctUp']:.1f}%/{o7['pctDn']:.1f}%")

    return errs


def main():
    all_errors = []
    for p in PAGES:
        all_errors.extend(check_page(p))
    all_errors.extend(check_quantitative_benchmarks())
    if all_errors:
        print("\nVERIFICATION FAILED:")
        for e in all_errors:
            print("  -", e)
        sys.exit(1)
    print("\nALL 10 HTML PAGES & QUANTITATIVE BENCHMARKS PASSED 100%.")


if __name__ == "__main__":
    main()
