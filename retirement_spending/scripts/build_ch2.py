#!/usr/bin/env python3
"""Build Lab 1 (Chapter 2): Fixed Returns, PMT/NPER/RATE Solver, Return Waterfall, and Mortality Explorer."""

from shared_shell import dump_json_inline, load_csv_records, render_page
from shared_sim_js import SHARED_SIM_JS

EXTRA_CSS = """
    .hm-grid { font-size: 11.5px; }
    .hm-active { outline: 2px solid var(--accent); outline-offset: -2px; font-weight: 700 !important; background: var(--accent-soft) !important; }
"""


def build_ch2():
    mort_rows = load_csv_records("mortality_and_rmd_tables.csv")

    body_html = """  <main class="layout">
    <aside class="sidebar" aria-label="Simulation parameters" data-i18n-aria-label="aria_sidebar">
      <div class="side-section">
        <div class="sec-head-static">
          <h2 class="sec-title" data-i18n="sec_presets">Book Exhibit Presets</h2>
          <button type="button" class="link-btn" id="btnReset" data-i18n="btn_reset">Reset</button>
        </div>
        <div class="preset-grid">
          <button type="button" class="preset-btn active" data-preset="four_pct">
            <span class="p-title" data-i18n="pre_4pct_t">Ex. 2.8 · 4% Rule Eq.</span>
            <span class="p-meta" data-i18n="pre_4pct_m">1.33% real, 30 yrs</span>
          </button>
          <button type="button" class="preset-btn" data-preset="hist_5050">
            <span class="p-title" data-i18n="pre_hist_t">Ex. 2.1 · Hist 50/50</span>
            <span class="p-meta" data-i18n="pre_hist_m">5.1% real compounded</span>
          </button>
          <button type="button" class="preset-btn" data-preset="low_tips">
            <span class="p-title" data-i18n="pre_low_t">Ex. 2.1 · Low-Yield 50/50</span>
            <span class="p-meta" data-i18n="pre_low_m">2.7% real (0.1% TIPS)</span>
          </button>
          <button type="button" class="preset-btn" data-preset="soa_couple">
            <span class="p-title" data-i18n="pre_cpl_t">Ex. 2.4 · 65 Couple</span>
            <span class="p-meta" data-i18n="pre_cpl_m">10% surv. horizon</span>
          </button>
        </div>
      </div>

      <div class="side-section">
        <div class="sec-head-static"><h2 class="sec-title" data-i18n="sec_solver">Deterministic Solver</h2></div>
        <div class="control-group">
          <label><span data-i18n="lbl_solve_for">Solve for</span></label>
          <div class="seg-ctl" id="solverModeCtl" role="group">
            <button type="button" data-v="pmt" class="active" aria-pressed="true">PMT</button>
            <button type="button" data-v="nper" aria-pressed="false">NPER</button>
            <button type="button" data-v="rate" aria-pressed="false">RATE</button>
          </div>
        </div>
        <div class="control-group">
          <label for="initPortfolio"><span data-i18n="lbl_portfolio">Starting portfolio (PV)</span></label>
          <div class="currency-field"><span class="currency-prefix">$</span><input type="text" id="initPortfolio" value="1,000,000" inputmode="numeric" /></div>
        </div>
        <div class="control-group" id="grpTargetSpend" style="display:none;">
          <label for="targetSpend"><span data-i18n="lbl_target_spend">Annual real spending (PMT)</span></label>
          <div class="currency-field"><span class="currency-prefix">$</span><input type="text" id="targetSpend" value="40,109" inputmode="numeric" /></div>
        </div>
        <div class="control-group" id="grpRealReturn">
          <div class="label-row">
            <label for="realReturnInput"><span data-i18n="lbl_real_ret">Fixed real return (%/yr)</span></label>
            <span class="label-hint" id="retSrcHint"></span>
          </div>
          <input type="number" id="realReturnInput" value="1.33" min="-4" max="12" step="0.01" />
          <div class="chips" id="retChips">
            <button type="button" class="chip active" data-r="1.33">1.33%</button>
            <button type="button" class="chip" data-r="2.70">2.70%</button>
            <button type="button" class="chip" data-r="5.10">5.10%</button>
            <button type="button" class="chip" data-r="7.00">7.00%</button>
          </div>
        </div>
        <div class="control-group row-2">
          <div>
            <label for="legacyPct"><span data-i18n="lbl_legacy">End legacy (% PV)</span></label>
            <select id="legacyPct">
              <option value="0" selected data-i18n="opt_leg_0">0% (Deplete)</option>
              <option value="50" data-i18n="opt_leg_50">50% Preserve</option>
              <option value="100" data-i18n="opt_leg_100">100% Preserve</option>
            </select>
          </div>
          <div>
            <label for="withdrawTiming"><span data-i18n="lbl_timing">Withdrawal timing</span></label>
            <select id="withdrawTiming">
              <option value="1" selected data-i18n="opt_start">Start (type=1)</option>
              <option value="0" data-i18n="opt_end">End (type=0)</option>
            </select>
          </div>
        </div>
      </div>

      <div class="side-section">
        <div class="sec-head-static"><h2 class="sec-title" data-i18n="sec_longevity">Planning Age &amp; Mortality</h2></div>
        <div class="control-group row-2">
          <div>
            <label for="startAge"><span data-i18n="lbl_cur_age">Start age</span></label>
            <input type="number" id="startAge" value="65" min="50" max="85" step="1" />
          </div>
          <div>
            <label for="householdType"><span data-i18n="lbl_household">Household</span></label>
            <select id="householdType">
              <option value="male" data-i18n="hh_male">Male</option>
              <option value="female" data-i18n="hh_female">Female</option>
              <option value="couple" selected data-i18n="hh_couple">Opposite-Sex Couple</option>
              <option value="two_males" data-i18n="hh_2m">Two Males</option>
              <option value="two_females" data-i18n="hh_2f">Two Females</option>
            </select>
          </div>
        </div>
        <div class="control-group row-2">
          <div>
            <label for="mortTable"><span data-i18n="lbl_mort_tbl">Mortality table</span></label>
            <select id="mortTable">
              <option value="soa_2017" selected data-i18n="tbl_soa17">SOA IAM Cohort (2017)</option>
              <option value="soa_2026" data-i18n="tbl_soa26">SOA IAM Cohort (2026)</option>
              <option value="ssa" data-i18n="tbl_ssa">SSA Period Table</option>
            </select>
          </div>
          <div>
            <label for="healthClass"><span data-i18n="lbl_health">Health multiplier</span></label>
            <select id="healthClass">
              <option value="0.80" data-i18n="hlth_ex">Excellent (0.80× qₓ)</option>
              <option value="1.00" selected data-i18n="hlth_avg">Average (1.00× qₓ)</option>
              <option value="1.45" data-i18n="hlth_poor">Poor / Smoker (1.45× qₓ)</option>
            </select>
          </div>
        </div>
        <div class="control-group">
          <div class="switch-row">
            <label for="autoHorizonSwitch"><span data-i18n="lbl_auto_hor">Set horizon from survival target</span></label>
            <input type="checkbox" id="autoHorizonSwitch" class="switch" />
          </div>
        </div>
        <div class="control-group" id="grpSurvTarget" style="display:none;">
          <div class="label-row">
            <label for="survTargetPct"><span data-i18n="lbl_surv_target">Acceptable outliving prob.</span></label>
            <span class="label-hint" id="survTargetHint">10%</span>
          </div>
          <input type="range" id="survTargetPct" class="range-slider" min="5" max="50" step="5" value="10" />
        </div>
        <div class="control-group" id="grpHorizon">
          <div class="label-row">
            <label for="planHorizon"><span data-i18n="lbl_horizon">Planning horizon (yrs)</span></label>
            <span class="label-hint" id="planAgeHint">Age 95</span>
          </div>
          <input type="number" id="planHorizon" value="30" min="5" max="60" step="1" />
        </div>
      </div>

      <details class="side-section" id="detailsWaterfall">
        <summary>
          <div class="sec-text">
            <h2 class="sec-title" data-i18n="sec_waterfall">Exhibit 2.1 Return Builder</h2>
            <span class="sec-summary" id="wfSummary">50% Stock · 0.1% TIPS · 0 bps fee</span>
          </div>
          <span class="chev">&#9656;</span>
        </summary>
        <div class="control-group">
          <div class="label-row">
            <label for="wfStockPct"><span data-i18n="lbl_wf_stock">Stock allocation</span></label>
            <span class="label-hint" id="wfStockHint">50 / 50</span>
          </div>
          <input type="range" id="wfStockPct" class="ratio-slider" min="0" max="100" step="5" value="50" />
        </div>
        <div class="control-group row-2">
          <div>
            <label for="wfTipsShift"><span data-i18n="lbl_wf_tips">Bond real yield (%)</span></label>
            <input type="number" id="wfTipsShift" value="0.10" min="-2" max="6" step="0.1" />
          </div>
          <div>
            <label for="wfFeeBps"><span data-i18n="lbl_wf_fee">Fees + drag (bps)</span></label>
            <input type="number" id="wfFeeBps" value="0" min="0" max="250" step="5" />
          </div>
        </div>
        <button type="button" class="btn" id="btnApplyWaterfall" style="width:100%;justify-content:center;" data-i18n="btn_apply_wf">Use net compounded real return</button>
      </details>
    </aside>

    <section class="workspace" aria-label="Simulation outputs" data-i18n-aria-label="aria_workspace">
      <div class="results-shell">
        <div class="tabs-bar">
          <div class="tab-strip" role="tablist">
            <button type="button" class="tab-btn active" role="tab" aria-selected="true" data-tab="solver" data-i18n="tab_solver">PMT / NPER / RATE &amp; Waterfall</button>
            <button type="button" class="tab-btn" role="tab" aria-selected="false" data-tab="mortality" data-i18n="tab_mortality">Longevity &amp; Survival Curves</button>
            <button type="button" class="tab-btn" role="tab" aria-selected="false" data-tab="matrix" data-i18n="tab_matrix">Horizon × Return Matrix</button>
          </div>
        </div>
        <div class="results-body">
          <div id="paneSolver" class="tab-pane">
            <div class="kpis kpis-4 kpis-flush-top">
              <div class="kpi"><div class="kpi-label" id="kLbl1">Annual Real Spending</div><div class="kpi-val" id="kVal1">—</div><div class="kpi-sub" id="kSub1">—</div></div>
              <div class="kpi"><div class="kpi-label" id="kLbl2">Planning Horizon</div><div class="kpi-val" id="kVal2">—</div><div class="kpi-sub" id="kSub2">—</div></div>
              <div class="kpi"><div class="kpi-label" id="kLbl3">Assumed / Solved Real Return</div><div class="kpi-val" id="kVal3">—</div><div class="kpi-sub" id="kSub3">—</div></div>
              <div class="kpi"><div class="kpi-label" id="kLbl4">Risk of Outliving Plan</div><div class="kpi-val" id="kVal4">—</div><div class="kpi-sub" id="kSub4">—</div></div>
            </div>
            <div class="split-grid">
              <div class="grid-cell">
                <div class="legend">
                  <strong data-i18n="ttl_bal_path">Real Portfolio Balance &amp; Current WR%</strong>
                  <div class="legend-items">
                    <div class="legend-item"><span class="swatch" style="background:var(--port);"></span><span data-i18n="leg_real_bal">Real Wealth</span></div>
                    <div class="legend-item"><span class="swatch" style="background:var(--danger);"></span><span data-i18n="leg_cur_wr">Current WR %</span></div>
                  </div>
                </div>
                <div class="chart-wrap">
                  <canvas id="balCanvas" height="250"></canvas>
                  <div class="tooltip" id="balTip"></div>
                </div>
              </div>
              <div class="grid-cell">
                <div class="legend">
                  <strong data-i18n="ttl_wf_chart">Exhibit 2.1: Return Assumption Waterfall</strong>
                  <div class="legend-items">
                    <div class="legend-item"><span class="swatch" style="background:var(--accent);height:8px;"></span><span data-i18n="leg_hist_ret">Historical (1926–2016)</span></div>
                    <div class="legend-item"><span class="swatch" style="background:var(--port);height:8px;"></span><span data-i18n="leg_adj_ret">Yield &amp; Fee Adjusted</span></div>
                  </div>
                </div>
                <div class="chart-wrap">
                  <canvas id="wfCanvas" height="250"></canvas>
                  <div class="tooltip" id="wfTip"></div>
                </div>
              </div>
            </div>
            <div class="panel-block">
              <div class="card-title"><h3 class="sec-title" data-i18n="ttl_det_ledger">Deterministic Year-by-Year Schedule</h3><span class="subhead" id="excelEqnHint"></span></div>
              <div class="table-container" style="max-height:340px;">
                <table><thead id="detHead"></thead><tbody id="detBody"></tbody></table>
              </div>
            </div>
          </div>

          <div id="paneMortality" class="tab-pane" style="display:none;">
            <div class="kpis kpis-4 kpis-flush-top">
              <div class="kpi"><div class="kpi-label" data-i18n="mk_mean">Expected Death Age</div><div class="kpi-val" id="mkMean">—</div><div class="kpi-sub" id="mkMeanSub">—</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="mk_med">Median Death Age (50%)</div><div class="kpi-val" id="mkMed">—</div><div class="kpi-sub" data-i18n="mk_med_sub">50% survive past this age</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="mk_p10">10% Survival Age</div><div class="kpi-val pos" id="mkP10">—</div><div class="kpi-sub" data-i18n="mk_p10_sub">Conservative planning anchor</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="mk_p95">Survive to Age 95</div><div class="kpi-val" id="mkP95">—</div><div class="kpi-sub" id="mkP95Sub">—</div></div>
            </div>
            <div class="split-grid">
              <div class="grid-cell">
                <div class="legend">
                  <strong data-i18n="ttl_surv_curve">Ex. 2.4: Survival Probability from Start Age</strong>
                  <div class="legend-items">
                    <div class="legend-item"><span class="swatch" style="background:var(--accent);"></span><span data-i18n="hh_male">Male</span></div>
                    <div class="legend-item"><span class="swatch" style="background:var(--inflation);"></span><span data-i18n="hh_female">Female</span></div>
                    <div class="legend-item"><span class="swatch" style="background:var(--success);"></span><span data-i18n="hh_couple">Couple</span></div>
                  </div>
                </div>
                <div class="chart-wrap">
                  <canvas id="survCanvas" height="250"></canvas>
                  <div class="tooltip" id="survTip"></div>
                </div>
              </div>
              <div class="grid-cell">
                <div class="legend">
                  <strong data-i18n="ttl_pdf_curve">Ex. 2.5–2.7: Death Age Distribution &amp; Conditional Median</strong>
                  <div class="legend-items">
                    <div class="legend-item"><span class="swatch" style="background:var(--port);height:8px;"></span><span data-i18n="leg_death_prob">Annual Death %</span></div>
                    <div class="legend-item"><span class="swatch" style="background:var(--equity);"></span><span data-i18n="leg_cond_med">Conditional Median Age</span></div>
                  </div>
                </div>
                <div class="chart-wrap">
                  <canvas id="pdfCanvas" height="250"></canvas>
                  <div class="tooltip" id="pdfTip"></div>
                </div>
              </div>
            </div>
            <div class="panel-block">
              <div class="card-title"><h3 class="sec-title" data-i18n="ttl_mort_tbl">Ex. 2.3: Survival Comparison Across Groups &amp; Tables</h3></div>
              <div class="table-container" style="max-height:none;">
                <table><thead id="mortCompHead"></thead><tbody id="mortCompBody"></tbody></table>
              </div>
            </div>
          </div>

          <div id="paneMatrix" class="tab-pane" style="display:none;">
            <div class="panel-block">
              <div class="card-title">
                <h3 class="sec-title" id="matTitle">Exhibits 2.8–2.10: Sustainable Real Spending Rates (%)</h3>
                <span class="subhead" id="matSub"></span>
              </div>
              <div class="table-container" style="max-height:none;">
                <table class="hm-grid"><thead id="matHead"></thead><tbody id="matBody"></tbody></table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </main>"""

    page_i18n = {
        "page_title": {"en-UK": "Fixed Returns & Longevity Risk", "zh-CN": "固定收益与长寿风险"},
        "app_title": {"en-UK": "Fixed Returns & Longevity Risk", "zh-CN": "固定收益与长寿风险"},
        "sec_presets": {"en-UK": "Book Exhibit Presets", "zh-CN": "全书图表预设"},
        "pre_4pct_t": {"en-UK": "Ex. 2.8 · 4% Rule Eq.", "zh-CN": "图2.8 · 4% 法则等价"},
        "pre_4pct_m": {"en-UK": "1.33% real, 30 yrs", "zh-CN": "1.33% 实际收益, 30年"},
        "pre_hist_t": {"en-UK": "Ex. 2.1 · Hist 50/50", "zh-CN": "图2.1 · 历史 50/50"},
        "pre_hist_m": {"en-UK": "5.1% real compounded", "zh-CN": "5.1% 实际复利收益"},
        "pre_low_t": {"en-UK": "Ex. 2.1 · Low-Yield 50/50", "zh-CN": "图2.1 · 低利率 50/50"},
        "pre_low_m": {"en-UK": "2.7% real (0.1% TIPS)", "zh-CN": "2.7% 实际收益"},
        "pre_cpl_t": {"en-UK": "Ex. 2.4 · 65 Couple", "zh-CN": "图2.4 · 65岁夫妇"},
        "pre_cpl_m": {"en-UK": "10% surv. horizon", "zh-CN": "10% 存活概率年限"},
        "sec_solver": {"en-UK": "Deterministic Solver", "zh-CN": "确定性精算求解器"},
        "lbl_solve_for": {"en-UK": "Solve for", "zh-CN": "求解目标"},
        "lbl_portfolio": {"en-UK": "Starting portfolio (PV)", "zh-CN": "期初本金 (PV)"},
        "lbl_target_spend": {"en-UK": "Annual real spending (PMT)", "zh-CN": "年度实际支出 (PMT)"},
        "lbl_real_ret": {"en-UK": "Fixed real return (%/yr)", "zh-CN": "固定实际收益率 (%/年)"},
        "lbl_legacy": {"en-UK": "End legacy (% PV)", "zh-CN": "期末留存本金比例"},
        "opt_leg_0": {"en-UK": "0% (Deplete)", "zh-CN": "0%（耗尽）"},
        "opt_leg_50": {"en-UK": "50% Preserve", "zh-CN": "50% 实际保值"},
        "opt_leg_100": {"en-UK": "100% Preserve", "zh-CN": "100% 实际保值"},
        "lbl_timing": {"en-UK": "Withdrawal timing", "zh-CN": "提取时点"},
        "opt_start": {"en-UK": "Start (type=1)", "zh-CN": "年初提取 (type=1)"},
        "opt_end": {"en-UK": "End (type=0)", "zh-CN": "年末提取 (type=0)"},
        "sec_longevity": {"en-UK": "Planning Age & Mortality", "zh-CN": "规划年龄与长寿表"},
        "lbl_cur_age": {"en-UK": "Start age", "zh-CN": "退休起始年龄"},
        "lbl_household": {"en-UK": "Household", "zh-CN": "家庭结构"},
        "hh_male": {"en-UK": "Male", "zh-CN": "男性"},
        "hh_female": {"en-UK": "Female", "zh-CN": "女性"},
        "hh_couple": {"en-UK": "Opposite-Sex Couple", "zh-CN": "夫妻（取长寿者）"},
        "hh_2m": {"en-UK": "Two Males", "zh-CN": "两名男性"},
        "hh_2f": {"en-UK": "Two Females", "zh-CN": "两名女性"},
        "lbl_mort_tbl": {"en-UK": "Mortality table", "zh-CN": "生命表"},
        "tbl_soa17": {"en-UK": "SOA IAM Cohort (2017)", "zh-CN": "SOA 年金世代表 (2017)"},
        "tbl_soa26": {"en-UK": "SOA IAM Cohort (2026)", "zh-CN": "SOA 年金世代表 (2026)"},
        "tbl_ssa": {"en-UK": "SSA Period Table", "zh-CN": "SSA 时期生命表"},
        "lbl_health": {"en-UK": "Health multiplier", "zh-CN": "健康死亡率系数"},
        "hlth_ex": {"en-UK": "Excellent (0.80× qₓ)", "zh-CN": "极佳 (0.80× qₓ)"},
        "hlth_avg": {"en-UK": "Average (1.00× qₓ)", "zh-CN": "平均 (1.00× qₓ)"},
        "hlth_poor": {"en-UK": "Poor / Smoker (1.45× qₓ)", "zh-CN": "较差/吸烟 (1.45× qₓ)"},
        "lbl_auto_hor": {"en-UK": "Set horizon from survival target", "zh-CN": "按存活概率自动设规划年限"},
        "lbl_surv_target": {"en-UK": "Acceptable outliving prob.", "zh-CN": "可接受超寿概率"},
        "lbl_horizon": {"en-UK": "Planning horizon (yrs)", "zh-CN": "规划年数（年）"},
        "sec_waterfall": {"en-UK": "Exhibit 2.1 Return Builder", "zh-CN": "图 2.1 收益率拆解器"},
        "lbl_wf_stock": {"en-UK": "Stock allocation", "zh-CN": "股票配置比例"},
        "lbl_wf_tips": {"en-UK": "Bond real yield (%)", "zh-CN": "当前 TIPS 实际利率 (%)"},
        "lbl_wf_fee": {"en-UK": "Fees + drag (bps)", "zh-CN": "费用与损耗 (bps)"},
        "btn_apply_wf": {"en-UK": "Use net compounded real return", "zh-CN": "套用净实际复利收益率"},
        "tab_solver": {"en-UK": "PMT / NPER / RATE & Waterfall", "zh-CN": "PMT/NPER/RATE 求解与拆解"},
        "tab_mortality": {"en-UK": "Longevity & Survival Curves", "zh-CN": "长寿风险与生存概率曲线"},
        "tab_matrix": {"en-UK": "Horizon × Return Matrix", "zh-CN": "年限 × 收益率支出矩阵"},
        "ttl_bal_path": {"en-UK": "Real Portfolio Balance & Current WR%", "zh-CN": "实际资产余额与当年提取率"},
        "leg_real_bal": {"en-UK": "Real Wealth", "zh-CN": "实际余额"},
        "leg_cur_wr": {"en-UK": "Current WR %", "zh-CN": "当前提取率 %"},
        "ttl_wf_chart": {"en-UK": "Exhibit 2.1: Return Assumption Waterfall", "zh-CN": "图 2.1：组合收益率假设瀑布图"},
        "leg_hist_ret": {"en-UK": "Historical (1926–2016)", "zh-CN": "历史均值 (1926–2016)"},
        "leg_adj_ret": {"en-UK": "Yield & Fee Adjusted", "zh-CN": "低利率与扣费调整后"},
        "ttl_det_ledger": {"en-UK": "Deterministic Year-by-Year Schedule", "zh-CN": "逐年确定性收支明细"},
        "mk_mean": {"en-UK": "Expected Death Age", "zh-CN": "平均预期寿终年龄"},
        "mk_med": {"en-UK": "Median Death Age (50%)", "zh-CN": "中位寿终年龄 (50%)"},
        "mk_med_sub": {"en-UK": "50% survive past this age", "zh-CN": "半数人会活过此年龄"},
        "mk_p10": {"en-UK": "10% Survival Age", "zh-CN": "10% 存活规划年龄"},
        "mk_p10_sub": {"en-UK": "Conservative planning anchor", "zh-CN": "推荐的保守规划基准年龄"},
        "mk_p95": {"en-UK": "Survive to Age 95", "zh-CN": "活到 95 岁的概率"},
        "ttl_surv_curve": {"en-UK": "Ex. 2.4: Survival Probability from Start Age", "zh-CN": "图 2.4：从起始年龄起的存活概率"},
        "ttl_pdf_curve": {"en-UK": "Ex. 2.5–2.7: Death Distribution & Conditional Median", "zh-CN": "图 2.5–2.7：死亡年龄分布与条件预期寿命"},
        "leg_death_prob": {"en-UK": "Death Prob (%)", "zh-CN": "年死亡概率 (%)"},
        "leg_cond_med": {"en-UK": "Cond. Median Death Age", "zh-CN": "条件中位寿终年龄"},
        "ttl_mort_tbl": {"en-UK": "Ex. 2.3: Survival Comparison Across Groups & Tables", "zh-CN": "图 2.3：各家庭与生命表存活率对比"},
    }

    embedded = f"    const MORT_DATA = {dump_json_inline(mort_rows)};\n"
    page_js = SHARED_SIM_JS + r"""
    const STORAGE_KEY = "pfau_ch2_v1";
    const state = {
      solverMode: "pmt",
      tab: "solver",
      activePreset: "four_pct",
      lastSchedule: [],
      lastMortGroup: null
    };

    function getConfig() {
      const pv = Math.max(1000, parseMoney(document.getElementById("initPortfolio")));
      const targetSpend = Math.max(100, parseMoney(document.getElementById("targetSpend")));
      const realRet = (parseFloat(document.getElementById("realReturnInput").value) || 0) / 100;
      const legPct = (parseFloat(document.getElementById("legacyPct").value) || 0) / 100;
      const timing = parseInt(document.getElementById("withdrawTiming").value, 10);
      const startAge = Math.max(50, Math.min(85, parseInt(document.getElementById("startAge").value, 10) || 65));
      const household = document.getElementById("householdType").value;
      const table = document.getElementById("mortTable").value;
      const healthMult = parseFloat(document.getElementById("healthClass").value) || 1.0;
      const autoHor = document.getElementById("autoHorizonSwitch").checked;
      const survTarget = parseFloat(document.getElementById("survTargetPct").value) || 10;
      let horizon = Math.max(5, Math.min(60, parseInt(document.getElementById("planHorizon").value, 10) || 30));

      const curve = buildSurvivalCurve(MORT_DATA, { table, startAge, household, healthMult });
      if (autoHor) {
        const targetP = survTarget / 100;
        for (let k = 0; k < curve.surv.length - 1; k++) {
          if (curve.surv[k].p >= targetP && curve.surv[k + 1].p <= targetP) {
            horizon = Math.max(5, Math.min(60, Math.round(k + (curve.surv[k].p - targetP) / Math.max(1e-9, curve.surv[k].p - curve.surv[k + 1].p))));
            break;
          }
        }
        document.getElementById("planHorizon").value = horizon;
      }
      return { pv, targetSpend, realRet, legPct, timing, startAge, household, table, healthMult, autoHor, survTarget, horizon, curve };
    }

    function computeWaterfall() {
      const wEq = (parseFloat(document.getElementById("wfStockPct").value) || 50) / 100;
      const tipsY = parseFloat(document.getElementById("wfTipsShift").value) || 0.1;
      const fee = (parseFloat(document.getElementById("wfFeeBps").value) || 0) / 100;
      // Historical SBBI 1926-2016 real params (Ex. 2.1): Stock arith real 8.9%, SD 20.1%; Bond arith real 2.4%, SD 5.8%, corr ~0.10
      const muEq = 8.9, sdEq = 20.1, muBd = 2.4, sdBd = 5.8, rho = 0.10;
      const histArith = wEq * muEq + (1 - wEq) * muBd;
      const portVar = (wEq * sdEq) ** 2 + ((1 - wEq) * sdBd) ** 2 + 2 * wEq * (1 - wEq) * sdEq * sdBd * rho;
      const histSd = Math.sqrt(portVar);
      const histGeom = histArith - (portVar / 200);
      // Adjust bond yield from historical 2.2% real to current TIPS yield, preserving ERP
      const yieldCut = Math.max(0, 2.2 - tipsY);
      const adjArith = histArith - yieldCut;
      const adjGeom = adjArith - (portVar / 200);
      const netGeom = adjGeom - fee;
      return { wEq, tipsY, fee, histArith, histSd, histGeom, adjArith, adjGeom, netGeom };
    }

    function updateAll() {
      const cfg = getConfig();
      const wf = computeWaterfall();
      document.getElementById("wfStockHint").textContent = `${Math.round(wf.wEq * 100)} / ${Math.round((1 - wf.wEq) * 100)}`;
      document.getElementById("wfStockPct").style.setProperty("--pct", Math.round(wf.wEq * 100) + "%");
      document.getElementById("wfSummary").textContent =
        `${Math.round(wf.wEq * 100)}/${Math.round((1 - wf.wEq) * 100)} · ${wf.netGeom.toFixed(2)}% net real`;
      document.getElementById("survTargetHint").textContent = `${cfg.survTarget}%`;
      document.getElementById("planAgeHint").textContent = t("age_lbl", { a: cfg.startAge + cfg.horizon });
      document.getElementById("grpTargetSpend").style.display = state.solverMode === "pmt" ? "none" : "block";
      document.getElementById("grpRealReturn").style.display = state.solverMode === "rate" ? "none" : "block";
      document.getElementById("grpSurvTarget").style.display = cfg.autoHor ? "block" : "none";
      document.getElementById("planHorizon").disabled = cfg.autoHor;

      const fv = -cfg.pv * cfg.legPct;
      let solvedPmt = cfg.targetSpend, solvedNper = cfg.horizon, solvedRate = cfg.realRet;
      if (state.solverMode === "pmt") {
        solvedPmt = Math.max(0, -calcPMT(cfg.realRet, cfg.horizon, cfg.pv, fv, cfg.timing));
      } else if (state.solverMode === "nper") {
        solvedNper = calcNPER(cfg.realRet, -cfg.targetSpend, cfg.pv, fv, cfg.timing);
      } else {
        solvedRate = calcRATE(cfg.horizon, -cfg.targetSpend, cfg.pv, fv, cfg.timing);
      }

      const simR = isFinite(solvedRate) ? solvedRate : cfg.realRet;
      const simN = state.solverMode === "nper" ? (isFinite(solvedNper) ? Math.min(80, Math.max(1, Math.ceil(solvedNper))) : 60) : cfg.horizon;
      const pmtUsed = state.solverMode === "pmt" ? solvedPmt : cfg.targetSpend;
      const wrPct = (pmtUsed / cfg.pv) * 100;

      // Survival probability beyond planning horizon
      const survAtH = cfg.curve.surv[Math.min(cfg.curve.surv.length - 1, simN)]?.p ?? 0;

      const isZh = currentLang === "zh-CN";
      document.getElementById("kLbl1").textContent = isZh ? "年度实际可支配支出" : "Annual Real Spending";
      document.getElementById("kVal1").textContent = fmtExactMoney(pmtUsed);
      document.getElementById("kSub1").textContent = `${wrPct.toFixed(2)}% ${isZh ? "初始提取率" : "initial WR"}`;

      document.getElementById("kLbl2").textContent = isZh ? "资产可持续年数" : "Portfolio Horizon";
      document.getElementById("kVal2").textContent = isFinite(solvedNper) ? `${solvedNper.toFixed(1)} ${isZh ? "年" : "yrs"}` : "∞";
      document.getElementById("kSub2").textContent = `${isZh ? "规划至" : "To age"} ${cfg.startAge + simN}`;

      document.getElementById("kLbl3").textContent = state.solverMode === "rate" ? (isZh ? "所需实际年化收益" : "Required Real Return") : (isZh ? "假设固定实际收益" : "Assumed Real Return");
      document.getElementById("kVal3").textContent = isFinite(solvedRate) ? fmtPct(solvedRate * 100, 2, false) : (isZh ? "不可达" : "Infeasible");
      document.getElementById("kSub3").textContent = `${isZh ? "留存目标" : "Legacy"}: ${Math.round(cfg.legPct * 100)}%`;

      document.getElementById("kLbl4").textContent = isZh ? "活过规划年限概率" : "Outliving Horizon Prob.";
      document.getElementById("kVal4").textContent = (survAtH * 100).toFixed(1) + "%";
      document.getElementById("kVal4").className = "kpi-val " + (survAtH > 0.25 ? "neg" : (survAtH <= 0.12 ? "pos" : ""));
      document.getElementById("kSub4").textContent = `${isZh ? "中位寿终" : "Median death"}: ${cfg.curve.p50Age.toFixed(1)}`;

      // Build deterministic schedule
      const rows = [];
      let bal = cfg.pv;
      for (let t = 1; t <= simN; t++) {
        const startBal = bal;
        const curWr = startBal > 0 ? Math.min(100, (pmtUsed / startBal) * 100) : 0;
        let endBal = 0;
        if (cfg.timing === 1) {
          endBal = Math.max(0, startBal - pmtUsed) * (1 + simR);
        } else {
          endBal = Math.max(0, startBal * (1 + simR) - pmtUsed);
        }
        const survP = cfg.curve.surv[Math.min(cfg.curve.surv.length - 1, t)]?.p ?? 0;
        rows.push({ t, age: cfg.startAge + t - 1, startBal, pmt: Math.min(startBal, pmtUsed), endBal, curWr, survP });
        bal = endBal;
      }
      state.lastSchedule = rows;

      const fnName = state.solverMode.toUpperCase();
      document.getElementById("excelEqnHint").textContent =
        state.solverMode === "pmt"
          ? `=PMT(${simR.toFixed(4)}, ${cfg.horizon}, ${Math.round(cfg.pv)}, ${Math.round(fv)}, ${cfg.timing})`
          : state.solverMode === "nper"
          ? `=NPER(${simR.toFixed(4)}, -${Math.round(pmtUsed)}, ${Math.round(cfg.pv)}, ${Math.round(fv)}, ${cfg.timing})`
          : `=RATE(${cfg.horizon}, -${Math.round(pmtUsed)}, ${Math.round(cfg.pv)}, ${Math.round(fv)}, ${cfg.timing})`;

      // Render schedule table
      document.getElementById("detHead").innerHTML = `<tr><th>${isZh ? "年" : "Yr"}</th><th>${isZh ? "年龄" : "Age"}</th><th>${isZh ? "期初实际资产" : "Start Real Bal"}</th><th>${isZh ? "年度支出" : "Real Spend"}</th><th>${isZh ? "当前提取率" : "Current WR"}</th><th>${isZh ? "期末实际资产" : "End Real Bal"}</th><th>${isZh ? "存活概率" : "Survival %"}</th></tr>`;
      document.getElementById("detBody").innerHTML = rows.map(r => `<tr>
        <td><strong>${r.t}</strong></td><td>${r.age}</td><td>${fmtExactMoney(r.startBal)}</td>
        <td class="exp-col">${fmtExactMoney(r.pmt)}</td><td>${r.curWr.toFixed(2)}%</td>
        <td><strong>${fmtExactMoney(r.endBal)}</strong></td><td class="muted">${(r.survP * 100).toFixed(1)}%</td>
      </tr>`).join("");

      // Mortality tab metrics & table
      document.getElementById("mkMean").textContent = cfg.curve.meanAge.toFixed(1);
      document.getElementById("mkMeanSub").textContent = `${isZh ? "剩余" : "Remaining"} +${(cfg.curve.meanAge - cfg.startAge).toFixed(1)} ${isZh ? "年" : "yrs"}`;
      document.getElementById("mkMed").textContent = cfg.curve.p50Age.toFixed(1);
      document.getElementById("mkP10").textContent = cfg.curve.p10Age.toFixed(1);
      const idx95 = Math.max(0, Math.min(cfg.curve.surv.length - 1, 95 - cfg.startAge));
      const p95 = cfg.curve.surv[idx95]?.p ?? 0;
      document.getElementById("mkP95").textContent = (p95 * 100).toFixed(1) + "%";
      document.getElementById("mkP95Sub").textContent = `${isZh ? "相对95岁规划期" : "At age 95"}`;

      const cM = buildSurvivalCurve(MORT_DATA, { table: cfg.table, startAge: cfg.startAge, household: "male", healthMult: cfg.healthMult });
      const cF = buildSurvivalCurve(MORT_DATA, { table: cfg.table, startAge: cfg.startAge, household: "female", healthMult: cfg.healthMult });
      const cC = buildSurvivalCurve(MORT_DATA, { table: cfg.table, startAge: cfg.startAge, household: "couple", healthMult: cfg.healthMult });
      const cSSA = buildSurvivalCurve(MORT_DATA, { table: "ssa", startAge: cfg.startAge, household: "couple", healthMult: 1.0 });
      state.lastMortGroup = { cM, cF, cC, cSSA, cfg };

      const targetAges = [70, 75, 80, 85, 90, 95, 100].filter(a => a >= cfg.startAge);
      document.getElementById("mortCompHead").innerHTML = `<tr><th>${isZh ? "组别" : "Group"}</th><th>${isZh ? "期望寿终" : "Mean Age"}</th><th>${isZh ? "中位(50%)" : "Median"}</th><th>10% Surv.</th>${targetAges.map(a => `<th>${isZh ? a + "岁" : "Age " + a}</th>`).join("")}</tr>`;
      const mRows = [
        [isZh ? "男性 (所选表)" : "Male (Selected)", cM],
        [isZh ? "女性 (所选表)" : "Female (Selected)", cF],
        [isZh ? "夫妻长寿者 (所选表)" : "Couple (Selected)", cC],
        [isZh ? "夫妻长寿者 (SSA时期表)" : "Couple (SSA Period)", cSSA],
      ];
      document.getElementById("mortCompBody").innerHTML = mRows.map(([lbl, crv]) => `<tr>
        <td><strong>${lbl}</strong></td><td>${crv.meanAge.toFixed(1)}</td><td>${crv.p50Age.toFixed(1)}</td><td><strong>${crv.p10Age.toFixed(1)}</strong></td>
        ${targetAges.map(a => `<td>${((crv.surv[a - cfg.startAge]?.p ?? 0) * 100).toFixed(0)}%</td>`).join("")}
      </tr>`).join("");

      renderMatrix(cfg, simR);
      redrawCharts(cfg, wf, rows);
      try { localStorage.setItem(STORAGE_KEY, JSON.stringify({ solverMode: state.solverMode, tab: state.tab, pv: cfg.pv, realRet: cfg.realRet * 100, horizon: cfg.horizon, legPct: cfg.legPct * 100, timing: cfg.timing, startAge: cfg.startAge, household: cfg.household, table: cfg.table })); } catch (_) {}
    }

    function renderMatrix(cfg, simR) {
      const isZh = currentLang === "zh-CN";
      const horizons = [10, 15, 20, 25, 30, 35, 40, 45, 50];
      const rets = [-1, 0, 1, 1.33, 2, 3, 4, 5, 6, 7];
      const legLbl = cfg.legPct === 0 ? (isZh ? "耗尽本金 (0%)" : "Deplete All Assets (0%)") : (isZh ? `保留 ${Math.round(cfg.legPct * 100)}% 实际财富` : `Preserve ${Math.round(cfg.legPct * 100)}% Real Wealth`);
      document.getElementById("matTitle").textContent = `${isZh ? "图 2.8–2.10：可持续实际支出率 (%)" : "Ex. 2.8–2.10: Sustainable Real Spending Rates (%)"} · ${legLbl}`;
      document.getElementById("matSub").textContent = cfg.timing === 1 ? (isZh ? "年初提取 (type=1)" : "Start-of-year withdrawals") : (isZh ? "年末提取 (type=0)" : "End-of-year withdrawals");
      document.getElementById("matHead").innerHTML = `<tr><th>${isZh ? "固定实际收益 \\ 年限" : "Real Return \\ Horizon"}</th>${horizons.map(h => `<th>${h}${isZh ? "年" : "y"}</th>`).join("")}</tr>`;
      document.getElementById("matBody").innerHTML = rets.map(rPct => {
        const r = rPct / 100;
        const isRowActive = Math.abs(r - simR) < 0.004;
        return `<tr><td><strong>${rPct.toFixed(rPct === 1.33 ? 2 : 1)}%</strong></td>${horizons.map(h => {
          const wr = Math.max(0, -calcPMT(r, h, 100, -100 * cfg.legPct, cfg.timing));
          const isActive = isRowActive && h === cfg.horizon;
          return `<td class="hm-cell${isActive ? " hm-active" : ""}">${wr.toFixed(1)}%</td>`;
        }).join("")}</tr>`;
      }).join("");
    }

    function redrawCharts(cfg, wf, rows) {
      if (state.tab === "solver") {
        drawBalanceChart(rows, cfg);
        drawWaterfallChart(wf);
      } else if (state.tab === "mortality" && state.lastMortGroup) {
        drawSurvivalChart(state.lastMortGroup);
        drawPdfChart(cfg.curve);
      }
    }

    function drawBalanceChart(rows, cfg) {
      const sc = setupCanvas(document.getElementById("balCanvas"));
      if (!sc || !rows.length) return;
      const { ctx, w, h } = sc;
      const C = getThemeColors();
      ctx.clearRect(0, 0, w, h);
      const pad = { l: 64, r: 44, t: 18, b: 28 }, cw = w - pad.l - pad.r, ch = h - pad.t - pad.b;
      const bals = [cfg.pv, ...rows.map(r => r.endBal)];
      const maxB = Math.max(cfg.pv * 1.1, ...bals) * 1.05;
      const yTicks = computeNiceLinearTicks(0, maxB, 4);
      const minB = yTicks[0], topB = yTicks[yTicks.length - 1];
      const mapX = i => pad.l + (i / rows.length) * cw;
      const mapY = v => pad.t + ch - ((v - minB) / (topB - minB || 1)) * ch;
      const mapYWr = v => pad.t + ch - (Math.min(25, v) / 25) * ch;

      ctx.strokeStyle = C.grid; ctx.lineWidth = 1; ctx.fillStyle = C.muted; ctx.font = CANVAS_FONT; ctx.textAlign = "right";
      yTicks.forEach(v => {
        const y = mapY(v);
        ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(w - pad.r, y); ctx.stroke();
        ctx.fillText(fmtCompactMoney(v), pad.l - 6, y + 4);
      });
      ctx.fillStyle = C.danger; ctx.textAlign = "left";
      [0, 10, 20].forEach(v => ctx.fillText(v + "%", w - pad.r + 6, mapYWr(v) + 4));

      // Balance curve
      ctx.beginPath(); ctx.strokeStyle = C.port; ctx.lineWidth = 2.4;
      bals.forEach((b, i) => { const x = mapX(i), y = mapY(b); if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); });
      ctx.stroke();

      // Current WR curve
      ctx.beginPath(); ctx.strokeStyle = C.danger; ctx.lineWidth = 1.6; ctx.setLineDash([4, 3]);
      rows.forEach((r, i) => { const x = mapX(i + 1), y = mapYWr(r.curWr); if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); });
      ctx.stroke(); ctx.setLineDash([]);

      ctx.fillStyle = C.muted; ctx.textAlign = "center";
      [0, Math.round(rows.length / 2), rows.length].forEach(i => ctx.fillText("Yr " + i, mapX(i), h - 8));
    }

    function drawWaterfallChart(wf) {
      const sc = setupCanvas(document.getElementById("wfCanvas"));
      if (!sc) return;
      const { ctx, w, h } = sc;
      const C = getThemeColors();
      ctx.clearRect(0, 0, w, h);
      const isZh = currentLang === "zh-CN";
      const items = [
        [isZh ? "历史算术" : "Hist Arith", wf.histArith, C.accent],
        [isZh ? "历史复利" : "Hist Geom", wf.histGeom, C.accent],
        [isZh ? "低利率算术" : "Adj Arith", wf.adjArith, C.port],
        [isZh ? "低利率复利" : "Adj Geom", wf.adjGeom, C.port],
        [isZh ? "净实际复利" : "Net Real", wf.netGeom, C.success],
      ];
      const pad = { l: 44, r: 16, t: 22, b: 30 }, cw = w - pad.l - pad.r, ch = h - pad.t - pad.b;
      const maxV = Math.max(8, ...items.map(x => x[1])) * 1.15;
      const ticks = computeNiceLinearTicks(0, maxV, 4);
      const topV = ticks[ticks.length - 1];
      const mapY = v => pad.t + ch - (Math.max(0, v) / topV) * ch;
      ctx.strokeStyle = C.grid; ctx.font = CANVAS_FONT; ctx.textAlign = "right"; ctx.fillStyle = C.muted;
      ticks.forEach(v => {
        const y = mapY(v);
        ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(w - pad.r, y); ctx.stroke();
        ctx.fillText(v.toFixed(1) + "%", pad.l - 5, y + 4);
      });
      const bw = Math.min(44, (cw / items.length) * 0.56);
      items.forEach(([lbl, val, col], i) => {
        const cx = pad.l + ((i + 0.5) / items.length) * cw;
        const y = mapY(val), y0 = mapY(0);
        ctx.fillStyle = col;
        ctx.fillRect(cx - bw / 2, y, bw, y0 - y);
        ctx.fillStyle = C.text; ctx.textAlign = "center";
        ctx.fillText(val.toFixed(2) + "%", cx, y - 5);
        ctx.fillStyle = C.muted;
        ctx.fillText(lbl, cx, h - 9);
      });
    }

    function drawSurvivalChart(mg) {
      const sc = setupCanvas(document.getElementById("survCanvas"));
      if (!sc) return;
      const { ctx, w, h } = sc;
      const C = getThemeColors();
      ctx.clearRect(0, 0, w, h);
      const maxAge = 105, a0 = mg.cfg.startAge;
      const pad = { l: 44, r: 16, t: 18, b: 28 }, cw = w - pad.l - pad.r, ch = h - pad.t - pad.b;
      const mapX = age => pad.l + ((age - a0) / (maxAge - a0)) * cw;
      const mapY = p => pad.t + ch - p * ch;
      ctx.strokeStyle = C.grid; ctx.font = CANVAS_FONT; ctx.textAlign = "right"; ctx.fillStyle = C.muted;
      [0, 0.25, 0.5, 0.75, 1.0].forEach(p => {
        const y = mapY(p); ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(w - pad.r, y); ctx.stroke();
        ctx.fillText(Math.round(p * 100) + "%", pad.l - 5, y + 4);
      });
      const plot = (crv, col, dash = []) => {
        ctx.beginPath(); ctx.strokeStyle = col; ctx.lineWidth = 2.2; ctx.setLineDash(dash);
        crv.surv.filter(x => x.age <= maxAge).forEach((x, i) => {
          const px = mapX(x.age), py = mapY(x.p);
          if (i === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
        });
        ctx.stroke(); ctx.setLineDash([]);
      };
      plot(mg.cM, C.accent); plot(mg.cF, C.inflation); plot(mg.cC, C.success); plot(mg.cSSA, C.muted, [4, 3]);
      ctx.fillStyle = C.muted; ctx.textAlign = "center";
      for (let a = Math.ceil(a0 / 5) * 5; a <= maxAge; a += 10) ctx.fillText(String(a), mapX(a), h - 8);
    }

    function drawPdfChart(curve) {
      const sc = setupCanvas(document.getElementById("pdfCanvas"));
      if (!sc) return;
      const { ctx, w, h } = sc;
      const C = getThemeColors();
      ctx.clearRect(0, 0, w, h);
      const pts = curve.pdf.filter(x => x.age <= 105);
      const maxP = Math.max(0.05, ...pts.map(x => x.prob)) * 1.15;
      const pad = { l: 44, r: 16, t: 18, b: 28 }, cw = w - pad.l - pad.r, ch = h - pad.t - pad.b;
      const bw = Math.max(2, cw / pts.length * 0.75);
      const mapX = i => pad.l + ((i + 0.5) / pts.length) * cw;
      const mapY = p => pad.t + ch - (p / maxP) * ch;
      ctx.strokeStyle = C.grid; ctx.font = CANVAS_FONT; ctx.textAlign = "right"; ctx.fillStyle = C.muted;
      [0, maxP * 0.5, maxP].forEach(p => {
        const y = mapY(p); ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(w - pad.r, y); ctx.stroke();
        ctx.fillText((p * 100).toFixed(1) + "%", pad.l - 5, y + 4);
      });
      pts.forEach((pt, i) => {
        const x = mapX(i), y = mapY(pt.prob);
        ctx.fillStyle = Math.abs(pt.age - curve.p50Age) < 1 ? C.accent : C.port;
        ctx.globalAlpha = 0.78;
        ctx.fillRect(x - bw / 2, y, bw, pad.t + ch - y);
      });
      ctx.globalAlpha = 1.0;
      ctx.fillStyle = C.muted; ctx.textAlign = "center";
      pts.forEach((pt, i) => { if (pt.age % 10 === 0) ctx.fillText(String(pt.age), mapX(i), h - 8); });
    }

    function applyPreset(name) {
      document.querySelectorAll(".preset-btn").forEach(b => b.classList.toggle("active", b.dataset.preset === name));
      state.activePreset = name;
      if (name === "four_pct") {
        document.getElementById("realReturnInput").value = "1.33";
        document.getElementById("planHorizon").value = "30";
        document.getElementById("legacyPct").value = "0";
        document.getElementById("autoHorizonSwitch").checked = false;
      } else if (name === "hist_5050") {
        document.getElementById("realReturnInput").value = "5.10";
        document.getElementById("planHorizon").value = "30";
        document.getElementById("legacyPct").value = "0";
        document.getElementById("autoHorizonSwitch").checked = false;
      } else if (name === "low_tips") {
        document.getElementById("realReturnInput").value = "2.70";
        document.getElementById("planHorizon").value = "30";
        document.getElementById("autoHorizonSwitch").checked = false;
      } else if (name === "soa_couple") {
        document.getElementById("householdType").value = "couple";
        document.getElementById("mortTable").value = "soa_2017";
        document.getElementById("autoHorizonSwitch").checked = true;
        document.getElementById("survTargetPct").value = "10";
      }
      updateAll();
    }

    function onThemeOrLangChange() { updateAll(); }

    document.querySelectorAll("#solverModeCtl button").forEach(b => {
      b.addEventListener("click", () => {
        state.solverMode = b.dataset.v;
        document.querySelectorAll("#solverModeCtl button").forEach(x => setBtnActive(x, x === b));
        updateAll();
      });
    });
    document.querySelectorAll(".tab-btn").forEach(b => {
      b.addEventListener("click", () => {
        state.tab = b.dataset.tab;
        document.querySelectorAll(".tab-btn").forEach(x => { x.classList.toggle("active", x === b); x.setAttribute("aria-selected", x === b ? "true" : "false"); });
        document.getElementById("paneSolver").style.display = state.tab === "solver" ? "block" : "none";
        document.getElementById("paneMortality").style.display = state.tab === "mortality" ? "block" : "none";
        document.getElementById("paneMatrix").style.display = state.tab === "matrix" ? "block" : "none";
        updateAll();
      });
    });
    document.querySelectorAll(".preset-btn").forEach(b => b.addEventListener("click", () => applyPreset(b.dataset.preset)));
    document.querySelectorAll("#retChips .chip").forEach(c => {
      c.addEventListener("click", () => {
        document.getElementById("realReturnInput").value = c.dataset.r;
        document.querySelectorAll("#retChips .chip").forEach(x => setBtnActive(x, x === c));
        updateAll();
      });
    });
    document.getElementById("btnApplyWaterfall").addEventListener("click", () => {
      const wf = computeWaterfall();
      document.getElementById("realReturnInput").value = wf.netGeom.toFixed(2);
      updateAll();
    });
    document.getElementById("btnReset").addEventListener("click", () => applyPreset("four_pct"));
    document.getElementById("btnExportCsv").addEventListener("click", () => {
      downloadCsv("pfau_ch2_schedule.csv", ["Year", "Age", "Start_Real_Bal", "Real_Spend", "Current_WR_pct", "End_Real_Bal", "Survival_Pct"],
        state.lastSchedule.map(r => [r.t, r.age, r.startBal.toFixed(2), r.pmt.toFixed(2), r.curWr.toFixed(2), r.endBal.toFixed(2), (r.survP * 100).toFixed(2)]));
    });
    ["initPortfolio", "targetSpend", "realReturnInput", "legacyPct", "withdrawTiming", "startAge", "householdType", "mortTable", "healthClass", "autoHorizonSwitch", "survTargetPct", "planHorizon", "wfStockPct", "wfTipsShift", "wfFeeBps"].forEach(id => {
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
        slug="fixed-returns-longevity",
        title_en="Fixed Returns & Longevity Risk",
        extra_css=EXTRA_CSS,
        body_html=body_html,
        embedded_data_js=embedded,
        page_i18n=page_i18n,
        page_js=page_js,
    )


if __name__ == "__main__":
    build_ch2()
