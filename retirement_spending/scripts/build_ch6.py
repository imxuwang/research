#!/usr/bin/env python3
"""Build Lab 6 (Chapter 6): Variable Spending Rules, 10-Strategy Arena & PAY Rule Calibrator."""

from shared_shell import dump_json_inline, load_csv_records, render_page
from shared_sim_js import SHARED_SIM_JS


def build_ch6():
    nyu = load_csv_records("nyu_stern_1928_2025_full.csv")
    shiller = load_csv_records("shiller_us_1871_2025_annual.csv")
    mort = load_csv_records("mortality_and_rmd_tables.csv")

    rmd_pre = {str(int(r["Age"])): r["IRS_RMD_Divisor_Pre2022"] for r in mort if r.get("IRS_RMD_Divisor_Pre2022")}
    rmd_2022 = {str(int(r["Age"])): r["IRS_RMD_Divisor_2022Plus"] for r in mort if r.get("IRS_RMD_Divisor_2022Plus")}

    body_html = """  <main class="layout">
    <aside class="sidebar" aria-label="Simulation parameters" data-i18n-aria-label="aria_sidebar">
      <div class="side-section">
        <div class="sec-head-static">
          <h2 class="sec-title" data-i18n="sec_presets">Book Exhibit Presets</h2>
          <button type="button" class="link-btn" id="btnReset" data-i18n="btn_reset">Reset</button>
        </div>
        <div class="preset-grid">
          <button type="button" class="preset-btn active" data-preset="fixed4">
            <span class="p-title" data-i18n="pre_f4_t">Ex. 6.16–6.21 · Fixed 4%</span>
            <span class="p-meta" data-i18n="pre_f4_m">50/50 · 4.0% Initial WR</span>
          </button>
          <button type="button" class="preset-btn" data-preset="cons">
            <span class="p-title" data-i18n="pre_c_t">Ex. 6.22 · Cons. PAY</span>
            <span class="p-meta" data-i18n="pre_c_m">25/75 · 5% &lt; $20k Yr 30</span>
          </button>
          <button type="button" class="preset-btn" data-preset="mod">
            <span class="p-title" data-i18n="pre_m_t">Ex. 6.23 · Mod. PAY</span>
            <span class="p-meta" data-i18n="pre_m_m">50/50 · 10% &lt; $15k Yr 30</span>
          </button>
          <button type="button" class="preset-btn" data-preset="aggr">
            <span class="p-title" data-i18n="pre_a_t">Ex. 6.24 · Aggr. PAY</span>
            <span class="p-meta" data-i18n="pre_a_m">75/25 · 20% &lt; $10k Yr 30</span>
          </button>
        </div>
      </div>

      <div class="side-section">
        <div class="sec-head-static"><h2 class="sec-title" data-i18n="sec_engine">Return Engine &amp; Portfolio</h2></div>
        <div class="control-group">
          <label for="engineMode"><span data-i18n="lbl_engine">Market Return Regime</span></label>
          <select id="engineMode">
            <option value="ch3a" selected data-i18n="eng_ch3a">Ch. 3A Low-Yield AR(1) Monte Carlo</option>
            <option value="shiller" data-i18n="eng_shiller">Shiller 1871–2025 Rolling Cohorts</option>
            <option value="nyu" data-i18n="eng_nyu">NYU 1928–2025 Rolling Cohorts</option>
          </select>
        </div>
        <div class="control-group" id="mcPathsGroup">
          <label><span data-i18n="lbl_mc_paths">Monte Carlo sample paths</span></label>
          <div class="seg-ctl" id="mcPathsCtl">
            <button type="button" class="active" data-val="1000">1,000</button>
            <button type="button" data-val="3000">3,000</button>
          </div>
        </div>
        <div class="control-group">
          <label for="eqSlider"><span data-i18n="lbl_eq_wt">Portfolio Allocation (Stocks / Bonds)</span></label>
          <input type="range" id="eqSlider" class="ratio-slider" min="0" max="100" step="5" value="50" />
          <div class="ratio-labels"><span id="eqLbl">50% Stocks</span><span id="bdLbl">50% Bonds</span></div>
        </div>
        <div class="control-group row-2">
          <div>
            <label for="initPortfolio"><span data-i18n="lbl_v0">Initial Portfolio ($)</span></label>
            <div class="currency-field"><span class="currency-prefix">$</span><input type="text" id="initPortfolio" value="100,000" inputmode="numeric" /></div>
          </div>
          <div>
            <label for="horizonYrs"><span data-i18n="lbl_horizon">Horizon (yrs)</span></label>
            <input type="number" id="horizonYrs" value="30" min="15" max="45" step="5" />
          </div>
        </div>
      </div>

      <div class="side-section">
        <div class="sec-head-static">
          <h2 class="sec-title" data-i18n="sec_calib">Initial Withdrawal Calibration</h2>
          <button type="button" class="info-btn" data-info-key="info_pay" aria-expanded="false" aria-label="PAY Rule info">?</button>
        </div>
        <div class="control-group">
          <div class="seg-ctl" id="calibModeCtl">
            <button type="button" class="active" data-val="fixed" data-i18n="mode_fixed">Fixed Initial WR</button>
            <button type="button" data-val="pay" data-i18n="mode_pay">PAY Rule™ Target</button>
          </div>
        </div>
        <div class="control-group" id="fixedWrBox">
          <label for="initWrPct"><span data-i18n="lbl_w0">Initial Withdrawal Rate (%)</span></label>
          <input type="number" id="initWrPct" value="4.0" min="1.5" max="10.0" step="0.25" />
        </div>
        <div class="control-group row-2" id="payBox" style="display:none;">
          <div>
            <label for="payXpct"><span data-i18n="lbl_pay_x">Max Shortfall Prob X (%)</span></label>
            <input type="number" id="payXpct" value="10" min="1" max="40" step="1" />
          </div>
          <div>
            <label for="payYamt"><span data-i18n="lbl_pay_y">Min Real Legacy Y ($)</span></label>
            <div class="currency-field"><span class="currency-prefix">$</span><input type="text" id="payYamt" value="15,000" inputmode="numeric" /></div>
          </div>
        </div>
      </div>

      <div class="side-section">
        <div class="sec-head-static"><h2 class="sec-title" data-i18n="sec_rules">Focus Strategy &amp; Rule Tuning</h2></div>
        <div class="control-group">
          <label for="focusStrat"><span data-i18n="lbl_focus">Focus Strategy (1–10)</span></label>
          <select id="focusStrat">
            <option value="1" data-i18n="st_1">1. Constant Real (Bengen)</option>
            <option value="2" data-i18n="st_2">2. Fixed Percentage</option>
            <option value="3" data-i18n="st_3">3. Endowment Hybrid (50/50)</option>
            <option value="4" data-i18n="st_4">4. Endowment 3-Yr Moving Avg</option>
            <option value="5" data-i18n="st_5">5. Bengen Floor/Ceiling (-15%/+20%)</option>
            <option value="6" data-i18n="st_6">6. Vanguard Floor/Ceiling (-2.5%/+5%)</option>
            <option value="7" data-i18n="st_7">7. Kitces Ratcheting (+10% &gt;150%)</option>
            <option value="8" selected data-i18n="st_8">8. Guyton-Klinger Guardrails</option>
            <option value="9" data-i18n="st_9">9. Zolt Target Glide Path</option>
            <option value="10" data-i18n="st_10">10. Modified IRS RMD</option>
          </select>
        </div>
        <div class="control-group row-2">
          <div>
            <label for="gkGuardPct"><span data-i18n="lbl_gk">G-K Guardrail (±%)</span></label>
            <input type="number" id="gkGuardPct" value="20" min="10" max="40" step="5" />
          </div>
          <div>
            <label for="hybridAlphaPct"><span data-i18n="lbl_hyb">Hybrid Fixed Wt (%)</span></label>
            <input type="number" id="hybridAlphaPct" value="50" min="10" max="90" step="10" />
          </div>
        </div>
        <div class="control-group row-2">
          <div>
            <label for="zoltHor"><span data-i18n="lbl_zolt_h">Zolt Glidepath (yrs)</span></label>
            <input type="number" id="zoltHor" value="45" min="30" max="60" step="5" />
          </div>
          <div>
            <label for="rmdMode"><span data-i18n="lbl_rmd_tbl">IRS RMD Table</span></label>
            <select id="rmdMode">
              <option value="pre2022" selected data-i18n="rmd_book">Pre-2022 Book (31.0 @ 65)</option>
              <option value="2022plus" data-i18n="rmd_new">2022+ Updated (33.4 @ 65)</option>
            </select>
          </div>
        </div>
        <div class="control-group switch-row">
          <label for="vgNominalSwitch" data-i18n="lbl_vg_nom">Vanguard rule on nominal prior spend</label>
          <input type="checkbox" id="vgNominalSwitch" class="switch" checked />
        </div>
      </div>
    </aside>

    <section class="workspace" aria-label="Simulation outputs" data-i18n-aria-label="aria_workspace">
      <div class="results-shell">
        <div class="tabs-bar">
          <div class="tab-strip" role="tablist">
            <button type="button" class="tab-btn active" role="tab" aria-selected="true" data-tab="matrix" data-i18n="tab_matrix">10-Strategy Matrix &amp; PAY Rule™</button>
            <button type="button" class="tab-btn" role="tab" aria-selected="false" data-tab="focus" data-i18n="tab_focus">Strategy Fan &amp; Zolt Glidepath</button>
            <button type="button" class="tab-btn" role="tab" aria-selected="false" data-tab="hist" data-i18n="tab_hist">Historical Cohort Arena</button>
          </div>
        </div>

        <div class="results-body">
          <div id="paneMatrix" class="tab-pane">
            <div class="kpis kpis-4 kpis-flush-top">
              <div class="kpi"><div class="kpi-label" data-i18n="k_w0">Focus Initial WR / Yr-1</div><div class="kpi-val" id="kW0">—</div><div class="kpi-sub" id="kW0Sub">—</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="k_med30">Median Yr-30 Real Spend</div><div class="kpi-val pos" id="kMed30">—</div><div class="kpi-sub" id="kMed30Sub">—</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="k_wlth">Real Legacy (50th / 10th)</div><div class="kpi-val" id="kWlth">—</div><div class="kpi-sub" id="kWlthSub">—</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="k_dsv">Downside Spend Volatility</div><div class="kpi-val neg" id="kDsv">—</div><div class="kpi-sub" id="kDsvSub">—</div></div>
            </div>

            <div class="panel-block">
              <div class="legend">
                <strong data-i18n="ttl_scatter">Spending-Volatility Frontier: Median Yr-30 Real Spending vs. Median DSV (%)</strong>
                <div class="legend-items">
                  <div class="legend-item"><span class="swatch" style="background:var(--port);"></span><span data-i18n="leg_focus">Selected Focus Strategy</span></div>
                  <div class="legend-item"><span class="swatch" style="background:var(--muted);"></span><span data-i18n="leg_others">Other Strategies (1–10)</span></div>
                </div>
              </div>
              <div class="chart-wrap"><canvas id="scatterCanvas" height="250"></canvas><div class="tooltip" id="scatterTip"></div></div>
            </div>

            <div class="panel-block">
              <div class="card-title">
                <h3 class="sec-title" data-i18n="ttl_table">Ex. 6.16–6.24: Full 10-Strategy Distribution &amp; DSV Comparison (click row to inspect)</h3>
                <span class="subhead" id="matrixSub">—</span>
              </div>
              <div class="table-container" style="max-height:none;"><table><thead id="matrixHead"></thead><tbody id="matrixBody"></tbody></table></div>
            </div>
          </div>

          <div id="paneFocus" class="tab-pane" style="display:none;">
            <div class="split-grid">
              <div class="grid-cell">
                <div class="legend">
                  <strong id="ttlFanSpend">Real Spending Percentiles (10th / 50th / 90th)</strong>
                  <div class="legend-items">
                    <div class="legend-item"><span class="swatch" style="background:var(--port);"></span><span data-i18n="leg_sel_med">Selected Median</span></div>
                    <div class="legend-item"><span class="swatch" style="background:var(--muted);"></span><span data-i18n="leg_base_med">Constant-Real Base</span></div>
                  </div>
                </div>
                <div class="chart-wrap"><canvas id="spendFanCanvas" height="270"></canvas><div class="tooltip" id="spendFanTip"></div></div>
              </div>
              <div class="grid-cell">
                <div class="legend">
                  <strong data-i18n="ttl_fan_wealth">Real Portfolio Wealth Percentiles (10th / 50th / 90th)</strong>
                  <div class="legend-items">
                    <div class="legend-item"><span class="swatch" style="background:var(--success);"></span><span data-i18n="leg_sel_wlth">Selected Median</span></div>
                    <div class="legend-item"><span class="swatch" style="background:var(--mc-outer-band);height:8px;"></span><span>10–90%</span></div>
                  </div>
                </div>
                <div class="chart-wrap"><canvas id="wealthFanCanvas" height="270"></canvas><div class="tooltip" id="wealthFanTip"></div></div>
              </div>
            </div>

            <div class="panel-block">
              <div class="card-title">
                <h3 class="sec-title" data-i18n="ttl_zolt">Ex. 6.13: Zolt Nominal Target Glide Path Calibration</h3>
                <span class="subhead" id="zoltSub">—</span>
              </div>
              <div class="chart-wrap"><canvas id="zoltCanvas" height="225"></canvas><div class="tooltip" id="zoltTip"></div></div>
            </div>
          </div>

          <div id="paneHist" class="tab-pane" style="display:none;">
            <div class="panel-block">
              <div class="card-title">
                <h3 class="sec-title" data-i18n="ttl_hist_ctrl">Cohort Stress Test (Actual Inflation &amp; Sequence Returns)</h3>
                <select id="cohortYearSel" style="width:auto;min-width:210px;">
                  <option value="1966" selected data-i18n="coh_1966">1966 · Stagflation (Worst 30Y US)</option>
                  <option value="1929" data-i18n="coh_1929">1929 · Great Depression &amp; Deflation</option>
                  <option value="1946" data-i18n="coh_1946">1946 · Post-WWII Inflation</option>
                  <option value="1973" data-i18n="coh_1973">1973 · Oil Shock</option>
                  <option value="1982" data-i18n="coh_1982">1982 · Secular Bull Market</option>
                  <option value="1996" data-i18n="coh_1996">1996 · Tech Bubble &amp; GFC 30Y</option>
                </select>
              </div>
              <div class="split-grid" style="border-top:1px solid var(--border);margin-top:8px;">
                <div class="grid-cell">
                  <div class="legend"><strong data-i18n="ttl_hs">Real Annual Spending ($) Across 5 Archetypes</strong></div>
                  <div class="chart-wrap"><canvas id="histSpendCanvas" height="255"></canvas><div class="tooltip" id="histSpendTip"></div></div>
                </div>
                <div class="grid-cell">
                  <div class="legend"><strong data-i18n="ttl_hw">Remaining Real Portfolio Wealth ($)</strong></div>
                  <div class="chart-wrap"><canvas id="histWealthCanvas" height="255"></canvas><div class="tooltip" id="histWealthTip"></div></div>
                </div>
              </div>
            </div>
            <div class="panel-block">
              <div class="table-container" style="max-height:300px;"><table><thead id="histHead"></thead><tbody id="histBody"></tbody></table></div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </main>
"""

    page_i18n = {
        "page_title": {"en-UK": "Variable Spending & PAY Rule™ Lab · Ch. 6", "zh-CN": "动态支出法则与 PAY Rule™ 实验室 · 第6章"},
        "app_title": {"en-UK": "Ch. 6 · Variable Spending Rules & PAY Rule™", "zh-CN": "第6章 · 动态支出策略矩阵与 PAY Rule™"},
        "sec_presets": {"en-UK": "Book Exhibit Presets", "zh-CN": "全书图表预设"},
        "pre_f4_t": {"en-UK": "Ex. 6.16–6.21 · Fixed 4%", "zh-CN": "图 6.16–6.21 · 固定 4%"},
        "pre_f4_m": {"en-UK": "50/50 · 4.0% Initial WR", "zh-CN": "50/50 · 初始提取率 4.0%"},
        "pre_c_t": {"en-UK": "Ex. 6.22 · Cons. PAY", "zh-CN": "表 6.22 · 保守 PAY"},
        "pre_c_m": {"en-UK": "25/75 · 5% < $20k Yr 30", "zh-CN": "25/75 · 5% 低于 $20k"},
        "pre_m_t": {"en-UK": "Ex. 6.23 · Mod. PAY", "zh-CN": "表 6.23 · 稳健 PAY"},
        "pre_m_m": {"en-UK": "50/50 · 10% < $15k Yr 30", "zh-CN": "50/50 · 10% 低于 $15k"},
        "pre_a_t": {"en-UK": "Ex. 6.24 · Aggr. PAY", "zh-CN": "表 6.24 · 进取 PAY"},
        "pre_a_m": {"en-UK": "75/25 · 20% < $10k Yr 30", "zh-CN": "75/25 · 20% 低于 $10k"},
        "sec_engine": {"en-UK": "Return Engine & Portfolio", "zh-CN": "收益引擎与组合权重"},
        "lbl_engine": {"en-UK": "Market Return Regime", "zh-CN": "市场收益情境"},
        "eng_ch3a": {"en-UK": "Ch. 3A Low-Yield AR(1) Monte Carlo", "zh-CN": "第3A章 低利率 AR(1) 蒙特卡洛"},
        "eng_shiller": {"en-UK": "Shiller 1871–2025 Rolling Cohorts", "zh-CN": "Shiller 1871–2025 历史滚动"},
        "eng_nyu": {"en-UK": "NYU 1928–2025 Rolling Cohorts", "zh-CN": "NYU 1928–2025 历史滚动"},
        "lbl_mc_paths": {"en-UK": "Monte Carlo sample paths", "zh-CN": "蒙特卡洛模拟路径数"},
        "lbl_eq_wt": {"en-UK": "Portfolio Allocation (Stocks / Bonds)", "zh-CN": "股债配置权重"},
        "lbl_v0": {"en-UK": "Initial Portfolio ($)", "zh-CN": "期初本金 ($)"},
        "lbl_horizon": {"en-UK": "Horizon (yrs)", "zh-CN": "退休期限 (年)"},
        "sec_calib": {"en-UK": "Initial Withdrawal Calibration", "zh-CN": "初始提取率校准模式"},
        "info_pay": {
            "en-UK": "<strong>Pfau's PAY Rule™ (Probability / Amount / Year):</strong> Calibrates the highest initial withdrawal rate w0 such that no more than <strong>X%</strong> of paths finish Year Z below <strong>$Y</strong> in real remaining wealth.",
            "zh-CN": "<strong>Pfau PAY Rule™（概率/金额/年份规则）：</strong>反解最大初始提取率 w0，使第 Z 年实际剩余资产低于目标下限 <strong>$Y</strong> 的情景概率不超过 <strong>X%</strong>。"
        },
        "mode_fixed": {"en-UK": "Fixed Initial WR", "zh-CN": "固定初始提取率"},
        "mode_pay": {"en-UK": "PAY Rule™ Target", "zh-CN": "PAY Rule™ 反解"},
        "lbl_w0": {"en-UK": "Initial Withdrawal Rate (%)", "zh-CN": "初始提取率 (%)"},
        "lbl_pay_x": {"en-UK": "Max Shortfall Prob X (%)", "zh-CN": "最大失血概率 X (%)"},
        "lbl_pay_y": {"en-UK": "Min Real Legacy Y ($)", "zh-CN": "实际遗留资产下限 Y ($)"},
        "sec_rules": {"en-UK": "Focus Strategy & Rule Tuning", "zh-CN": "重点策略与规则微调"},
        "lbl_focus": {"en-UK": "Focus Strategy (1–10)", "zh-CN": "当前重点策略 (1–10)"},
        "st_1": {"en-UK": "1. Constant Real (Bengen)", "zh-CN": "1. 固定实际支出 (Bengen)"},
        "st_2": {"en-UK": "2. Fixed Percentage", "zh-CN": "2. 固定比例百分比"},
        "st_3": {"en-UK": "3. Endowment Hybrid (50/50)", "zh-CN": "3. 捐赠基金混合规则"},
        "st_4": {"en-UK": "4. Endowment 3-Yr Moving Avg", "zh-CN": "4. 3年名义余额均线"},
        "st_5": {"en-UK": "5. Bengen Floor/Ceiling (-15%/+20%)", "zh-CN": "5. Bengen 硬性上下限 (-15%/+20%)"},
        "st_6": {"en-UK": "6. Vanguard Floor/Ceiling (-2.5%/+5%)", "zh-CN": "6. Vanguard 比率上下限 (-2.5%/+5%)"},
        "st_7": {"en-UK": "7. Kitces Ratcheting (+10% >150%)", "zh-CN": "7. Kitces 棘轮上调 (+10%)"},
        "st_8": {"en-UK": "8. Guyton-Klinger Guardrails", "zh-CN": "8. Guyton-Klinger 动态护栏"},
        "st_9": {"en-UK": "9. Zolt Target Glide Path", "zh-CN": "9. Zolt 目标下滑轨迹"},
        "st_10": {"en-UK": "10. Modified IRS RMD", "zh-CN": "10. 修正 IRS RMD 法则"},
        "lbl_gk": {"en-UK": "G-K Guardrail (±%)", "zh-CN": "G-K 护栏阈值 (±%)"},
        "lbl_hyb": {"en-UK": "Hybrid Fixed Wt (%)", "zh-CN": "混合规则固定权重 (%)"},
        "lbl_zolt_h": {"en-UK": "Zolt Glidepath (yrs)", "zh-CN": "Zolt 轨迹年限 (年)"},
        "lbl_rmd_tbl": {"en-UK": "IRS RMD Table", "zh-CN": "IRS 寿命除数表"},
        "rmd_book": {"en-UK": "Pre-2022 Book (31.0 @ 65)", "zh-CN": "原书表 Pre-2022 (65岁 31.0)"},
        "rmd_new": {"en-UK": "2022+ Updated (33.4 @ 65)", "zh-CN": "2022新版 (65岁 33.4)"},
        "lbl_vg_nom": {"en-UK": "Vanguard rule on nominal prior spend", "zh-CN": "Vanguard 按原书名义上期支出基准"},
        "tab_matrix": {"en-UK": "10-Strategy Matrix & PAY Rule™", "zh-CN": "十策略全景矩阵与 PAY Rule™"},
        "tab_focus": {"en-UK": "Strategy Fan & Zolt Glidepath", "zh-CN": "单策略扇形分布与 Zolt 轨迹"},
        "tab_hist": {"en-UK": "Historical Cohort Arena", "zh-CN": "历史危机队列实战"},
        "k_w0": {"en-UK": "Focus Initial WR / Yr-1", "zh-CN": "初始提取率 / 首年额度"},
        "k_med30": {"en-UK": "Median Yr-30 Real Spend", "zh-CN": "期末实际支出中位数"},
        "k_wlth": {"en-UK": "Real Legacy (50th / 10th)", "zh-CN": "期末实际资产 (中位 / 10分位)"},
        "k_dsv": {"en-UK": "Downside Spend Volatility", "zh-CN": "下行支出波动 DSV (50th/10th)"},
        "ttl_scatter": {"en-UK": "Spending-Volatility Frontier: Median End Real Spending vs. Median DSV (%)", "zh-CN": "支出与稳定度权衡前沿：期末实际支出中位数 vs 下行波动 DSV (%)"},
        "leg_focus": {"en-UK": "Selected Focus Strategy", "zh-CN": "当前重点策略"},
        "leg_others": {"en-UK": "Other Strategies (1–10)", "zh-CN": "其余策略 (1–10)"},
        "ttl_table": {"en-UK": "Ex. 6.16–6.24: Full 10-Strategy Distribution & DSV Comparison (click row to inspect)", "zh-CN": "图 6.16–6.24：十大策略全分布与 DSV 对比表（点击行切换重点策略）"},
        "ttl_fan_wealth": {"en-UK": "Real Portfolio Wealth Percentiles (10th / 50th / 90th)", "zh-CN": "实际组合余额分位数 (10th / 50th / 90th)"},
        "leg_sel_med": {"en-UK": "Selected Median", "zh-CN": "所选策略中位数"},
        "leg_base_med": {"en-UK": "Constant-Real Base", "zh-CN": "固定实际基准线"},
        "leg_sel_wlth": {"en-UK": "Selected Median", "zh-CN": "所选策略中位数"},
        "ttl_zolt": {"en-UK": "Ex. 6.13: Zolt Nominal Target Glide Path Calibration", "zh-CN": "图 6.13：Zolt 名义目标余额下滑轨迹校准"},
        "ttl_hist_ctrl": {"en-UK": "Cohort Stress Test (Actual Inflation & Sequence Returns)", "zh-CN": "历史队列压力测试（真实通胀与收益顺序）"},
        "coh_1966": {"en-UK": "1966 · Stagflation (Worst 30Y US)", "zh-CN": "1966 · 滞胀危机 (美国最差30年)"},
        "coh_1929": {"en-UK": "1929 · Great Depression & Deflation", "zh-CN": "1929 · 大萧条与通缩"},
        "coh_1946": {"en-UK": "1946 · Post-WWII Inflation", "zh-CN": "1946 · 战后高通胀冲击"},
        "coh_1973": {"en-UK": "1973 · Oil Shock", "zh-CN": "1973 · 石油危机"},
        "coh_1982": {"en-UK": "1982 · Secular Bull Market", "zh-CN": "1982 · 长牛起点"},
        "coh_1996": {"en-UK": "1996 · Tech Bubble & GFC 30Y", "zh-CN": "1996 · 科网泡沫与次贷完整30年"},
        "ttl_hs": {"en-UK": "Real Annual Spending ($) Across Archetypes", "zh-CN": "不同法则各年实际支出轨迹 ($)"},
        "ttl_hw": {"en-UK": "Remaining Real Portfolio Wealth ($)", "zh-CN": "剩余实际投资组合资产 ($)"}
    }

    embedded = (
        f"    const NYU = {dump_json_inline(nyu)};\n"
        f"    const SHILLER = {dump_json_inline(shiller)};\n"
        f"    const RMD_PRE = {dump_json_inline(rmd_pre)};\n"
        f"    const RMD_2022 = {dump_json_inline(rmd_2022)};\n"
        + SHARED_SIM_JS
    )

    page_js = r"""
    const STRAT_META = [
      { id: 1, en: "1. Constant Real", zh: "1. 固定实际支出" },
      { id: 2, en: "2. Fixed %", zh: "2. 固定比例" },
      { id: 3, en: "3. Endowment Hybrid", zh: "3. 捐赠基金混合" },
      { id: 4, en: "4. 3-Yr Moving Avg", zh: "4. 3年名义均线" },
      { id: 5, en: "5. Bengen Floor/Ceil", zh: "5. Bengen 硬上限" },
      { id: 6, en: "6. Vanguard Floor/Ceil", zh: "6. Vanguard 比率限" },
      { id: 7, en: "7. Kitces Ratchet", zh: "7. Kitces 棘轮" },
      { id: 8, en: "8. Guyton-Klinger", zh: "8. Guyton-Klinger" },
      { id: 9, en: "9. Zolt Glide Path", zh: "9. Zolt 轨迹" },
      { id: 10, en: "10. Modified RMD", zh: "10. 修正 RMD" }
    ];

    const state = {
      tab: "matrix",
      mcPaths: 1000,
      calibMode: "fixed",
      scatterPts: [],
      results: [],
      fanData: null,
      histData: null,
      zoltData: null,
      lastExport: []
    };

    const ch3aCal = calibrateCh3AEngine(SHILLER);
    const nyuEq = NYU.map(r => (r.NYU_SP500_pct || 0) / 100);
    const nyuBd = NYU.map(r => (r.NYU_US_10Y_TBond_pct || 0) / 100);
    const nyuInf = NYU.map(r => (r.NYU_US_CPI_Inflation_pct || 0) / 100);
    const shEq = SHILLER.map(r => (r.Shiller_SP500_TR_pct || 0) / 100);
    const shBd = SHILLER.map(r => (r.Shiller_10Y_TBond_pct || 0) / 100);
    const shInf = SHILLER.map(r => (r.Shiller_US_CPI_pct || 0) / 100);

    function buildReturnPaths(engine, horizon, nMc) {
      if (engine === "shiller") {
        const paths = [];
        for (let i = 0; i <= SHILLER.length - horizon; i++) {
          paths.push({
            eq: shEq.slice(i, i + horizon),
            bd: shBd.slice(i, i + horizon),
            inf: shInf.slice(i, i + horizon)
          });
        }
        return paths;
      }
      if (engine === "nyu") {
        const paths = [];
        for (let i = 0; i <= NYU.length - horizon; i++) {
          paths.push({
            eq: nyuEq.slice(i, i + horizon),
            bd: nyuBd.slice(i, i + horizon),
            inf: nyuInf.slice(i, i + horizon)
          });
        }
        return paths;
      }
      const rng = mulberry32(20260606);
      const paths = new Array(nMc);
      for (let i = 0; i < nMc; i++) paths[i] = simulateCh3APath(ch3aCal, horizon, rng, 0.0245, 0.017);
      return paths;
    }

    function readCfg() {
      const V0 = Math.max(1000, parseMoney(document.getElementById("initPortfolio")) || 100000);
      const eqW = (parseFloat(document.getElementById("eqSlider").value) || 50) / 100;
      const H = Math.min(45, Math.max(15, parseInt(document.getElementById("horizonYrs").value, 10) || 30));
      const engine = document.getElementById("engineMode").value;
      const w0Fixed = (parseFloat(document.getElementById("initWrPct").value) || 4.0) / 100;
      const payX = Math.min(45, Math.max(1, parseFloat(document.getElementById("payXpct").value) || 10));
      const payY = Math.max(0, parseMoney(document.getElementById("payYamt")));
      const focusId = parseInt(document.getElementById("focusStrat").value, 10) || 8;
      const gkG = (parseFloat(document.getElementById("gkGuardPct").value) || 20) / 100;
      const hybA = (parseFloat(document.getElementById("hybridAlphaPct").value) || 50) / 100;
      const zoltH = parseInt(document.getElementById("zoltHor").value, 10) || 45;
      const rmdByAge = document.getElementById("rmdMode").value === "2022plus" ? RMD_2022 : RMD_PRE;
      const vgNom = document.getElementById("vgNominalSwitch").checked;
      return {
        V0, eqW, H, engine, w0Fixed, payX, payY, focusId,
        simOpts: {
          V0, eqWeight: eqW, horizon: H, startAge: 65, rmdByAge,
          hybridAlpha: hybA, maN: 3, bengenFloor: 0.85, bengenCeil: 1.20,
          vgFloor: 0.975, vgCeil: 1.05, vgNominal: vgNom,
          kitcesThresh: 1.50, kitcesRaise: 1.10, kitcesCooldown: 3,
          gkGuardrail: gkG, gkCut: 0.90, gkRaise: 1.10, gkCutoffRem: 15,
          zoltH, zoltPi: 0.03
        }
      };
    }

    function summarizeStrategy(stratMeta, w0, paths, simOpts) {
      const N = paths.length, H = simOpts.horizon;
      const i10 = Math.min(H - 1, 9), i20 = Math.min(H - 1, 19), iEnd = H - 1;
      const s10 = new Float64Array(N), s20 = new Float64Array(N), s30 = new Float64Array(N);
      const wEnd = new Float64Array(N), dsvArr = new Float64Array(N);
      const allSpend = new Array(H), allWealth = new Array(H + 1);
      for (let t = 0; t < H; t++) allSpend[t] = new Float64Array(N);
      for (let t = 0; t <= H; t++) allWealth[t] = new Float64Array(N);

      for (let i = 0; i < N; i++) {
        const res = simulateCh6Strategy(stratMeta.id, w0, paths[i].eq, paths[i].bd, paths[i].inf, simOpts);
        s10[i] = res.spendReal[i10];
        s20[i] = res.spendReal[i20];
        s30[i] = res.spendReal[iEnd];
        wEnd[i] = res.endWealthReal;
        dsvArr[i] = res.dsvPct;
        for (let t = 0; t < H; t++) allSpend[t][i] = res.spendReal[t];
        for (let t = 0; t <= H; t++) allWealth[t][i] = res.wealthReal[t];
      }
      const qTriplet = arr => {
        const c = arr.slice().sort();
        return { p90: quantileSorted(c, 0.9), p50: quantileSorted(c, 0.5), p10: quantileSorted(c, 0.1), raw: c };
      };
      const t10 = qTriplet(s10), t20 = qTriplet(s20), t30 = qTriplet(s30), tw = qTriplet(wEnd);
      const dsvSorted = dsvArr.slice().sort();
      // DSV is negative magnitude; 10th percentile is the worst tail
      const dsvMed = quantileSorted(dsvSorted, 0.5), dsv10 = quantileSorted(dsvSorted, 0.1);
      const fanS = allSpend.map(col => {
        col.sort();
        return { p10: quantileSorted(col, 0.1), p50: quantileSorted(col, 0.5), p90: quantileSorted(col, 0.9) };
      });
      const fanW = allWealth.map(col => {
        col.sort();
        return { p10: quantileSorted(col, 0.1), p50: quantileSorted(col, 0.5), p90: quantileSorted(col, 0.9) };
      });
      return {
        meta: stratMeta, w0, s1: w0 * simOpts.V0,
        t10, t20, t30, tw, dsvMed, dsv10, fanS, fanW
      };
    }

    function updateAll() {
      const eqSlider = document.getElementById("eqSlider");
      const eqP = parseInt(eqSlider.value, 10);
      eqSlider.style.setProperty("--pct", eqP + "%");
      const isZh = currentLang === "zh-CN";
      document.getElementById("eqLbl").textContent = isZh ? `${eqP}% 股票` : `${eqP}% Stocks`;
      document.getElementById("bdLbl").textContent = isZh ? `${100 - eqP}% 债券` : `${100 - eqP}% Bonds`;

      const cfg = readCfg();
      document.getElementById("mcPathsGroup").style.display = cfg.engine === "ch3a" ? "" : "none";
      document.getElementById("fixedWrBox").style.display = state.calibMode === "fixed" ? "" : "none";
      document.getElementById("payBox").style.display = state.calibMode === "pay" ? "" : "none";

      const paths = buildReturnPaths(cfg.engine, cfg.H, state.mcPaths);
      const calPaths = paths.length > 800 ? paths.slice(0, 600) : paths;
      const results = [];
      let base1Med30 = 1;
      for (const sm of STRAT_META) {
        const w0 = state.calibMode === "pay"
          ? calibratePayRuleW0(sm.id, calPaths, cfg.payX, cfg.payY, cfg.H, cfg.simOpts)
          : cfg.w0Fixed;
        const sum = summarizeStrategy(sm, w0, paths, cfg.simOpts);
        if (sm.id === 1) base1Med30 = Math.max(1, sum.t30.p50);
        results.push(sum);
      }
      for (const r of results) {
        r.chgSelf50 = r.s1 > 0 ? ((r.t30.p50 - r.s1) / r.s1) * 100 : 0;
        r.chgBase50 = ((r.t30.p50 - base1Med30) / base1Med30) * 100;
      }
      state.results = results;

      const focus = results.find(r => r.meta.id === cfg.focusId) || results[0];
      const base1 = results[0];
      document.getElementById("kW0").textContent = `${(focus.w0 * 100).toFixed(2)}% / ${fmtExactMoney(focus.s1)}`;
      document.getElementById("kW0Sub").textContent = isZh ? focus.meta.zh : focus.meta.en;
      document.getElementById("kMed30").textContent = fmtExactMoney(focus.t30.p50);
      document.getElementById("kMed30Sub").textContent = (isZh ? "对比策略1: " : "vs Base 1: ") + fmtPct(focus.chgBase50, 1, true);
      document.getElementById("kWlth").textContent = `${fmtCompactMoney(focus.tw.p50)} / ${fmtCompactMoney(focus.tw.p10)}`;
      document.getElementById("kWlthSub").textContent = `Yr ${cfg.H} · ${paths.length} ${isZh ? "条路径" : "paths"}`;
      document.getElementById("kDsv").textContent = `${focus.dsvMed.toFixed(2)}% / ${focus.dsv10.toFixed(2)}%`;
      document.getElementById("kDsvSub").textContent = isZh ? "中位 / 10分位(最差) DSV" : "Median / 10th-pct tail DSV";

      document.getElementById("matrixSub").textContent = state.calibMode === "pay"
        ? (isZh ? `PAY Rule: 年数 ${cfg.H} 时少于 ${fmtExactMoney(cfg.payY)} 概率 ≤ ${cfg.payX}%` : `PAY Rule: ≤${cfg.payX}% below ${fmtExactMoney(cfg.payY)} at Yr ${cfg.H}`)
        : (isZh ? `统一初始提取率 ${(cfg.w0Fixed * 100).toFixed(2)}% · 组合 ${eqP}/${100 - eqP}` : `Fixed w0 = ${(cfg.w0Fixed * 100).toFixed(2)}% · ${eqP}/${100 - eqP} allocation`);

      const fm = v => fmtCompactMoney(v);
      document.getElementById("matrixHead").innerHTML = isZh
        ? `<tr><th>策略法则</th><th>初始w0</th><th>第10年支出 (90/50/10)</th><th>第20年支出 (90/50/10)</th><th>第${cfg.H}年支出 (90/50/10)</th><th>期末资产 (90/50/10)</th><th>对比基准1</th><th>DSV (50/10)</th></tr>`
        : `<tr><th>Strategy Rule</th><th>w0 (%)</th><th>Yr 10 Spend (90/50/10)</th><th>Yr 20 Spend (90/50/10)</th><th>Yr ${cfg.H} Spend (90/50/10)</th><th>Yr ${cfg.H} Wealth (90/50/10)</th><th>vs Base 1</th><th>DSV (50/10)</th></tr>`;

      const expRows = [];
      document.getElementById("matrixBody").innerHTML = results.map(r => {
        const nm = isZh ? r.meta.zh : r.meta.en;
        const hl = r.meta.id === cfg.focusId ? " class=\"highlight-row\"" : "";
        expRows.push([
          nm, (r.w0 * 100).toFixed(2), Math.round(r.t10.p90), Math.round(r.t10.p50), Math.round(r.t10.p10),
          Math.round(r.t20.p90), Math.round(r.t20.p50), Math.round(r.t20.p10),
          Math.round(r.t30.p90), Math.round(r.t30.p50), Math.round(r.t30.p10),
          Math.round(r.tw.p90), Math.round(r.tw.p50), Math.round(r.tw.p10),
          r.chgBase50.toFixed(1), r.dsvMed.toFixed(2), r.dsv10.toFixed(2)
        ]);
        return `<tr data-sid="${r.meta.id}" style="cursor:pointer;"${hl}>` +
          `<td>${nm}</td>` +
          `<td>${(r.w0 * 100).toFixed(2)}%</td>` +
          `<td>${fm(r.t10.p90)}/<strong>${fm(r.t10.p50)}</strong>/${fm(r.t10.p10)}</td>` +
          `<td>${fm(r.t20.p90)}/<strong>${fm(r.t20.p50)}</strong>/${fm(r.t20.p10)}</td>` +
          `<td>${fm(r.t30.p90)}/<strong>${fm(r.t30.p50)}</strong>/${fm(r.t30.p10)}</td>` +
          `<td>${fm(r.tw.p90)}/<strong>${fm(r.tw.p50)}</strong>/${fm(r.tw.p10)}</td>` +
          `<td class="${r.chgBase50 >= 0 ? "pos" : "neg"}">${fmtPct(r.chgBase50, 1, true)}</td>` +
          `<td>${r.dsvMed.toFixed(2)}%/${r.dsv10.toFixed(2)}%</td>` +
        `</tr>`;
      }).join("");
      state.lastExport = expRows;

      document.querySelectorAll("#matrixBody tr").forEach(tr => {
        tr.addEventListener("click", () => {
          document.getElementById("focusStrat").value = tr.dataset.sid;
          updateAll();
        });
      });

      drawScatter(results, cfg);
      if (state.tab === "focus") drawFocusTab(focus, base1, cfg);
      if (state.tab === "hist") drawHistTab(cfg);
    }

    function drawScatter(results, cfg) {
      const canvas = document.getElementById("scatterCanvas");
      const sc = setupCanvas(canvas);
      if (!sc) return;
      const { ctx, w, h } = sc;
      const C = getThemeColors();
      const isZh = currentLang === "zh-CN";
      ctx.clearRect(0, 0, w, h);

      const xs = results.map(r => r.t30.p50);
      const ys = results.map(r => Math.abs(r.dsvMed));
      const minX = Math.min(...xs) * 0.85, maxX = Math.max(...xs) * 1.12;
      const maxY = Math.max(0.5, ...ys) * 1.20;
      const pad = { l: 58, r: 24, t: 18, b: 42 };
      const cw = w - pad.l - pad.r, ch = h - pad.t - pad.b;
      const mapX = x => pad.l + ((x - minX) / Math.max(1, maxX - minX)) * cw;
      const mapY = y => pad.t + ch - (y / maxY) * ch;

      ctx.strokeStyle = C.grid; ctx.lineWidth = 1; ctx.font = CANVAS_FONT;
      computeNiceLinearTicks(0, maxY, 4).forEach(v => {
        const y = mapY(v);
        ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(w - pad.r, y); ctx.stroke();
        ctx.fillStyle = C.muted; ctx.textAlign = "right";
        ctx.fillText("-" + v.toFixed(1) + "%", pad.l - 6, y + 4);
      });
      computeNiceLinearTicks(minX, maxX, 5).forEach(v => {
        const x = mapX(v);
        ctx.fillStyle = C.muted; ctx.textAlign = "center";
        ctx.fillText(fmtCompactMoney(v), x, h - 18);
      });

      ctx.fillStyle = C.muted; ctx.font = CANVAS_LABEL_FONT; ctx.textAlign = "center";
      ctx.fillText(isZh ? `第${cfg.H}年实际支出中位数 → (越高越好)` : `Median Yr-${cfg.H} Real Spending → (higher better)`, pad.l + cw * 0.5, h - 3);
      ctx.save(); ctx.translate(13, pad.t + ch * 0.5); ctx.rotate(-Math.PI / 2);
      ctx.fillText(isZh ? "平均下行支出跌幅 |DSV| (越低越稳)" : "Median Downside |DSV| % (lower steadier)", 0, 0);
      ctx.restore();

      const pts = [];
      for (const r of results) {
        const px = mapX(r.t30.p50), py = mapY(Math.abs(r.dsvMed));
        const isF = r.meta.id === cfg.focusId;
        pts.push({ px, py, r });
        ctx.beginPath();
        ctx.arc(px, py, isF ? 8 : 6, 0, Math.PI * 2);
        ctx.fillStyle = isF ? C.port : C.accent;
        ctx.fill();
        ctx.strokeStyle = C.panel; ctx.lineWidth = 1.5; ctx.stroke();
        ctx.fillStyle = isF ? C.text : C.textSoft;
        ctx.font = CANVAS_LABEL_FONT; ctx.textAlign = "left";
        const lblY = Math.abs(r.dsvMed) < 0.3 ? py - 7 : py + 4;
        ctx.fillText(String(r.meta.id), px + 9, lblY);
      }
      state.scatterPts = pts;
    }

    function drawFocusTab(focus, base1, cfg) {
      const isZh = currentLang === "zh-CN";
      document.getElementById("ttlFanSpend").textContent = (isZh ? focus.meta.zh : focus.meta.en) + (isZh ? "：实际支出分位数 (10 / 50 / 90)" : ": Real Spending Fan (10th / 50th / 90th)");
      const H = cfg.H;

      const drawFan = (canvasId, fanArr, baseArr, isSpend) => {
        const canvas = document.getElementById(canvasId);
        const sc = setupCanvas(canvas);
        if (!sc) return;
        const { ctx, w, h } = sc;
        const C = getThemeColors();
        ctx.clearRect(0, 0, w, h);
        let maxV = 10;
        fanArr.forEach(d => { if (d.p90 > maxV) maxV = d.p90; });
        baseArr.forEach(d => { if (d.p50 > maxV) maxV = d.p50; });
        maxV *= 1.08;
        const pad = { l: 56, r: 16, t: 18, b: 28 }, cw = w - pad.l - pad.r, ch = h - pad.t - pad.b;
        const mapX = i => pad.l + (i / Math.max(1, fanArr.length - 1)) * cw;
        const mapY = v => pad.t + ch - (v / maxV) * ch;

        ctx.strokeStyle = C.grid; ctx.lineWidth = 1; ctx.font = CANVAS_FONT; ctx.textAlign = "right";
        computeNiceLinearTicks(0, maxV, 4).forEach(v => {
          const y = mapY(v);
          ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(w - pad.r, y); ctx.stroke();
          ctx.fillStyle = C.muted; ctx.fillText(fmtCompactMoney(v), pad.l - 5, y + 4);
        });
        ctx.beginPath();
        fanArr.forEach((d, i) => { const x = mapX(i), y = mapY(d.p90); if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); });
        for (let i = fanArr.length - 1; i >= 0; i--) ctx.lineTo(mapX(i), mapY(fanArr[i].p10));
        ctx.closePath();
        ctx.fillStyle = C.mcOuterBand; ctx.fill();

        ctx.beginPath(); ctx.setLineDash([4, 4]); ctx.strokeStyle = C.muted; ctx.lineWidth = 1.6;
        baseArr.forEach((d, i) => { const x = mapX(i), y = mapY(d.p50); if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); });
        ctx.stroke(); ctx.setLineDash([]);

        ctx.beginPath(); ctx.strokeStyle = isSpend ? C.port : C.success; ctx.lineWidth = 2.6;
        fanArr.forEach((d, i) => { const x = mapX(i), y = mapY(d.p50); if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); });
        ctx.stroke();

        ctx.fillStyle = C.muted; ctx.textAlign = "center";
        [0, 10, 20, H - (isSpend ? 1 : 0)].filter((v, idx, a) => v >= 0 && v < fanArr.length && a.indexOf(v) === idx).forEach(i => {
          ctx.fillText("Yr " + (isSpend ? i + 1 : i), mapX(i), h - 8);
        });
      };

      drawFan("spendFanCanvas", focus.fanS, base1.fanS, true);
      drawFan("wealthFanCanvas", focus.fanW, base1.fanW, false);
      state.fanData = { focus, base1 };

      // Zolt 45-Yr Glidepath
      const zRes = computeZoltGlidePath(cfg.V0, focus.w0, cfg.simOpts.zoltH, 0.03);
      let pkVal = 0, pkYr = 0;
      zRes.path.forEach((v, idx) => { if (v > pkVal) { pkVal = v; pkYr = idx; } });
      document.getElementById("zoltSub").textContent = isZh
        ? `所需名义回报率 rReq = ${(zRes.rReq * 100).toFixed(2)}% · 第${pkYr}年名义峰值 ${fmtExactMoney(pkVal)}`
        : `Required Nominal Return rReq = ${(zRes.rReq * 100).toFixed(2)}% · Peak ${fmtExactMoney(pkVal)} in Yr ${pkYr}`;
      state.zoltData = zRes;

      const zCanvas = document.getElementById("zoltCanvas");
      const zsc = setupCanvas(zCanvas);
      if (zsc) {
        const { ctx, w, h } = zsc;
        const C = getThemeColors();
        ctx.clearRect(0, 0, w, h);
        const maxV = Math.max(cfg.V0 * 1.1, pkVal) * 1.08;
        const pad = { l: 58, r: 18, t: 18, b: 28 }, cw = w - pad.l - pad.r, ch = h - pad.t - pad.b;
        const mapX = i => pad.l + (i / (zRes.path.length - 1)) * cw;
        const mapY = v => pad.t + ch - (v / maxV) * ch;
        ctx.strokeStyle = C.grid; ctx.lineWidth = 1; ctx.font = CANVAS_FONT; ctx.textAlign = "right";
        computeNiceLinearTicks(0, maxV, 4).forEach(v => {
          const y = mapY(v);
          ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(w - pad.r, y); ctx.stroke();
          ctx.fillStyle = C.muted; ctx.fillText(fmtCompactMoney(v), pad.l - 5, y + 4);
        });
        ctx.beginPath(); ctx.strokeStyle = C.accent; ctx.lineWidth = 2.6;
        zRes.path.forEach((v, i) => { const x = mapX(i), y = mapY(v); if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); });
        ctx.stroke();
        ctx.beginPath(); ctx.arc(mapX(pkYr), mapY(pkVal), 5, 0, Math.PI * 2); ctx.fillStyle = C.port; ctx.fill();
        ctx.fillStyle = C.text; ctx.textAlign = "center"; ctx.font = CANVAS_LABEL_FONT;
        ctx.fillText(`Yr ${pkYr}: ${fmtExactMoney(pkVal)}`, mapX(pkYr), Math.max(pad.t + 12, mapY(pkVal) - 10));
        ctx.fillStyle = C.muted; ctx.font = CANVAS_FONT;
        [0, 15, 30, zRes.path.length - 1].forEach(i => ctx.fillText("Yr " + i, mapX(i), h - 8));
      }
    }

    function drawHistTab(cfg) {
      const startYr = parseInt(document.getElementById("cohortYearSel").value, 10) || 1966;
      const idx = NYU.findIndex(r => r.Year === startYr);
      if (idx < 0) return;
      const availH = Math.min(cfg.H, NYU.length - idx);
      const eq = nyuEq.slice(idx, idx + availH), bd = nyuBd.slice(idx, idx + availH), inf = nyuInf.slice(idx, idx + availH);
      const ids = Array.from(new Set([1, 2, 5, 8, 10, cfg.focusId]));
      const C = getThemeColors();
      const colMap = { 1: C.muted, 2: C.inflation, 3: C.bond, 4: C.bond, 5: C.equity, 6: C.accent, 7: C.success, 8: C.port, 9: C.accent, 10: C.danger };
      const sims = ids.map(id => ({
        meta: STRAT_META.find(m => m.id === id),
        res: simulateCh6Strategy(id, cfg.w0Fixed, eq, bd, inf, { ...cfg.simOpts, horizon: availH }),
        col: colMap[id] || C.accent
      }));
      state.histData = { startYr, availH, sims };

      const drawLines = (canvasId, key) => {
        const sc = setupCanvas(document.getElementById(canvasId));
        if (!sc) return;
        const { ctx, w, h } = sc; ctx.clearRect(0, 0, w, h);
        let maxV = 10;
        sims.forEach(s => s.res[key].forEach(v => { if (v > maxV) maxV = v; }));
        maxV *= 1.08;
        const len = sims[0].res[key].length;
        const pad = { l: 56, r: 16, t: 18, b: 28 }, cw = w - pad.l - pad.r, ch = h - pad.t - pad.b;
        const mapX = i => pad.l + (i / Math.max(1, len - 1)) * cw;
        const mapY = v => pad.t + ch - (v / maxV) * ch;
        ctx.strokeStyle = C.grid; ctx.lineWidth = 1; ctx.font = CANVAS_FONT; ctx.textAlign = "right";
        computeNiceLinearTicks(0, maxV, 4).forEach(v => {
          const y = mapY(v); ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(w - pad.r, y); ctx.stroke();
          ctx.fillStyle = C.muted; ctx.fillText(fmtCompactMoney(v), pad.l - 5, y + 4);
        });
        sims.forEach(s => {
          ctx.beginPath(); ctx.strokeStyle = s.col; ctx.lineWidth = s.meta.id === cfg.focusId ? 2.6 : 1.8;
          s.res[key].forEach((v, i) => { const x = mapX(i), y = mapY(v); if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); });
          ctx.stroke();
        });
        ctx.fillStyle = C.muted; ctx.textAlign = "center";
        [0, 9, 19, len - 1].filter((v, idx, a) => v >= 0 && v < len && a.indexOf(v) === idx).forEach(i => {
          ctx.fillText(String(startYr + i), mapX(i), h - 8);
        });
      };
      drawLines("histSpendCanvas", "spendReal");
      drawLines("histWealthCanvas", "wealthReal");

      const isZh = currentLang === "zh-CN";
      document.getElementById("histHead").innerHTML = `<tr><th>${isZh ? "年份" : "Year"}</th>` +
        sims.map(s => `<th>${isZh ? s.meta.zh : s.meta.en} ($)</th>`).join("") + `</tr>`;
      const rows = [];
      for (let t = 0; t < availH; t++) {
        rows.push(`<tr><td>${startYr + t} (Yr ${t + 1})</td>` +
          sims.map(s => `<td>${fmtExactMoney(s.res.spendReal[t])}</td>`).join("") + `</tr>`);
      }
      document.getElementById("histBody").innerHTML = rows.join("");
    }

    attachCanvasHover(document.getElementById("scatterCanvas"), document.getElementById("scatterTip"), (e, canvas, tip) => {
      if (!e || !state.scatterPts.length) return;
      const rect = canvas.getBoundingClientRect();
      const mx = e.clientX - rect.left, my = e.clientY - rect.top;
      let best = null, bd = 9999;
      for (const p of state.scatterPts) {
        const d = Math.hypot(p.px - mx, p.py - my);
        if (d < bd) { bd = d; best = p; }
      }
      if (!best || bd > 28) { tip.style.display = "none"; return; }
      const r = best.r, isZh = currentLang === "zh-CN";
      tip.innerHTML = `<strong>${isZh ? r.meta.zh : r.meta.en}</strong>` +
        `<div class="tip-row"><span>w0</span><span>${(r.w0 * 100).toFixed(2)}%</span></div>` +
        `<div class="tip-row"><span>${isZh ? "期末支出中位" : "Med End Spend"}</span><span>${fmtExactMoney(r.t30.p50)}</span></div>` +
        `<div class="tip-row"><span>${isZh ? "期末资产中位" : "Med End Wealth"}</span><span>${fmtCompactMoney(r.tw.p50)}</span></div>` +
        `<div class="tip-row"><span>DSV (50/10)</span><span>${r.dsvMed.toFixed(2)}% / ${r.dsv10.toFixed(2)}%</span></div>`;
      placeTooltip(tip, canvas, e.clientX, e.clientY);
    });

    attachCanvasHover(document.getElementById("spendFanCanvas"), document.getElementById("spendFanTip"), (e, canvas, tip) => {
      if (!e || !state.fanData) return;
      const rect = canvas.getBoundingClientRect(), fan = state.fanData.focus.fanS;
      const padL = 56, padR = 16, cw = rect.width - padL - padR;
      const idx = Math.max(0, Math.min(fan.length - 1, Math.round(((e.clientX - rect.left - padL) / Math.max(1, cw)) * (fan.length - 1))));
      const d = fan[idx];
      tip.innerHTML = `<strong>Yr ${idx + 1}</strong>` +
        `<div class="tip-row"><span>90th</span><span>${fmtExactMoney(d.p90)}</span></div>` +
        `<div class="tip-row"><span>50th</span><span>${fmtExactMoney(d.p50)}</span></div>` +
        `<div class="tip-row"><span>10th</span><span>${fmtExactMoney(d.p10)}</span></div>`;
      placeTooltip(tip, canvas, e.clientX, e.clientY);
    });

    attachCanvasHover(document.getElementById("wealthFanCanvas"), document.getElementById("wealthFanTip"), (e, canvas, tip) => {
      if (!e || !state.fanData) return;
      const rect = canvas.getBoundingClientRect(), fan = state.fanData.focus.fanW;
      const padL = 56, padR = 16, cw = rect.width - padL - padR;
      const idx = Math.max(0, Math.min(fan.length - 1, Math.round(((e.clientX - rect.left - padL) / Math.max(1, cw)) * (fan.length - 1))));
      const d = fan[idx];
      tip.innerHTML = `<strong>Yr ${idx}</strong>` +
        `<div class="tip-row"><span>90th</span><span>${fmtCompactMoney(d.p90)}</span></div>` +
        `<div class="tip-row"><span>50th</span><span>${fmtCompactMoney(d.p50)}</span></div>` +
        `<div class="tip-row"><span>10th</span><span>${fmtCompactMoney(d.p10)}</span></div>`;
      placeTooltip(tip, canvas, e.clientX, e.clientY);
    });

    attachCanvasHover(document.getElementById("zoltCanvas"), document.getElementById("zoltTip"), (e, canvas, tip) => {
      if (!e || !state.zoltData) return;
      const rect = canvas.getBoundingClientRect(), arr = state.zoltData.path;
      const padL = 58, padR = 18, cw = rect.width - padL - padR;
      const idx = Math.max(0, Math.min(arr.length - 1, Math.round(((e.clientX - rect.left - padL) / Math.max(1, cw)) * (arr.length - 1))));
      tip.innerHTML = `<strong>Yr ${idx}</strong><div class="tip-row"><span>Target</span><span>${fmtExactMoney(arr[idx])}</span></div>`;
      placeTooltip(tip, canvas, e.clientX, e.clientY);
    });

    function setSegVal(ctlId, val) {
      document.querySelectorAll(`#${ctlId} button`).forEach(b => b.classList.toggle("active", b.dataset.val === String(val)));
    }

    function applyPreset(name) {
      document.querySelectorAll(".preset-btn").forEach(b => b.classList.toggle("active", b.dataset.preset === name));
      document.getElementById("engineMode").value = "ch3a";
      document.getElementById("initPortfolio").value = "100,000";
      document.getElementById("horizonYrs").value = "30";
      if (name === "fixed4") {
        state.calibMode = "fixed"; setSegVal("calibModeCtl", "fixed");
        document.getElementById("eqSlider").value = "50";
        document.getElementById("initWrPct").value = "4.0";
      } else if (name === "cons") {
        state.calibMode = "pay"; setSegVal("calibModeCtl", "pay");
        document.getElementById("eqSlider").value = "25";
        document.getElementById("payXpct").value = "5";
        document.getElementById("payYamt").value = "20,000";
      } else if (name === "mod") {
        state.calibMode = "pay"; setSegVal("calibModeCtl", "pay");
        document.getElementById("eqSlider").value = "50";
        document.getElementById("payXpct").value = "10";
        document.getElementById("payYamt").value = "15,000";
      } else if (name === "aggr") {
        state.calibMode = "pay"; setSegVal("calibModeCtl", "pay");
        document.getElementById("eqSlider").value = "75";
        document.getElementById("payXpct").value = "20";
        document.getElementById("payYamt").value = "10,000";
      }
      updateAll();
    }

    function onThemeOrLangChange() { updateAll(); }

    document.querySelectorAll(".tab-btn").forEach(b => {
      b.addEventListener("click", () => {
        state.tab = b.dataset.tab;
        document.querySelectorAll(".tab-btn").forEach(x => { x.classList.toggle("active", x === b); x.setAttribute("aria-selected", x === b ? "true" : "false"); });
        const map = { matrix: "paneMatrix", focus: "paneFocus", hist: "paneHist" };
        Object.entries(map).forEach(([k, id]) => document.getElementById(id).style.display = k === state.tab ? "block" : "none");
        updateAll();
      });
    });
    document.querySelectorAll("#mcPathsCtl button").forEach(b => b.addEventListener("click", () => {
      state.mcPaths = parseInt(b.dataset.val, 10); setSegVal("mcPathsCtl", state.mcPaths); updateAll();
    }));
    document.querySelectorAll("#calibModeCtl button").forEach(b => b.addEventListener("click", () => {
      state.calibMode = b.dataset.val; setSegVal("calibModeCtl", state.calibMode); updateAll();
    }));
    document.querySelectorAll(".preset-btn").forEach(b => b.addEventListener("click", () => applyPreset(b.dataset.preset)));
    document.getElementById("btnReset").addEventListener("click", () => applyPreset("fixed4"));
    document.getElementById("btnExportCsv").addEventListener("click", () => {
      downloadCsv("pfau_ch6_variable_spending.csv", [
        "Strategy", "w0_pct", "Yr10_90", "Yr10_50", "Yr10_10", "Yr20_90", "Yr20_50", "Yr20_10",
        "YrEnd_90", "YrEnd_50", "YrEnd_10", "WealthEnd_90", "WealthEnd_50", "WealthEnd_10", "Chg_vs_Base1_pct", "DSV_50_pct", "DSV_10_pct"
      ], state.lastExport);
    });
    ["engineMode", "eqSlider", "initPortfolio", "horizonYrs", "initWrPct", "payXpct", "payYamt", "focusStrat", "gkGuardPct", "hybridAlphaPct", "zoltHor", "rmdMode", "vgNominalSwitch", "cohortYearSel"].forEach(id => {
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
        slug="variable-spending",
        title_en="Variable Spending & PAY Rule™ Lab",
        extra_css="#paneMatrix table { font-size: 11.5px; } #paneMatrix th, #paneMatrix td { padding: 6px 6px; }",
        body_html=body_html,
        embedded_data_js=embedded,
        page_i18n=page_i18n,
        page_js=page_js,
    )


if __name__ == "__main__":
    build_ch6()
