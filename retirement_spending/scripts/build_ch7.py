#!/usr/bin/env python3
"""Build Lab 7 (Chapter 7): STRIPS & TIPS Bond Ladders, Duration/Convexity & Time-Segmentation Buckets."""

from shared_shell import dump_json_inline, load_csv_records, render_page
from shared_sim_js import SHARED_SIM_JS


def build_ch7():
    quotes = load_csv_records("pfau_2017_strips_tips_quotes.csv")
    curves = load_csv_records("us_treasury_tips_yields.csv")
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
          <button type="button" class="preset-btn active" data-preset="wsj2017">
            <span class="p-title" data-i18n="pre_w17_t">Ex. 7.11–7.12 · 2017 WSJ</span>
            <span class="p-meta" data-i18n="pre_w17_m">$1.04M STRIPS / $1.07M TIPS</span>
          </button>
          <button type="button" class="preset-btn" data-preset="latest">
            <span class="p-title" data-i18n="pre_lat_t">2026 Live Yields</span>
            <span class="p-meta" data-i18n="pre_lat_m">2.6–3.2% Real TIPS Curve</span>
          </button>
          <button type="button" class="preset-btn" data-preset="duration">
            <span class="p-title" data-i18n="pre_dur_t">Ex. 7.2 · Duration</span>
            <span class="p-meta" data-i18n="pre_dur_m">30Y 2% Bond (±1% Yield)</span>
          </button>
          <button type="button" class="preset-btn" data-preset="buckets">
            <span class="p-title" data-i18n="pre_bkt_t">Ex. 7.14–7.21 · Buckets</span>
            <span class="p-meta" data-i18n="pre_bkt_m">10Y Ladder vs Total Return</span>
          </button>
        </div>
      </div>

      <div class="side-section">
        <div class="sec-head-static"><h2 class="sec-title" data-i18n="sec_ladder">Bond Ladder Inputs (Ex. 7.11–7.12)</h2></div>
        <div class="control-group">
          <label for="curveSel"><span data-i18n="lbl_curve">Treasury / TIPS Yield Curve</span></label>
          <select id="curveSel"></select>
        </div>
        <div class="control-group row-2">
          <div>
            <label for="ladSpend"><span data-i18n="lbl_lspend">Year-1 Spend ($)</span></label>
            <div class="currency-field"><span class="currency-prefix">$</span><input type="text" id="ladSpend" value="40,000" inputmode="numeric" /></div>
          </div>
          <div>
            <label for="ladBudget"><span data-i18n="lbl_lbudg">Portfolio Budget ($)</span></label>
            <div class="currency-field"><span class="currency-prefix">$</span><input type="text" id="ladBudget" value="1,000,000" inputmode="numeric" /></div>
          </div>
        </div>
        <div class="control-group row-2">
          <div>
            <label for="ladHorizon"><span data-i18n="lbl_lhor">Ladder Rungs (yrs)</span></label>
            <input type="number" id="ladHorizon" value="30" min="5" max="30" step="1" />
          </div>
          <div>
            <label for="ladCola"><span data-i18n="lbl_lcola">STRIPS COLA (%)</span></label>
            <input type="number" id="ladCola" value="2.0" min="0.0" max="5.0" step="0.25" />
          </div>
        </div>
      </div>

      <div class="side-section">
        <div class="sec-head-static"><h2 class="sec-title" data-i18n="sec_bond">Single Bond Duration (Ex. 7.1–7.9)</h2></div>
        <div class="control-group row-2">
          <div>
            <label for="bMat"><span data-i18n="lbl_bmat">Maturity T (yrs)</span></label>
            <input type="number" id="bMat" value="30" min="1" max="30" step="1" />
          </div>
          <div>
            <label for="bCoup"><span data-i18n="lbl_bcoup">Coupon Rate (%)</span></label>
            <input type="number" id="bCoup" value="2.0" min="0" max="10" step="0.25" />
          </div>
        </div>
        <div class="control-group row-2">
          <div>
            <label for="bY0"><span data-i18n="lbl_by0">Initial YTM (%)</span></label>
            <input type="number" id="bY0" value="2.0" min="-2" max="12" step="0.25" />
          </div>
          <div>
            <label for="bShock"><span data-i18n="lbl_bshock">Yield Shock Δy (%)</span></label>
            <input type="number" id="bShock" value="1.0" min="-4" max="5" step="0.25" />
          </div>
        </div>
      </div>

      <div class="side-section">
        <div class="sec-head-static"><h2 class="sec-title" data-i18n="sec_bkt">Time-Segmentation MC (Ex. 7.14+)</h2></div>
        <div class="control-group row-2">
          <div>
            <label for="bktYrs"><span data-i18n="lbl_bktyrs">Ladder Length H (yrs)</span></label>
            <input type="number" id="bktYrs" value="10" min="3" max="20" step="1" />
          </div>
          <div>
            <label for="bktHor"><span data-i18n="lbl_bkthor">Plan Horizon (yrs)</span></label>
            <input type="number" id="bktHor" value="40" min="25" max="45" step="5" />
          </div>
        </div>
        <div class="control-group">
          <label><span data-i18n="lbl_bktmc">Monte Carlo Paths</span></label>
          <div class="seg-ctl" id="bktMcCtl">
            <button type="button" class="active" data-val="1000">1,000</button>
            <button type="button" class="btn-m" data-val="2500">2,500</button>
          </div>
        </div>
      </div>
    </aside>

    <section class="workspace" aria-label="Simulation outputs" data-i18n-aria-label="aria_workspace">
      <div class="results-shell">
        <div class="tabs-bar">
          <div class="tab-strip" role="tablist">
            <button type="button" class="tab-btn active" role="tab" aria-selected="true" data-tab="ladder" data-i18n="tab_ladder">STRIPS &amp; TIPS Ladder (Ex. 7.11–7.12)</button>
            <button type="button" class="tab-btn" role="tab" aria-selected="false" data-tab="duration" data-i18n="tab_duration">Duration, Convexity &amp; Pull-to-Par</button>
            <button type="button" class="tab-btn" role="tab" aria-selected="false" data-tab="buckets" data-i18n="tab_buckets">Time Segmentation vs Total Return</button>
          </div>
        </div>

        <div class="results-body">
          <div id="paneLadder" class="tab-pane">
            <div class="kpis kpis-4 kpis-flush-top">
              <div class="kpi"><div class="kpi-label" data-i18n="kl_strips">STRIPS Ladder Cost</div><div class="kpi-val" id="klStrips">—</div><div class="kpi-sub" id="klStripsSub">—</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="kl_tips">TIPS Ladder Cost</div><div class="kpi-val" id="klTips">—</div><div class="kpi-sub" id="klTipsSub">—</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="kl_aff">Years Affordable on Budget</div><div class="kpi-val pos" id="klAff">—</div><div class="kpi-sub" id="klAffSub">—</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="kl_bei">Ladder Breakeven Inflation</div><div class="kpi-val" id="klBei">—</div><div class="kpi-sub" id="klBeiSub">—</div></div>
            </div>

            <div class="panel-block">
              <div class="legend">
                <strong data-i18n="ttl_lad_chart">Annual Rung Purchase Cost: Forward STRIPS vs. Backward-Induction TIPS</strong>
                <div class="legend-items">
                  <div class="legend-item"><span class="swatch" style="background:var(--bond);"></span><span data-i18n="leg_strips">STRIPS Rung Cost</span></div>
                  <div class="legend-item"><span class="swatch" style="background:var(--port);"></span><span data-i18n="leg_tips">TIPS Rung Cost (incl. Gap Reserves)</span></div>
                </div>
              </div>
              <div class="chart-wrap"><canvas id="ladCanvas" height="245"></canvas><div class="tooltip" id="ladTip"></div></div>
            </div>

            <div class="panel-block">
              <div class="card-title">
                <h3 class="sec-title" data-i18n="ttl_lad_tbl">Rung-by-Rung Ladder Schedule (Gap Years Reserve Un-Discounted Cash in Preceding Maturity)</h3>
              </div>
              <div class="table-container" style="max-height:330px;"><table><thead id="ladHead"></thead><tbody id="ladBody"></tbody></table></div>
            </div>
          </div>

          <div id="paneDuration" class="tab-pane" style="display:none;">
            <div class="kpis kpis-4 kpis-flush-top">
              <div class="kpi"><div class="kpi-label" data-i18n="kd_px">Exact Initial Price / $1,000</div><div class="kpi-val" id="kdPx">—</div><div class="kpi-sub" id="kdPxSub">—</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="kd_dur">Modified Duration / Convexity</div><div class="kpi-val" id="kdDur">—</div><div class="kpi-sub" id="kdDurSub">—</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="kd_up">Price Change at -Δy</div><div class="kpi-val pos" id="kdUp">—</div><div class="kpi-sub" id="kdUpSub">—</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="kd_dn">Price Change at +Δy</div><div class="kpi-val neg" id="kdDn">—</div><div class="kpi-sub" id="kdDnSub">—</div></div>
            </div>

            <div class="split-grid">
              <div class="grid-cell">
                <div class="legend"><strong data-i18n="ttl_ex72">Ex. 7.2: Exact Price vs. Linear Duration vs. Convexity Curve</strong></div>
                <div class="chart-wrap"><canvas id="durCurveCanvas" height="255"></canvas><div class="tooltip" id="durCurveTip"></div></div>
              </div>
              <div class="grid-cell">
                <div class="legend"><strong data-i18n="ttl_ex79">Ex. 7.9: Individual Bond Pull-to-Par vs. Perpetual Bond Fund ($1k @ +Δy)</strong></div>
                <div class="chart-wrap"><canvas id="ptpCanvas" height="255"></canvas><div class="tooltip" id="ptpTip"></div></div>
              </div>
            </div>

            <div class="panel-block">
              <div class="card-title"><h3 class="sec-title" data-i18n="ttl_dur_mat">Interest-Rate Sensitivity Matrix (Maturity × Yield Shock, 2% Coupon)</h3></div>
              <div class="table-container" style="max-height:none;"><table><thead id="durHead"></thead><tbody id="durBody"></tbody></table></div>
            </div>
          </div>

          <div id="paneBuckets" class="tab-pane" style="display:none;">
            <div class="kpis kpis-4 kpis-flush-top">
              <div class="kpi"><div class="kpi-label" data-i18n="kb_cross">Ex. 7.13 Equity Beat Bonds Horizon</div><div class="kpi-val pos" id="kbCross">—</div><div class="kpi-sub" id="kbCrossSub">—</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="kb_bkt1">Initial H-Yr Bond Bucket</div><div class="kpi-val" id="kbBkt1">—</div><div class="kpi-sub" id="kbBkt1Sub">—</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="kb_crit">Ex. 7.18 Critical Path r* (45y)</div><div class="kpi-val" id="kbCrit">—</div><div class="kpi-sub" id="kbCritSub">—</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="kb_best">Best Bucket vs Total Return</div><div class="kpi-val" id="kbBest">—</div><div class="kpi-sub" id="kbBestSub">—</div></div>
            </div>

            <div class="split-grid">
              <div class="grid-cell">
                <div class="legend">
                  <strong data-i18n="ttl_ex713">Ex. 7.13: Historical Worst-Case Annualized Return by Horizon (1–30Y)</strong>
                  <div class="legend-items">
                    <div class="legend-item"><span class="swatch" style="background:var(--equity);"></span><span data-i18n="leg_eq">Stocks (Real)</span></div>
                    <div class="legend-item"><span class="swatch" style="background:var(--bond);"></span><span data-i18n="leg_bd">10Y Treasuries (Real)</span></div>
                  </div>
                </div>
                <div class="chart-wrap"><canvas id="crossCanvas" height="245"></canvas><div class="tooltip" id="crossTip"></div></div>
              </div>
              <div class="grid-cell">
                <div class="legend"><strong data-i18n="ttl_bkt_bar">Ex. 7.14–7.21: Success Rate (%) Across 7 Bucket &amp; Total Return Rules</strong></div>
                <div class="chart-wrap"><canvas id="bktBarCanvas" height="245"></canvas><div class="tooltip" id="bktBarTip"></div></div>
              </div>
            </div>

            <div class="panel-block">
              <div class="card-title"><h3 class="sec-title" data-i18n="ttl_bkt_tbl">Ex. 7.14–7.21: 7-Strategy Monte Carlo Comparison ($1M Start, $40k + 2%/yr Spend)</h3></div>
              <div class="table-container" style="max-height:none;"><table><thead id="bktHead"></thead><tbody id="bktBody"></tbody></table></div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </main>
