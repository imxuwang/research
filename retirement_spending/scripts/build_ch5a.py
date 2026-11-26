#!/usr/bin/env python3
"""Build Lab 4 (Chapter 5 Part I): Market Valuations (PE10 + Yields), Safe Savings Rates, Global 4% Rule & 5-Asset Optimizer, and Fee/Tax/Mistiming Drag."""

from shared_shell import dump_json_inline, load_csv_records, render_page
from shared_sim_js import SHARED_SIM_JS


def build_ch5a():
    shiller = load_csv_records("shiller_us_1871_2025_annual.csv")
    nyu = load_csv_records("nyu_stern_1928_2025_full.csv")
    dms = load_csv_records("dms_global_swr_benchmarks.csv")
    all_ctry = load_csv_records("backtest_1988_2025_all_country.csv")

    body_html = """  <main class="layout">
    <aside class="sidebar" aria-label="Simulation parameters" data-i18n-aria-label="aria_sidebar">
      <div class="side-section">
        <div class="sec-head-static">
          <h2 class="sec-title" data-i18n="sec_presets">Book Exhibit Presets</h2>
          <button type="button" class="link-btn" id="btnReset" data-i18n="btn_reset">Reset</button>
        </div>
        <div class="preset-grid">
          <button type="button" class="preset-btn active" data-preset="ex58">
            <span class="p-title" data-i18n="pre_58_t">Ex. 5.8 · CAPE &amp; Yields</span>
            <span class="p-meta" data-i18n="pre_58_m">PE10=28.2, Y10=2.45%</span>
          </button>
          <button type="button" class="preset-btn" data-preset="ex59">
            <span class="p-title" data-i18n="pre_59_t">Ex. 5.9–5.11 · Safe Savings</span>
            <span class="p-meta" data-i18n="pre_59_m">17.6% SAFEMIN lifecycle</span>
          </button>
          <button type="button" class="preset-btn" data-preset="ex526">
            <span class="p-title" data-i18n="pre_26_t">Ex. 5.2, 5.28 · Global 5-Asset</span>
            <span class="p-meta" data-i18n="pre_26_m">20 countries + 3.61% OPT</span>
          </button>
          <button type="button" class="preset-btn" data-preset="ex512">
            <span class="p-title" data-i18n="pre_12_t">Ex. 5.12–5.13 · Drag &amp; Timing</span>
            <span class="p-meta" data-i18n="pre_12_m">1% fee, tax, mistiming</span>
          </button>
        </div>
      </div>

      <div class="side-section">
        <div class="sec-head-static"><h2 class="sec-title" data-i18n="sec_val">Valuations &amp; Portfolio</h2></div>
        <div class="control-group row-2">
          <div>
            <label for="testPe10"><span data-i18n="lbl_pe10">Test Shiller PE10</span></label>
            <input type="number" id="testPe10" value="28.2" min="5" max="60" step="0.2" />
          </div>
          <div>
            <label for="testY10"><span data-i18n="lbl_y10">Test 10Y Yield (%)</span></label>
            <input type="number" id="testY10" value="2.45" min="0.5" max="16" step="0.1" />
          </div>
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
            <label for="retYrs"><span data-i18n="lbl_ret_yrs">Retirement (yrs)</span></label>
            <input type="number" id="retYrs" value="30" min="15" max="45" step="5" />
          </div>
          <div>
            <label for="olsSample"><span data-i18n="lbl_ols_samp">OLS Sample</span></label>
            <select id="olsSample">
              <option value="1987" selected data-i18n="opt_s87">1881–1987 (Book)</option>
              <option value="1995" data-i18n="opt_s95">1881–1995 (Extended)</option>
            </select>
          </div>
        </div>
      </div>

      <div class="side-section">
        <div class="sec-head-static"><h2 class="sec-title" data-i18n="sec_sav_drag">Savings, Fees &amp; Taxes</h2></div>
        <div class="control-group row-2">
          <div>
            <label for="workYrs"><span data-i18n="lbl_work">Career (yrs)</span></label>
            <input type="number" id="workYrs" value="30" min="15" max="40" step="5" />
          </div>
          <div>
            <label for="replRatePct"><span data-i18n="lbl_rr">Replacement (%)</span></label>
            <input type="number" id="replRatePct" value="50" min="20" max="80" step="5" />
          </div>
        </div>
        <div class="control-group row-2">
          <div>
            <label for="feeBps"><span data-i18n="lbl_fee">Annual fee (bps)</span></label>
            <input type="number" id="feeBps" value="100" min="0" max="250" step="10" />
          </div>
          <div>
            <label for="margTaxPct"><span data-i18n="lbl_tax">Taxable rate (%)</span></label>
            <input type="number" id="margTaxPct" value="0" min="0" max="45" step="5" />
          </div>
        </div>
        <div class="notice" id="taxEffNote" style="margin-top:4px;"></div>
      </div>
    </aside>

    <section class="workspace" aria-label="Simulation outputs" data-i18n-aria-label="aria_workspace">
      <div class="results-shell">
        <div class="tabs-bar">
          <div class="tab-strip" role="tablist">
            <button type="button" class="tab-btn active" role="tab" aria-selected="true" data-tab="val" data-i18n="tab_val">PE10 &amp; Yields (Ex. 5.4–5.8)</button>
            <button type="button" class="tab-btn" role="tab" aria-selected="false" data-tab="ssr" data-i18n="tab_ssr">Safe Savings Rates (Ex. 5.9–5.11)</button>
            <button type="button" class="tab-btn" role="tab" aria-selected="false" data-tab="intl" data-i18n="tab_intl">Global &amp; 5-Asset (Ex. 5.2, 5.26–5.28)</button>
            <button type="button" class="tab-btn" role="tab" aria-selected="false" data-tab="drag" data-i18n="tab_drag">Fees, Taxes &amp; Mistiming (Ex. 5.12–5.13)</button>
          </div>
        </div>

        <div class="results-body">
          <div id="paneVal" class="tab-pane">
            <div class="kpis kpis-4 kpis-flush-top">
              <div class="kpi"><div class="kpi-label" data-i18n="kv_book_pred">Book OLS Prediction (50% Odds)</div><div class="kpi-val" id="kvBook">—</div><div class="kpi-sub">12.15 − 2.47 ln(PE10) + 0.05 Y₁₀</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="kv_live_pred">Live Shiller OLS (50% Odds)</div><div class="kpi-val" id="kvLive">—</div><div class="kpi-sub" id="kvLiveEqn">—</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="kv_p90_safe">Conservative 90% Success Est.</div><div class="kpi-val pos" id="kvP90">—</div><div class="kpi-sub" id="kvRmseSub">—</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="kv_r2">OLS Explanatory Power (R²)</div><div class="kpi-val" id="kvR2">—</div><div class="kpi-sub" id="kvSampSub">—</div></div>
            </div>
            <div class="split-grid">
              <div class="grid-cell">
                <div class="legend">
                  <strong data-i18n="ttl_ex58">Ex. 5.8: Actual vs. Predicted 30-Yr MWR (Shiller)</strong>
                  <div class="legend-items">
                    <div class="legend-item"><span class="swatch" style="background:var(--port);"></span><span data-i18n="leg_act">Actual MWR</span></div>
                    <div class="legend-item"><span class="swatch" style="background:var(--accent);"></span><span data-i18n="leg_pred">OLS Predicted</span></div>
                  </div>
                </div>
                <div class="chart-wrap"><canvas id="olsCanvas" height="250"></canvas><div class="tooltip" id="olsTip"></div></div>
              </div>
              <div class="grid-cell">
                <div class="legend">
                  <strong data-i18n="ttl_ex54">Ex. 5.4–5.5: Shiller PE10 &amp; 10Y Yield (1871–2025)</strong>
                  <div class="legend-items">
                    <div class="legend-item"><span class="swatch" style="background:var(--equity);"></span><span>PE10 (CAPE)</span></div>
                    <div class="legend-item"><span class="swatch" style="background:var(--bond);"></span><span>10Y Yield (%)</span></div>
                  </div>
                </div>
                <div class="chart-wrap"><canvas id="capeCanvas" height="250"></canvas><div class="tooltip" id="capeTip"></div></div>
              </div>
            </div>
          </div>

          <div id="paneSsr" class="tab-pane" style="display:none;">
            <div class="kpis kpis-4 kpis-flush-top">
              <div class="kpi"><div class="kpi-label" data-i18n="ks_safemin">Lifecycle SAFEMIN (Max LMSR)</div><div class="kpi-val pos" id="ksSafemin">—</div><div class="kpi-sub" id="ksSafeminSub">—</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="ks_min_lmsr">Lowest Lifecycle Savings Rate</div><div class="kpi-val" id="ksMinLmsr">—</div><div class="kpi-sub" id="ksMinLmsrSub">—</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="ks_max_msr">Peak Isolated Target MSR (12.5×)</div><div class="kpi-val" id="ksMaxMsr">—</div><div class="kpi-sub" id="ksMaxMsrSub">—</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="ks_r2">Variance of MWR Explained by MSR</div><div class="kpi-val" id="ksR2">—</div><div class="kpi-sub" data-i18n="ks_r2_sub">Ex. 5.10 integration link</div></div>
            </div>
            <div class="panel-block">
              <div class="legend">
                <strong data-i18n="ttl_ex511">Ex. 5.9–5.11: Isolated MSR vs. Lifecycle LMSR (by Retirement Year)</strong>
                <div class="legend-items">
                  <div class="legend-item"><span class="swatch" style="background:var(--muted);"></span><span data-i18n="leg_msr">Isolated MSR</span></div>
                  <div class="legend-item"><span class="swatch" style="background:var(--port);"></span><span data-i18n="leg_lmsr">Lifecycle LMSR</span></div>
                </div>
              </div>
              <div class="chart-wrap"><canvas id="ssrCanvas" height="260"></canvas><div class="tooltip" id="ssrTip"></div></div>
            </div>
            <div class="panel-block">
              <div class="card-title"><h3 class="sec-title" data-i18n="ttl_paradox">Safe Withdrawal Rate Paradox Demo (2008 vs. 2009 Retiree)</h3></div>
              <p class="method-note" id="paradoxNote"></p>
            </div>
          </div>

          <div id="paneIntl" class="tab-pane" style="display:none;">
            <div class="split-grid">
              <div class="grid-cell">
                <div class="legend"><strong data-i18n="ttl_ex52">Ex. 5.2: DMS 20-Country 50/50 SAFEMAX (1900–2015)</strong></div>
                <div class="chart-wrap"><canvas id="dmsCanvas" height="275"></canvas><div class="tooltip" id="dmsTip"></div></div>
              </div>
              <div class="grid-cell">
                <div class="legend">
                  <strong data-i18n="ttl_ex527">Ex. 5.26–5.28: 2-Asset vs. 5-Asset Efficient Frontier</strong>
                  <div class="legend-items">
                    <div class="legend-item"><span class="swatch" style="background:var(--muted);"></span><span>2-Asset (US Eq/Bd)</span></div>
                    <div class="legend-item"><span class="swatch" style="background:var(--success);"></span><span>5-Asset (+REIT/EAFE/Bill)</span></div>
                  </div>
                </div>
                <div class="chart-wrap"><canvas id="fiveAssetCanvas" height="275"></canvas><div class="tooltip" id="fiveAssetTip"></div></div>
              </div>
            </div>
            <div class="panel-block">
              <div class="card-title"><h3 class="sec-title" data-i18n="ttl_ex528_tbl">Ex. 5.28: Optimal 10%-Failure Portfolio Weights &amp; Global Benchmarks</h3></div>
              <p class="method-note" id="fiveAssetSummary" style="margin-bottom:10px;"></p>
              <div class="table-container" style="max-height:260px;">
                <table><thead id="dmsHead"></thead><tbody id="dmsBody"></tbody></table>
              </div>
            </div>
          </div>

          <div id="paneDrag" class="tab-pane" style="display:none;">
            <div class="kpis kpis-4 kpis-flush-top">
              <div class="kpi"><div class="kpi-label" data-i18n="kd_pure">Gross Index SAFEMAX</div><div class="kpi-val pos" id="kdPure">—</div><div class="kpi-sub" id="kdPureSub">—</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="kd_net">Net After Fee &amp; Tax Drag</div><div class="kpi-val" id="kdNet">—</div><div class="kpi-sub" id="kdNetSub">—</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="kd_mistime">Market Mistiming SAFEMAX</div><div class="kpi-val neg" id="kdMistime">—</div><div class="kpi-sub" data-i18n="kd_mis_sub">75% peak / 0% crash panic</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="kd_contrarian">Contrarian PE10 Timing SAFEMAX</div><div class="kpi-val pos" id="kdContra">—</div><div class="kpi-sub" data-i18n="kd_con_sub">25% peak / 75% undervalued</div></div>
            </div>
            <div class="split-grid">
              <div class="grid-cell">
                <div class="legend"><strong data-i18n="ttl_ex512">Ex. 5.12: Gross vs. Fee/Tax-Dragged 30-Yr MWR</strong></div>
                <div class="chart-wrap"><canvas id="dragCanvas" height="255"></canvas><div class="tooltip" id="dragTip"></div></div>
              </div>
              <div class="grid-cell">
                <div class="legend">
                  <strong data-i18n="ttl_ex513">Ex. 5.13: Fixed 50/50 vs. Mistiming vs. Contrarian PE10</strong>
                  <div class="legend-items">
                    <div class="legend-item"><span class="swatch" style="background:var(--muted);"></span><span>Fixed 50/50</span></div>
                    <div class="legend-item"><span class="swatch" style="background:var(--danger);"></span><span>Mistiming</span></div>
                    <div class="legend-item"><span class="swatch" style="background:var(--success);"></span><span>Contrarian</span></div>
                  </div>
                </div>
                <div class="chart-wrap"><canvas id="timingCanvas" height="255"></canvas><div class="tooltip" id="timingTip"></div></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </main>"""

    page_i18n = {
        "page_title": {"en-UK": "Valuations, Safe Savings & Drag", "zh-CN": "市场估值、安全储蓄率与损耗"},
        "app_title": {"en-UK": "Valuations, Safe Savings & Drag", "zh-CN": "市场估值、安全储蓄率与损耗"},
        "sec_presets": {"en-UK": "Book Exhibit Presets", "zh-CN": "全书图表预设"},
        "pre_58_t": {"en-UK": "Ex. 5.8 · CAPE & Yields", "zh-CN": "图5.8 · CAPE 与美债利率"},
        "pre_58_m": {"en-UK": "PE10=28.2, Y10=2.45%", "zh-CN": "PE10=28.2, 利率=2.45%"},
        "pre_59_t": {"en-UK": "Ex. 5.9–5.11 · Safe Savings", "zh-CN": "图5.9–5.11 · 安全储蓄率"},
        "pre_59_m": {"en-UK": "17.6% SAFEMIN lifecycle", "zh-CN": "17.6% SAFEMIN 全周期"},
        "pre_26_t": {"en-UK": "Ex. 5.2, 5.28 · Global 5-Asset", "zh-CN": "图5.2, 5.28 · 全球与5资产"},
        "pre_26_m": {"en-UK": "20 countries + 3.61% OPT", "zh-CN": "20国数据 + 5资产优化"},
        "pre_12_t": {"en-UK": "Ex. 5.12–5.13 · Drag & Timing", "zh-CN": "图5.12–5.13 · 损耗与择时"},
        "pre_12_m": {"en-UK": "1% fee, tax, mistiming", "zh-CN": "1%费用、税负与择时失误"},
        "sec_val": {"en-UK": "Valuations & Portfolio", "zh-CN": "市场估值与配置"},
        "lbl_pe10": {"en-UK": "Test Shiller PE10", "zh-CN": "测试席勒 PE10"},
        "lbl_y10": {"en-UK": "Test 10Y Yield (%)", "zh-CN": "测试 10年美债利率 (%)"},
        "lbl_eq": {"en-UK": "Stock / Bond mix", "zh-CN": "股 / 债比例"},
        "lbl_ret_yrs": {"en-UK": "Retirement (yrs)", "zh-CN": "退休年限"},
        "lbl_ols_samp": {"en-UK": "OLS Sample", "zh-CN": "回归样本期"},
        "opt_s87": {"en-UK": "1881–1987 (Book)", "zh-CN": "1881–1987 (原书)"},
        "opt_s95": {"en-UK": "1881–1995 (Extended)", "zh-CN": "1881–1995 (扩展)"},
        "sec_sav_drag": {"en-UK": "Savings, Fees & Taxes", "zh-CN": "储蓄率、费用与税负"},
        "lbl_work": {"en-UK": "Career (yrs)", "zh-CN": "工作年数"},
        "lbl_rr": {"en-UK": "Replacement (%)", "zh-CN": "退休薪资替代率 (%)"},
        "lbl_fee": {"en-UK": "Annual fee (bps)", "zh-CN": "年度管理费 (bps)"},
        "lbl_tax": {"en-UK": "Taxable rate (%)", "zh-CN": "边际所得税率 (%)"},
        "tab_val": {"en-UK": "PE10 & Yields (Ex. 5.4–5.8)", "zh-CN": "估值与利率预测 (5.4–5.8)"},
        "tab_ssr": {"en-UK": "Safe Savings Rates (Ex. 5.9–5.11)", "zh-CN": "安全储蓄率 (5.9–5.11)"},
        "tab_intl": {"en-UK": "Global & 5-Asset (Ex. 5.2, 5.26–5.28)", "zh-CN": "全球历史与5资产配置"},
        "tab_drag": {"en-UK": "Fees, Taxes & Mistiming (Ex. 5.12–5.13)", "zh-CN": "费用、税负与择时 (5.12–5.13)"},
        "kv_book_pred": {"en-UK": "Book OLS Prediction (50% Odds)", "zh-CN": "原书回归预测 (50%成功率)"},
        "kv_live_pred": {"en-UK": "Live Shiller OLS (50% Odds)", "zh-CN": "当前Shiller回归预测"},
        "kv_p90_safe": {"en-UK": "Conservative 90% Success Est.", "zh-CN": "90% 置信保守估计"},
        "kv_r2": {"en-UK": "OLS Explanatory Power (R²)", "zh-CN": "模型方差解释度 (R²)"},
        "ttl_ex58": {"en-UK": "Ex. 5.8: Actual vs. Predicted 30-Yr MWR (Shiller)", "zh-CN": "图 5.8：实际 vs 回归预测 30年 MWR"},
        "leg_act": {"en-UK": "Actual MWR", "zh-CN": "实际 MWR"},
        "leg_pred": {"en-UK": "OLS Predicted", "zh-CN": "回归预测"},
        "ttl_ex54": {"en-UK": "Ex. 5.4–5.5: Shiller PE10 & 10Y Yield (1871–2025)", "zh-CN": "图 5.4–5.5：席勒 PE10 与 10年期国债利率"},
        "ks_safemin": {"en-UK": "Lifecycle SAFEMIN (Max LMSR)", "zh-CN": "全周期最安全储蓄率 (SAFEMIN)"},
        "ks_min_lmsr": {"en-UK": "Lowest Lifecycle Savings Rate", "zh-CN": "全周期最低所需储蓄率"},
        "ks_max_msr": {"en-UK": "Peak Isolated Target MSR (12.5×)", "zh-CN": "孤立目标最高储蓄率"},
        "ks_r2": {"en-UK": "Variance of MWR Explained by MSR", "zh-CN": "MSR 对 MWR 方差解释度"},
        "ks_r2_sub": {"en-UK": "Ex. 5.10 integration link", "zh-CN": "图 5.10 累积与提取周期联动"},
        "ttl_ex511": {"en-UK": "Ex. 5.9–5.11: Isolated MSR vs. Lifecycle LMSR (by Retirement Year)", "zh-CN": "图 5.9–5.11：孤立储蓄率 MSR vs 全周期储蓄率 LMSR"},
        "leg_msr": {"en-UK": "Isolated MSR", "zh-CN": "孤立 MSR"},
        "leg_lmsr": {"en-UK": "Lifecycle LMSR", "zh-CN": "全周期 LMSR"},
        "ttl_paradox": {"en-UK": "Safe Withdrawal Rate Paradox Demo (2008 vs. 2009 Retiree)", "zh-CN": "安全提取率悖论演示（2008 vs 2009 退休者）"},
        "ttl_ex52": {"en-UK": "Ex. 5.2: DMS 20-Country 50/50 SAFEMAX (1900–2015)", "zh-CN": "图 5.2：DMS 20国 50/50 SAFEMAX 对比 (1900–2015)"},
        "ttl_ex527": {"en-UK": "Ex. 5.26–5.28: 2-Asset vs. 5-Asset Efficient Frontier", "zh-CN": "图 5.26–5.28：2资产 vs 5资产有效前沿对比"},
        "ttl_ex528_tbl": {"en-UK": "Ex. 5.28: Optimal 10%-Failure Portfolio Weights & Global Benchmarks", "zh-CN": "图 5.28：最优配置权重与国际基准表"},
        "kd_pure": {"en-UK": "Gross Index SAFEMAX", "zh-CN": "无费税基准 SAFEMAX"},
        "kd_net": {"en-UK": "Net After Fee & Tax Drag", "zh-CN": "扣除费用与税负后 SAFEMAX"},
        "kd_mistime": {"en-UK": "Market Mistiming SAFEMAX", "zh-CN": "追涨杀跌择时 SAFEMAX"},
        "kd_mis_sub": {"en-UK": "75% peak / 0% crash panic", "zh-CN": "高估追高 75% / 低估恐慌清仓 0%"},
        "kd_contrarian": {"en-UK": "Contrarian PE10 Timing SAFEMAX", "zh-CN": "逆向估值再平衡 SAFEMAX"},
        "kd_con_sub": {"en-UK": "25% peak / 75% undervalued", "zh-CN": "高估降仓 25% / 低估加仓 75%"},
        "ttl_ex512": {"en-UK": "Ex. 5.12: Gross vs. Fee/Tax-Dragged 30-Yr MWR", "zh-CN": "图 5.12：净指数收益 vs 扣费扣税后 MWR"},
        "ttl_ex513": {"en-UK": "Ex. 5.13: Fixed 50/50 vs. Mistiming vs. Contrarian PE10", "zh-CN": "图 5.13：固定 50/50 vs 择时失误 vs 逆向估值切换"},
    }

    embedded = (
        f"    const SHILLER = {dump_json_inline(shiller)};\n"
        f"    const NYU = {dump_json_inline(nyu)};\n"
        f"    const DMS = {dump_json_inline(dms)};\n"
    )
    page_js = SHARED_SIM_JS + r"""
    const state = { tab: "val", lastExport: [] };

    function updateAll() {
      const pe10 = Math.max(4, parseFloat(document.getElementById("testPe10").value) || 28.2);
      const y10 = Math.max(0.1, parseFloat(document.getElementById("testY10").value) || 2.45);
      const eqW = (parseFloat(document.getElementById("eqPctSlider").value) || 50) / 100;
      document.getElementById("eqPctHint").textContent = `${Math.round(eqW * 100)} / ${Math.round((1 - eqW) * 100)}`;
      document.getElementById("eqPctSlider").style.setProperty("--pct", Math.round(eqW * 100) + "%");
      const H = Math.max(15, Math.min(45, parseInt(document.getElementById("retYrs").value, 10) || 30));
      const maxEndYr = parseInt(document.getElementById("olsSample").value, 10) === 1995 ? 2025 - H + 1 : 1987;
      const workY = Math.max(15, Math.min(40, parseInt(document.getElementById("workYrs").value, 10) || 30));
      const rr = (parseFloat(document.getElementById("replRatePct").value) || 50) / 100;
      const feeDec = (parseFloat(document.getElementById("feeBps").value) || 0) / 10000;
      const margTax = (parseFloat(document.getElementById("margTaxPct").value) || 0) / 100;
      const taxEff = Math.min(0.65, 1.25 * margTax); // Bengen 2006 rule
      const isZh = currentLang === "zh-CN";
      document.getElementById("taxEffNote").textContent =
        isZh ? `Bengen 应税账户有效税率折算 τ_eff = 1.25×${Math.round(margTax * 100)}% = ${(taxEff * 100).toFixed(1)}%`
             : `Bengen (2006) effective tax drag τ_eff = 1.25 × ${Math.round(margTax * 100)}% = ${(taxEff * 100).toFixed(1)}%`;

      const eqArr = SHILLER.map(r => r.Shiller_SP500_TR_pct / 100);
      const bdArr = SHILLER.map(r => r.Shiller_10Y_TBond_pct / 100);
      const infArr = SHILLER.map(r => r.Shiller_US_CPI_pct / 100);

      // 1. Valuation OLS
      const olsRows = [];
      const yVec = [], xMat = [];
      for (let i = 0; i <= SHILLER.length - H; i++) {
        const r = SHILLER[i];
        if (r.Year < 1881 || r.Year > maxEndYr || !r.Jan_PE10_CAPE) continue;
        const mwr = computeCohortMWR(eqArr, bdArr, infArr, i, H, eqW, { timing: "start" });
        olsRows.push({ yr: r.Year, pe10: r.Jan_PE10_CAPE, y10: r.Jan_10Y_Yield_pct, mwr });
        yVec.push(mwr);
        xMat.push([1.0, Math.log(r.Jan_PE10_CAPE), r.Jan_10Y_Yield_pct]);
      }
      const fit = fitOLS(yVec, xMat);
      const bookPred = 12.15 - 2.47 * Math.log(pe10) + 0.05 * y10;
      const livePred = fit ? (fit.beta[0] + fit.beta[1] * Math.log(pe10) + fit.beta[2] * y10) : 0;
      const p90Safe = livePred - 1.2816 * (fit ? fit.rmse : 0.8);
      document.getElementById("kvBook").textContent = bookPred.toFixed(2) + "%";
      document.getElementById("kvLive").textContent = livePred.toFixed(2) + "%";
      document.getElementById("kvLiveEqn").textContent = fit ? `${fit.beta[0].toFixed(2)} ${fit.beta[1] >= 0 ? "+" : "−"} ${Math.abs(fit.beta[1]).toFixed(2)} ln(PE10) + ${fit.beta[2].toFixed(2)} Y₁₀` : "—";
      document.getElementById("kvP90").textContent = Math.max(0.5, p90Safe).toFixed(2) + "%";
      document.getElementById("kvRmseSub").textContent = `RMSE: ±${(fit ? fit.rmse : 0).toFixed(2)}%`;
      document.getElementById("kvR2").textContent = ((fit ? fit.r2 : 0) * 100).toFixed(1) + "%";
      document.getElementById("kvSampSub").textContent = `1881–${maxEndYr} (n=${olsRows.length})`;

      state.lastExport = olsRows.map((r, i) => [r.yr, r.pe10.toFixed(2), r.y10.toFixed(2), r.mwr.toFixed(2), (fit ? fit.preds[i] : 0).toFixed(2)]);

      if (state.tab === "val") {
        drawValCharts(olsRows, fit);
      } else if (state.tab === "ssr") {
        drawSsrTab(eqArr, bdArr, infArr, workY, H, rr, eqW);
      } else if (state.tab === "intl") {
        drawIntlTab();
      } else {
        drawDragTab(feeDec, taxEff, H, eqW);
      }
    }

    function drawValCharts(olsRows, fit) {
      const sc1 = setupCanvas(document.getElementById("olsCanvas"));
      if (sc1 && fit) {
        const { ctx, w, h } = sc1; const C = getThemeColors(); ctx.clearRect(0, 0, w, h);
        const pad = { l: 42, r: 16, t: 18, b: 28 }, cw = w - pad.l - pad.r, ch = h - pad.t - pad.b;
        const maxY = Math.max(10, ...olsRows.map(r => r.mwr)) * 1.05;
        const mapX = i => pad.l + (i / (olsRows.length - 1)) * cw;
        const mapY = v => pad.t + ch - (v / maxY) * ch;
        ctx.strokeStyle = C.grid; ctx.font = CANVAS_FONT; ctx.textAlign = "right"; ctx.fillStyle = C.muted;
        computeNiceLinearTicks(0, maxY, 4).forEach(v => { const y = mapY(v); ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(w - pad.r, y); ctx.stroke(); ctx.fillText(v + "%", pad.l - 5, y + 4); });
        ctx.beginPath(); ctx.strokeStyle = C.port; ctx.lineWidth = 2.2;
        olsRows.forEach((r, i) => { const x = mapX(i), y = mapY(r.mwr); if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); });
        ctx.stroke();
        ctx.beginPath(); ctx.strokeStyle = C.accent; ctx.lineWidth = 2; ctx.setLineDash([4, 3]);
        fit.preds.forEach((p, i) => { const x = mapX(i), y = mapY(p); if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); });
        ctx.stroke(); ctx.setLineDash([]);
        ctx.fillStyle = C.muted; ctx.textAlign = "center";
        olsRows.forEach((r, i) => { if (r.yr % 20 === 0 || i === 0 || i === olsRows.length - 1) ctx.fillText(String(r.yr), mapX(i), h - 8); });
      }
      const sc2 = setupCanvas(document.getElementById("capeCanvas"));
      if (sc2) {
        const { ctx, w, h } = sc2; const C = getThemeColors(); ctx.clearRect(0, 0, w, h);
        const rows = SHILLER.filter(r => r.Jan_PE10_CAPE !== null);
        const pad = { l: 42, r: 42, t: 18, b: 28 }, cw = w - pad.l - pad.r, ch = h - pad.t - pad.b;
        const maxPe = Math.max(45, ...rows.map(r => r.Jan_PE10_CAPE)) * 1.05;
        const maxY = Math.max(16, ...rows.map(r => r.Jan_10Y_Yield_pct || 0)) * 1.05;
        const mapX = i => pad.l + (i / (rows.length - 1)) * cw;
        const mapYP = v => pad.t + ch - (v / maxPe) * ch;
        const mapYY = v => pad.t + ch - (v / maxY) * ch;
        ctx.strokeStyle = C.grid; ctx.font = CANVAS_FONT;
        [0, 15, 30, 45].forEach(v => { const y = mapYP(v); ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(w - pad.r, y); ctx.stroke(); ctx.fillStyle = C.equity; ctx.textAlign = "right"; ctx.fillText(String(v), pad.l - 5, y + 4); });
        [0, 5, 10, 15].forEach(v => { ctx.fillStyle = C.bond; ctx.textAlign = "left"; ctx.fillText(v + "%", w - pad.r + 5, mapYY(v) + 4); });
        ctx.beginPath(); ctx.strokeStyle = C.equity; ctx.lineWidth = 2;
        rows.forEach((r, i) => { const x = mapX(i), y = mapYP(r.Jan_PE10_CAPE); if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); });
        ctx.stroke();
        ctx.beginPath(); ctx.strokeStyle = C.bond; ctx.lineWidth = 1.6;
        rows.forEach((r, i) => { const x = mapX(i), y = mapYY(r.Jan_10Y_Yield_pct || 0); if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); });
        ctx.stroke();
        ctx.fillStyle = C.muted; ctx.textAlign = "center";
        rows.forEach((r, i) => { if (r.Year % 25 === 0) ctx.fillText(String(r.Year), mapX(i), h - 8); });
      }
    }

    function drawSsrTab(eqArr, bdArr, infArr, workY, H, rr, eqW) {
      const billArr = SHILLER.map(r => (r.US_Short_Bill_pct || 3.0) / 100);
      const targetMult = rr / 0.04; // e.g., 50% / 4% = 12.5x
      const pts = [];
      for (let i = workY; i <= SHILLER.length - H; i++) {
        let sumAcc = 0, prod = 1;
        for (let k = i - 1; k >= i - workY; k--) {
          const rp = eqW * eqArr[k] + (1 - eqW) * billArr[k];
          const rrReal = (1 + rp) / (1 + infArr[k]) - 1;
          prod *= (1 + rrReal);
          sumAcc += prod;
        }
        const msr = (targetMult / sumAcc) * 100;
        const mwr = computeCohortMWR(eqArr, billArr, infArr, i, H, eqW, { timing: "start" });
        const lmsr = msr * (4.0 / Math.max(0.5, mwr));
        pts.push({ yr: SHILLER[i].Year, msr, mwr, lmsr });
      }
      const safemin = pts.reduce((a, b) => b.lmsr > a.lmsr ? b : a, pts[0]);
      const minL = pts.reduce((a, b) => b.lmsr < a.lmsr ? b : a, pts[0]);
      const maxM = pts.reduce((a, b) => b.msr > a.msr ? b : a, pts[0]);
      const fitS = fitOLS(pts.map(p => p.mwr), pts.map(p => [1, p.msr]));
      document.getElementById("ksSafemin").textContent = safemin.lmsr.toFixed(1) + "%";
      document.getElementById("ksSafeminSub").textContent = `${safemin.yr} cohort`;
      document.getElementById("ksMinLmsr").textContent = minL.lmsr.toFixed(1) + "%";
      document.getElementById("ksMinLmsrSub").textContent = `${minL.yr} cohort`;
      document.getElementById("ksMaxMsr").textContent = maxM.msr.toFixed(1) + "%";
      document.getElementById("ksMaxMsrSub").textContent = `${maxM.yr} cohort`;
      document.getElementById("ksR2").textContent = fitS ? (fitS.r2 * 100).toFixed(1) + "%" : "—";

      const isZh = currentLang === "zh-CN";
      document.getElementById("paradoxNote").textContent = isZh
        ? `安全提取率悖论：假设两人均在 2008 年初持有 $1,000,000。A 于 2008 年退休按 4% 提取 $40,000/年；经 2008 年大跌 40% 后，两人资产均缩水至 $600,000。B 于 2009 年退休若仍套用 4% 法则，支出骤降至 $24,000（暴跌 40%）！而采用工作期安全储蓄率 ${safemin.lmsr.toFixed(1)}% 即可消除退休时点运气导致的断崖差异。`
        : `SWR Paradox: Person A retires at the start of 2008 with $1,000,000 (4% WR = $40,000/yr real). After a 40% market drop leaves both A and B with $600,000, Person B retiring in 2009 under the 4% rule drops to $24,000/yr—a 40% cliff despite identical careers. Anchoring to a steady Safe Savings Rate (${safemin.lmsr.toFixed(1)}%) bridges accumulation and distribution smoothly.`;

      const sc = setupCanvas(document.getElementById("ssrCanvas"));
      if (sc) {
        const { ctx, w, h } = sc; const C = getThemeColors(); ctx.clearRect(0, 0, w, h);
        const pad = { l: 44, r: 16, t: 18, b: 28 }, cw = w - pad.l - pad.r, ch = h - pad.t - pad.b;
        const maxV = Math.min(45, Math.max(25, ...pts.map(p => Math.max(p.msr, p.lmsr)))) * 1.05;
        const mapX = i => pad.l + (i / (pts.length - 1)) * cw;
        const mapY = v => pad.t + ch - (Math.min(maxV, v) / maxV) * ch;
        ctx.strokeStyle = C.grid; ctx.font = CANVAS_FONT; ctx.textAlign = "right"; ctx.fillStyle = C.muted;
        computeNiceLinearTicks(0, maxV, 4).forEach(v => { const y = mapY(v); ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(w - pad.r, y); ctx.stroke(); ctx.fillText(v + "%", pad.l - 5, y + 4); });
        ctx.beginPath(); ctx.strokeStyle = C.muted; ctx.lineWidth = 1.6;
        pts.forEach((p, i) => { const x = mapX(i), y = mapY(p.msr); if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); });
        ctx.stroke();
        ctx.beginPath(); ctx.strokeStyle = C.port; ctx.lineWidth = 2.4;
        pts.forEach((p, i) => { const x = mapX(i), y = mapY(p.lmsr); if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); });
        ctx.stroke();
        ctx.fillStyle = C.muted; ctx.textAlign = "center";
        pts.forEach((p, i) => { if (p.yr % 15 === 0) ctx.fillText(String(p.yr), mapX(i), h - 8); });
      }
    }

    function drawIntlTab() {
      const isZh = currentLang === "zh-CN";
      // DMS Bar Chart
      const sc1 = setupCanvas(document.getElementById("dmsCanvas"));
      if (sc1) {
        const { ctx, w, h } = sc1; const C = getThemeColors(); ctx.clearRect(0, 0, w, h);
        const pad = { l: 96, r: 22, t: 12, b: 24 }, cw = w - pad.l - pad.r, ch = h - pad.t - pad.b;
        const mapX = v => pad.l + (v / 4.5) * cw;
        const rowH = ch / DMS.length;
        ctx.strokeStyle = C.grid; ctx.font = '10.5px ui-monospace, monospace';
        [0, 1, 2, 3, 4].forEach(v => {
          const x = mapX(v); ctx.beginPath(); ctx.moveTo(x, pad.t); ctx.lineTo(x, pad.t + ch); ctx.stroke();
          ctx.fillStyle = C.muted; ctx.textAlign = "center"; ctx.fillText(v + "%", x, h - 6);
        });
        DMS.forEach((r, i) => {
          const y = pad.t + i * rowH;
          ctx.fillStyle = r.SAFEMAX_50_50_pct >= 3.9 ? C.success : (r.SAFEMAX_50_50_pct < 2 ? C.danger : C.accent);
          ctx.fillRect(pad.l, y + 1.5, Math.max(2, mapX(r.SAFEMAX_50_50_pct) - pad.l), Math.max(4, rowH - 3));
          ctx.fillStyle = C.textSoft; ctx.textAlign = "right";
          ctx.fillText(r.Country_Or_Index, pad.l - 6, y + rowH * 0.72);
        });
      }

      // Ex. 5.26-5.28 2-asset vs 5-asset Markowitz Frontier
      const means5 = [0.065, 0.055, 0.065, 0.007, -0.003];
      const stds5 = [0.20, 0.16, 0.22, 0.07, 0.04];
      const corr5 = [
        [1, 0.7, 0.6, 0.1, 0.1],
        [0.7, 1, 0.5, 0.3, 0.4],
        [0.6, 0.5, 1, -0.1, -0.1],
        [0.1, 0.3, -0.1, 1, 0.7],
        [0.1, 0.4, -0.1, 0.7, 1],
      ];
      const front5 = solveEfficientFrontier(means5, stds5, corr5, 36);
      const front2 = solveEfficientFrontier([0.065, 0.007], [0.20, 0.07], [[1, 0.1], [0.1, 1]], 30);
      // Evaluate 10%-fail SWR along both frontiers
      const rng = mulberry32(state.seed);
      const N = 1500, H = 30;
      const Z = Array.from({ length: N }, () => Array.from({ length: H }, () => randNormal(rng)));
      const swr10 = (mu, sd) => {
        const arr = new Float64Array(N);
        const s2 = sd * sd, vLog = Math.log(1 + s2 / ((1 + mu) ** 2));
        const mLog = Math.log(1 + mu) - 0.5 * vLog, sLog = Math.sqrt(vLog);
        for (let i = 0; i < N; i++) {
          let den = 0, cp = 1;
          for (let t = 0; t < H; t++) { den += 1 / cp; cp *= Math.exp(mLog + sLog * Z[i][t]); }
          arr[i] = 100 / den;
        }
        arr.sort(); return quantileSorted(arr, 0.10);
      };
      const best2 = front2.map(p => ({ ...p, wr: swr10(p.mean, p.std) })).reduce((a, b) => b.wr > a.wr ? b : a);
      const best5 = front5.map(p => ({ ...p, wr: swr10(p.mean, p.std) })).reduce((a, b) => b.wr > a.wr ? b : a);
      const w5 = best5.weights.map(x => (x * 100).toFixed(1) + "%");
      document.getElementById("fiveAssetSummary").textContent = isZh
        ? `Ex. 5.28 求解结果 — 2资产最优 10%失败提取率: ${best2.wr.toFixed(2)}% (${(best2.weights[0]*100).toFixed(1)}%美股 / ${(best2.weights[1]*100).toFixed(1)}%美债) → 扩展至5资产提升至: ${best5.wr.toFixed(2)}% (美股 ${w5[0]} / REITs ${w5[1]} / 国际EAFE ${w5[2]} / 美债 ${w5[3]} / 国库券 ${w5[4]})。`
        : `Ex. 5.28 Frontier Result — 2-Asset Optimal 10%-Fail WR: ${best2.wr.toFixed(2)}% (${(best2.weights[0]*100).toFixed(1)}% US Stocks / ${(best2.weights[1]*100).toFixed(1)}% US Bonds) → 5-Asset Optimal: ${best5.wr.toFixed(2)}% (US Stocks ${w5[0]} / REITs ${w5[1]} / EAFE ${w5[2]} / US Bonds ${w5[3]} / Bills ${w5[4]}).`;

      const sc2 = setupCanvas(document.getElementById("fiveAssetCanvas"));
      if (sc2) {
        const { ctx, w, h } = sc2; const C = getThemeColors(); ctx.clearRect(0, 0, w, h);
        const pad = { l: 44, r: 16, t: 18, b: 28 }, cw = w - pad.l - pad.r, ch = h - pad.t - pad.b;
        const mapX = sd => pad.l + (sd / 0.22) * cw;
        const mapY = mu => pad.t + ch - (mu / 0.08) * ch;
        ctx.strokeStyle = C.grid; ctx.font = CANVAS_FONT; ctx.textAlign = "right"; ctx.fillStyle = C.muted;
        [0, 2, 4, 6, 8].forEach(v => { const y = mapY(v / 100); ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(w - pad.r, y); ctx.stroke(); ctx.fillText(v + "%", pad.l - 5, y + 4); });
        ctx.beginPath(); ctx.strokeStyle = C.muted; ctx.lineWidth = 2;
        front2.forEach((p, i) => { const x = mapX(p.std), y = mapY(p.mean); if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); });
        ctx.stroke();
        ctx.beginPath(); ctx.strokeStyle = C.success; ctx.lineWidth = 2.6;
        front5.forEach((p, i) => { const x = mapX(p.std), y = mapY(p.mean); if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); });
        ctx.stroke();
        ctx.beginPath(); ctx.arc(mapX(best2.std), mapY(best2.mean), 5, 0, Math.PI * 2); ctx.fillStyle = C.muted; ctx.fill();
        ctx.beginPath(); ctx.arc(mapX(best5.std), mapY(best5.mean), 6, 0, Math.PI * 2); ctx.fillStyle = C.success; ctx.fill();
        ctx.fillStyle = C.muted; ctx.textAlign = "center";
        [0, 5, 10, 15, 20].forEach(s => ctx.fillText("σ=" + s + "%", mapX(s / 100), h - 8));
      }

      document.getElementById("dmsHead").innerHTML = `<tr><th>${isZh ? "国家/指数" : "Country / Index"}</th><th>50/50 SAFEMAX</th><th>${isZh ? "最差年份" : "Year"}</th><th>P10 MWR</th><th>4% ${isZh ? "失败率" : "Fail %"}</th><th>5% ${isZh ? "失败率" : "Fail %"}</th></tr>`;
      document.getElementById("dmsBody").innerHTML = DMS.map(r => `<tr>
        <td><strong>${r.Country_Or_Index}</strong></td>
        <td class="${r.SAFEMAX_50_50_pct >= 4 ? 'pos' : (r.SAFEMAX_50_50_pct < 2 ? 'neg' : '')}"><strong>${r.SAFEMAX_50_50_pct.toFixed(1)}%</strong></td>
        <td>${r.SAFEMAX_Year}</td><td>${r.Pct10_MWR_pct.toFixed(1)}%</td><td>${r.WR4_Fail_pct}%</td><td>${r.WR5_Fail_pct}%</td>
      </tr>`).join("");
    }

    function drawDragTab(feeDec, taxEff, H, eqW) {
      const eqN = NYU.map(r => r.NYU_SP500_pct / 100);
      const bdN = NYU.map(r => r.NYU_US_10Y_TBond_pct / 100);
      const infN = NYU.map(r => r.NYU_US_CPI_Inflation_pct / 100);
      const nC = NYU.length - H + 1;
      const pureM = [], netM = [], yrsN = [];
      for (let i = 0; i < nC; i++) {
        yrsN.push(NYU[i].Year);
        pureM.push(computeCohortMWR(eqN, bdN, infN, i, H, eqW, { timing: "start" }));
        netM.push(computeCohortMWR(eqN, bdN, infN, i, H, eqW, { timing: "start", feeDec, taxEff }));
      }
      document.getElementById("kdPure").textContent = Math.min(...pureM).toFixed(2) + "%";
      document.getElementById("kdPureSub").textContent = `Mean ${meanArr(pureM).toFixed(2)}%`;
      document.getElementById("kdNet").textContent = Math.min(...netM).toFixed(2) + "%";
      document.getElementById("kdNetSub").textContent = `-${(Math.min(...pureM) - Math.min(...netM)).toFixed(2)} pp`;

      // Ex. 5.13 Shiller Mistiming vs Contrarian
      const sRows = SHILLER.filter(r => r.Year >= 1881);
      const eqS = sRows.map(r => r.Shiller_SP500_TR_pct / 100);
      const bdS = sRows.map(r => r.Shiller_10Y_TBond_pct / 100);
      const infS = sRows.map(r => r.Shiller_US_CPI_pct / 100);
      const mistimeW = [], contraW = [], histPe = [];
      for (let i = 0; i < sRows.length; i++) {
        const pe = sRows[i].Jan_PE10_CAPE || 15;
        histPe.push(pe);
        const sortedPe = histPe.slice().sort((a, b) => a - b);
        const medPe = quantileSorted(sortedPe, 0.5);
        const avgPe = meanArr(histPe);
        mistimeW.push(pe > (4 / 3) * medPe ? 0.75 : pe < (2 / 3) * medPe ? 0.0 : 0.50);
        contraW.push(pe > (4 / 3) * avgPe ? 0.25 : pe < (2 / 3) * avgPe ? 0.75 : 0.50);
      }
      const fixS = [], misS = [], conS = [], yrsS = [];
      for (let i = 0; i <= sRows.length - H; i++) {
        yrsS.push(sRows[i].Year);
        fixS.push(computeCohortMWR(eqS, bdS, infS, i, H, 0.50));
        misS.push(computeCohortMWR(eqS, bdS, infS, i, H, 0.50, { eqGlideWeights: mistimeW.slice(i, i + H) }));
        conS.push(computeCohortMWR(eqS, bdS, infS, i, H, 0.50, { eqGlideWeights: contraW.slice(i, i + H) }));
      }
      document.getElementById("kdMistime").textContent = Math.min(...misS).toFixed(2) + "%";
      document.getElementById("kdContra").textContent = Math.min(...conS).toFixed(2) + "%";

      const plotLines = (canvasId, yrs, seriesList) => {
        const sc = setupCanvas(document.getElementById(canvasId));
        if (!sc) return;
        const { ctx, w, h } = sc; const C = getThemeColors(); ctx.clearRect(0, 0, w, h);
        const pad = { l: 42, r: 16, t: 18, b: 28 }, cw = w - pad.l - pad.r, ch = h - pad.t - pad.b;
        const maxV = Math.max(10, ...seriesList.flatMap(s => s[0])) * 1.05;
        const mapX = i => pad.l + (i / (yrs.length - 1)) * cw;
        const mapY = v => pad.t + ch - (v / maxV) * ch;
        ctx.strokeStyle = C.grid; ctx.font = CANVAS_FONT; ctx.textAlign = "right"; ctx.fillStyle = C.muted;
        computeNiceLinearTicks(0, maxV, 4).forEach(v => { const y = mapY(v); ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(w - pad.r, y); ctx.stroke(); ctx.fillText(v + "%", pad.l - 5, y + 4); });
        seriesList.forEach(([arr, col, lw]) => {
          ctx.beginPath(); ctx.strokeStyle = col; ctx.lineWidth = lw;
          arr.forEach((v, i) => { const x = mapX(i), y = mapY(v); if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); });
          ctx.stroke();
        });
        ctx.fillStyle = C.muted; ctx.textAlign = "center";
        yrs.forEach((y, i) => { if (y % 20 === 0 || i === 0 || i === yrs.length - 1) ctx.fillText(String(y), mapX(i), h - 8); });
      };

      const C = getThemeColors();
      plotLines("dragCanvas", yrsN, [[pureM, C.success, 2.2], [netM, C.port, 2.2]]);
      plotLines("timingCanvas", yrsS, [[fixS, C.muted, 1.6], [misS, C.danger, 2.0], [conS, C.success, 2.2]]);
    }

    function applyPreset(name) {
      document.querySelectorAll(".preset-btn").forEach(b => b.classList.toggle("active", b.dataset.preset === name));
      if (name === "ex58") {
        document.getElementById("testPe10").value = "28.2"; document.getElementById("testY10").value = "2.45";
        document.querySelector('[data-tab="val"]').click();
      } else if (name === "ex59") {
        document.querySelector('[data-tab="ssr"]').click();
      } else if (name === "ex526") {
        document.querySelector('[data-tab="intl"]').click();
      } else if (name === "ex512") {
        document.getElementById("feeBps").value = "100";
        document.querySelector('[data-tab="drag"]').click();
      }
      updateAll();
    }

    function onThemeOrLangChange() { updateAll(); }

    document.querySelectorAll(".tab-btn").forEach(b => {
      b.addEventListener("click", () => {
        state.tab = b.dataset.tab;
        document.querySelectorAll(".tab-btn").forEach(x => { x.classList.toggle("active", x === b); x.setAttribute("aria-selected", x === b ? "true" : "false"); });
        const map = { val: "paneVal", ssr: "paneSsr", intl: "paneIntl", drag: "paneDrag" };
        Object.entries(map).forEach(([k, id]) => document.getElementById(id).style.display = k === state.tab ? "block" : "none");
        updateAll();
      });
    });
    document.querySelectorAll(".preset-btn").forEach(b => b.addEventListener("click", () => applyPreset(b.dataset.preset)));
    document.getElementById("btnReset").addEventListener("click", () => applyPreset("ex58"));
    document.getElementById("btnExportCsv").addEventListener("click", () => {
      downloadCsv("pfau_ch5_valuations_mwr.csv", ["Year", "Jan_PE10", "Jan_10Y_Yield_pct", "Actual_MWR_pct", "OLS_Pred_MWR_pct"], state.lastExport);
    });
    ["testPe10", "testY10", "eqPctSlider", "retYrs", "olsSample", "workYrs", "replRatePct", "feeBps", "margTaxPct"].forEach(id => {
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
        slug="valuations-and-savings",
        title_en="Valuations, Safe Savings & Drag",
        extra_css="",
        body_html=body_html,
        embedded_data_js=embedded,
        page_i18n=page_i18n,
        page_js=page_js,
    )


if __name__ == "__main__":
    build_ch5a()
