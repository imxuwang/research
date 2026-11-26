#!/usr/bin/env python3
"""Build Lab 2 (Chapter 3): Sequence-of-Returns Risk, 60-Year Lifecycle Attribution, and Reverse-Engineered IRRs."""

from shared_shell import dump_json_inline, load_csv_records, render_page
from shared_sim_js import SHARED_SIM_JS


def build_ch3():
    shiller = load_csv_records("shiller_us_1871_2025_annual.csv")
    nyu = load_csv_records("nyu_stern_1928_2025_full.csv")

    body_html = """  <main class="layout">
    <aside class="sidebar" aria-label="Simulation parameters" data-i18n-aria-label="aria_sidebar">
      <div class="side-section">
        <div class="sec-head-static">
          <h2 class="sec-title" data-i18n="sec_presets">Book Exhibit Presets</h2>
          <button type="button" class="link-btn" id="btnReset" data-i18n="btn_reset">Reset</button>
        </div>
        <div class="preset-grid">
          <button type="button" class="preset-btn active" data-preset="ex32">
            <span class="p-title" data-i18n="pre_32_t">Ex. 3.2 · 6.3% Sequence</span>
            <span class="p-meta" data-i18n="pre_32_m">50/50 · 6.3% WR vs 5.1% avg</span>
          </button>
          <button type="button" class="preset-btn" data-preset="ex34">
            <span class="p-title" data-i18n="pre_34_t">Ex. 3.4–3.6 · Adam 60Y</span>
            <span class="p-meta" data-i18n="pre_34_m">30y save 15% + 30y ret</span>
          </button>
          <button type="button" class="preset-btn" data-preset="ex38">
            <span class="p-title" data-i18n="pre_38_t">Ex. 3.8 · MWR vs CAGR</span>
            <span class="p-meta" data-i18n="pre_38_m">1966 vs 1982 cohorts</span>
          </button>
          <button type="button" class="preset-btn" data-preset="ex39">
            <span class="p-title" data-i18n="pre_39_t">Ex. 3.9 · Reverse IRR</span>
            <span class="p-meta" data-i18n="pre_39_m">Lump / Accum / Retiree MC</span>
          </button>
        </div>
      </div>

      <div class="side-section">
        <div class="sec-head-static"><h2 class="sec-title" data-i18n="sec_params">Simulation Parameters</h2></div>
        <div class="control-group">
          <label for="datasetSelect"><span data-i18n="lbl_dataset">Historical dataset</span></label>
          <select id="datasetSelect">
            <option value="nyu" selected data-i18n="ds_nyu">NYU Stern US SBBI Proxy (1928–2025)</option>
            <option value="shiller" data-i18n="ds_shiller">Robert Shiller Long-Run US (1871–2025)</option>
          </select>
        </div>
        <div class="control-group">
          <div class="label-row">
            <label for="eqPctSlider"><span data-i18n="lbl_eq">Stock / Bond mix</span></label>
            <span class="label-hint" id="eqPctHint">50 / 50</span>
          </div>
          <input type="range" id="eqPctSlider" class="ratio-slider" min="0" max="100" step="10" value="50" />
        </div>
        <div class="control-group row-2">
          <div>
            <label for="initWrPct"><span data-i18n="lbl_init_wr">Initial WR (%)</span></label>
            <input type="number" id="initWrPct" value="6.3" min="2" max="12" step="0.1" />
          </div>
          <div>
            <label for="retYrs"><span data-i18n="lbl_ret_yrs">Retirement (yrs)</span></label>
            <input type="number" id="retYrs" value="30" min="15" max="45" step="5" />
          </div>
        </div>
        <div class="control-group row-2">
          <div>
            <label for="workYrs"><span data-i18n="lbl_work_yrs">Career yrs (Adam)</span></label>
            <input type="number" id="workYrs" value="30" min="10" max="40" step="5" />
          </div>
          <div>
            <label for="saveRatePct"><span data-i18n="lbl_save_rate">Savings rate (%)</span></label>
            <input type="number" id="saveRatePct" value="15" min="5" max="40" step="1" />
          </div>
        </div>
        <div class="control-group row-2">
          <div>
            <label for="focusCohort"><span data-i18n="lbl_focus_yr">Highlight cohort</span></label>
            <select id="focusCohort"></select>
          </div>
          <div>
            <label for="timingSel"><span data-i18n="lbl_timing">Withdraw timing</span></label>
            <select id="timingSel">
              <option value="start" selected data-i18n="opt_start">Start of year</option>
              <option value="end" data-i18n="opt_end">End of year</option>
            </select>
          </div>
        </div>
        <div class="control-group">
          <label><span data-i18n="lbl_mc_mode">Monte Carlo engine (10,000 runs)</span></label>
          <div class="seg-ctl" id="mcModeCtl" role="group">
            <button type="button" data-v="bootstrap" class="active" aria-pressed="true" data-i18n="mc_boot">Historical Bootstrap</button>
            <button type="button" data-v="ch3a" aria-pressed="false" data-i18n="mc_ch3a">Ch. 3A Low-Yield AR(1)</button>
          </div>
        </div>
      </div>
    </aside>

    <section class="workspace" aria-label="Simulation outputs" data-i18n-aria-label="aria_workspace">
      <div class="results-shell">
        <div class="tabs-bar">
          <div class="tab-strip" role="tablist">
            <button type="button" class="tab-btn active" role="tab" aria-selected="true" data-tab="glide" data-i18n="tab_glide">Glide Paths &amp; WR Spirals (Ex. 3.1–3.3)</button>
            <button type="button" class="tab-btn" role="tab" aria-selected="false" data-tab="lifetime" data-i18n="tab_life">Lifetime Sequence Risk (Ex. 3.4–3.6)</button>
            <button type="button" class="tab-btn" role="tab" aria-selected="false" data-tab="reverse" data-i18n="tab_rev">Inv. vs. Sequence &amp; Reverse IRR (Ex. 3.7–3.9)</button>
          </div>
          <div class="tabs-controls">
            <button type="button" class="btn btn-accent" id="btnRerun" data-i18n="btn_rerun">&#8635; Re-run MC</button>
          </div>
        </div>

        <div class="results-body">
          <div id="paneGlide" class="tab-pane">
            <div class="kpis kpis-4 kpis-flush-top">
              <div class="kpi"><div class="kpi-label" data-i18n="k3_surv">Historical Survival</div><div class="kpi-val" id="k3Surv">—</div><div class="kpi-sub" id="k3SurvSub">—</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="k3_best_end">Best Terminal Real Wealth</div><div class="kpi-val pos" id="k3Best">—</div><div class="kpi-sub" id="k3BestSub">—</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="k3_worst_end">Earliest Depletion Cohort</div><div class="kpi-val neg" id="k3Worst">—</div><div class="kpi-sub" id="k3WorstSub">—</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="k3_focus">Highlighted Cohort</div><div class="kpi-val" id="k3Focus">—</div><div class="kpi-sub" id="k3FocusSub">—</div></div>
            </div>
            <div class="split-grid">
              <div class="grid-cell">
                <div class="legend">
                  <strong data-i18n="ttl_ex32">Ex. 3.1–3.2: Rolling Real Wealth ($100 start)</strong>
                  <div class="legend-items">
                    <div class="legend-item"><span class="swatch" style="background:var(--port);"></span><span data-i18n="leg_focus">Highlighted</span></div>
                    <div class="legend-item"><span class="swatch" style="background:var(--accent);"></span><span data-i18n="leg_fixed_avg">Fixed Mean CAGR</span></div>
                  </div>
                </div>
                <div class="chart-wrap"><canvas id="glideCanvas" height="270"></canvas><div class="tooltip" id="glideTip"></div></div>
              </div>
              <div class="grid-cell">
                <div class="legend">
                  <strong data-i18n="ttl_ex33">Ex. 3.3: Current Withdrawal Rate ($W_t / V_t$, capped 30%)</strong>
                  <div class="legend-items">
                    <div class="legend-item"><span class="swatch" style="background:var(--danger);"></span><span data-i18n="leg_10pct">10% Tipping Point</span></div>
                  </div>
                </div>
                <div class="chart-wrap"><canvas id="wrCanvas" height="270"></canvas><div class="tooltip" id="wrTip"></div></div>
              </div>
            </div>
          </div>

          <div id="paneLifetime" class="tab-pane" style="display:none;">
            <div class="kpis kpis-4 kpis-flush-top">
              <div class="kpi"><div class="kpi-label" data-i18n="k_acc_med">Median Career Multiple</div><div class="kpi-val" id="kAccMed">—</div><div class="kpi-sub" id="kAccSub">—</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="k_acc_rng">Min / Max Accumulation</div><div class="kpi-val" id="kAccRng">—</div><div class="kpi-sub" id="kAccRngSub">—</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="k_mwr_rng">Retiree MWR Range</div><div class="kpi-val" id="kMwrRng">—</div><div class="kpi-sub" id="kMwrRngSub">—</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="k_yr1_r2">Yr 1 Retirement Return R²</div><div class="kpi-val" id="kYr1R2">—</div><div class="kpi-sub" data-i18n="k_yr1_sub">Share of MWR explained by Yr 1</div></div>
            </div>
            <div class="split-grid">
              <div class="grid-cell">
                <div class="legend"><strong data-i18n="ttl_ex34">Ex. 3.4 &amp; 3.5: Career Wealth Multiple vs. Sustainable WR</strong></div>
                <div class="chart-wrap"><canvas id="adamCanvas" height="250"></canvas><div class="tooltip" id="adamTip"></div></div>
              </div>
              <div class="grid-cell">
                <div class="legend"><strong data-i18n="ttl_ex36">Ex. 3.6: Lifetime Sequence-Risk R² Attribution (Years 1–60)</strong></div>
                <div class="chart-wrap"><canvas id="r2Canvas" height="250"></canvas><div class="tooltip" id="r2Tip"></div></div>
              </div>
            </div>
          </div>

          <div id="paneReverse" class="tab-pane" style="display:none;">
            <div class="split-grid">
              <div class="grid-cell">
                <div class="legend">
                  <strong data-i18n="ttl_ex38">Ex. 3.7–3.8: Actual MWR vs. Fixed-30Y-CAGR Implied MWR</strong>
                  <div class="legend-items">
                    <div class="legend-item"><span class="swatch" style="background:var(--port);"></span><span data-i18n="leg_act_mwr">Actual Sequence MWR</span></div>
                    <div class="legend-item"><span class="swatch" style="background:var(--accent);"></span><span data-i18n="leg_cagr_mwr">Fixed-CAGR Implied MWR</span></div>
                  </div>
                </div>
                <div class="chart-wrap"><canvas id="seqGapCanvas" height="255"></canvas><div class="tooltip" id="seqGapTip"></div></div>
              </div>
              <div class="grid-cell">
                <div class="legend"><strong data-i18n="ttl_ex39_c">Ex. 3.9: 10,000-Run Compounded Real IRR Distributions</strong></div>
                <div class="chart-wrap"><canvas id="irrCanvas" height="255"></canvas><div class="tooltip" id="irrTip"></div></div>
              </div>
            </div>
            <div class="panel-block">
              <div class="card-title"><h3 class="sec-title" data-i18n="ttl_ex39_t">Ex. 3.9: Reverse-Engineered Fixed Real Return Assumptions (%/yr)</h3></div>
              <div class="table-container" style="max-height:none;">
                <table><thead id="irrHead"></thead><tbody id="irrBody"></tbody></table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </main>"""

    page_i18n = {
        "page_title": {"en-UK": "Sequence-of-Returns Risk", "zh-CN": "收益率顺序风险"},
        "app_title": {"en-UK": "Sequence-of-Returns Risk", "zh-CN": "收益率顺序风险"},
        "sec_presets": {"en-UK": "Book Exhibit Presets", "zh-CN": "全书图表预设"},
        "pre_32_t": {"en-UK": "Ex. 3.2 · 6.3% Sequence", "zh-CN": "图3.2 · 6.3% 顺序演示"},
        "pre_32_m": {"en-UK": "50/50 · 6.3% WR vs 5.1% avg", "zh-CN": "50/50 组合 6.3% 提取"},
        "pre_34_t": {"en-UK": "Ex. 3.4–3.6 · Adam 60Y", "zh-CN": "图3.4–3.6 · 60年全周期"},
        "pre_34_m": {"en-UK": "30y save 15% + 30y ret", "zh-CN": "工作30年+退休30年"},
        "pre_38_t": {"en-UK": "Ex. 3.8 · MWR vs CAGR", "zh-CN": "图3.8 · 实际 vs 均率"},
        "pre_38_m": {"en-UK": "1966 vs 1982 cohorts", "zh-CN": "1966 对比 1982 年起点"},
        "pre_39_t": {"en-UK": "Ex. 3.9 · Reverse IRR", "zh-CN": "图3.9 · 反推固定收益"},
        "pre_39_m": {"en-UK": "Lump / Accum / Retiree MC", "zh-CN": "整存/定投/退休分布"},
        "sec_params": {"en-UK": "Simulation Parameters", "zh-CN": "模拟参数"},
        "lbl_dataset": {"en-UK": "Historical dataset", "zh-CN": "历史数据集"},
        "ds_nyu": {"en-UK": "NYU Stern US SBBI Proxy (1928–2025)", "zh-CN": "NYU Stern 美国数据 (1928–2025)"},
        "ds_shiller": {"en-UK": "Robert Shiller Long-Run US (1871–2025)", "zh-CN": "Robert Shiller 长周期数据 (1871–2025)"},
        "lbl_eq": {"en-UK": "Stock / Bond mix", "zh-CN": "股票 / 债券比例"},
        "lbl_init_wr": {"en-UK": "Initial WR (%)", "zh-CN": "初始提取率 (%)"},
        "lbl_ret_yrs": {"en-UK": "Retirement (yrs)", "zh-CN": "退休年数"},
        "lbl_work_yrs": {"en-UK": "Career yrs (Adam)", "zh-CN": "工作储蓄年数"},
        "lbl_save_rate": {"en-UK": "Savings rate (%)", "zh-CN": "年储蓄率 (%)"},
        "lbl_focus_yr": {"en-UK": "Highlight cohort", "zh-CN": "高亮退休起点年份"},
        "lbl_timing": {"en-UK": "Withdraw timing", "zh-CN": "提取时点"},
        "opt_start": {"en-UK": "Start of year", "zh-CN": "年初提取"},
        "opt_end": {"en-UK": "End of year", "zh-CN": "年末提取"},
        "lbl_mc_mode": {"en-UK": "Monte Carlo engine (10,000 runs)", "zh-CN": "蒙特卡洛引擎 (10,000次)"},
        "mc_boot": {"en-UK": "Historical Bootstrap", "zh-CN": "历史有放回抽样"},
        "mc_ch3a": {"en-UK": "Ch. 3A Low-Yield AR(1)", "zh-CN": "第3章附录低利率 AR(1)"},
        "btn_rerun": {"en-UK": "↻ Re-run MC", "zh-CN": "↻ 重新抽样"},
        "tab_glide": {"en-UK": "Glide Paths & WR Spirals (Ex. 3.1–3.3)", "zh-CN": "资产路径与提取率螺旋 (3.1–3.3)"},
        "tab_life": {"en-UK": "Lifetime Sequence Risk (Ex. 3.4–3.6)", "zh-CN": "全生命周期顺序风险 (3.4–3.6)"},
        "tab_rev": {"en-UK": "Inv. vs. Sequence & Reverse IRR (Ex. 3.7–3.9)", "zh-CN": "投资 vs 顺序风险与反推收益 (3.7–3.9)"},
        "k3_surv": {"en-UK": "Historical Survival", "zh-CN": "历史窗口存活率"},
        "k3_best_end": {"en-UK": "Best Terminal Real Wealth", "zh-CN": "最佳期末实际资产"},
        "k3_worst_end": {"en-UK": "Earliest Depletion Cohort", "zh-CN": "最早耗尽年份"},
        "k3_focus": {"en-UK": "Highlighted Cohort", "zh-CN": "高亮起点结局"},
        "ttl_ex32": {"en-UK": "Ex. 3.1–3.2: Rolling Real Wealth ($100 start)", "zh-CN": "图 3.1–3.2：滚动实际资产轨迹（$100 起点）"},
        "leg_focus": {"en-UK": "Highlighted", "zh-CN": "高亮年份"},
        "leg_fixed_avg": {"en-UK": "Fixed Mean CAGR", "zh-CN": "固定平均复利基准"},
        "ttl_ex33": {"en-UK": "Ex. 3.3: Current Withdrawal Rate (Wt / Vt, capped 30%)", "zh-CN": "图 3.3：动态当前提取率 (Wt / Vt，上限30%)"},
        "leg_10pct": {"en-UK": "10% Danger Threshold", "zh-CN": "10% 危险阈值"},
        "k_acc_med": {"en-UK": "Median Career Multiple", "zh-CN": "工作期中位积累倍数"},
        "k_acc_rng": {"en-UK": "Min / Max Accumulation", "zh-CN": "最小 / 最大积累倍数"},
        "k_mwr_rng": {"en-UK": "Retiree MWR Range", "zh-CN": "退休期 MWR 极值范围"},
        "k_yr1_r2": {"en-UK": "Yr 1 Retirement Return R²", "zh-CN": "退休首年收益 R² 贡献"},
        "k_yr1_sub": {"en-UK": "Share of MWR explained by Yr 1", "zh-CN": "首年收益对总MWR方差的解释力"},
        "ttl_ex34": {"en-UK": "Ex. 3.4 & 3.5: Career Wealth Multiple vs. Sustainable WR", "zh-CN": "图 3.4 & 3.5：工作期积累倍数 vs 退休期可持续提取率"},
        "ttl_ex36": {"en-UK": "Ex. 3.6: Lifetime Sequence-Risk R² Attribution (Years 1–60)", "zh-CN": "图 3.6：全生命周期各年收益对结果的方差解释度 (R²)"},
        "ttl_ex38": {"en-UK": "Ex. 3.7–3.8: Actual MWR vs. Fixed-30Y-CAGR Implied MWR", "zh-CN": "图 3.7–3.8：实际顺序 MWR vs 固定平均复利 MWR"},
        "leg_act_mwr": {"en-UK": "Actual Sequence MWR", "zh-CN": "实际市场顺序 MWR"},
        "leg_cagr_mwr": {"en-UK": "Fixed-CAGR Implied MWR", "zh-CN": "同期固定年化收益 MWR"},
        "ttl_ex39_c": {"en-UK": "Ex. 3.9: 10,000-Run Compounded Real IRR Distributions", "zh-CN": "图 3.9：10,000 次蒙特卡洛实际内部收益率分布"},
        "ttl_ex39_t": {"en-UK": "Ex. 3.9: Reverse-Engineered Fixed Real Return Assumptions (%/yr)", "zh-CN": "图 3.9：反推确定性表格应使用的保守实际收益率假设 (%/年)"},
    }

    embedded = f"    const SHILLER_DATA = {dump_json_inline(shiller)};\n    const NYU_DATA = {dump_json_inline(nyu)};\n"
    page_js = SHARED_SIM_JS + r"""
    const state = { tab: "glide", mcMode: "bootstrap", seed: 202603, lastExport: [], cachedLife: null, cachedRev: null };
    const CH3A_CAL = calibrateCh3AEngine(SHILLER_DATA);

    function getSeriesData() {
      const ds = document.getElementById("datasetSelect").value;
      const rows = ds === "nyu" ? NYU_DATA : SHILLER_DATA;
      const years = rows.map(r => r.Year);
      const eq = rows.map(r => (ds === "nyu" ? r.NYU_SP500_pct : r.Shiller_SP500_TR_pct) / 100);
      const bd = rows.map(r => (ds === "nyu" ? r.NYU_US_10Y_TBond_pct : r.Shiller_10Y_TBond_pct) / 100);
      const inf = rows.map(r => (ds === "nyu" ? r.NYU_US_CPI_Inflation_pct : r.Shiller_US_CPI_pct) / 100);
      return { ds, years, eq, bd, inf };
    }

    function syncCohortSelect(years, retYrs) {
      const sel = document.getElementById("focusCohort");
      const maxIdx = years.length - retYrs;
      const cur = parseInt(sel.value, 10) || 1966;
      sel.innerHTML = "";
      for (let i = 0; i <= maxIdx; i++) {
        const y = years[i];
        const o = document.createElement("option");
        o.value = y; o.textContent = y;
        if (y === cur) o.selected = true;
        sel.appendChild(o);
      }
      if (!sel.value && maxIdx >= 0) sel.value = years[Math.min(maxIdx, 0)];
    }

    function computeAll() {
      const s = getSeriesData();
      const eqW = (parseFloat(document.getElementById("eqPctSlider").value) || 50) / 100;
      document.getElementById("eqPctHint").textContent = `${Math.round(eqW * 100)} / ${Math.round((1 - eqW) * 100)}`;
      document.getElementById("eqPctSlider").style.setProperty("--pct", Math.round(eqW * 100) + "%");
      const wr = (parseFloat(document.getElementById("initWrPct").value) || 6.3) / 100;
      const retYrs = Math.max(10, Math.min(45, parseInt(document.getElementById("retYrs").value, 10) || 30));
      const workYrs = Math.max(10, Math.min(40, parseInt(document.getElementById("workYrs").value, 10) || 30));
      const saveRate = (parseFloat(document.getElementById("saveRatePct").value) || 15) / 100;
      const timing = document.getElementById("timingSel").value;
      syncCohortSelect(s.years, retYrs);
      const focusYr = parseInt(document.getElementById("focusCohort").value, 10) || 1966;

      // Mean real compounded return for fixed benchmark
      let prodR = 1;
      for (let i = 0; i < s.years.length; i++) {
        const rp = eqW * s.eq[i] + (1 - eqW) * s.bd[i];
        prodR *= (1 + rp) / (1 + s.inf[i]);
      }
      const avgRealCagr = Math.pow(prodR, 1 / s.years.length) - 1;

      // Rolling retirement cohorts
      const cohorts = [];
      const nCoh = s.years.length - retYrs + 1;
      for (let i = 0; i < nCoh; i++) {
        let bal = 100.0;
        const wPath = [100.0], wrPath = [];
        let depletedYr = null;
        let realProd = 1.0;
        for (let t = 0; t < retYrs; t++) {
          const rp = eqW * s.eq[i + t] + (1 - eqW) * s.bd[i + t];
          const rr = (1 + rp) / (1 + s.inf[i + t]) - 1;
          realProd *= (1 + rr);
          const wAmt = wr * 100.0;
          if (bal <= 0) {
            wrPath.push(30);
          } else if (timing === "start") {
            wrPath.push(Math.min(30, (wAmt / bal) * 100));
            bal = Math.max(0, bal - wAmt) * (1 + rr);
            if (bal <= 0 && depletedYr === null) depletedYr = t + 1;
          } else {
            const g = bal * (1 + rr);
            wrPath.push(g > 0 ? Math.min(30, (wAmt / g) * 100) : 30);
            bal = Math.max(0, g - wAmt);
            if (bal <= 0 && depletedYr === null) depletedYr = t + 1;
          }
          wPath.push(bal);
        }
        const mwr = computeCohortMWR(s.eq, s.bd, s.inf, i, retYrs, eqW, { timing });
        const cagr = Math.pow(realProd, 1 / retYrs) - 1;
        const cagrMwr = Math.max(0, -calcPMT(cagr, retYrs, 100, 0, timing === "start" ? 1 : 0));
        cohorts.push({ yr: s.years[i], wPath, wrPath, endBal: bal, depletedYr, mwr, cagr: cagr * 100, cagrMwr });
      }
      // Fixed benchmark path at avgRealCagr
      const fixedW = [100.0];
      let fb = 100.0;
      for (let t = 0; t < retYrs; t++) {
        fb = timing === "start" ? Math.max(0, fb - wr * 100) * (1 + avgRealCagr) : Math.max(0, fb * (1 + avgRealCagr) - wr * 100);
        fixedW.push(fb);
      }

      const survCnt = cohorts.filter(c => c.endBal > 0).length;
      const bestC = cohorts.reduce((a, b) => b.endBal > a.endBal ? b : a, cohorts[0]);
      const depCohs = cohorts.filter(c => c.depletedYr !== null);
      const worstC = depCohs.length ? depCohs.reduce((a, b) => b.depletedYr < a.depletedYr ? b : a, depCohs[0]) : cohorts.reduce((a, b) => b.endBal < a.endBal ? b : a, cohorts[0]);
      const focusC = cohorts.find(c => c.yr === focusYr) || cohorts[0];

      const isZh = currentLang === "zh-CN";
      document.getElementById("k3Surv").textContent = `${((survCnt / cohorts.length) * 100).toFixed(1)}%`;
      document.getElementById("k3SurvSub").textContent = `${survCnt} / ${cohorts.length} ${isZh ? "个历史起点" : "cohorts"}`;
      document.getElementById("k3Best").textContent = `$${bestC.endBal.toFixed(1)}`;
      document.getElementById("k3BestSub").textContent = `${bestC.yr} (${isZh ? "初始 $100" : "of $100"})`;
      document.getElementById("k3Worst").textContent = worstC.depletedYr ? `${isZh ? "第" : "Yr "}${worstC.depletedYr}${isZh ? "年" : ""}` : `$${worstC.endBal.toFixed(1)}`;
      document.getElementById("k3WorstSub").textContent = `${worstC.yr} (${isZh ? "历史最差" : "worst cohort"})`;
      document.getElementById("k3Focus").textContent = focusC.depletedYr ? `${isZh ? "耗尽 Yr" : "Depleted Yr "}${focusC.depletedYr}` : `$${focusC.endBal.toFixed(1)}`;
      document.getElementById("k3FocusSub").textContent = `${focusC.yr} · MWR ${focusC.mwr.toFixed(2)}%`;

      state.lastExport = cohorts.map(c => [c.yr, c.endBal.toFixed(2), c.mwr.toFixed(2), c.cagr.toFixed(2), c.cagrMwr.toFixed(2), c.depletedYr || ""]);

      if (state.tab === "glide") {
        drawSpaghetti(cohorts, focusC, fixedW, retYrs);
        drawWrSpiral(cohorts, focusC, retYrs);
      } else if (state.tab === "lifetime") {
        computeAndDrawLifetime(s, eqW, workYrs, retYrs, saveRate, timing, cohorts);
      } else {
        computeAndDrawReverse(s, eqW, workYrs, retYrs, saveRate, timing, cohorts, avgRealCagr);
      }
    }

    function drawSpaghetti(cohorts, focusC, fixedW, retYrs) {
      const sc = setupCanvas(document.getElementById("glideCanvas"));
      if (!sc) return;
      const { ctx, w, h } = sc; const C = getThemeColors(); ctx.clearRect(0, 0, w, h);
      const maxV = Math.min(500, Math.max(200, ...cohorts.map(c => Math.max(...c.wPath)))) * 1.05;
      const pad = { l: 48, r: 16, t: 18, b: 28 }, cw = w - pad.l - pad.r, ch = h - pad.t - pad.b;
      const ticks = computeNiceLinearTicks(0, maxV, 4); const topV = ticks[ticks.length - 1];
      const mapX = t => pad.l + (t / retYrs) * cw;
      const mapY = v => pad.t + ch - (Math.min(topV, Math.max(0, v)) / topV) * ch;
      ctx.strokeStyle = C.grid; ctx.font = CANVAS_FONT; ctx.textAlign = "right"; ctx.fillStyle = C.muted;
      ticks.forEach(v => { const y = mapY(v); ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(w - pad.r, y); ctx.stroke(); ctx.fillText("$" + v, pad.l - 6, y + 4); });
      ctx.save(); ctx.strokeStyle = C.muted; ctx.globalAlpha = 0.22; ctx.lineWidth = 1;
      cohorts.forEach(c => {
        ctx.beginPath(); c.wPath.forEach((v, t) => { const x = mapX(t), y = mapY(v); if (t === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); }); ctx.stroke();
      });
      ctx.restore();
      // Fixed mean line
      ctx.beginPath(); ctx.strokeStyle = C.accent; ctx.lineWidth = 2.2; ctx.setLineDash([5, 3]);
      fixedW.forEach((v, t) => { const x = mapX(t), y = mapY(v); if (t === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); });
      ctx.stroke(); ctx.setLineDash([]);
      // Highlighted cohort
      ctx.beginPath(); ctx.strokeStyle = C.port; ctx.lineWidth = 2.6;
      focusC.wPath.forEach((v, t) => { const x = mapX(t), y = mapY(v); if (t === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); });
      ctx.stroke();
      ctx.fillStyle = C.muted; ctx.textAlign = "center";
      [0, Math.round(retYrs / 2), retYrs].forEach(t => ctx.fillText("Yr " + t, mapX(t), h - 8));
    }

    function drawWrSpiral(cohorts, focusC, retYrs) {
      const sc = setupCanvas(document.getElementById("wrCanvas"));
      if (!sc) return;
      const { ctx, w, h } = sc; const C = getThemeColors(); ctx.clearRect(0, 0, w, h);
      const pad = { l: 44, r: 16, t: 18, b: 28 }, cw = w - pad.l - pad.r, ch = h - pad.t - pad.b;
      const mapX = t => pad.l + (t / (retYrs - 1)) * cw;
      const mapY = v => pad.t + ch - (Math.min(30, v) / 30) * ch;
      ctx.strokeStyle = C.grid; ctx.font = CANVAS_FONT; ctx.textAlign = "right"; ctx.fillStyle = C.muted;
      [0, 10, 20, 30].forEach(v => { const y = mapY(v); ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(w - pad.r, y); ctx.stroke(); ctx.fillText(v + "%", pad.l - 6, y + 4); });
      // 10% threshold line
      ctx.strokeStyle = C.danger; ctx.lineWidth = 1.3; ctx.setLineDash([4, 3]);
      ctx.beginPath(); ctx.moveTo(pad.l, mapY(10)); ctx.lineTo(w - pad.r, mapY(10)); ctx.stroke(); ctx.setLineDash([]);
      ctx.save(); ctx.strokeStyle = C.muted; ctx.globalAlpha = 0.22; ctx.lineWidth = 1;
      cohorts.forEach(c => { ctx.beginPath(); c.wrPath.forEach((v, t) => { const x = mapX(t), y = mapY(v); if (t === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); }); ctx.stroke(); });
      ctx.restore();
      ctx.beginPath(); ctx.strokeStyle = C.port; ctx.lineWidth = 2.6;
      focusC.wrPath.forEach((v, t) => { const x = mapX(t), y = mapY(v); if (t === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); });
      ctx.stroke();
      ctx.fillStyle = C.muted; ctx.textAlign = "center";
      [0, Math.round((retYrs - 1) / 2), retYrs - 1].forEach(t => ctx.fillText("Yr " + (t + 1), mapX(t), h - 8));
    }

    function computeAndDrawLifetime(s, eqW, workYrs, retYrs, saveRate, timing, cohorts) {
      // Accumulation cohorts: 30-yr work ending in year Y
      const acc = [];
      for (let i = workYrs; i < s.years.length; i++) {
        let mult = 0;
        for (let k = 0; k < workYrs; k++) {
          const idx = i - workYrs + k;
          const rr = (1 + eqW * s.eq[idx] + (1 - eqW) * s.bd[idx]) / (1 + s.inf[idx]) - 1;
          mult = (mult + saveRate) * (1 + rr);
        }
        acc.push({ retYr: s.years[i], mult });
      }
      const mults = acc.map(a => a.mult).slice().sort((a, b) => a - b);
      const minA = acc.reduce((a, b) => b.mult < a.mult ? b : a, acc[0]);
      const maxA = acc.reduce((a, b) => b.mult > a.mult ? b : a, acc[0]);
      const minM = cohorts.reduce((a, b) => b.mwr < a.mwr ? b : a, cohorts[0]);
      const maxM = cohorts.reduce((a, b) => b.mwr > a.mwr ? b : a, cohorts[0]);

      document.getElementById("kAccMed").textContent = quantileSorted(mults, 0.5).toFixed(1) + "×";
      document.getElementById("kAccSub").textContent = `${workYrs}y @ ${Math.round(saveRate * 100)}%`;
      document.getElementById("kAccRng").textContent = `${minA.mult.toFixed(1)}× – ${maxA.mult.toFixed(1)}×`;
      document.getElementById("kAccRngSub").textContent = `${minA.retYr} / ${maxA.retYr}`;
      document.getElementById("kMwrRng").textContent = `${minM.mwr.toFixed(2)}% – ${maxM.mwr.toFixed(2)}%`;
      document.getElementById("kMwrRngSub").textContent = `${minM.yr} / ${maxM.yr}`;

      // MC R^2 attribution (Ex. 3.6): 2,000 simulated 60-yr lifecycles (fast & accurate to 0.2%)
      const totYrs = workYrs + retYrs;
      const N = 2500;
      const rng = mulberry32(state.seed);
      const W = s.years.length;
      const matR = Array.from({ length: totYrs }, () => new Float64Array(N));
      const accOut = new Float64Array(N), retOut = new Float64Array(N);
      for (let i = 0; i < N; i++) {
        const path = state.mcMode === "ch3a" ? simulateCh3APath(CH3A_CAL, totYrs, rng) : null;
        const eqArr = new Float64Array(totYrs), bdArr = new Float64Array(totYrs), infArr = new Float64Array(totYrs);
        for (let t = 0; t < totYrs; t++) {
          if (path) { eqArr[t] = path.eq[t]; bdArr[t] = path.bd[t]; infArr[t] = path.inf[t]; }
          else { const k = Math.floor(rng() * W); eqArr[t] = s.eq[k]; bdArr[t] = s.bd[k]; infArr[t] = s.inf[k]; }
          matR[t][i] = (1 + eqW * eqArr[t] + (1 - eqW) * bdArr[t]) / (1 + infArr[t]) - 1;
        }
        let mult = 0;
        for (let t = 0; t < workYrs; t++) mult = (mult + saveRate) * (1 + matR[t][i]);
        accOut[i] = mult;
        retOut[i] = computeCohortMWR(eqArr, bdArr, infArr, workYrs, retYrs, eqW, { timing });
      }
      const r2ByYr = [];
      for (let t = 0; t < totYrs; t++) {
        const yVec = t < workYrs ? accOut : retOut;
        const x = matR[t];
        const mx = meanArr(x), my = meanArr(yVec);
        let cov = 0, vx = 0, vy = 0;
        for (let i = 0; i < N; i++) {
          const dx = x[i] - mx, dy = yVec[i] - my;
          cov += dx * dy; vx += dx * dx; vy += dy * dy;
        }
        r2ByYr.push(vx > 0 && vy > 0 ? ((cov * cov) / (vx * vy)) * 100 : 0);
      }
      document.getElementById("kYr1R2").textContent = r2ByYr[workYrs].toFixed(1) + "%";

      // Draw Adam chart (Ex. 3.4 & 3.5)
      const sc1 = setupCanvas(document.getElementById("adamCanvas"));
      if (sc1) {
        const { ctx, w, h } = sc1; const C = getThemeColors(); ctx.clearRect(0, 0, w, h);
        const pad = { l: 44, r: 44, t: 18, b: 28 }, cw = w - pad.l - pad.r, ch = h - pad.t - pad.b;
        const mMap = {}; cohorts.forEach(c => { mMap[c.yr] = c.mwr; });
        const aMap = {}; acc.forEach(a => { aMap[a.retYr] = a.mult; });
        const allY = s.years;
        const mapX = i => pad.l + (i / (allY.length - 1)) * cw;
        const maxMult = Math.max(18, maxA.mult) * 1.05;
        const maxMwr = Math.max(10, maxM.mwr) * 1.05;
        const mapY1 = v => pad.t + ch - (v / maxMult) * ch;
        const mapY2 = v => pad.t + ch - (v / maxMwr) * ch;
        ctx.strokeStyle = C.grid; ctx.font = CANVAS_FONT;
        [0, 5, 10, 15, 20].filter(v => v <= maxMult).forEach(v => {
          const y = mapY1(v); ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(w - pad.r, y); ctx.stroke();
          ctx.fillStyle = C.accent; ctx.textAlign = "right"; ctx.fillText(v + "×", pad.l - 5, y + 4);
        });
        [0, 4, 8, 12].filter(v => v <= maxMwr).forEach(v => {
          ctx.fillStyle = C.port; ctx.textAlign = "left"; ctx.fillText(v + "%", w - pad.r + 5, mapY2(v) + 4);
        });
        ctx.beginPath(); ctx.strokeStyle = C.accent; ctx.lineWidth = 2;
        let started = false;
        allY.forEach((y, i) => { if (aMap[y] !== undefined) { const px = mapX(i), py = mapY1(aMap[y]); if (!started) { ctx.moveTo(px, py); started = true; } else ctx.lineTo(px, py); } });
        ctx.stroke();
        ctx.beginPath(); ctx.strokeStyle = C.port; ctx.lineWidth = 2;
        started = false;
        allY.forEach((y, i) => { if (mMap[y] !== undefined) { const px = mapX(i), py = mapY2(mMap[y]); if (!started) { ctx.moveTo(px, py); started = true; } else ctx.lineTo(px, py); } });
        ctx.stroke();
        ctx.fillStyle = C.muted; ctx.textAlign = "center";
        allY.forEach((y, i) => { if (y % 20 === 0) ctx.fillText(String(y), mapX(i), h - 8); });
      }

      // Draw R2 chart (Ex. 3.6)
      const sc2 = setupCanvas(document.getElementById("r2Canvas"));
      if (sc2) {
        const { ctx, w, h } = sc2; const C = getThemeColors(); ctx.clearRect(0, 0, w, h);
        const pad = { l: 42, r: 16, t: 18, b: 28 }, cw = w - pad.l - pad.r, ch = h - pad.t - pad.b;
        const maxR2 = Math.max(15, ...r2ByYr) * 1.1;
        const bw = Math.max(2, (cw / totYrs) * 0.72);
        const mapX = i => pad.l + ((i + 0.5) / totYrs) * cw;
        const mapY = v => pad.t + ch - (v / maxR2) * ch;
        ctx.strokeStyle = C.grid; ctx.font = CANVAS_FONT; ctx.textAlign = "right"; ctx.fillStyle = C.muted;
        computeNiceLinearTicks(0, maxR2, 4).forEach(v => {
          const y = mapY(v); ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(w - pad.r, y); ctx.stroke();
          ctx.fillText(v.toFixed(0) + "%", pad.l - 5, y + 4);
        });
        r2ByYr.forEach((v, i) => {
          ctx.fillStyle = i < workYrs ? C.accent : C.port;
          const x = mapX(i), y = mapY(v);
          ctx.fillRect(x - bw / 2, y, bw, pad.t + ch - y);
        });
        ctx.fillStyle = C.muted; ctx.textAlign = "center";
        [0, workYrs - 1, workYrs, totYrs - 1].forEach(i => ctx.fillText("Yr " + (i + 1), mapX(i), h - 8));
      }
    }

    function computeAndDrawReverse(s, eqW, workYrs, retYrs, saveRate, timing, cohorts) {
      // Draw Ex. 3.8 MWR vs Fixed-CAGR MWR
      const sc1 = setupCanvas(document.getElementById("seqGapCanvas"));
      if (sc1) {
        const { ctx, w, h } = sc1; const C = getThemeColors(); ctx.clearRect(0, 0, w, h);
        const pad = { l: 44, r: 16, t: 18, b: 28 }, cw = w - pad.l - pad.r, ch = h - pad.t - pad.b;
        const maxM = Math.max(10, ...cohorts.map(c => Math.max(c.mwr, c.cagrMwr))) * 1.05;
        const ticks = computeNiceLinearTicks(0, maxM, 4); const topM = ticks[ticks.length - 1];
        const mapX = i => pad.l + (i / (cohorts.length - 1)) * cw;
        const mapY = v => pad.t + ch - (v / topM) * ch;
        ctx.strokeStyle = C.grid; ctx.font = CANVAS_FONT; ctx.textAlign = "right"; ctx.fillStyle = C.muted;
        ticks.forEach(v => { const y = mapY(v); ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(w - pad.r, y); ctx.stroke(); ctx.fillText(v + "%", pad.l - 5, y + 4); });
        ctx.beginPath(); ctx.strokeStyle = C.accent; ctx.lineWidth = 2;
        cohorts.forEach((c, i) => { const x = mapX(i), y = mapY(c.cagrMwr); if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); });
        ctx.stroke();
        ctx.beginPath(); ctx.strokeStyle = C.port; ctx.lineWidth = 2.4;
        cohorts.forEach((c, i) => { const x = mapX(i), y = mapY(c.mwr); if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); });
        ctx.stroke();
        ctx.fillStyle = C.muted; ctx.textAlign = "center";
        cohorts.forEach((c, i) => { if (c.yr % 15 === 0 || i === 0 || i === cohorts.length - 1) ctx.fillText(String(c.yr), mapX(i), h - 8); });
      }

      // Compute Ex. 3.9 Reverse-Engineered IRRs across 5,000 runs
      const N = 5000, rng = mulberry32(state.seed), W = s.years.length;
      const irrLump = new Float64Array(N), irrAcc = new Float64Array(N), irrRet = new Float64Array(N);
      const tType = timing === "start" ? 1 : 0;
      for (let i = 0; i < N; i++) {
        const len = Math.max(workYrs, retYrs);
        const path = state.mcMode === "ch3a" ? simulateCh3APath(CH3A_CAL, len, rng) : null;
        const eqArr = new Float64Array(len), bdArr = new Float64Array(len), infArr = new Float64Array(len);
        const rr = new Float64Array(len);
        for (let t = 0; t < len; t++) {
          if (path) { eqArr[t] = path.eq[t]; bdArr[t] = path.bd[t]; infArr[t] = path.inf[t]; }
          else { const k = Math.floor(rng() * W); eqArr[t] = s.eq[k]; bdArr[t] = s.bd[k]; infArr[t] = s.inf[k]; }
          rr[t] = (1 + eqW * eqArr[t] + (1 - eqW) * bdArr[t]) / (1 + infArr[t]) - 1;
        }
        let prod = 1.0;
        for (let t = 0; t < retYrs; t++) prod *= (1 + rr[t]);
        irrLump[i] = (Math.pow(prod, 1 / retYrs) - 1) * 100;
        let mult = 0;
        for (let t = 0; t < workYrs; t++) mult = (mult + saveRate) * (1 + rr[t]);
        const rA = calcRATE(workYrs, -saveRate, 0, mult, 0);
        irrAcc[i] = isFinite(rA) ? rA * 100 : 0;
        const mwrDec = computeCohortMWR(eqArr, bdArr, infArr, 0, retYrs, eqW, { timing }) / 100;
        const rRet = calcRATE(retYrs, -mwrDec, 1.0, 0, tType);
        irrRet[i] = isFinite(rRet) ? rRet * 100 : 0;
      }
      irrLump.sort(); irrAcc.sort(); irrRet.sort();
      const pcts = [0.05, 0.10, 0.25, 0.50, 0.75, 0.90];
      const isZh = currentLang === "zh-CN";
      document.getElementById("irrHead").innerHTML = `<tr><th>${isZh ? "投资阶段" : "Investor Phase"}</th>${pcts.map(p => `<th>P${Math.round(p * 100)} (${Math.round((1 - p) * 100)}% ${isZh ? "达标" : "succ."})</th>`).join("")}<th>SD</th></tr>`;
      const sdOf = a => { const m = meanArr(a); let s2 = 0; for (let i = 0; i < a.length; i++) s2 += (a[i] - m) ** 2; return Math.sqrt(s2 / a.length); };
      const rows = [
        [isZh ? "整笔投资 (Lump-Sum)" : "Lump-Sum Investor", irrLump],
        [isZh ? "工作期储蓄 (Accumulator)" : "Career Accumulator", irrAcc],
        [isZh ? "退休期提取 (Retiree)" : "Retiree (Sequence Risk)", irrRet],
      ];
      document.getElementById("irrBody").innerHTML = rows.map(([lbl, arr]) => `<tr><td><strong>${lbl}</strong></td>${pcts.map(p => `<td>${quantileSorted(arr, p).toFixed(2)}%</td>`).join("")}<td>${sdOf(arr).toFixed(2)}%</td></tr>`).join("");

      const sc2 = setupCanvas(document.getElementById("irrCanvas"));
      if (sc2) {
        const { ctx, w, h } = sc2; const C = getThemeColors(); ctx.clearRect(0, 0, w, h);
        const pad = { l: 44, r: 16, t: 18, b: 28 }, cw = w - pad.l - pad.r, ch = h - pad.t - pad.b;
        const minY = Math.min(-2, quantileSorted(irrRet, 0.05)) - 0.5, maxY = Math.max(10, quantileSorted(irrRet, 0.95)) + 0.5;
        const ticks = computeNiceLinearTicks(minY, maxY, 4); const bV = ticks[0], tV = ticks[ticks.length - 1];
        const mapX = i => pad.l + (i / (pcts.length - 1)) * cw;
        const mapY = v => pad.t + ch - ((v - bV) / (tV - bV || 1)) * ch;
        ctx.strokeStyle = C.grid; ctx.font = CANVAS_FONT; ctx.textAlign = "right"; ctx.fillStyle = C.muted;
        ticks.forEach(v => { const y = mapY(v); ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(w - pad.r, y); ctx.stroke(); ctx.fillText(v.toFixed(1) + "%", pad.l - 5, y + 4); });
        const cols = [C.muted, C.accent, C.port];
        rows.forEach(([_, arr], rIdx) => {
          ctx.beginPath(); ctx.strokeStyle = cols[rIdx]; ctx.lineWidth = rIdx === 2 ? 2.6 : 1.8;
          pcts.forEach((p, i) => { const x = mapX(i), y = mapY(quantileSorted(arr, p)); if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); });
          ctx.stroke();
        });
        ctx.fillStyle = C.muted; ctx.textAlign = "center";
        pcts.forEach((p, i) => ctx.fillText("P" + Math.round(p * 100), mapX(i), h - 8));
      }
    }

    function applyPreset(name) {
      document.querySelectorAll(".preset-btn").forEach(b => b.classList.toggle("active", b.dataset.preset === name));
      if (name === "ex32") {
        document.getElementById("initWrPct").value = "6.3"; document.getElementById("eqPctSlider").value = "50";
        document.getElementById("focusCohort").value = "1966";
        document.querySelector('[data-tab="glide"]').click();
      } else if (name === "ex34") {
        document.getElementById("saveRatePct").value = "15"; document.getElementById("workYrs").value = "30";
        document.querySelector('[data-tab="lifetime"]').click();
      } else if (name === "ex38") {
        document.querySelector('[data-tab="reverse"]').click();
      } else if (name === "ex39") {
        document.querySelector('[data-tab="reverse"]').click();
      }
      computeAll();
    }

    function onThemeOrLangChange() { computeAll(); }

    document.querySelectorAll(".tab-btn").forEach(b => {
      b.addEventListener("click", () => {
        state.tab = b.dataset.tab;
        document.querySelectorAll(".tab-btn").forEach(x => { x.classList.toggle("active", x === b); x.setAttribute("aria-selected", x === b ? "true" : "false"); });
        document.getElementById("paneGlide").style.display = state.tab === "glide" ? "block" : "none";
        document.getElementById("paneLifetime").style.display = state.tab === "lifetime" ? "block" : "none";
        document.getElementById("paneReverse").style.display = state.tab === "reverse" ? "block" : "none";
        computeAll();
      });
    });
    document.querySelectorAll("#mcModeCtl button").forEach(b => {
      b.addEventListener("click", () => {
        state.mcMode = b.dataset.v;
        document.querySelectorAll("#mcModeCtl button").forEach(x => setBtnActive(x, x === b));
        computeAll();
      });
    });
    document.getElementById("btnRerun").addEventListener("click", () => { state.seed = (state.seed + 7919) >>> 0; computeAll(); });
    document.querySelectorAll(".preset-btn").forEach(b => b.addEventListener("click", () => applyPreset(b.dataset.preset)));
    document.getElementById("btnReset").addEventListener("click", () => applyPreset("ex32"));
    document.getElementById("btnExportCsv").addEventListener("click", () => {
      downloadCsv("pfau_ch3_cohorts.csv", ["Start_Year", "End_Real_Wealth_100", "MWR_pct", "Real_CAGR_pct", "Fixed_CAGR_MWR_pct", "Depleted_Yr"], state.lastExport);
    });
    ["datasetSelect", "eqPctSlider", "initWrPct", "retYrs", "workYrs", "saveRatePct", "focusCohort", "timingSel"].forEach(id => {
      const el = document.getElementById(id);
      el.addEventListener("input", computeAll);
      el.addEventListener("change", computeAll);
    });
    window.addEventListener("resize", () => requestAnimationFrame(computeAll));

    initSharedControls();
    applyStaticI18n();
    computeAll();
"""

    render_page(
        slug="sequence-of-returns-risk",
        title_en="Sequence-of-Returns Risk",
        extra_css="",
        body_html=body_html,
        embedded_data_js=embedded,
        page_i18n=page_i18n,
        page_js=page_js,
    )


if __name__ == "__main__":
    build_ch3()