"""

    page_i18n = {
        "page_title": {"en-UK": "Bond Ladders & Time Segmentation · Ch. 7", "zh-CN": "债券阶梯与时间分段蓄水池 · 第7章"},
        "app_title": {"en-UK": "Ch. 7 · Bond Ladders, Duration & Time Segmentation", "zh-CN": "第7章 · STRIPS/TIPS 阶梯、久期与时间分段"},
        "sec_presets": {"en-UK": "Book Exhibit Presets", "zh-CN": "全书图表预设"},
        "pre_w17_t": {"en-UK": "Ex. 7.11–7.12 · 2017 WSJ", "zh-CN": "图 7.11–7.12 · 2017 WSJ"},
        "pre_w17_m": {"en-UK": "$1.04M STRIPS / $1.07M TIPS", "zh-CN": "$1.04M STRIPS / $1.07M TIPS"},
        "pre_lat_t": {"en-UK": "2026 Live Yields", "zh-CN": "2026 最新国债/TIPS 曲线"},
        "pre_lat_m": {"en-UK": "2.6–3.2% Real TIPS Curve", "zh-CN": "真实利率约 2.6%–3.2%"},
        "pre_dur_t": {"en-UK": "Ex. 7.2 · Duration", "zh-CN": "图 7.2 · 久期与凸性"},
        "pre_dur_m": {"en-UK": "30Y 2% Bond (±1% Yield)", "zh-CN": "30年期 2% 票息债券 (±1%)"},
        "pre_bkt_t": {"en-UK": "Ex. 7.14–7.21 · Buckets", "zh-CN": "图 7.14–7.21 · 蓄水池策略"},
        "pre_bkt_m": {"en-UK": "10Y Ladder vs Total Return", "zh-CN": "10年债券阶梯 vs 总回报法"},
        "sec_ladder": {"en-UK": "Bond Ladder Inputs (Ex. 7.11–7.12)", "zh-CN": "债券阶梯参数 (图 7.11–7.12)"},
        "lbl_curve": {"en-UK": "Treasury / TIPS Yield Curve", "zh-CN": "收益率曲线数据源"},
        "lbl_lspend": {"en-UK": "Year-1 Spend ($)", "zh-CN": "首年支出目标 ($)"},
        "lbl_lbudg": {"en-UK": "Portfolio Budget ($)", "zh-CN": "可用资金预算 ($)"},
        "lbl_lhor": {"en-UK": "Ladder Rungs (yrs)", "zh-CN": "阶梯涵盖年限 (年)"},
        "lbl_lcola": {"en-UK": "STRIPS COLA (%)", "zh-CN": "STRIPS 年递增率 (%)"},
        "sec_bond": {"en-UK": "Single Bond Duration (Ex. 7.1–7.9)", "zh-CN": "单只债券定价与久期 (图 7.1–7.9)"},
        "lbl_bmat": {"en-UK": "Maturity T (yrs)", "zh-CN": "剩余到期年限 T"},
        "lbl_bcoup": {"en-UK": "Coupon Rate (%)", "zh-CN": "票面利率 (%)"},
        "lbl_by0": {"en-UK": "Initial YTM (%)", "zh-CN": "初始到期收益率 (%)"},
        "lbl_bshock": {"en-UK": "Yield Shock Δy (%)", "zh-CN": "利率冲击幅度 Δy (%)"},
        "sec_bkt": {"en-UK": "Time-Segmentation MC (Ex. 7.14+)", "zh-CN": "时间分段蒙特卡洛 (图 7.14+)"},
        "lbl_bktyrs": {"en-UK": "Ladder Length H (yrs)", "zh-CN": "债券池覆盖年限 H"},
        "lbl_bkthor": {"en-UK": "Plan Horizon (yrs)", "zh-CN": "退休总期限 (年)"},
        "lbl_bktmc": {"en-UK": "Monte Carlo Paths", "zh-CN": "蒙特卡洛路径数"},
        "tab_ladder": {"en-UK": "STRIPS & TIPS Ladder (Ex. 7.11–7.12)", "zh-CN": "STRIPS 与 TIPS 阶梯定价"},
        "tab_duration": {"en-UK": "Duration, Convexity & Pull-to-Par", "zh-CN": "久期、凸性与到期回归面值"},
        "tab_buckets": {"en-UK": "Time Segmentation vs Total Return", "zh-CN": "时间分段蓄水池 vs 总回报"},
        "kl_strips": {"en-UK": "STRIPS Ladder Cost", "zh-CN": "STRIPS 阶梯总成本"},
        "kl_tips": {"en-UK": "TIPS Ladder Cost", "zh-CN": "TIPS 阶梯总成本"},
        "kl_aff": {"en-UK": "Years Affordable on Budget", "zh-CN": "预算可锁定年限"},
        "kl_bei": {"en-UK": "Ladder Breakeven Inflation", "zh-CN": "阶梯盈亏平衡通胀率"},
        "ttl_lad_chart": {"en-UK": "Annual Rung Purchase Cost: Forward STRIPS vs. Backward-Induction TIPS", "zh-CN": "逐年购买成本：正向 STRIPS vs 逆向归纳 TIPS（含缺口年份预留）"},
        "leg_strips": {"en-UK": "STRIPS Rung Cost", "zh-CN": "STRIPS 单期成本"},
        "leg_tips": {"en-UK": "TIPS Rung Cost (incl. Gap Reserves)", "zh-CN": "TIPS 单期成本（含缺口预留）"},
        "ttl_lad_tbl": {"en-UK": "Rung-by-Rung Ladder Schedule (Gap Years Reserve Un-Discounted Cash in Preceding Maturity)", "zh-CN": "逐年阶梯持仓明细（缺口年份在上一到期日预留无折现现金）"},
        "kd_px": {"en-UK": "Exact Initial Price / $1,000", "zh-CN": "初始精准价格 (每$1,000)"},
        "kd_dur": {"en-UK": "Modified Duration / Convexity", "zh-CN": "修正久期 / 凸性"},
        "kd_up": {"en-UK": "Price Change at -Δy", "zh-CN": "利率下降 -Δy 时涨幅"},
        "kd_dn": {"en-UK": "Price Change at +Δy", "zh-CN": "利率上升 +Δy 时跌幅"},
        "ttl_ex72": {"en-UK": "Ex. 7.2: Exact Price vs. Linear Duration vs. Convexity Curve", "zh-CN": "图 7.2：精确债券价格 vs 线性久期近似曲线"},
        "ttl_ex79": {"en-UK": "Ex. 7.9: Individual Bond Pull-to-Par vs. Perpetual Bond Fund ($1k @ +Δy)", "zh-CN": "图 7.9：持有单券回归面值 Pull-to-Par vs 滚动债券基金"},
        "ttl_dur_mat": {"en-UK": "Interest-Rate Sensitivity Matrix (Maturity × Yield Shock, Selected Coupon)", "zh-CN": "利率冲击价格敏感性矩阵（到期年限 × 收益率变动）"},
        "kb_cross": {"en-UK": "Ex. 7.13 Equity Beat Bonds Horizon", "zh-CN": "图 7.13 股票最差超越债券年限"},
        "kb_bkt1": {"en-UK": "Initial H-Yr Bond Bucket", "zh-CN": "期初 H 年债券阶梯占比"},
        "kb_crit": {"en-UK": "Ex. 7.18 Critical Path r* (45y)", "zh-CN": "图 7.18 关键路径门槛 r*"},
        "kb_best": {"en-UK": "Best Bucket vs Total Return", "zh-CN": "最优蓄水池 vs 固定总回报"},
        "ttl_ex713": {"en-UK": "Ex. 7.13: Historical Worst-Case Annualized Return by Horizon (1–30Y)", "zh-CN": "图 7.13：不同持有期历史最差实际年化收益率对比 (1–30年)"},
        "leg_eq": {"en-UK": "Stocks (Real)", "zh-CN": "股票 (实际收益)"},
        "leg_bd": {"en-UK": "10Y Treasuries (Real)", "zh-CN": "10年期国债 (实际收益)"},
        "ttl_bkt_bar": {"en-UK": "Ex. 7.14–7.21: Success Rate (%) Across 7 Bucket & Total Return Rules", "zh-CN": "表 7.14–7.21：7种时间分段与匹配总回报法则成功率 (%)"},
        "ttl_bkt_tbl": {"en-UK": "Ex. 7.14–7.21: 7-Strategy Monte Carlo Comparison", "zh-CN": "表 7.14–7.21：7种策略蒙特卡洛分布与期初成本详情"}
    }

    embedded = (
        f"    const QUOTES_2017 = {dump_json_inline(quotes)};\n"
        f"    const CURVES = {dump_json_inline(curves)};\n"
        f"    const NYU = {dump_json_inline(nyu)};\n"
        f"    const SHILLER = {dump_json_inline(shiller)};\n"
        + SHARED_SIM_JS
    )

    page_js = r"""
    const state = { tab: "ladder", mcPaths: 1000, ladRows: [], lastExport: [], crossRows: [], bktSummary: [] };
    const ch3aCal = calibrateCh3AEngine(SHILLER);

    // Populate curve selector
    (function populateCurves() {
      const sel = document.getElementById("curveSel");
      const o1 = document.createElement("option");
      o1.value = "wsj2017";
      o1.textContent = "WSJ Jan 3, 2017 (Pfau Book Quotes)";
      sel.appendChild(o1);
      for (let i = CURVES.length - 1; i >= 0; i--) {
        const c = CURVES[i];
        const opt = document.createElement("option");
        opt.value = c.Date;
        opt.textContent = `${c.Label} (10Y Nom ${c.DGS10}% / Real ${c.DFII10 ?? "—"}%)`;
        sel.appendChild(opt);
      }
      sel.value = "wsj2017";
    })();

    function interpCurve(knots, t) {
      if (t <= knots[0][0]) return knots[0][1];
      if (t >= knots[knots.length - 1][0]) return knots[knots.length - 1][1];
      for (let i = 0; i < knots.length - 1; i++) {
        const [x0, y0] = knots[i], [x1, y1] = knots[i + 1];
        if (t >= x0 && t <= x1) return y0 + ((t - x0) / (x1 - x0)) * (y1 - y0);
      }
      return knots[0][1];
    }

    function solveLadder(curveKey, spend1, horizon, colaPct, budget) {
      const cola = colaPct / 100;
      const scaleSpend = spend1 / 40000;
      const rows = [];
      let stripsTotal = 0, tipsTotal = 0;
      let stripsIrrCf = [], tipsIrrCf = [];
      let yr1TipsCash = 0, yr1TipsCoup = 0;

      if (curveKey === "wsj2017") {
        // Exact WSJ Jan 3, 2017 Forward STRIPS + Backward-Induction TIPS
        const slice = QUOTES_2017.slice(0, horizon);
        const N = slice.length;
        // 1. Forward STRIPS (Price is per $1,000 maturity face)
        const sCosts = new Float64Array(N), sTargs = new Float64Array(N), sShares = new Float64Array(N);
        for (let i = 0; i < N; i++) {
          const target = spend1 * Math.pow(1 + cola, i);
          const shares = target / 1000.0;
          const cost = shares * slice[i].STRIPS_Ask_Price;
          sTargs[i] = target; sShares[i] = shares; sCosts[i] = cost;
          stripsTotal += cost;
        }
        // 2. Backward-Induction TIPS (Shares in $1,000 original face units; real payoff at maturity = accrued * (1 + coupon/100))
        const tShares = new Float64Array(N), tCosts = new Float64Array(N), tCouponsRec = new Float64Array(N);
        let gapReserve = 0;
        const coupSumAt = tIdx => {
          let cs = 0;
          for (let j = tIdx + 1; j < N; j++) {
            if (tShares[j] > 0) {
              const qj = slice[j];
              cs += tShares[j] * (qj.TIPS_Accrued_Principal || 1000) * ((qj.TIPS_Coupon_pct || 0) / 100);
            }
          }
          return cs;
        };
        for (let i = N - 1; i >= 1; i--) {
          const q = slice[i];
          const coupRec = coupSumAt(i);
          tCouponsRec[i] = coupRec;
          if (!q.TIPS_Available) {
            gapReserve += Math.max(0, spend1 - coupRec);
          } else {
            const need = Math.max(0, spend1 + gapReserve - coupRec);
            gapReserve = 0;
            const acc = q.TIPS_Accrued_Principal || 1000;
            const cPct = (q.TIPS_Coupon_pct || 0) / 100;
            const sh = need / (acc * (1 + cPct));
            const nomPricePer1k = acc * ((q.TIPS_Real_Ask_Price || 100) / 100);
            tShares[i] = sh;
            tCosts[i] = sh * nomPricePer1k;
            tipsTotal += tCosts[i];
          }
        }
        yr1TipsCoup = coupSumAt(0);
        tCouponsRec[0] = yr1TipsCoup;
        yr1TipsCash = Math.max(0, spend1 + gapReserve - yr1TipsCoup);
        tShares[0] = yr1TipsCash / 1000;
        tCosts[0] = yr1TipsCash;
        tipsTotal += yr1TipsCash;

        for (let i = 0; i < N; i++) {
          rows.push({
            year: slice[i].Year, t: i + 1,
            stripsTarget: sTargs[i], stripsYtm: slice[i].STRIPS_YTM_pct || 0, stripsCost: sCosts[i],
            tipsAvail: slice[i].TIPS_Available === 1,
            tipsYtm: slice[i].TIPS_Real_YTM_pct,
            tipsShares: tShares[i], tipsCouponsRec: tCouponsRec[i], tipsCost: tCosts[i]
          });
        }
        stripsIrrCf = rows.map(r => r.stripsTarget);
        tipsIrrCf = rows.map(() => spend1);
      } else {
        const cRow = CURVES.find(x => x.Date === curveKey) || CURVES[CURVES.length - 1];
        const nomKnots = [
          [1, cRow.DGS1], [2, cRow.DGS2], [3, cRow.DGS3], [5, cRow.DGS5],
          [7, cRow.DGS7], [10, cRow.DGS10], [20, cRow.DGS20], [30, cRow.DGS30]
        ].filter(k => k[1] !== null && isFinite(k[1]));
        const realKnots = [
          [5, cRow.DFII5], [7, cRow.DFII7], [10, cRow.DFII10], [20, cRow.DFII20], [30, cRow.DFII30]
        ].filter(k => k[1] !== null && isFinite(k[1]));
        // Extrapolate short end real yield from 5Y using nominal 1Y-5Y slope
        if (realKnots.length) {
          const slope1_5 = (interpCurve(nomKnots, 5) - interpCurve(nomKnots, 1)) * 0.65;
          realKnots.unshift([1, realKnots[0][1] - slope1_5]);
        }
        const sYear = parseInt(String(cRow.Date).slice(0, 4), 10) || 2026;
        for (let i = 0; i < horizon; i++) {
          const ny = interpCurve(nomKnots, i + 1) / 100;
          const ry = (realKnots.length ? interpCurve(realKnots, i + 1) : (ny * 100 - 2.1)) / 100;
          const target = spend1 * Math.pow(1 + cola, i);
          const sc = i === 0 ? target : target / Math.pow(1 + ny, i);
          const tc = i === 0 ? spend1 : spend1 / Math.pow(1 + ry, i);
          stripsTotal += sc; tipsTotal += tc;
          rows.push({
            year: sYear + i, t: i + 1,
            stripsTarget: target, stripsYtm: ny * 100, stripsCost: sc,
            tipsAvail: true, tipsYtm: ry * 100, tipsShares: tc / 1000, tipsCouponsRec: 0, tipsCost: tc
          });
        }
        stripsIrrCf = rows.map(r => r.stripsTarget);
        tipsIrrCf = rows.map(() => spend1);
      }

      const solveIRR = (initCost, cfs) => {
        let lo = -0.05, hi = 0.15;
        const npv = r => cfs.reduce((acc, cf, i) => acc + cf / Math.pow(1 + r, i), 0) - initCost;
        for (let it = 0; it < 60; it++) {
          const mid = 0.5 * (lo + hi);
          if (npv(mid) > 0) lo = mid; else hi = mid;
        }
        return (0.5 * (lo + hi)) * 100;
      };
      const stripsIrr = solveIRR(stripsTotal, stripsIrrCf);
      const tipsIrr = solveIRR(tipsTotal, tipsIrrCf);
      const beInf = ((1 + stripsIrr / 100) / (1 + tipsIrr / 100) - 1) * 100;

      let cumS = 0, cumT = 0, affS = 0, affT = 0;
      for (let i = 0; i < rows.length; i++) {
        cumS += rows[i].stripsCost; if (cumS <= budget) affS = i + 1;
        cumT += rows[i].tipsCost; if (cumT <= budget) affT = i + 1;
      }
      return { rows, stripsTotal, tipsTotal, stripsIrr, tipsIrr, beInf, affS, affT, yr1TipsCash, yr1TipsCoup };
    }

    function bondAnalytics(face, cPct, T, yPct) {
      const c = cPct / 100, y = yPct / 100;
      let px = 0, macNum = 0, convNum = 0;
      for (let t = 1; t <= T; t++) {
        const cf = (t === T ? face * (1 + c) : face * c);
        const df = Math.pow(1 + y, -t);
        const pv = cf * df;
        px += pv;
        macNum += t * pv;
        convNum += t * (t + 1) * pv;
      }
      const macDur = px > 0 ? macNum / px : 0;
      const modDur = macDur / (1 + y);
      const convexity = px > 0 ? convNum / (px * Math.pow(1 + y, 2)) : 0;
      return { px, macDur, modDur, convexity };
    }

    function computeEx713Crossover() {
      const eqReal = NYU.map(r => (1 + (r.NYU_SP500_pct || 0) / 100) / (1 + (r.NYU_US_CPI_Inflation_pct || 0) / 100) - 1);
      const bdReal = NYU.map(r => (1 + (r.NYU_US_10Y_TBond_pct || 0) / 100) / (1 + (r.NYU_US_CPI_Inflation_pct || 0) / 100) - 1);
      const eqNom = NYU.map(r => (r.NYU_SP500_pct || 0) / 100);
      const bdNom = NYU.map(r => (r.NYU_US_10Y_TBond_pct || 0) / 100);
      const worstByH = [];
      let crossReal = null, crossNom = null;
      for (let h = 1; h <= 30; h++) {
        let minER = Infinity, minBR = Infinity, minEN = Infinity, minBN = Infinity;
        for (let i = 0; i <= NYU.length - h; i++) {
          let pER = 1, pBR = 1, pEN = 1, pBN = 1;
          for (let k = 0; k < h; k++) {
            pER *= (1 + eqReal[i + k]); pBR *= (1 + bdReal[i + k]);
            pEN *= (1 + eqNom[i + k]); pBN *= (1 + bdNom[i + k]);
          }
          const cER = Math.pow(pER, 1 / h) - 1, cBR = Math.pow(pBR, 1 / h) - 1;
          const cEN = Math.pow(pEN, 1 / h) - 1, cBN = Math.pow(pBN, 1 / h) - 1;
          if (cER < minER) minER = cER; if (cBR < minBR) minBR = cBR;
          if (cEN < minEN) minEN = cEN; if (cBN < minBN) minBN = cBN;
        }
        if (crossReal === null && minER > minBR) crossReal = h;
        if (crossNom === null && minEN > minBN) crossNom = h;
        worstByH.push({ h, minER: minER * 100, minBR: minBR * 100, minEN: minEN * 100, minBN: minBN * 100 });
      }
      return { worstByH, crossReal, crossNom };
    }

    function solveCriticalPath(V0, S1, g, horizonGP = 45) {
      // Solve r* such that W_0 = V0 depletes in 45 years with spending S_t = S1*(1+g)^t
      let lo = 0.0, hi = 0.15;
      const simRem = r => {
        let w = V0, s = S1;
        for (let t = 0; t < horizonGP; t++) { w = (w - s) * (1 + r); s *= (1 + g); }
        return w;
      };
      for (let it = 0; it < 60; it++) {
        const mid = 0.5 * (lo + hi);
        if (simRem(mid) < 0) lo = mid; else hi = mid;
      }
      const rStar = 0.5 * (lo + hi);
      const wStar = [V0];
      let w = V0, s = S1;
      for (let t = 0; t < horizonGP; t++) { w = Math.max(0, (w - s) * (1 + rStar)); wStar.push(w); s *= (1 + g); }
      return { rStar, wStar };
    }

    function simulateBucketsMC(V0, S1, g, Hlad, Thor, yBkt, nMc) {
      const rng = mulberry32(20260707);
      const paths = new Array(nMc);
      for (let i = 0; i < nMc; i++) paths[i] = simulateCh3APath(ch3aCal, Thor, rng, 0.0245, 0.017);

      // Initial H-year bond ladder present value
      let bInit = 0;
      for (let k = 0; k < Hlad; k++) bInit += (S1 * Math.pow(1 + g, k)) / Math.pow(1 + yBkt, k);
      const eInit = Math.max(0, V0 - bInit);
      const eqShareInit = eInit / V0;
      const crit = solveCriticalPath(V0, S1, g, 45);

      const strategies = [
        { id: "b_auto", en: "1. Automatic Annual Bucket Rolling", zh: "1. 自动按年滚动延长阶梯" },
        { id: "b_mkt", en: "2. Market-Based Rolling (Stock R ≥ 0)", zh: "2. 市场条件滚动 (股市≥0才续期)" },
        { id: "b_crit", en: "3. Personalized Critical-Path Buckets", zh: "3. 关键路径门槛蓄水池" },
        { id: "tr_fix", en: "4. Fixed Total Return (Matched Initial Eq%)", zh: "4. 固定总回报对比组合" },
        { id: "tr_auto", en: "5. Matched Dynamic TR (Automatic)", zh: "5. 动态同步总回报 (对齐自动)" },
        { id: "tr_mkt", en: "6. Matched Dynamic TR (Market-Based)", zh: "6. 动态同步总回报 (对齐市场)" },
        { id: "tr_crit", en: "7. Matched Dynamic TR (Critical-Path)", zh: "7. 动态同步总回报 (对齐关键路径)" }
      ];

      // Run bucket strategies while recording pathwise equity share history so matched TR uses identical risk profile
      const runMode = (mode, matchedWeights) => {
        const endW = new Float64Array(nMc);
        const wPaths = matchedWeights ? null : new Array(nMc);
        let succ = 0;
        for (let p = 0; p < nMc; p++) {
          const path = paths[p];
          if (!matchedWeights) {
            // Explicit H-rung ladder + stock sleeve
            const rungs = new Array(Hlad).fill(0);
            for (let k = 0; k < Hlad; k++) rungs[k] = S1 * Math.pow(1 + g, k);
            let eqBal = eInit;
            let failed = false;
            const eqHist = new Float64Array(Thor);
            for (let t = 0; t < Thor; t++) {
              const sNeeded = rungs[0] || (S1 * Math.pow(1 + g, t));
              // Ladder value after rung[0] paid
              let ladRemPV = 0;
              for (let k = 1; k < rungs.length; k++) ladRemPV += rungs[k] / Math.pow(1 + yBkt, k - 1);
              const curTotal = rungs[0] + ladRemPV + eqBal;
              const paidFromLadder = Math.min(sNeeded, rungs[0]);
              const deficit = sNeeded - paidFromLadder;
              if (eqBal + ladRemPV < deficit - 1e-6) { failed = true; eqBal = 0; for (let k = 0; k < Hlad; k++) rungs[k] = 0; eqHist[t] = 0; break; }
              eqBal = Math.max(0, eqBal - deficit);
              // Advance ladder by 1 year
              rungs.shift(); rungs.push(0);
              const wTotalAfterSpend = Math.max(1e-6, ladRemPV + eqBal);
              eqHist[t] = eqBal / wTotalAfterSpend;
              // Replenish new rung at end of H-yr ladder
              const nextRungDue = S1 * Math.pow(1 + g, t + Hlad);
              const costNext = nextRungDue / Math.pow(1 + path.yld[t], Hlad - 1);
              const wantRepl = (t + Hlad < Thor) && (
                mode === "b_auto" ||
                (mode === "b_mkt" && path.eq[t] >= 0) ||
                (mode === "b_crit" && curTotal >= crit.wStar[Math.min(t, crit.wStar.length - 1)])
              );
              if (wantRepl && eqBal >= costNext) {
                eqBal -= costNext;
                rungs[Hlad - 1] = nextRungDue;
              }
              eqBal *= (1 + path.eq[t]);
              // Also handle if stocks hit 0 and ladder runs short before maturity -> liquidate tail rungs proportionally if needed later
            }
            let ladEnd = 0;
            for (let k = 0; k < rungs.length; k++) ladEnd += rungs[k] / Math.pow(1 + yBkt, k);
            const finalW = failed ? 0 : (eqBal + ladEnd);
            if (!failed) succ++;
            endW[p] = finalW;
            wPaths[p] = eqHist;
          } else {
            let port = V0, failed = false;
            for (let t = 0; t < Thor; t++) {
              const sNeeded = S1 * Math.pow(1 + g, t);
              if (port < sNeeded - 1e-6) { failed = true; port = 0; break; }
              const wEq = mode === "tr_fix" ? eqShareInit : (matchedWeights[p][t] || 0);
              const rPort = wEq * path.eq[t] + (1 - wEq) * path.bd[t];
              port = (port - sNeeded) * (1 + rPort);
            }
            if (!failed) succ++;
            endW[p] = port;
          }
        }
        const sorted = endW.slice().sort();
        return {
          succPct: (succ / nMc) * 100,
          p50: quantileSorted(sorted, 0.5),
          p10: quantileSorted(sorted, 0.1),
          p90: quantileSorted(sorted, 0.9),
          wPaths
        };
      };

      const rAuto = runMode("b_auto", null);
      const rMkt = runMode("b_mkt", null);
      const rCrit = runMode("b_crit", null);
      const rTrFix = runMode("tr_fix", []);
      const rTrAuto = runMode("tr_auto", rAuto.wPaths);
      const rTrMkt = runMode("tr_mkt", rMkt.wPaths);
      const rTrCrit = runMode("tr_crit", rCrit.wPaths);

      const all = [rAuto, rMkt, rCrit, rTrFix, rTrAuto, rTrMkt, rTrCrit];
      return {
        bInit, eInit, eqShareInit, crit,
        rows: strategies.map((s, idx) => ({ ...s, ...all[idx] }))
      };
    }

    const crossCache = computeEx713Crossover();

    function updateAll() {
      const isZh = currentLang === "zh-CN";
      const curveKey = document.getElementById("curveSel").value;
      const spend1 = Math.max(1000, parseMoney(document.getElementById("ladSpend")) || 40000);
      const budget = Math.max(10000, parseMoney(document.getElementById("ladBudget")) || 1000000);
      const horizon = Math.min(30, Math.max(5, parseInt(document.getElementById("ladHorizon").value, 10) || 30));
      const colaPct = Math.max(0, parseFloat(document.getElementById("ladCola").value) || 0);

      // 1. Ladder Tab
      const lad = solveLadder(curveKey, spend1, horizon, colaPct, budget);
      state.ladRows = lad.rows;
      document.getElementById("klStrips").textContent = fmtExactMoney(lad.stripsTotal);
      document.getElementById("klStripsSub").textContent = `IRR ${lad.stripsIrr.toFixed(2)}% · ${((spend1 / Math.max(1, lad.stripsTotal)) * 100).toFixed(2)}% ${isZh ? "初始提取率" : "payout"}`;
      document.getElementById("klTips").textContent = fmtExactMoney(lad.tipsTotal);
      document.getElementById("klTipsSub").textContent = `Real IRR ${lad.tipsIrr.toFixed(2)}% · Yr-1 Cash ${fmtExactMoney(lad.yr1TipsCash)}`;
      document.getElementById("klAff").textContent = `${lad.affS} / ${lad.affT} ${isZh ? "年" : "yrs"}`;
      document.getElementById("klAffSub").textContent = isZh ? `STRIPS vs TIPS (${fmtCompactMoney(budget)})` : `STRIPS vs TIPS on ${fmtCompactMoney(budget)}`;
      document.getElementById("klBei").textContent = lad.beInf.toFixed(2) + "%";
      document.getElementById("klBeiSub").textContent = isZh ? `高出 TIPS ${fmtExactMoney(Math.abs(lad.tipsTotal - lad.stripsTotal))}` : `Spread ${lad.tipsTotal >= lad.stripsTotal ? "+" : ""}${fmtExactMoney(lad.tipsTotal - lad.stripsTotal)}`;

      state.lastExport = lad.rows.map(r => [
        r.year, r.t, Math.round(r.stripsTarget), r.stripsYtm.toFixed(2), Math.round(r.stripsCost),
        r.tipsAvail ? 1 : 0, r.tipsYtm ?? "", r.tipsShares.toFixed(2), Math.round(r.tipsCouponsRec), Math.round(r.tipsCost)
      ]);

      document.getElementById("ladHead").innerHTML = isZh
        ? `<tr><th>到期年</th><th>STRIPS目标($)</th><th>STRIPS利率%</th><th>STRIPS成本($)</th><th>TIPS可买</th><th>TIPS实率%</th><th>TIPS份数</th><th>获前息($)</th><th>TIPS总成本($)</th></tr>`
        : `<tr><th>Year</th><th>STRIPS Target</th><th>STRIPS YTM</th><th>STRIPS Cost</th><th>TIPS Avail</th><th>TIPS Real YTM</th><th>TIPS Shares</th><th>Coupons Rec</th><th>TIPS Cost</th></tr>`;
      document.getElementById("ladBody").innerHTML = lad.rows.map(r => {
        const av = r.tipsAvail ? (isZh ? "是" : "Yes") : `<span class="year-pill">${isZh ? "缺口" : "Gap"}</span>`;
        const hl = !r.tipsAvail ? ' style="opacity:0.75;"' : "";
        return `<tr${hl}><td>${r.year} (Yr ${r.t})</td><td>${fmtExactMoney(r.stripsTarget)}</td><td>${r.stripsYtm.toFixed(2)}%</td><td>${fmtExactMoney(r.stripsCost)}</td><td>${av}</td><td>${r.tipsYtm !== null && r.tipsYtm !== undefined ? Number(r.tipsYtm).toFixed(2) + "%" : "—"}</td><td>${r.tipsShares.toFixed(2)}</td><td>${fmtExactMoney(r.tipsCouponsRec)}</td><td>${fmtExactMoney(r.tipsCost)}</td></tr>`;
      }).join("");

      const ladCanvas = document.getElementById("ladCanvas");
      const lsc = setupCanvas(ladCanvas);
      if (lsc) {
        const { ctx, w, h } = lsc, C = getThemeColors();
        ctx.clearRect(0, 0, w, h);
        const maxV = Math.max(1000, ...lad.rows.map(r => Math.max(r.stripsCost, r.tipsCost))) * 1.12;
        const pad = { l: 58, r: 16, t: 18, b: 28 }, cw = w - pad.l - pad.r, ch = h - pad.t - pad.b;
        const mapY = v => pad.t + ch - (v / maxV) * ch;
        ctx.strokeStyle = C.grid; ctx.font = CANVAS_FONT; ctx.textAlign = "right";
        computeNiceLinearTicks(0, maxV, 4).forEach(v => {
          const y = mapY(v); ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(w - pad.r, y); ctx.stroke();
          ctx.fillStyle = C.muted; ctx.fillText(fmtCompactMoney(v), pad.l - 5, y + 4);
        });
        const grpW = cw / lad.rows.length;
        const bw = Math.max(2, grpW * 0.38);
        lad.rows.forEach((r, i) => {
          const x0 = pad.l + i * grpW + grpW * 0.1;
          const yS = mapY(r.stripsCost), yT = mapY(r.tipsCost);
          ctx.fillStyle = C.bond; ctx.fillRect(x0, yS, bw, pad.t + ch - yS);
          ctx.fillStyle = C.port; ctx.fillRect(x0 + bw + 1, yT, bw, pad.t + ch - yT);
          if (i === 0 || i === lad.rows.length - 1 || i % 5 === 0) {
            ctx.fillStyle = C.muted; ctx.textAlign = "center";
            ctx.fillText(String(r.year), x0 + bw, h - 8);
          }
        });
      }

      // 2. Duration Tab
      const T = Math.min(30, Math.max(1, parseInt(document.getElementById("bMat").value, 10) || 30));
      const cPct = Math.max(0, parseFloat(document.getElementById("bCoup").value) || 0);
      const y0Pct = parseFloat(document.getElementById("bY0").value) || 2.0;
      const dYPct = parseFloat(document.getElementById("bShock").value) || 1.0;
      const baseB = bondAnalytics(1000, cPct, T, y0Pct);
      const upB = bondAnalytics(1000, cPct, T, y0Pct - dYPct);
      const dnB = bondAnalytics(1000, cPct, T, y0Pct + dYPct);
      const pctUp = ((upB.px - baseB.px) / baseB.px) * 100;
      const pctDn = ((dnB.px - baseB.px) / baseB.px) * 100;
      const linUp = baseB.modDur * dYPct, linDn = -baseB.modDur * dYPct;

      if (state.tab === "duration") {
        document.getElementById("kdPx").textContent = "$" + baseB.px.toFixed(2);
        document.getElementById("kdPxSub").textContent = `MacDur ${baseB.macDur.toFixed(2)} yrs`;
        document.getElementById("kdDur").textContent = `${baseB.modDur.toFixed(2)} / ${baseB.convexity.toFixed(1)}`;
        document.getElementById("kdDurSub").textContent = isZh ? "修正久期 / 凸性因子" : "Mod. Duration / Convexity";
        document.getElementById("kdUp").textContent = fmtPct(pctUp, 2, true);
        document.getElementById("kdUpSub").textContent = `Duration lin: ${fmtPct(linUp, 2, true)}`;
        document.getElementById("kdDn").textContent = fmtPct(pctDn, 2, true);
        document.getElementById("kdDnSub").textContent = `Duration lin: ${fmtPct(linDn, 2, true)}`;

        const shocks = [-3, -2, -1, 0, 1, 2, 3];
        const mats = [2, 5, 10, 20, 30];
        document.getElementById("durHead").innerHTML = `<tr><th>${isZh ? "期限 \\ 冲击" : "Maturity \\ Δy"}</th>${shocks.map(s => `<th>${s > 0 ? "+" + s : s}%</th>`).join("")}</tr>`;
        document.getElementById("durBody").innerHTML = mats.map(m => {
          const b0 = bondAnalytics(1000, cPct, m, y0Pct);
          return `<tr><td><strong>${m}Y (${b0.modDur.toFixed(1)} dur)</strong></td>` + shocks.map(s => {
            const bm = bondAnalytics(1000, cPct, m, y0Pct + s);
            const chg = ((bm.px - b0.px) / b0.px) * 100;
            return `<td class="hm-cell ${chg > 0 ? "pos" : (chg < 0 ? "neg" : "")}">${fmtPct(chg, 1, true)}</td>`;
          }).join("") + `</tr>`;
        }).join("");

        const dc = setupCanvas(document.getElementById("durCurveCanvas"));
        if (dc) {
          const { ctx, w, h } = dc, C = getThemeColors(); ctx.clearRect(0, 0, w, h);
          const xs = [];
          for (let dy = -3; dy <= 3.01; dy += 0.25) {
            const ex = ((bondAnalytics(1000, cPct, T, y0Pct + dy).px / baseB.px) - 1) * 100;
            const ln = -baseB.modDur * dy;
            xs.push({ dy, ex, ln });
          }
          const minY = Math.min(...xs.map(p => Math.min(p.ex, p.ln))) * 1.08;
          const maxY = Math.max(...xs.map(p => Math.max(p.ex, p.ln))) * 1.08;
          const pad = { l: 48, r: 16, t: 18, b: 28 }, cw = w - pad.l - pad.r, ch = h - pad.t - pad.b;
          const mapX = dy => pad.l + ((dy + 3) / 6) * cw;
          const mapY = v => pad.t + ch - ((v - minY) / Math.max(1, maxY - minY)) * ch;
          ctx.strokeStyle = C.grid; ctx.font = CANVAS_FONT; ctx.textAlign = "right";
          computeNiceLinearTicks(minY, maxY, 4).forEach(v => {
            const y = mapY(v); ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(w - pad.r, y); ctx.stroke();
            ctx.fillStyle = C.muted; ctx.fillText(v.toFixed(0) + "%", pad.l - 5, y + 4);
          });
          ctx.beginPath(); ctx.setLineDash([4, 4]); ctx.strokeStyle = C.muted; ctx.lineWidth = 1.6;
          xs.forEach((p, i) => { const x = mapX(p.dy), y = mapY(p.ln); if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); });
          ctx.stroke(); ctx.setLineDash([]);
          ctx.beginPath(); ctx.strokeStyle = C.port; ctx.lineWidth = 2.6;
          xs.forEach((p, i) => { const x = mapX(p.dy), y = mapY(p.ex); if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); });
          ctx.stroke();
          ctx.fillStyle = C.muted; ctx.textAlign = "center";
          [-3, -1, 0, 1, 3].forEach(d => ctx.fillText((d > 0 ? "+" : "") + d + "%", mapX(d), h - 8));
        }

        const ptp = setupCanvas(document.getElementById("ptpCanvas"));
        if (ptp) {
          const { ctx, w, h } = ptp, C = getThemeColors(); ctx.clearRect(0, 0, w, h);
          const indiv = [], fund = [];
          const newY = y0Pct + Math.abs(dYPct);
          let fVal = 1000 * (bondAnalytics(1000, cPct, T, newY).px / baseB.px);
          for (let t = 0; t <= T; t++) {
            const rem = Math.max(1, T - t);
            indiv.push(t === T ? 1000 : bondAnalytics(1000, cPct, rem, newY).px);
            fund.push(fVal);
            fVal = fVal * (1 + newY / 100);
          }
          const minP = Math.min(700, ...indiv) * 0.96, maxP = Math.max(1050, ...indiv) * 1.04;
          const pad = { l: 48, r: 16, t: 18, b: 28 }, cw = w - pad.l - pad.r, ch = h - pad.t - pad.b;
          const mapX = t => pad.l + (t / T) * cw;
          const mapY = v => pad.t + ch - ((v - minP) / Math.max(1, maxP - minP)) * ch;
          ctx.strokeStyle = C.grid; ctx.font = CANVAS_FONT; ctx.textAlign = "right";
          computeNiceLinearTicks(minP, maxP, 4).forEach(v => {
            const y = mapY(v); ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(w - pad.r, y); ctx.stroke();
            ctx.fillStyle = C.muted; ctx.fillText("$" + Math.round(v), pad.l - 5, y + 4);
          });
          ctx.beginPath(); ctx.strokeStyle = C.port; ctx.lineWidth = 2.6;
          indiv.forEach((v, i) => { const x = mapX(i), y = mapY(v); if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); });
          ctx.stroke();
          ctx.fillStyle = C.muted; ctx.textAlign = "center";
          [0, Math.round(T / 2), T].forEach(t => ctx.fillText("Yr " + t, mapX(t), h - 8));
        }
      }

      // 3. Time-Segmentation Buckets Tab
      if (state.tab === "buckets") {
        const Hlad = Math.min(20, Math.max(3, parseInt(document.getElementById("bktYrs").value, 10) || 10));
        const Thor = Math.min(45, Math.max(25, parseInt(document.getElementById("bktHor").value, 10) || 40));
        const sim = simulateBucketsMC(budget, spend1, colaPct / 100, Hlad, Thor, 0.0245, state.mcPaths);
        state.bktSummary = sim.rows;

        document.getElementById("kbCross").textContent = `${crossCache.crossReal || "—"} / ${crossCache.crossNom || "—"} ${isZh ? "年" : "yrs"}`;
        document.getElementById("kbCrossSub").textContent = isZh ? "实际 / 名义最差回报反超年限" : "Real / Nominal worst beat horizon";
        document.getElementById("kbBkt1").textContent = `${fmtCompactMoney(sim.bInit)} (${((1 - sim.eqShareInit) * 100).toFixed(1)}%)`;
        document.getElementById("kbBkt1Sub").textContent = `${(sim.eqShareInit * 100).toFixed(1)}% ${isZh ? "股票蓄水池" : "Growth Equity Sleeve"}`;
        document.getElementById("kbCrit").textContent = (sim.crit.rStar * 100).toFixed(2) + "%";
        document.getElementById("kbCritSub").textContent = isZh ? "45年关键路径门槛收益率" : "Ex. 7.18 required path rate";
        const bestBkt = Math.max(sim.rows[0].succPct, sim.rows[1].succPct, sim.rows[2].succPct);
        const fixTr = sim.rows[3].succPct;
        document.getElementById("kbBest").textContent = `${bestBkt.toFixed(1)}% vs ${fixTr.toFixed(1)}%`;
        document.getElementById("kbBestSub").textContent = `${state.mcPaths} ${isZh ? "次模拟成功率" : "MC success rate"}`;

        document.getElementById("bktHead").innerHTML = isZh
          ? `<tr><th>蓄水池 / 总回报策略</th><th>成功率</th><th>10分位期末($)</th><th>中位数期末($)</th><th>90分位期末($)</th></tr>`
          : `<tr><th>Bucket / Total Return Strategy</th><th>Success Rate</th><th>10th-Pct End Wealth</th><th>Median End Wealth</th><th>90th-Pct End Wealth</th></tr>`;
        document.getElementById("bktBody").innerHTML = sim.rows.map((r, i) => {
          const nm = isZh ? r.zh : r.en;
          return `<tr${i === 2 || i === 3 ? ' class="highlight-row"' : ""}><td>${nm}</td><td><strong>${r.succPct.toFixed(1)}%</strong></td><td>${fmtCompactMoney(r.p10)}</td><td>${fmtCompactMoney(r.p50)}</td><td>${fmtCompactMoney(r.p90)}</td></tr>`;
        }).join("");

        const cc = setupCanvas(document.getElementById("crossCanvas"));
        if (cc) {
          const { ctx, w, h } = cc, C = getThemeColors(); ctx.clearRect(0, 0, w, h);
          const rows = crossCache.worstByH;
          const minY = Math.min(...rows.map(r => Math.min(r.minER, r.minBR))) - 2;
          const maxY = Math.max(...rows.map(r => Math.max(r.minER, r.minBR))) + 2;
          const pad = { l: 48, r: 16, t: 18, b: 28 }, cw = w - pad.l - pad.r, ch = h - pad.t - pad.b;
          const mapX = hr => pad.l + ((hr - 1) / 29) * cw;
          const mapY = v => pad.t + ch - ((v - minY) / Math.max(1, maxY - minY)) * ch;
          ctx.strokeStyle = C.grid; ctx.font = CANVAS_FONT; ctx.textAlign = "right";
          computeNiceLinearTicks(minY, maxY, 4).forEach(v => {
            const y = mapY(v); ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(w - pad.r, y); ctx.stroke();
            ctx.fillStyle = C.muted; ctx.fillText(v.toFixed(0) + "%", pad.l - 5, y + 4);
          });
          [[r => r.minER, C.equity], [r => r.minBR, C.bond]].forEach(([fn, col]) => {
            ctx.beginPath(); ctx.strokeStyle = col; ctx.lineWidth = 2.4;
            rows.forEach((r, i) => { const x = mapX(r.h), y = mapY(fn(r)); if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); });
            ctx.stroke();
          });
          ctx.fillStyle = C.muted; ctx.textAlign = "center";
          [1, 10, 20, 30].forEach(hr => ctx.fillText(hr + "Y", mapX(hr), h - 8));
        }

        const bc = setupCanvas(document.getElementById("bktBarCanvas"));
        if (bc) {
          const { ctx, w, h } = bc, C = getThemeColors(); ctx.clearRect(0, 0, w, h);
          const pad = { l: 46, r: 16, t: 18, b: 36 }, cw = w - pad.l - pad.r, ch = h - pad.t - pad.b;
          const mapY = v => pad.t + ch - (v / 100) * ch;
          ctx.strokeStyle = C.grid; ctx.font = CANVAS_FONT; ctx.textAlign = "right";
          [0, 25, 50, 75, 100].forEach(v => {
            const y = mapY(v); ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(w - pad.r, y); ctx.stroke();
            ctx.fillStyle = C.muted; ctx.fillText(v + "%", pad.l - 5, y + 4);
          });
          const bw = cw / sim.rows.length;
          sim.rows.forEach((r, i) => {
            const x = pad.l + i * bw + bw * 0.2, ww = bw * 0.6, y = mapY(r.succPct);
            ctx.fillStyle = i < 3 ? C.port : (i === 3 ? C.muted : C.accent);
            ctx.fillRect(x, y, ww, pad.t + ch - y);
            ctx.fillStyle = C.text; ctx.textAlign = "center";
            ctx.fillText(r.succPct.toFixed(0) + "%", x + ww * 0.5, y - 5);
            ctx.fillStyle = C.muted; ctx.fillText("#" + (i + 1), x + ww * 0.5, h - 10);
          });
        }
      }
    }

    attachCanvasHover(document.getElementById("ladCanvas"), document.getElementById("ladTip"), (e, canvas, tip) => {
      if (!e || !state.ladRows.length) return;
      const rect = canvas.getBoundingClientRect();
      const padL = 58, padR = 16, cw = rect.width - padL - padR;
      const idx = Math.max(0, Math.min(state.ladRows.length - 1, Math.floor(((e.clientX - rect.left - padL) / Math.max(1, cw)) * state.ladRows.length)));
      const r = state.ladRows[idx];
      tip.innerHTML = `<strong>${r.year} (Yr ${r.t})</strong>` +
        `<div class="tip-row"><span>STRIPS Cost</span><span>${fmtExactMoney(r.stripsCost)}</span></div>` +
        `<div class="tip-row"><span>TIPS Cost</span><span>${fmtExactMoney(r.tipsCost)}</span></div>`;
      placeTooltip(tip, canvas, e.clientX, e.clientY);
    });

    function applyPreset(name) {
      document.querySelectorAll(".preset-btn").forEach(b => b.classList.toggle("active", b.dataset.preset === name));
      if (name === "wsj2017") {
        document.getElementById("curveSel").value = "wsj2017";
        document.getElementById("ladSpend").value = "40,000";
        document.getElementById("ladHorizon").value = "30";
        document.getElementById("ladCola").value = "2.0";
        document.querySelector('[data-tab="ladder"]').click();
      } else if (name === "latest") {
        document.getElementById("curveSel").value = CURVES[CURVES.length - 1].Date;
        document.querySelector('[data-tab="ladder"]').click();
      } else if (name === "duration") {
        document.getElementById("bMat").value = "30"; document.getElementById("bCoup").value = "2.0";
        document.getElementById("bY0").value = "2.0"; document.getElementById("bShock").value = "1.0";
        document.querySelector('[data-tab="duration"]').click();
      } else if (name === "buckets") {
        document.getElementById("bktYrs").value = "10"; document.getElementById("bktHor").value = "40";
        document.querySelector('[data-tab="buckets"]').click();
      }
      updateAll();
    }

    function onThemeOrLangChange() { updateAll(); }

    document.querySelectorAll(".tab-btn").forEach(b => {
      b.addEventListener("click", () => {
        state.tab = b.dataset.tab;
        document.querySelectorAll(".tab-btn").forEach(x => { x.classList.toggle("active", x === b); x.setAttribute("aria-selected", x === b ? "true" : "false"); });
        const map = { ladder: "paneLadder", duration: "paneDuration", buckets: "paneBuckets" };
        Object.entries(map).forEach(([k, id]) => document.getElementById(id).style.display = k === state.tab ? "block" : "none");
        updateAll();
      });
    });
    document.querySelectorAll("#bktMcCtl button").forEach(b => b.addEventListener("click", () => {
      state.mcPaths = parseInt(b.dataset.val, 10);
      document.querySelectorAll("#bktMcCtl button").forEach(x => x.classList.toggle("active", x === b));
      updateAll();
    }));
    document.querySelectorAll(".preset-btn").forEach(b => b.addEventListener("click", () => applyPreset(b.dataset.preset)));
    document.getElementById("btnReset").addEventListener("click", () => applyPreset("wsj2017"));
    document.getElementById("btnExportCsv").addEventListener("click", () => {
      downloadCsv("pfau_ch7_bond_ladder.csv", ["Year", "Rung", "STRIPS_Target", "STRIPS_YTM", "STRIPS_Cost", "TIPS_Avail", "TIPS_Real_YTM", "TIPS_Shares", "TIPS_Coupons", "TIPS_Cost"], state.lastExport);
    });
    ["curveSel", "ladSpend", "ladBudget", "ladHorizon", "ladCola", "bMat", "bCoup", "bY0", "bShock", "bktYrs", "bktHor"].forEach(id => {
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
        slug="bonds-and-buckets",
        title_en="Bond Ladders & Time Segmentation",
        extra_css="",
        body_html=body_html,
        embedded_data_js=embedded,
        page_i18n=page_i18n,
        page_js=page_js,
    )


if __name__ == "__main__":
    build_ch7()
