#!/usr/bin/env python3
"""Build Lab 3 (Chapter 4): Bengen SAFEMAX, Trinity Study Matrix, Overlap Bias vs MC, and SWR Isoquants."""

from shared_shell import dump_json_inline, load_csv_records, render_page
from shared_sim_js import SHARED_SIM_JS


def build_ch4():
    nyu = load_csv_records("nyu_stern_1928_2025_full.csv")
    shiller = load_csv_records("shiller_us_1871_2025_annual.csv")

    body_html = """  <main class="layout">
    <aside class="sidebar" aria-label="Simulation parameters" data-i18n-aria-label="aria_sidebar">
      <div class="side-section">
        <div class="sec-head-static">
          <h2 class="sec-title" data-i18n="sec_presets">Book Exhibit Presets</h2>
          <button type="button" class="link-btn" id="btnReset" data-i18n="btn_reset">Reset</button>
        </div>
        <div class="preset-grid">
          <button type="button" class="preset-btn active" data-preset="bengen">
            <span class="p-title" data-i18n="pre_ben_t">Ex. 4.1–4.4 · Bengen 50/50</span>
            <span class="p-meta" data-i18n="pre_ben_m">10Y Treasury · Start-yr WR</span>
          </button>
          <button type="button" class="preset-btn" data-preset="trinity">
            <span class="p-title" data-i18n="pre_tri_t">Ex. 4.5 · Trinity Matrix</span>
            <span class="p-meta" data-i18n="pre_tri_m">Corp Baa Bonds · 15–40y</span>
          </button>
          <button type="button" class="preset-btn" data-preset="overlap">
            <span class="p-title" data-i18n="pre_ov_t">Ex. 4.6 · Overlap vs MC</span>
            <span class="p-meta" data-i18n="pre_ov_m">4% WR across 0–100% Eq</span>
          </button>
          <button type="button" class="preset-btn" data-preset="frontier">
            <span class="p-title" data-i18n="pre_fr_t">Ex. 4.7–4.8 · SWR Frontier</span>
            <span class="p-meta" data-i18n="pre_fr_m">10% failure isoquants</span>
          </button>
        </div>
      </div>

      <div class="side-section">
        <div class="sec-head-static"><h2 class="sec-title" data-i18n="sec_params">Simulation Parameters</h2></div>
        <div class="control-group">
          <label for="datasetSel"><span data-i18n="lbl_dataset">Dataset &amp; Bond Proxy</span></label>
          <select id="datasetSel">
            <option value="nyu_10y" selected data-i18n="ds_nyu_10y">NYU 1928–2025 · S&amp;P 500 + 10Y Treasury (Bengen)</option>
            <option value="nyu_baa" data-i18n="ds_nyu_baa">NYU 1928–2025 · S&amp;P 500 + Baa Corp (Trinity)</option>
            <option value="nyu_sc" data-i18n="ds_nyu_sc">NYU 1928–2025 · Small Cap + 10Y Treasury</option>
            <option value="shiller" data-i18n="ds_shiller">Shiller 1871–2025 · S&amp;P + 10Y Treasury</option>
          </select>
        </div>
        <div class="control-group">
          <div class="label-row">
            <label for="eqPctSlider"><span data-i18n="lbl_eq">Stock / Bond mix</span></label>
            <span class="label-hint" id="eqPctHint">50 / 50</span>
          </div>
          <input type="range" id="eqPctSlider" class="ratio-slider" min="0" max="100" step="5" value="50" />
        </div>
        <div class="control-group row-2">
          <div>
            <label for="horizonYrs"><span data-i18n="lbl_horizon">Horizon (yrs)</span></label>
            <input type="number" id="horizonYrs" value="30" min="10" max="50" step="5" />
          </div>
          <div>
            <label for="testWrPct"><span data-i18n="lbl_test_wr">Test WR (%)</span></label>
            <input type="number" id="testWrPct" value="4.0" min="2" max="10" step="0.25" />
          </div>
        </div>
        <div class="control-group row-2">
          <div>
            <label for="timingSel"><span data-i18n="lbl_timing">Withdrawal timing</span></label>
            <select id="timingSel">
              <option value="start" selected data-i18n="opt_start">Start of year</option>
              <option value="end" data-i18n="opt_end">End of year</option>
            </select>
          </div>
          <div>
            <label for="failTolPct"><span data-i18n="lbl_fail_tol">Allowed failure (%)</span></label>
            <select id="failTolPct">
              <option value="1">1%</option>
              <option value="5">5%</option>
              <option value="10" selected>10%</option>
              <option value="20">20%</option>
              <option value="25">25%</option>
            </select>
          </div>
        </div>
        <div class="control-group row-2">
          <div>
            <label for="feeBps"><span data-i18n="lbl_fee">Annual fee (bps)</span></label>
            <input type="number" id="feeBps" value="0" min="0" max="200" step="10" />
          </div>
          <div>
            <label for="cmaHaircut"><span data-i18n="lbl_cma">MC Return Regime</span></label>
            <select id="cmaHaircut">
              <option value="hist" selected data-i18n="cma_hist">Historical Averages</option>
              <option value="low" data-i18n="cma_low">Low-Yield AR(1) (2.45% Y10)</option>
            </select>
          </div>
        </div>
      </div>
    </aside>

    <section class="workspace" aria-label="Simulation outputs" data-i18n-aria-label="aria_workspace">
      <div class="results-shell">
        <div class="tabs-bar">
          <div class="tab-strip" role="tablist">
            <button type="button" class="tab-btn active" role="tab" aria-selected="true" data-tab="safemax" data-i18n="tab_safemax">Bengen SAFEMAX (Ex. 4.1–4.4)</button>
            <button type="button" class="tab-btn" role="tab" aria-selected="false" data-tab="trinity" data-i18n="tab_trinity">Trinity Matrix (Ex. 4.5)</button>
            <button type="button" class="tab-btn" role="tab" aria-selected="false" data-tab="overlap" data-i18n="tab_overlap">Overlap Bias vs. MC (Ex. 4.6)</button>
            <button type="button" class="tab-btn" role="tab" aria-selected="false" data-tab="frontier" data-i18n="tab_frontier">SWR Isoquants &amp; Frontier (Ex. 4.7–4.8)</button>
          </div>
          <div class="tabs-controls">
            <button type="button" class="btn btn-accent" id="btnRerun" data-i18n="btn_rerun">&#8635; Re-run MC</button>
          </div>
        </div>
        <div class="results-body">
          <div id="paneSafemax" class="tab-pane">
            <div class="kpis kpis-4 kpis-flush-top">
              <div class="kpi"><div class="kpi-label" data-i18n="k4_safemax">Historical SAFEMAX</div><div class="kpi-val pos" id="k4Safemax">—</div><div class="kpi-sub" id="k4SafemaxSub">—</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="k4_succ">Test WR Success Rate</div><div class="kpi-val" id="k4Succ">—</div><div class="kpi-sub" id="k4SuccSub">—</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="k4_med_mwr">Median Cohort MWR</div><div class="kpi-val" id="k4MedMwr">—</div><div class="kpi-sub" id="k4MedMwrSub">—</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="k4_med_end">Median End Wealth Mult.</div><div class="kpi-val" id="k4MedEnd">—</div><div class="kpi-sub" id="k4MedEndSub">—</div></div>
            </div>
            <div class="panel-block">
              <div class="legend"><strong data-i18n="ttl_ex41">Ex. 4.1–4.2: Maximum Sustainable Withdrawal Rate by Retirement Year</strong><span class="subhead" id="ex41Sub"></span></div>
              <div class="chart-wrap"><canvas id="mwrHistCanvas" height="240"></canvas><div class="tooltip" id="mwrHistTip"></div></div>
            </div>
            <div class="split-grid">
              <div class="grid-cell">
                <div class="legend"><strong data-i18n="ttl_ex43">Ex. 4.3: SAFEMAX vs. Stock Allocation</strong></div>
                <div class="chart-wrap"><canvas id="safemaxAllocCanvas" height="225"></canvas><div class="tooltip" id="safemaxAllocTip"></div></div>
              </div>
              <div class="grid-cell">
                <div class="legend"><strong data-i18n="ttl_ex44">Ex. 4.4: Median &amp; P10 Real End Wealth vs. Stock %</strong></div>
                <div class="chart-wrap"><canvas id="wealthAllocCanvas" height="225"></canvas><div class="tooltip" id="wealthAllocTip"></div></div>
              </div>
            </div>
          </div>

          <div id="paneTrinity" class="tab-pane" style="display:none;">
            <div class="panel-block">
              <div class="card-title">
                <h3 class="sec-title" data-i18n="ttl_ex45">Ex. 4.5: Portfolio Success Rates (%) &amp; Median Terminal Wealth</h3>
                <div class="seg-group" id="trinitySourceCtl" role="group">
                  <button type="button" class="scale-btn active" data-src="hist" aria-pressed="true" data-i18n="src_hist">Historical Rolling</button>
                  <button type="button" class="scale-btn" data-src="mc" aria-pressed="false" data-i18n="src_mc">Monte Carlo (5,000 runs)</button>
                </div>
              </div>
              <div class="table-container" style="max-height:none;">
                <table><thead id="triHead"></thead><tbody id="triBody"></tbody></table>
              </div>
            </div>
          </div>

          <div id="paneOverlap" class="tab-pane" style="display:none;">
            <div class="split-grid">
              <div class="grid-cell">
                <div class="legend">
                  <strong data-i18n="ttl_ex46">Ex. 4.6: Portfolio Success Rates (Rolling Historical vs. MC)</strong>
                  <div class="legend-items">
                    <div class="legend-item"><span class="swatch" style="background:var(--port);"></span><span data-i18n="leg_roll">Rolling Hist.</span></div>
                    <div class="legend-item"><span class="swatch" style="background:var(--accent);"></span><span data-i18n="leg_boot">Bootstrap MC</span></div>
                    <div class="legend-item"><span class="swatch" style="background:var(--danger);"></span><span data-i18n="leg_ar1">Low-Yield AR(1) MC</span></div>
                  </div>
                </div>
                <div class="chart-wrap"><canvas id="overlapCompCanvas" height="260"></canvas><div class="tooltip" id="overlapCompTip"></div></div>
              </div>
              <div class="grid-cell">
                <div class="legend"><strong data-i18n="ttl_ov_weights">Overlapping Cohort Bias: Appearances per Historical Year</strong></div>
                <div class="chart-wrap"><canvas id="ovWeightsCanvas" height="260"></canvas><div class="tooltip" id="ovWeightsTip"></div></div>
              </div>
            </div>
          </div>

          <div id="paneFrontier" class="tab-pane" style="display:none;">
            <div class="kpis kpis-3 kpis-flush-top">
              <div class="kpi"><div class="kpi-label" data-i18n="kf_max_wr">Max Sustainable WR at Target Failure</div><div class="kpi-val pos" id="kfMaxWr">—</div><div class="kpi-sub" id="kfMaxSub">—</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="kf_opt_eq">Optimal Stock Allocation</div><div class="kpi-val" id="kfOptEq">—</div><div class="kpi-sub" id="kfOptSub">—</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="kf_near">Near-Optimal Range (-0.1% WR)</div><div class="kpi-val" id="kfNear">—</div><div class="kpi-sub" data-i18n="kf_near_sub">Allocations within 10 bps of peak</div></div>
            </div>
            <div class="split-grid">
              <div class="grid-cell">
                <div class="legend"><strong data-i18n="ttl_ex47">Ex. 4.7: SWR Isoquants &amp; Efficient Frontier (Std Dev vs Real Return)</strong></div>
                <div class="chart-wrap"><canvas id="isoCanvas" height="265"></canvas><div class="tooltip" id="isoTip"></div></div>
              </div>
              <div class="grid-cell">
                <div class="card-title"><h3 class="sec-title" data-i18n="ttl_ex48">Ex. 4.8: Optimal WR &amp; Stock Range by Horizon &amp; Failure %</h3></div>
                <div class="table-container" style="max-height:265px;">
                  <table><thead id="ex48Head"></thead><tbody id="ex48Body"></tbody></table>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </main>"""

    page_i18n = {
        "page_title": {"en-UK": "Safe Withdrawal Rates & Trinity Study", "zh-CN": "安全提取率与 Trinity 研究"},
        "app_title": {"en-UK": "Safe Withdrawal Rates & Trinity Study", "zh-CN": "安全提取率与 Trinity 研究"},
        "sec_presets": {"en-UK": "Book Exhibit Presets", "zh-CN": "全书图表预设"},
        "pre_ben_t": {"en-UK": "Ex. 4.1–4.4 · Bengen 50/50", "zh-CN": "图4.1–4.4 · Bengen 50/50"},
        "pre_ben_m": {"en-UK": "10Y Treasury · Start-yr WR", "zh-CN": "10年美债 · 年初提取"},
        "pre_tri_t": {"en-UK": "Ex. 4.5 · Trinity Matrix", "zh-CN": "图4.5 · Trinity 矩阵"},
        "pre_tri_m": {"en-UK": "Corp Baa Bonds · 15–40y", "zh-CN": "Baa企业债 · 15–40年"},
        "pre_ov_t": {"en-UK": "Ex. 4.6 · Overlap vs MC", "zh-CN": "图4.6 · 重叠偏差对比"},
        "pre_ov_m": {"en-UK": "4% WR across 0–100% Eq", "zh-CN": "全股票比例 4% 提取对比"},
        "pre_fr_t": {"en-UK": "Ex. 4.7–4.8 · SWR Frontier", "zh-CN": "图4.7–4.8 · 有效前沿"},
        "pre_fr_m": {"en-UK": "10% failure isoquants", "zh-CN": "10% 失败率等提取率线"},
        "sec_params": {"en-UK": "Simulation Parameters", "zh-CN": "模拟参数"},
        "lbl_dataset": {"en-UK": "Dataset & Bond Proxy", "zh-CN": "数据集与债券基准"},
        "ds_nyu_10y": {"en-UK": "NYU 1928–2025 · S&P 500 + 10Y Treasury (Bengen)", "zh-CN": "NYU 1928–2025 · 标普500 + 10年美债 (Bengen)"},
        "ds_nyu_baa": {"en-UK": "NYU 1928–2025 · S&P 500 + Baa Corp (Trinity)", "zh-CN": "NYU 1928–2025 · 标普500 + Baa企业债 (Trinity)"},
        "ds_nyu_sc": {"en-UK": "NYU 1928–2025 · Small Cap + 10Y Treasury", "zh-CN": "NYU 1928–2025 · 美国小盘股 + 10年美债"},
        "ds_shiller": {"en-UK": "Shiller 1871–2025 · S&P + 10Y Treasury", "zh-CN": "Shiller 1871–2025 · 标普 + 10年美债"},
        "lbl_eq": {"en-UK": "Stock / Bond mix", "zh-CN": "股票 / 债券比例"},
        "lbl_horizon": {"en-UK": "Horizon (yrs)", "zh-CN": "退休年数"},
        "lbl_test_wr": {"en-UK": "Test WR (%)", "zh-CN": "测试提取率 (%)"},
        "lbl_timing": {"en-UK": "Withdrawal timing", "zh-CN": "提取时点"},
        "opt_start": {"en-UK": "Start of year", "zh-CN": "年初提取"},
        "opt_end": {"en-UK": "End of year", "zh-CN": "年末提取"},
        "lbl_fail_tol": {"en-UK": "Allowed failure (%)", "zh-CN": "容许失败率 (%)"},
        "lbl_fee": {"en-UK": "Annual fee (bps)", "zh-CN": "年费率 (bps)"},
        "lbl_cma": {"en-UK": "MC Return Regime", "zh-CN": "蒙特卡洛收益机制"},
        "cma_hist": {"en-UK": "Historical Averages", "zh-CN": "历史均值分布"},
        "cma_low": {"en-UK": "Low-Yield AR(1) (2.45% Y10)", "zh-CN": "低利率 AR(1) 模型"},
        "btn_rerun": {"en-UK": "↻ Re-run MC", "zh-CN": "↻ 重新抽样"},
        "tab_safemax": {"en-UK": "Bengen SAFEMAX (Ex. 4.1–4.4)", "zh-CN": "Bengen SAFEMAX (4.1–4.4)"},
        "tab_trinity": {"en-UK": "Trinity Matrix (Ex. 4.5)", "zh-CN": "Trinity 成功率矩阵 (4.5)"},
        "tab_overlap": {"en-UK": "Overlap Bias vs. MC (Ex. 4.6)", "zh-CN": "历史重叠偏差 vs MC (4.6)"},
        "tab_frontier": {"en-UK": "SWR Isoquants & Frontier (Ex. 4.7–4.8)", "zh-CN": "等提取率线与有效前沿 (4.7–4.8)"},
        "k4_safemax": {"en-UK": "Historical SAFEMAX", "zh-CN": "历史最差 SAFEMAX"},
        "k4_succ": {"en-UK": "Test WR Success Rate", "zh-CN": "测试提取率存活率"},
        "k4_med_mwr": {"en-UK": "Median Cohort MWR", "zh-CN": "历史中位 MWR"},
        "k4_med_end": {"en-UK": "Median End Wealth Mult.", "zh-CN": "中位期末实际财富倍数"},
        "ttl_ex41": {"en-UK": "Ex. 4.1–4.2: Maximum Sustainable Withdrawal Rate by Retirement Year", "zh-CN": "图 4.1–4.2：各历史退休起点最大可持续提取率"},
        "ttl_ex43": {"en-UK": "Ex. 4.3: SAFEMAX vs. Stock Allocation", "zh-CN": "图 4.3：SAFEMAX 随股票配置比例变化"},
        "ttl_ex44": {"en-UK": "Ex. 4.4: Median & P10 Real End Wealth vs. Stock %", "zh-CN": "图 4.4：期末中位与10%分位实际财富倍数"},
        "ttl_ex45": {"en-UK": "Ex. 4.5: Portfolio Success Rates (%) & Median Terminal Wealth", "zh-CN": "图 4.5：不同提取率、年限与股债配置下的成功率 (%)"},
        "src_hist": {"en-UK": "Historical Rolling", "zh-CN": "历史滚动回测"},
        "src_mc": {"en-UK": "Monte Carlo (5,000 runs)", "zh-CN": "蒙特卡洛 (5,000次)"},
        "ttl_ex46": {"en-UK": "Ex. 4.6: Portfolio Success Rates (Rolling Historical vs. MC)", "zh-CN": "图 4.6：成功率对比（历史滚动 vs 随机抽样 vs AR(1)）"},
        "leg_roll": {"en-UK": "Rolling Hist.", "zh-CN": "历史滚动"},
        "leg_boot": {"en-UK": "Bootstrap MC", "zh-CN": "历史有放回抽样 MC"},
        "leg_ar1": {"en-UK": "Low-Yield AR(1) MC", "zh-CN": "低利率 AR(1) MC"},
        "ttl_ov_weights": {"en-UK": "Overlapping Cohort Bias: Appearances per Historical Year", "zh-CN": "历史滚动窗口重叠偏差：各年份被采样次数"},
        "kf_max_wr": {"en-UK": "Max Sustainable WR at Target Failure", "zh-CN": "目标失败率下的最高可持续提取率"},
        "kf_opt_eq": {"en-UK": "Optimal Stock Allocation", "zh-CN": "最优股票配置比例"},
        "kf_near": {"en-UK": "Near-Optimal Range (-0.1% WR)", "zh-CN": "近优配置区间 (-0.1% 提取率)"},
        "kf_near_sub": {"en-UK": "Allocations within 10 bps of peak", "zh-CN": "距峰值不超过 10 bps 的股票区间"},
        "ttl_ex47": {"en-UK": "Ex. 4.7: SWR Isoquants & Efficient Frontier (Std Dev vs Real Return)", "zh-CN": "图 4.7：有效前沿与等安全提取率曲线 (波动率 vs 实际收益)"},
        "ttl_ex48": {"en-UK": "Ex. 4.8: Optimal WR & Stock Range by Horizon & Failure %", "zh-CN": "图 4.8：各退休年限与容许失败率下的最优配置总表"},
    }

    embedded = f"    const NYU_DATA = {dump_json_inline(nyu)};\n    const SHILLER_DATA = {dump_json_inline(shiller)};\n"
    page_js = SHARED_SIM_JS + r"""
    const state = { tab: "safemax", triSource: "hist", seed: 202604, lastExport: [] };
    const CH3A_CAL = calibrateCh3AEngine(SHILLER_DATA);

    function getDataset() {
      const sel = document.getElementById("datasetSel").value;
      const rows = sel === "shiller" ? SHILLER_DATA : NYU_DATA;
      const years = rows.map(r => r.Year);
      const eq = rows.map(r => (sel === "shiller" ? r.Shiller_SP500_TR_pct : sel === "nyu_sc" ? r.NYU_US_Small_Cap_pct : r.NYU_SP500_pct) / 100);
      const bd = rows.map(r => (sel === "shiller" ? r.Shiller_10Y_TBond_pct : sel === "nyu_baa" ? r.NYU_US_Baa_Corp_Bond_pct : r.NYU_US_10Y_TBond_pct) / 100);
      const inf = rows.map(r => (sel === "shiller" ? r.Shiller_US_CPI_pct : r.NYU_US_CPI_Inflation_pct) / 100);
      return { years, eq, bd, inf };
    }

    function simPathEnd(eqArr, bdArr, infArr, startIdx, horizon, eqW, wr, timing, feeDec) {
      let bal = 1.0;
      for (let t = 0; t < horizon; t++) {
        const idx = startIdx + t;
        const rr = (1 + (eqW * eqArr[idx] + (1 - eqW) * bdArr[idx] - feeDec)) / (1 + infArr[idx]) - 1;
        if (timing === "start") {
          bal = Math.max(0, bal - wr) * (1 + rr);
          if (bal <= 0) return 0;
        } else {
          bal = Math.max(0, bal * (1 + rr) - wr);
          if (bal <= 0) return 0;
        }
      }
      return bal;
    }

    function updateAll() {
      const d = getDataset();
      const eqW = (parseFloat(document.getElementById("eqPctSlider").value) || 50) / 100;
      document.getElementById("eqPctHint").textContent = `${Math.round(eqW * 100)} / ${Math.round((1 - eqW) * 100)}`;
      document.getElementById("eqPctSlider").style.setProperty("--pct", Math.round(eqW * 100) + "%");
      const H = Math.max(10, Math.min(50, parseInt(document.getElementById("horizonYrs").value, 10) || 30));
      const wr = (parseFloat(document.getElementById("testWrPct").value) || 4.0) / 100;
      const timing = document.getElementById("timingSel").value;
      const failTol = parseFloat(document.getElementById("failTolPct").value) || 10;
      const feeDec = (parseFloat(document.getElementById("feeBps").value) || 0) / 10000;
      const isLowYield = document.getElementById("cmaHaircut").value === "low";
      const isZh = currentLang === "zh-CN";

      // Rolling cohorts
      const nCoh = Math.max(1, d.years.length - H + 1);
      const cohMwrs = [], cohEnds = [];
      for (let i = 0; i < nCoh; i++) {
        const mwr = computeCohortMWR(d.eq, d.bd, d.inf, i, H, eqW, { timing, feeDec });
        const end = simPathEnd(d.eq, d.bd, d.inf, i, H, eqW, wr, timing, feeDec);
        cohMwrs.push({ yr: d.years[i], mwr, end });
        cohEnds.push(end);
      }
      const worstC = cohMwrs.reduce((a, b) => b.mwr < a.mwr ? b : a, cohMwrs[0]);
      const succCnt = cohMwrs.filter(c => c.end > 0).length;
      const sortedM = cohMwrs.map(c => c.mwr).sort((a, b) => a - b);
      const sortedE = cohEnds.slice().sort((a, b) => a - b);

      document.getElementById("k4Safemax").textContent = worstC.mwr.toFixed(2) + "%";
      document.getElementById("k4SafemaxSub").textContent = `${isZh ? "最差起点" : "Worst cohort"}: ${worstC.yr}`;
      document.getElementById("k4Succ").textContent = `${((succCnt / cohMwrs.length) * 100).toFixed(1)}%`;
      document.getElementById("k4SuccSub").textContent = `${succCnt}/${cohMwrs.length} @ ${(wr * 100).toFixed(2)}% WR`;
      document.getElementById("k4MedMwr").textContent = quantileSorted(sortedM, 0.5).toFixed(2) + "%";
      document.getElementById("k4MedMwrSub").textContent = `P10: ${quantileSorted(sortedM, 0.1).toFixed(2)}% · P90: ${quantileSorted(sortedM, 0.9).toFixed(2)}%`;
      document.getElementById("k4MedEnd").textContent = quantileSorted(sortedE, 0.5).toFixed(2) + "×";
      document.getElementById("k4MedEndSub").textContent = `P10: ${quantileSorted(sortedE, 0.1).toFixed(2)}× · P90: ${quantileSorted(sortedE, 0.9).toFixed(2)}×`;
      document.getElementById("ex41Sub").textContent = `${d.years[0]}–${d.years[nCoh - 1]} (${nCoh} ${isZh ? "个" : ""}${H}${isZh ? "年期" : "-yr cohorts"})`;

      state.lastExport = cohMwrs.map(c => [c.yr, c.mwr.toFixed(2), c.end.toFixed(4)]);

      if (state.tab === "safemax") {
        drawSafemaxCharts(d, cohMwrs, worstC, H, wr, timing, feeDec);
      } else if (state.tab === "trinity") {
        renderTrinityMatrix(d, timing, feeDec, isLowYield);
      } else if (state.tab === "overlap") {
        drawOverlapTab(d, H, wr, timing, feeDec);
      } else {
        drawFrontierTab(d, H, failTol, timing, feeDec, isLowYield);
      }
    }

    function drawSafemaxCharts(d, cohMwrs, worstC, H, wr, timing, feeDec) {
      const sc1 = setupCanvas(document.getElementById("mwrHistCanvas"));
      if (sc1) {
        const { ctx, w, h } = sc1; const C = getThemeColors(); ctx.clearRect(0, 0, w, h);
        const pad = { l: 44, r: 16, t: 18, b: 28 }, cw = w - pad.l - pad.r, ch = h - pad.t - pad.b;
        const maxM = Math.max(10, ...cohMwrs.map(c => c.mwr)) * 1.05;
        const ticks = computeNiceLinearTicks(0, maxM, 4); const topM = ticks[ticks.length - 1];
        const mapX = i => pad.l + (i / Math.max(1, cohMwrs.length - 1)) * cw;
        const mapY = v => pad.t + ch - (v / topM) * ch;
        ctx.strokeStyle = C.grid; ctx.font = CANVAS_FONT; ctx.textAlign = "right"; ctx.fillStyle = C.muted;
        ticks.forEach(v => { const y = mapY(v); ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(w - pad.r, y); ctx.stroke(); ctx.fillText(v + "%", pad.l - 5, y + 4); });
        // 4% reference line
        ctx.strokeStyle = C.danger; ctx.setLineDash([4, 3]); ctx.beginPath(); ctx.moveTo(pad.l, mapY(4)); ctx.lineTo(w - pad.r, mapY(4)); ctx.stroke(); ctx.setLineDash([]);
        ctx.beginPath(); ctx.strokeStyle = C.port; ctx.lineWidth = 2.2;
        cohMwrs.forEach((c, i) => { const x = mapX(i), y = mapY(c.mwr); if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); });
        ctx.stroke();
        const wIdx = cohMwrs.indexOf(worstC);
        ctx.beginPath(); ctx.arc(mapX(wIdx), mapY(worstC.mwr), 5, 0, Math.PI * 2); ctx.fillStyle = C.danger; ctx.fill();
        ctx.fillStyle = C.muted; ctx.textAlign = "center";
        cohMwrs.forEach((c, i) => { if (c.yr % 15 === 0 || i === 0 || i === cohMwrs.length - 1) ctx.fillText(String(c.yr), mapX(i), h - 8); });
      }

      const allocs = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100];
      const safemaxes = [], medEnds = [], p10Ends = [];
      const nCoh = Math.max(1, d.years.length - H + 1);
      allocs.forEach(a => {
        const wEq = a / 100;
        let minM = 999; const ends = [];
        for (let i = 0; i < nCoh; i++) {
          const m = computeCohortMWR(d.eq, d.bd, d.inf, i, H, wEq, { timing, feeDec });
          if (m < minM) minM = m;
          ends.push(simPathEnd(d.eq, d.bd, d.inf, i, H, wEq, wr, timing, feeDec));
        }
        ends.sort((x, y) => x - y);
        safemaxes.push(minM); medEnds.push(quantileSorted(ends, 0.5)); p10Ends.push(quantileSorted(ends, 0.1));
      });

      const sc2 = setupCanvas(document.getElementById("safemaxAllocCanvas"));
      if (sc2) {
        const { ctx, w, h } = sc2; const C = getThemeColors(); ctx.clearRect(0, 0, w, h);
        const pad = { l: 42, r: 16, t: 18, b: 28 }, cw = w - pad.l - pad.r, ch = h - pad.t - pad.b;
        const maxS = Math.max(5, ...safemaxes) * 1.1;
        const ticks = computeNiceLinearTicks(0, maxS, 4); const topS = ticks[ticks.length - 1];
        const mapX = i => pad.l + (i / (allocs.length - 1)) * cw;
        const mapY = v => pad.t + ch - (v / topS) * ch;
        ctx.strokeStyle = C.grid; ctx.font = CANVAS_FONT; ctx.textAlign = "right"; ctx.fillStyle = C.muted;
        ticks.forEach(v => { const y = mapY(v); ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(w - pad.r, y); ctx.stroke(); ctx.fillText(v.toFixed(1) + "%", pad.l - 5, y + 4); });
        ctx.beginPath(); ctx.strokeStyle = C.accent; ctx.lineWidth = 2.4;
        safemaxes.forEach((v, i) => { const x = mapX(i), y = mapY(v); if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); });
        ctx.stroke();
        allocs.forEach((a, i) => {
          ctx.beginPath(); ctx.arc(mapX(i), mapY(safemaxes[i]), 3.5, 0, Math.PI * 2); ctx.fillStyle = C.accent; ctx.fill();
          if (i % 2 === 0) { ctx.fillStyle = C.muted; ctx.textAlign = "center"; ctx.fillText(a + "%", mapX(i), h - 8); }
        });
      }

      const sc3 = setupCanvas(document.getElementById("wealthAllocCanvas"));
      if (sc3) {
        const { ctx, w, h } = sc3; const C = getThemeColors(); ctx.clearRect(0, 0, w, h);
        const pad = { l: 42, r: 16, t: 18, b: 28 }, cw = w - pad.l - pad.r, ch = h - pad.t - pad.b;
        const maxE = Math.max(2, ...medEnds) * 1.1;
        const ticks = computeNiceLinearTicks(0, maxE, 4); const topE = ticks[ticks.length - 1];
        const mapX = i => pad.l + (i / (allocs.length - 1)) * cw;
        const mapY = v => pad.t + ch - (v / topE) * ch;
        ctx.strokeStyle = C.grid; ctx.font = CANVAS_FONT; ctx.textAlign = "right"; ctx.fillStyle = C.muted;
        ticks.forEach(v => { const y = mapY(v); ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(w - pad.r, y); ctx.stroke(); ctx.fillText(v.toFixed(1) + "×", pad.l - 5, y + 4); });
        ctx.beginPath(); ctx.strokeStyle = C.success; ctx.lineWidth = 2.4;
        medEnds.forEach((v, i) => { const x = mapX(i), y = mapY(v); if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); });
        ctx.stroke();
        ctx.beginPath(); ctx.strokeStyle = C.danger; ctx.lineWidth = 1.6; ctx.setLineDash([4, 3]);
        p10Ends.forEach((v, i) => { const x = mapX(i), y = mapY(v); if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); });
        ctx.stroke(); ctx.setLineDash([]);
        allocs.forEach((a, i) => { if (i % 2 === 0) { ctx.fillStyle = C.muted; ctx.textAlign = "center"; ctx.fillText(a + "%", mapX(i), h - 8); } });
      }
    }

    function renderTrinityMatrix(d, timing, feeDec, isLowYield) {
      const horizons = [15, 20, 25, 30, 35, 40];
      const allocs = [100, 75, 50, 25, 0];
      const wrs = [3, 4, 5, 6, 7, 8];
      const isZh = currentLang === "zh-CN";
      document.getElementById("triHead").innerHTML = `<tr><th>${isZh ? "股票/债券 · 初始WR" : "Allocation · WR"}</th>${horizons.map(h => `<th>${h} ${isZh ? "年" : "Yrs"}</th>`).join("")}</tr>`;
      const Nmc = 3000;
      const rng = mulberry32(state.seed);
      let mcPaths = null;
      if (state.triSource === "mc") {
        mcPaths = [];
        for (let r = 0; r < Nmc; r++) {
          if (isLowYield) mcPaths.push(simulateCh3APath(CH3A_CAL, 40, rng));
          else {
            const eq = new Float64Array(40), bd = new Float64Array(40), inf = new Float64Array(40);
            for (let t = 0; t < 40; t++) { const k = Math.floor(rng() * d.years.length); eq[t] = d.eq[k]; bd[t] = d.bd[k]; inf[t] = d.inf[k]; }
            mcPaths.push({ eq, bd, inf });
          }
        }
      }

      const rowsHtml = [];
      allocs.forEach(a => {
        const wEq = a / 100;
        rowsHtml.push(`<tr style="background:var(--panel-alt);"><td colspan="${horizons.length + 1}"><strong>${a}% ${isZh ? "股票" : "Stocks"} / ${100 - a}% ${isZh ? "债券" : "Bonds"}</strong></td></tr>`);
        wrs.forEach(wrPct => {
          const wr = wrPct / 100;
          const cells = horizons.map(H => {
            let succ = 0, tot = 0;
            if (state.triSource === "hist") {
              const nCoh = Math.max(1, d.years.length - H + 1);
              tot = nCoh;
              for (let i = 0; i < nCoh; i++) if (simPathEnd(d.eq, d.bd, d.inf, i, H, wEq, wr, timing, feeDec) > 0) succ++;
            } else {
              tot = Nmc;
              for (let i = 0; i < Nmc; i++) if (simPathEnd(mcPaths[i].eq, mcPaths[i].bd, mcPaths[i].inf, 0, H, wEq, wr, timing, feeDec) > 0) succ++;
            }
            const pct = (succ / tot) * 100;
            const cls = pct >= 95 ? "pos" : (pct < 70 ? "neg" : "");
            return `<td class="hm-cell ${cls}">${Math.round(pct)}%</td>`;
          }).join("");
          rowsHtml.push(`<tr><td style="padding-left:20px;">${wrPct}% WR</td>${cells}</tr>`);
        });
      });
      document.getElementById("triBody").innerHTML = rowsHtml.join("");
    }

    function drawOverlapTab(d, H, wr, timing, feeDec) {
      const allocs = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100];
      const nCoh = Math.max(1, d.years.length - H + 1);
      const Nmc = 4000;
      const rng = mulberry32(state.seed);
      const bootPaths = [], ar1Paths = [];
      for (let r = 0; r < Nmc; r++) {
        const eq = new Float64Array(H), bd = new Float64Array(H), inf = new Float64Array(H);
        for (let t = 0; t < H; t++) { const k = Math.floor(rng() * d.years.length); eq[t] = d.eq[k]; bd[t] = d.bd[k]; inf[t] = d.inf[k]; }
        bootPaths.push({ eq, bd, inf });
        ar1Paths.push(simulateCh3APath(CH3A_CAL, H, rng));
      }
      const rollSucc = [], bootSucc = [], ar1Succ = [];
      allocs.forEach(a => {
        const wEq = a / 100;
        let sR = 0, sB = 0, sA = 0;
        for (let i = 0; i < nCoh; i++) if (simPathEnd(d.eq, d.bd, d.inf, i, H, wEq, wr, timing, feeDec) > 0) sR++;
        for (let i = 0; i < Nmc; i++) {
          if (simPathEnd(bootPaths[i].eq, bootPaths[i].bd, bootPaths[i].inf, 0, H, wEq, wr, timing, feeDec) > 0) sB++;
          if (simPathEnd(ar1Paths[i].eq, ar1Paths[i].bd, ar1Paths[i].inf, 0, H, wEq, wr, timing, feeDec) > 0) sA++;
        }
        rollSucc.push((sR / nCoh) * 100); bootSucc.push((sB / Nmc) * 100); ar1Succ.push((sA / Nmc) * 100);
      });

      const sc1 = setupCanvas(document.getElementById("overlapCompCanvas"));
      if (sc1) {
        const { ctx, w, h } = sc1; const C = getThemeColors(); ctx.clearRect(0, 0, w, h);
        const pad = { l: 44, r: 16, t: 18, b: 28 }, cw = w - pad.l - pad.r, ch = h - pad.t - pad.b;
        const mapX = i => pad.l + (i / (allocs.length - 1)) * cw;
        const mapY = v => pad.t + ch - (v / 100) * ch;
        ctx.strokeStyle = C.grid; ctx.font = CANVAS_FONT; ctx.textAlign = "right"; ctx.fillStyle = C.muted;
        [0, 25, 50, 75, 100].forEach(v => { const y = mapY(v); ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(w - pad.r, y); ctx.stroke(); ctx.fillText(v + "%", pad.l - 5, y + 4); });
        [[rollSucc, C.port], [bootSucc, C.accent], [ar1Succ, C.danger]].forEach(([arr, col]) => {
          ctx.beginPath(); ctx.strokeStyle = col; ctx.lineWidth = 2.4;
          arr.forEach((v, i) => { const x = mapX(i), y = mapY(v); if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); });
          ctx.stroke();
        });
        allocs.forEach((a, i) => { if (i % 2 === 0) { ctx.fillStyle = C.muted; ctx.textAlign = "center"; ctx.fillText(a + "%", mapX(i), h - 8); } });
      }

      // Appearance counts per year in rolling H-year cohorts
      const counts = new Array(d.years.length).fill(0);
      for (let i = 0; i < nCoh; i++) for (let t = 0; t < H; t++) counts[i + t]++;
      const sc2 = setupCanvas(document.getElementById("ovWeightsCanvas"));
      if (sc2) {
        const { ctx, w, h } = sc2; const C = getThemeColors(); ctx.clearRect(0, 0, w, h);
        const pad = { l: 42, r: 16, t: 18, b: 28 }, cw = w - pad.l - pad.r, ch = h - pad.t - pad.b;
        const mapX = i => pad.l + ((i + 0.5) / counts.length) * cw;
        const mapY = v => pad.t + ch - (v / H) * ch;
        const bw = Math.max(1.5, (cw / counts.length) * 0.8);
        ctx.strokeStyle = C.grid; ctx.font = CANVAS_FONT; ctx.textAlign = "right"; ctx.fillStyle = C.muted;
        [0, Math.round(H / 2), H].forEach(v => { const y = mapY(v); ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(w - pad.r, y); ctx.stroke(); ctx.fillText(v + "×", pad.l - 5, y + 4); });
        counts.forEach((c, i) => {
          ctx.fillStyle = c >= H ? C.port : C.accent;
          const x = mapX(i), y = mapY(c);
          ctx.fillRect(x - bw / 2, y, bw, pad.t + ch - y);
        });
        ctx.fillStyle = C.muted; ctx.textAlign = "center";
        d.years.forEach((y, i) => { if (y % 20 === 0 || i === 0 || i === d.years.length - 1) ctx.fillText(String(y), mapX(i), h - 8); });
      }
    }

    function drawFrontierTab(d, H, failTol, timing, feeDec, isLowYield) {
      const N = 2500, rng = mulberry32(state.seed);
      // Real arithmetic means, SDs, correlation from dataset
      const eqReals = d.years.map((_, i) => ((1 + d.eq[i] - feeDec) / (1 + d.inf[i]) - 1));
      const bdReals = d.years.map((_, i) => ((1 + d.bd[i] - feeDec) / (1 + d.inf[i]) - 1));
      let muE = meanArr(eqReals), muB = meanArr(bdReals);
      if (isLowYield) { muE -= 0.02; muB -= 0.015; }
      const sdOf = a => { const m = meanArr(a); return Math.sqrt(meanArr(a.map(x => (x - m) ** 2))); };
      const sdE = sdOf(eqReals), sdB = sdOf(bdReals);
      let cov = 0; for (let i = 0; i < eqReals.length; i++) cov += (eqReals[i] - meanArr(eqReals)) * (bdReals[i] - meanArr(bdReals));
      const rho = (cov / eqReals.length) / (sdE * sdB || 1);

      // Simulate i.i.d. lognormal grid or asset paths for frontier 0..100% stocks
      const Z = Array.from({ length: N }, () => Array.from({ length: H }, () => randNormal(rng)));
      const wrAt = (mu, sd, hor, qFail) => {
        const mwrs = new Float64Array(N);
        const s2 = sd * sd, mLog = Math.log(1 + mu) - 0.5 * Math.log(1 + s2 / ((1 + mu) ** 2));
        const sLog = Math.sqrt(Math.log(1 + s2 / ((1 + mu) ** 2)));
        for (let i = 0; i < N; i++) {
          let denom = 0, cumP = 1;
          for (let t = 0; t < hor; t++) {
            if (timing === "start") denom += 1 / cumP;
            const r = Math.exp(mLog + sLog * Z[i][t]) - 1;
            cumP *= (1 + r);
            if (timing === "end") denom += 1 / cumP;
          }
          mwrs[i] = (1 / denom) * 100;
        }
        mwrs.sort();
        return quantileSorted(mwrs, qFail / 100);
      };

      const pts = [];
      for (let a = 0; a <= 100; a += 5) {
        const wE = a / 100, wB = 1 - wE;
        const mu = wE * muE + wB * muB;
        const sd = Math.sqrt((wE * sdE) ** 2 + (wB * sdB) ** 2 + 2 * wE * wB * sdE * sdB * rho);
        const wr = wrAt(mu, sd, H, failTol);
        pts.push({ eqPct: a, mu: mu * 100, sd: sd * 100, wr });
      }
      const best = pts.reduce((a, b) => b.wr > a.wr ? b : a, pts[0]);
      const near = pts.filter(p => p.wr >= best.wr - 0.10);
      const minEq = near[0].eqPct, maxEq = near[near.length - 1].eqPct;

      const isZh = currentLang === "zh-CN";
      document.getElementById("kfMaxWr").textContent = best.wr.toFixed(2) + "%";
      document.getElementById("kfMaxSub").textContent = `${H}y · ${failTol}% ${isZh ? "容许失败" : "fail"}`;
      document.getElementById("kfOptEq").textContent = `${best.eqPct}% / ${100 - best.eqPct}%`;
      document.getElementById("kfOptSub").textContent = `μ=${best.mu.toFixed(1)}% · σ=${best.sd.toFixed(1)}%`;
      document.getElementById("kfNear").textContent = `${minEq}% – ${maxEq}%`;

      // Draw Isoquant & Frontier chart (Ex. 4.7)
      const sc1 = setupCanvas(document.getElementById("isoCanvas"));
      if (sc1) {
        const { ctx, w, h } = sc1; const C = getThemeColors(); ctx.clearRect(0, 0, w, h);
        const pad = { l: 46, r: 16, t: 18, b: 30 }, cw = w - pad.l - pad.r, ch = h - pad.t - pad.b;
        const maxSd = Math.max(22, sdE * 100 + 2), minMu = 0, maxMu = Math.max(10, muE * 100 + 1.5);
        const mapX = sd => pad.l + (sd / maxSd) * cw;
        const mapY = mu => pad.t + ch - ((mu - minMu) / (maxMu - minMu)) * ch;
        ctx.strokeStyle = C.grid; ctx.font = CANVAS_FONT; ctx.textAlign = "right"; ctx.fillStyle = C.muted;
        computeNiceLinearTicks(minMu, maxMu, 4).forEach(v => { const y = mapY(v); ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(w - pad.r, y); ctx.stroke(); ctx.fillText(v.toFixed(0) + "%", pad.l - 5, y + 4); });

        // Plot SWR isoquants for 3%, 4%, 5%, 6% by finding required arithmetic mean mu at each std dev sd
        [3, 4, 5, 6].forEach(targetW => {
          ctx.beginPath(); ctx.strokeStyle = C.muted; ctx.globalAlpha = 0.45; ctx.lineWidth = 1.2; ctx.setLineDash([4, 3]);
          for (let s = 2; s <= maxSd; s += 2) {
            let lo = -0.02, hi = 0.16;
            for (let it = 0; it < 14; it++) {
              const mid = 0.5 * (lo + hi);
              if (wrAt(mid, s / 100, H, failTol) < targetW) lo = mid; else hi = mid;
            }
            const x = mapX(s), y = mapY(0.5 * (lo + hi) * 100);
            if (s === 2) ctx.moveTo(x, y); else ctx.lineTo(x, y);
          }
          ctx.stroke(); ctx.setLineDash([]); ctx.globalAlpha = 1.0;
        });

        // Efficient frontier curve
        ctx.beginPath(); ctx.strokeStyle = C.accent; ctx.lineWidth = 2.4;
        pts.forEach((p, i) => { const x = mapX(p.sd), y = mapY(p.mu); if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); });
        ctx.stroke();
        // Highlight optimal tangency point
        ctx.beginPath(); ctx.arc(mapX(best.sd), mapY(best.mu), 6, 0, Math.PI * 2); ctx.fillStyle = C.success; ctx.fill();
        ctx.fillStyle = C.muted; ctx.textAlign = "center";
        [0, 5, 10, 15, 20].filter(v => v <= maxSd).forEach(s => ctx.fillText("σ=" + s + "%", mapX(s), h - 8));
      }

      // Ex. 4.8 summary table across horizons x fail tolerances
      const hors = [20, 25, 30, 35, 40];
      const fails = [5, 10, 20];
      document.getElementById("ex48Head").innerHTML = `<tr><th>${isZh ? "年限 \\ 失败率" : "Horizon \\ Fail"}</th>${fails.map(f => `<th>${f}% ${isZh ? "失败 (WR/股%)" : "Fail (WR / Eq%)"}</th>`).join("")}</tr>`;
      document.getElementById("ex48Body").innerHTML = hors.map(hr => {
        const tds = fails.map(fl => {
          let bWr = 0, bEq = 0;
          for (let a = 0; a <= 100; a += 10) {
            const wE = a / 100, mu = wE * muE + (1 - wE) * muB;
            const sd = Math.sqrt((wE * sdE) ** 2 + ((1 - wE) * sdB) ** 2 + 2 * wE * (1 - wE) * sdE * sdB * rho);
            const val = wrAt(mu, sd, Math.min(H, hr), fl);
            if (val > bWr) { bWr = val; bEq = a; }
          }
          return `<td><strong>${bWr.toFixed(2)}%</strong> <span class="muted">(${bEq}%)</span></td>`;
        }).join("");
        return `<tr><td><strong>${hr} ${isZh ? "年" : "yrs"}</strong></td>${tds}</tr>`;
      }).join("");
    }

    function applyPreset(name) {
      document.querySelectorAll(".preset-btn").forEach(b => b.classList.toggle("active", b.dataset.preset === name));
      if (name === "bengen") {
        document.getElementById("datasetSel").value = "nyu_10y"; document.getElementById("eqPctSlider").value = "50";
        document.querySelector('[data-tab="safemax"]').click();
      } else if (name === "trinity") {
        document.getElementById("datasetSel").value = "nyu_baa";
        document.querySelector('[data-tab="trinity"]').click();
      } else if (name === "overlap") {
        document.getElementById("datasetSel").value = "nyu_10y"; document.getElementById("testWrPct").value = "4.0";
        document.querySelector('[data-tab="overlap"]').click();
      } else if (name === "frontier") {
        document.getElementById("failTolPct").value = "10";
        document.querySelector('[data-tab="frontier"]').click();
      }
      updateAll();
    }

    function onThemeOrLangChange() { updateAll(); }

    document.querySelectorAll(".tab-btn").forEach(b => {
      b.addEventListener("click", () => {
        state.tab = b.dataset.tab;
        document.querySelectorAll(".tab-btn").forEach(x => { x.classList.toggle("active", x === b); x.setAttribute("aria-selected", x === b ? "true" : "false"); });
        ["paneSafemax", "paneTrinity", "paneOverlap", "paneFrontier"].forEach(id => {
          document.getElementById(id).style.display = id.toLowerCase().includes(state.tab) ? "block" : "none";
        });
        updateAll();
      });
    });
    document.querySelectorAll("#trinitySourceCtl button").forEach(b => {
      b.addEventListener("click", () => {
        state.triSource = b.dataset.src;
        document.querySelectorAll("#trinitySourceCtl button").forEach(x => setBtnActive(x, x === b));
        updateAll();
      });
    });
    document.getElementById("btnRerun").addEventListener("click", () => { state.seed = (state.seed + 7919) >>> 0; updateAll(); });
    document.querySelectorAll(".preset-btn").forEach(b => b.addEventListener("click", () => applyPreset(b.dataset.preset)));
    document.getElementById("btnReset").addEventListener("click", () => applyPreset("bengen"));
    document.getElementById("btnExportCsv").addEventListener("click", () => {
      downloadCsv("pfau_ch4_safemax.csv", ["Start_Year", "MWR_pct", "End_Wealth_Multiple"], state.lastExport);
    });
    ["datasetSel", "eqPctSlider", "horizonYrs", "testWrPct", "timingSel", "failTolPct", "feeBps", "cmaHaircut"].forEach(id => {
      const el = document.getElementById(id);
      el.addEventListener("input", updateAll);
      el.addEventListener("change", updateAll);
    });
    window.addEventListener("resize", () => requestAnimationFrame(updateAll));

    initSharedControls();
    applyStaticI18n();
    updateAll();
"""

    render_page(
        slug="safe-withdrawal-rates",
        title_en="Safe Withdrawal Rates & Trinity Study",
        extra_css=".hm-grid { font-size: 11.5px; }",
        body_html=body_html,
        embedded_data_js=embedded,
        page_i18n=page_i18n,
        page_js=page_js,
    )


if __name__ == "__main__":
    build_ch4()
