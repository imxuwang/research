#!/usr/bin/env python3
"""Build Lab 5 (Chapter 5 Part II): Spending Smiles, Age-Banding, Wealth Preservation, Horizon vs. RMD, and Bond Tent Glidepaths."""

from shared_shell import dump_json_inline, load_csv_records, render_page
from shared_sim_js import SHARED_SIM_JS


def build_ch5b():
    nyu = load_csv_records("nyu_stern_1928_2025_full.csv")
    shiller = load_csv_records("shiller_us_1871_2025_annual.csv")
    mort = load_csv_records("mortality_and_rmd_tables.csv")

    body_html = """  <main class="layout">
    <aside class="sidebar" aria-label="Simulation parameters" data-i18n-aria-label="aria_sidebar">
      <div class="side-section">
        <div class="sec-head-static">
          <h2 class="sec-title" data-i18n="sec_presets">Book Exhibit Presets</h2>
          <button type="button" class="link-btn" id="btnReset" data-i18n="btn_reset">Reset</button>
        </div>
        <div class="preset-grid">
          <button type="button" class="preset-btn active" data-preset="smile">
            <span class="p-title" data-i18n="pre_sm_t">Ex. 5.18–5.20 · Smile</span>
            <span class="p-meta" data-i18n="pre_sm_m">Blanchett $100k (-25.9%)</span>
          </button>
          <button type="button" class="preset-btn" data-preset="basu">
            <span class="p-title" data-i18n="pre_ba_t">Ex. 5.21 · Age Banding</span>
            <span class="p-meta" data-i18n="pre_ba_m">7% health care inflation</span>
          </button>
          <button type="button" class="preset-btn" data-preset="preserve">
            <span class="p-title" data-i18n="pre_pr_t">Ex. 5.14, 5.23 · Legacy/RMD</span>
            <span class="p-meta" data-i18n="pre_pr_m">100% Real vs. Depletion</span>
          </button>
          <button type="button" class="preset-btn" data-preset="tent">
            <span class="p-title" data-i18n="pre_tn_t">Ex. 5.29 · Bond Tent</span>
            <span class="p-meta" data-i18n="pre_tn_m">Rising 30% → 70% Stocks</span>
          </button>
        </div>
      </div>

      <div class="side-section">
        <div class="sec-head-static"><h2 class="sec-title" data-i18n="sec_spend">Age-Spending Pattern</h2></div>
        <div class="control-group">
          <label for="spendModel"><span data-i18n="lbl_spend_model">Real spending path</span></label>
          <select id="spendModel">
            <option value="smile" selected data-i18n="sm_blanchett">Blanchett HRS Spending Smile</option>
            <option value="basu" data-i18n="sm_basu">Basu 4-Category Age Banding</option>
            <option value="constant" data-i18n="sm_const">Constant Real (0% real change)</option>
            <option value="decline1" data-i18n="sm_dec1">Gradual Decline (-0.7%/yr real)</option>
          </select>
        </div>
        <div class="control-group row-2">
          <div>
            <label for="initBudget"><span data-i18n="lbl_budget">Age-65 budget ($)</span></label>
            <div class="currency-field"><span class="currency-prefix">$</span><input type="text" id="initBudget" value="100,000" inputmode="numeric" /></div>
          </div>
          <div>
            <label for="horizonYrs"><span data-i18n="lbl_horizon">Horizon (yrs)</span></label>
            <input type="number" id="horizonYrs" value="30" min="10" max="50" step="5" />
          </div>
        </div>
        <div class="control-group row-2">
          <div>
            <label for="hcInfPct"><span data-i18n="lbl_hc_inf">Health-care infl. (%)</span></label>
            <input type="number" id="hcInfPct" value="7.0" min="2" max="12" step="0.5" />
          </div>
          <div>
            <label for="cpiBasePct"><span data-i18n="lbl_cpi_base">General CPI (%)</span></label>
            <input type="number" id="cpiBasePct" value="3.0" min="1" max="8" step="0.5" />
          </div>
        </div>
      </div>

      <div class="side-section">
        <div class="sec-head-static"><h2 class="sec-title" data-i18n="sec_glide">Legacy, Mortality &amp; Glidepath</h2></div>
        <div class="control-group row-2">
          <div>
            <label for="preserveMode"><span data-i18n="lbl_preserve">Terminal objective</span></label>
            <select id="preserveMode">
              <option value="deplete" selected data-i18n="opt_dep">Deplete (0%)</option>
              <option value="nominal" data-i18n="opt_nom">100% Nominal</option>
              <option value="real" data-i18n="opt_real">100% Real</option>
            </select>
          </div>
          <div>
            <label for="hhMortality"><span data-i18n="lbl_mort">Competing Mortality</span></label>
            <select id="hhMortality">
              <option value="couple" selected data-i18n="hh_cpl">Couple (SOA 2017)</option>
              <option value="female" data-i18n="hh_fem">Female (SOA 2017)</option>
              <option value="male" data-i18n="hh_mal">Male (SOA 2017)</option>
            </select>
          </div>
        </div>
        <div class="control-group row-2">
          <div>
            <label for="gpStartEq"><span data-i18n="lbl_gp_start">Start Equity (%)</span></label>
            <input type="number" id="gpStartEq" value="30" min="0" max="100" step="10" />
          </div>
          <div>
            <label for="gpEndEq"><span data-i18n="lbl_gp_end">End Equity (%)</span></label>
            <input type="number" id="gpEndEq" value="70" min="0" max="100" step="10" />
          </div>
        </div>
        <div class="control-group row-2">
          <div>
            <label for="tentWrPct"><span data-i18n="lbl_tent_wr">Glidepath Test WR (%)</span></label>
            <input type="number" id="tentWrPct" value="4.0" min="2.5" max="7.0" step="0.25" />
          </div>
          <div>
            <label for="tentMcMode"><span data-i18n="lbl_tent_mc">MC Regime</span></label>
            <select id="tentMcMode">
              <option value="ch3a" selected data-i18n="mc_ch3a">Low-Yield AR(1)</option>
              <option value="boot" data-i18n="mc_boot">NYU Bootstrap</option>
            </select>
          </div>
        </div>
      </div>
    </aside>

    <section class="workspace" aria-label="Simulation outputs" data-i18n-aria-label="aria_workspace">
      <div class="results-shell">
        <div class="tabs-bar">
          <div class="tab-strip" role="tablist">
            <button type="button" class="tab-btn active" role="tab" aria-selected="true" data-tab="smile" data-i18n="tab_smile">Spending Smile &amp; Age-Banding (Ex. 5.18–5.21)</button>
            <button type="button" class="tab-btn" role="tab" aria-selected="false" data-tab="legacy" data-i18n="tab_legacy">Legacy, Horizons &amp; Mortality (Ex. 5.14, 5.22–5.25)</button>
            <button type="button" class="tab-btn" role="tab" aria-selected="false" data-tab="tent" data-i18n="tab_tent">Rising Equity Glidepath Heatmap (Ex. 5.29)</button>
          </div>
        </div>

        <div class="results-body">
          <div id="paneSmile" class="tab-pane">
            <div class="kpis kpis-4 kpis-flush-top">
              <div class="kpi"><div class="kpi-label" data-i18n="ks_trough">Smile Trough Real Spend</div><div class="kpi-val" id="ksTrough">—</div><div class="kpi-sub" id="ksTroughSub">—</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="ks_const_safe">Constant-Real SAFEMAX</div><div class="kpi-val" id="ksConstSafe">—</div><div class="kpi-sub">50/50 · NYU 1928–2025</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="ks_mod_safe">Selected Pattern SAFEMAX</div><div class="kpi-val pos" id="ksModSafe">—</div><div class="kpi-sub" id="ksModGain">—</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="ks_sav_cut">Implied Required Nest-Egg Cut</div><div class="kpi-val pos" id="ksSavCut">—</div><div class="kpi-sub" data-i18n="ks_sav_sub">vs. constant inflation-adjusted</div></div>
            </div>
            <div class="split-grid">
              <div class="grid-cell">
                <div class="legend">
                  <strong data-i18n="ttl_ex518">Ex. 5.18 &amp; 5.21: Real Spending Trajectory by Age</strong>
                  <div class="legend-items">
                    <div class="legend-item"><span class="swatch" style="background:var(--port);"></span><span data-i18n="leg_smile">Blanchett Smile</span></div>
                    <div class="legend-item"><span class="swatch" style="background:var(--inflation);"></span><span data-i18n="leg_basu">Basu Age-Banding</span></div>
                    <div class="legend-item"><span class="swatch" style="background:var(--muted);"></span><span data-i18n="leg_const">Constant Real</span></div>
                  </div>
                </div>
                <div class="chart-wrap"><canvas id="smileCanvas" height="255"></canvas><div class="tooltip" id="smileTip"></div></div>
              </div>
              <div class="grid-cell">
                <div class="legend"><strong data-i18n="ttl_ex520">Ex. 5.20: Rolling Historical 30-Yr MWR (Pattern vs. Constant)</strong></div>
                <div class="chart-wrap"><canvas id="smileMwrCanvas" height="255"></canvas><div class="tooltip" id="smileMwrTip"></div></div>
              </div>
            </div>
            <div class="panel-block">
              <div class="card-title"><h3 class="sec-title" data-i18n="ttl_jpm">J.P. Morgan / Roy &amp; Carson (2015) Five Household Spending Profiles</h3></div>
              <div class="table-container" style="max-height:none;"><table><thead id="jpmHead"></thead><tbody id="jpmBody"></tbody></table></div>
            </div>
          </div>

          <div id="paneLegacy" class="tab-pane" style="display:none;">
            <div class="kpis kpis-4 kpis-flush-top">
              <div class="kpi"><div class="kpi-label" data-i18n="kl_dep">0% Depletion SAFEMAX</div><div class="kpi-val" id="klDep">—</div><div class="kpi-sub">50/50 · NYU SBBI</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="kl_nom">100% Nominal SAFEMAX</div><div class="kpi-val" id="klNom">—</div><div class="kpi-sub" id="klNomSub">—</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="kl_real">100% Real SAFEMAX</div><div class="kpi-val" id="klReal">—</div><div class="kpi-sub" id="klRealSub">—</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="kl_comp">Competing-Risks Lifetime Ruin</div><div class="kpi-val neg" id="klComp">—</div><div class="kpi-sub" id="klCompSub">—</div></div>
            </div>
            <div class="split-grid">
              <div class="grid-cell">
                <div class="legend"><strong data-i18n="ttl_ex522">Ex. 5.22–5.24: SAFEMAX by Horizon (100/50/0% Eq) vs. IRS RMD %</strong></div>
                <div class="chart-wrap"><canvas id="horCanvas" height="255"></canvas><div class="tooltip" id="horTip"></div></div>
              </div>
              <div class="grid-cell">
                <div class="legend"><strong data-i18n="ttl_comp">Fixed-Horizon Ruin vs. Mortality-Weighted Lifetime Ruin (MC)</strong></div>
                <div class="chart-wrap"><canvas id="compCanvas" height="255"></canvas><div class="tooltip" id="compTip"></div></div>
              </div>
            </div>
            <div class="panel-block">
              <div class="card-title"><h3 class="sec-title" data-i18n="ttl_ex514">Ex. 5.14–5.15: Cohort MWR &amp; Remaining Wealth under 4% WR</h3></div>
              <div class="table-container" style="max-height:260px;"><table><thead id="legHead"></thead><tbody id="legBody"></tbody></table></div>
            </div>
          </div>

          <div id="paneTent" class="tab-pane" style="display:none;">
            <div class="kpis kpis-4 kpis-flush-top">
              <div class="kpi"><div class="kpi-label" data-i18n="kt_static">Static Start-Eq MC Success</div><div class="kpi-val" id="ktStatic">—</div><div class="kpi-sub" id="ktStaticSub">—</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="kt_glide">Rising Glidepath MC Success</div><div class="kpi-val pos" id="ktGlide">—</div><div class="kpi-sub" id="ktGlideSub">—</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="kt_1966">1966 Stagflation Ending Bal</div><div class="kpi-val" id="kt1966">—</div><div class="kpi-sub" id="kt1966Sub">—</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="kt_best_pair">Best Heatmap Pair (Success %)</div><div class="kpi-val pos" id="ktBest">—</div><div class="kpi-sub" id="ktBestSub">—</div></div>
            </div>
            <div class="panel-block">
              <div class="card-title"><h3 class="sec-title" data-i18n="ttl_ex529">Ex. 5.29: Start Equity % × End Equity % Monte Carlo Success Rate (%)</h3><span class="subhead" id="tentSub"></span></div>
              <div class="table-container" style="max-height:none;"><table><thead id="tentHead"></thead><tbody id="tentBody"></tbody></table></div>
            </div>
            <div class="panel-block">
              <div class="legend"><strong data-i18n="ttl_tent_curve">Selected Glidepath Weight Schedule &amp; 1966 Real Wealth Comparison</strong></div>
              <div class="chart-wrap"><canvas id="tentCanvas" height="235"></canvas><div class="tooltip" id="tentTip"></div></div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </main>"""

    page_i18n = {
        "page_title": {"en-UK": "Spending Smiles & Bond Tents", "zh-CN": "支出微笑曲线与动态股债滑道"},
        "app_title": {"en-UK": "Spending Smiles & Bond Tents", "zh-CN": "支出微笑曲线与动态股债滑道"},
        "sec_presets": {"en-UK": "Book Exhibit Presets", "zh-CN": "全书图表预设"},
        "pre_sm_t": {"en-UK": "Ex. 5.18–5.20 · Smile", "zh-CN": "图5.18–5.20 · 微笑曲线"},
        "pre_sm_m": {"en-UK": "Blanchett $100k (-25.9%)", "zh-CN": "Blanchett 84岁低谷 -25.9%"},
        "pre_ba_t": {"en-UK": "Ex. 5.21 · Age Banding", "zh-CN": "图5.21 · 分年龄段通胀"},
        "pre_ba_m": {"en-UK": "7% health care inflation", "zh-CN": "医疗 7% 通胀模型"},
        "pre_pr_t": {"en-UK": "Ex. 5.14, 5.23 · Legacy/RMD", "zh-CN": "图5.14, 5.23 · 留存与RMD"},
        "pre_pr_m": {"en-UK": "100% Real vs. Depletion", "zh-CN": "100% 实际保值 vs 耗尽"},
        "pre_tn_t": {"en-UK": "Ex. 5.29 · Bond Tent", "zh-CN": "图5.29 · 债券帐篷滑道"},
        "pre_tn_m": {"en-UK": "Rising 30% → 70% Stocks", "zh-CN": "股票从 30% 升至 70%"},
        "sec_spend": {"en-UK": "Age-Spending Pattern", "zh-CN": "年龄支出曲线模型"},
        "lbl_spend_model": {"en-UK": "Real spending path", "zh-CN": "实际支出路径"},
        "sm_blanchett": {"en-UK": "Blanchett HRS Spending Smile", "zh-CN": "Blanchett 退休支出微笑曲线"},
        "sm_basu": {"en-UK": "Basu 4-Category Age Banding", "zh-CN": "Basu 四大类分年龄段模型"},
        "sm_const": {"en-UK": "Constant Real (0% real change)", "zh-CN": "恒定实际支出 (0% 实际变化)"},
        "sm_dec1": {"en-UK": "Gradual Decline (-0.7%/yr real)", "zh-CN": "温和递减 (-0.7%/年实际)"},
        "lbl_budget": {"en-UK": "Age-65 budget ($)", "zh-CN": "65岁初始预算 ($)"},
        "lbl_horizon": {"en-UK": "Horizon (yrs)", "zh-CN": "规划年限"},
        "lbl_hc_inf": {"en-UK": "Health-care infl. (%)", "zh-CN": "医疗通胀率 (%)"},
        "lbl_cpi_base": {"en-UK": "General CPI (%)", "zh-CN": "一般 CPI (%)"},
        "sec_glide": {"en-UK": "Legacy, Mortality & Glidepath", "zh-CN": "留存、死亡率与股债滑道"},
        "lbl_preserve": {"en-UK": "Terminal objective", "zh-CN": "期末目标"},
        "opt_dep": {"en-UK": "Deplete (0%)", "zh-CN": "允许耗尽 (0%)"},
        "opt_nom": {"en-UK": "100% Nominal", "zh-CN": "100% 名义保本"},
        "opt_real": {"en-UK": "100% Real", "zh-CN": "100% 实际购买力保值"},
        "lbl_mort": {"en-UK": "Competing Mortality", "zh-CN": "竞争性寿命风险表"},
        "hh_cpl": {"en-UK": "Couple (SOA 2017)", "zh-CN": "夫妻长寿者 (SOA 2017)"},
        "hh_fem": {"en-UK": "Female (SOA 2017)", "zh-CN": "女性 (SOA 2017)"},
        "hh_mal": {"en-UK": "Male (SOA 2017)", "zh-CN": "男性 (SOA 2017)"},
        "lbl_gp_start": {"en-UK": "Start Equity (%)", "zh-CN": "期初股票 (%)"},
        "lbl_gp_end": {"en-UK": "End Equity (%)", "zh-CN": "期末股票 (%)"},
        "lbl_tent_wr": {"en-UK": "Glidepath Test WR (%)", "zh-CN": "滑道测试提取率 (%)"},
        "lbl_tent_mc": {"en-UK": "MC Regime", "zh-CN": "蒙特卡洛环境"},
        "mc_ch3a": {"en-UK": "Low-Yield AR(1)", "zh-CN": "低利率 AR(1)"},
        "mc_boot": {"en-UK": "NYU Bootstrap", "zh-CN": "NYU 随机抽样"},
        "tab_smile": {"en-UK": "Spending Smile & Age-Banding (Ex. 5.18–5.21)", "zh-CN": "支出微笑曲线与年龄分段 (5.18–5.21)"},
        "tab_legacy": {"en-UK": "Legacy, Horizons & Mortality (Ex. 5.14, 5.22–5.25)", "zh-CN": "留存目标、年限与竞争寿命风险"},
        "tab_tent": {"en-UK": "Rising Equity Glidepath Heatmap (Ex. 5.29)", "zh-CN": "递增股票滑道热力图 (5.29)"},
        "ks_trough": {"en-UK": "Smile Trough Real Spend", "zh-CN": "微笑曲线最低实际支出"},
        "ks_const_safe": {"en-UK": "Constant-Real SAFEMAX", "zh-CN": "恒定支出 SAFEMAX"},
        "ks_mod_safe": {"en-UK": "Selected Pattern SAFEMAX", "zh-CN": "所选支出曲线 SAFEMAX"},
        "ks_sav_cut": {"en-UK": "Implied Required Nest-Egg Cut", "zh-CN": "对应所需本金可减少"},
        "ks_sav_sub": {"en-UK": "vs. constant inflation-adjusted", "zh-CN": "对比恒定通胀调整支出"},
        "ttl_ex518": {"en-UK": "Ex. 5.18 & 5.21: Real Spending Trajectory by Age", "zh-CN": "图 5.18 & 5.21：不同年龄实际支出曲线"},
        "leg_smile": {"en-UK": "Blanchett Smile", "zh-CN": "Blanchett 微笑曲线"},
        "leg_basu": {"en-UK": "Basu Age-Banding", "zh-CN": "Basu 年龄分段"},
        "leg_const": {"en-UK": "Constant Real", "zh-CN": "恒定实际支出"},
        "ttl_ex520": {"en-UK": "Ex. 5.20: Rolling Historical 30-Yr MWR (Pattern vs. Constant)", "zh-CN": "图 5.20：历史各起点可持续提取率对比"},
        "ttl_jpm": {"en-UK": "J.P. Morgan / Roy & Carson (2015) Five Household Spending Profiles", "zh-CN": "摩根大通 (2015) 五类退休家庭支出画像"},
        "kl_dep": {"en-UK": "0% Depletion SAFEMAX", "zh-CN": "允许耗尽 SAFEMAX"},
        "kl_nom": {"en-UK": "100% Nominal SAFEMAX", "zh-CN": "名义保本 SAFEMAX"},
        "kl_real": {"en-UK": "100% Real SAFEMAX", "zh-CN": "实际保值 SAFEMAX"},
        "kl_comp": {"en-UK": "Competing-Risks Lifetime Ruin", "zh-CN": "寿命竞争下终身破产率"},
        "ttl_ex522": {"en-UK": "Ex. 5.22–5.24: SAFEMAX by Horizon (100/50/0% Eq) vs. IRS RMD %", "zh-CN": "图 5.22–5.24：不同年限 SAFEMAX 对比 IRS RMD 比例"},
        "ttl_comp": {"en-UK": "Fixed-Horizon Ruin vs. Mortality-Weighted Lifetime Ruin (MC)", "zh-CN": "固定年限破产率 vs 含死亡概率的终身破产率"},
        "ttl_ex514": {"en-UK": "Ex. 5.14–5.15: Cohort MWR & Remaining Wealth under 4% WR", "zh-CN": "图 5.14–5.15：各起点最大提取率与 4% 法则期末余值"},
        "kt_static": {"en-UK": "Static Start-Eq MC Success", "zh-CN": "静态初始股比 MC 成功率"},
        "kt_glide": {"en-UK": "Rising Glidepath MC Success", "zh-CN": "动态滑道 MC 成功率"},
        "kt_1966": {"en-UK": "1966 Stagflation Ending Bal", "zh-CN": "1966 滞胀起点期末余额"},
        "kt_best_pair": {"en-UK": "Best Heatmap Pair (Success %)", "zh-CN": "热力图最优股比组合"},
        "ttl_ex529": {"en-UK": "Ex. 5.29: Start Equity % × End Equity % Monte Carlo Success Rate (%)", "zh-CN": "图 5.29：期初股票% × 期末股票% 蒙特卡洛成功率矩阵 (%)"},
        "ttl_tent_curve": {"en-UK": "Selected Glidepath Weight Schedule & 1966 Real Wealth Comparison", "zh-CN": "所选滑道股票权重变化与 1966 历史模拟对比"},
    }

    embedded = (
        f"    const NYU = {dump_json_inline(nyu)};\n"
        f"    const SHILLER = {dump_json_inline(shiller)};\n"
        f"    const MORT = {dump_json_inline(mort)};\n"
    )
    page_js = SHARED_SIM_JS + r"""
    const state = { tab: "smile", seed: 202605, lastExport: [] };
    const CH3A_CAL = calibrateCh3AEngine(SHILLER);

    function blanchettMultipliers(horizon, budget65) {
      const m = [1.0];
      let cur = 1.0;
      for (let t = 1; t < horizon; t++) {
        const age = 65 + t;
        const dAS = 0.00008 * age * age - 0.0125 * age - 0.0066 * Math.log(Math.max(10000, budget65)) + 0.546;
        cur *= (1 + dAS);
        m.push(cur);
      }
      return m;
    }

    function basuMultipliers(horizon, hcInf, cpiBase) {
      // Equal baseline mix at pre-retirement scaled to Age 65 = 1.0 (Taxes 0.50, Basic 0.70, Health 1.15, Leisure 1.50; Ex. 5.21)
      const cats = [
        { w: 0.15, pi: cpiBase, f65: 0.50, f75: 1.00, f85: 1.00 },
        { w: 0.50, pi: cpiBase, f65: 0.70, f75: 0.80, f85: 0.90 },
        { w: 0.15, pi: hcInf,   f65: 1.15, f75: 1.20, f85: 1.25 },
        { w: 0.20, pi: hcInf,   f65: 1.50, f75: 0.50, f85: 0.25 },
      ];
      const valAt = t => {
        const age = 65 + t;
        let tot = 0;
        cats.forEach(c => {
          let f = c.f65;
          if (age >= 75) f *= c.f75;
          if (age >= 85) f *= c.f85;
          tot += c.w * f * Math.pow((1 + c.pi) / (1 + cpiBase), t);
        });
        return tot;
      };
      const base65 = valAt(0);
      return Array.from({ length: horizon }, (_, t) => valAt(t) / base65);
    }

    function getMultipliers(model, horizon, budget65, hcInf, cpiBase) {
      if (model === "smile") return blanchettMultipliers(horizon, budget65);
      if (model === "basu") return basuMultipliers(horizon, hcInf, cpiBase);
      if (model === "decline1") return Array.from({ length: horizon }, (_, t) => Math.pow(0.993, t));
      return Array.from({ length: horizon }, () => 1.0);
    }

    function updateAll() {
      const model = document.getElementById("spendModel").value;
      const budget65 = Math.max(10000, parseMoney(document.getElementById("initBudget")));
      const H = Math.max(10, Math.min(50, parseInt(document.getElementById("horizonYrs").value, 10) || 30));
      const hcInf = (parseFloat(document.getElementById("hcInfPct").value) || 7.0) / 100;
      const cpiBase = (parseFloat(document.getElementById("cpiBasePct").value) || 3.0) / 100;
      const presMode = document.getElementById("preserveMode").value;
      const hhMort = document.getElementById("hhMortality").value;
      const gpStart = Math.max(0, Math.min(100, parseFloat(document.getElementById("gpStartEq").value) || 30)) / 100;
      const gpEnd = Math.max(0, Math.min(100, parseFloat(document.getElementById("gpEndEq").value) || 70)) / 100;
      const tentWr = (parseFloat(document.getElementById("tentWrPct").value) || 4.0) / 100;
      const isCh3a = document.getElementById("tentMcMode").value === "ch3a";

      const eqN = NYU.map(r => r.NYU_SP500_pct / 100);
      const bdN = NYU.map(r => r.NYU_US_10Y_TBond_pct / 100);
      const infN = NYU.map(r => r.NYU_US_CPI_Inflation_pct / 100);

      if (state.tab === "smile") {
        renderSmileTab(model, budget65, H, hcInf, cpiBase, eqN, bdN, infN);
      } else if (state.tab === "legacy") {
        renderLegacyTab(H, presMode, hhMort, tentWr, eqN, bdN, infN);
      } else {
        renderTentTab(H, gpStart, gpEnd, tentWr, isCh3a, eqN, bdN, infN);
      }
    }

    function renderSmileTab(model, budget65, H, hcInf, cpiBase, eqN, bdN, infN) {
      const mSmile = blanchettMultipliers(H, budget65);
      const mBasu = basuMultipliers(H, hcInf, cpiBase);
      const mConst = Array.from({ length: H }, () => 1.0);
      const mSel = getMultipliers(model, H, budget65, hcInf, cpiBase);

      let minIdx = 0;
      for (let i = 1; i < mSmile.length; i++) if (mSmile[i] < mSmile[minIdx]) minIdx = i;
      document.getElementById("ksTrough").textContent = fmtExactMoney(budget65 * mSmile[minIdx]);
      document.getElementById("ksTroughSub").textContent = `Age ${65 + minIdx} (${((mSmile[minIdx] - 1) * 100).toFixed(1)}%)`;

      const nC = NYU.length - H + 1;
      const yrs = [], cMwr = [], sMwr = [];
      for (let i = 0; i < nC; i++) {
        yrs.push(NYU[i].Year);
        cMwr.push(computeCohortMWR(eqN, bdN, infN, i, H, 0.50));
        sMwr.push(computeCohortMWR(eqN, bdN, infN, i, H, 0.50, { realSpendMultipliers: mSel }));
      }
      const safeC = Math.min(...cMwr), safeS = Math.min(...sMwr);
      document.getElementById("ksConstSafe").textContent = safeC.toFixed(2) + "%";
      document.getElementById("ksModSafe").textContent = safeS.toFixed(2) + "%";
      document.getElementById("ksModGain").textContent = `${safeS >= safeC ? "+" : ""}${(safeS - safeC).toFixed(2)} pp vs const`;
      document.getElementById("ksSavCut").textContent = `${((1 - safeC / Math.max(0.1, safeS)) * 100).toFixed(1)}%`;

      state.lastExport = yrs.map((y, i) => [y, cMwr[i].toFixed(2), sMwr[i].toFixed(2)]);

      const sc1 = setupCanvas(document.getElementById("smileCanvas"));
      if (sc1) {
        const { ctx, w, h } = sc1; const C = getThemeColors(); ctx.clearRect(0, 0, w, h);
        const pad = { l: 56, r: 16, t: 18, b: 28 }, cw = w - pad.l - pad.r, ch = h - pad.t - pad.b;
        const maxV = Math.max(1.2, ...mBasu, ...mSmile) * budget65 * 1.05;
        const mapX = i => pad.l + (i / (H - 1)) * cw;
        const mapY = m => pad.t + ch - ((m * budget65) / maxV) * ch;
        ctx.strokeStyle = C.grid; ctx.font = CANVAS_FONT; ctx.textAlign = "right"; ctx.fillStyle = C.muted;
        computeNiceLinearTicks(0, maxV, 4).forEach(v => { const y = mapY(v / budget65); ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(w - pad.r, y); ctx.stroke(); ctx.fillText(fmtCompactMoney(v), pad.l - 5, y + 4); });
        [[mConst, C.muted, 1.5], [mBasu, C.inflation, 2.1], [mSmile, C.port, 2.5]].forEach(([arr, col, lw]) => {
          ctx.beginPath(); ctx.strokeStyle = col; ctx.lineWidth = lw;
          arr.forEach((v, i) => { const x = mapX(i), y = mapY(v); if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); });
          ctx.stroke();
        });
        ctx.fillStyle = C.muted; ctx.textAlign = "center";
        for (let t = 0; t < H; t += 10) ctx.fillText("Age " + (65 + t), mapX(t), h - 8);
      }

      const sc2 = setupCanvas(document.getElementById("smileMwrCanvas"));
      if (sc2) {
        const { ctx, w, h } = sc2; const C = getThemeColors(); ctx.clearRect(0, 0, w, h);
        const pad = { l: 42, r: 16, t: 18, b: 28 }, cw = w - pad.l - pad.r, ch = h - pad.t - pad.b;
        const maxM = Math.max(11, ...sMwr, ...cMwr) * 1.05;
        const mapX = i => pad.l + (i / (yrs.length - 1)) * cw;
        const mapY = v => pad.t + ch - (v / maxM) * ch;
        ctx.strokeStyle = C.grid; ctx.font = CANVAS_FONT; ctx.textAlign = "right"; ctx.fillStyle = C.muted;
        computeNiceLinearTicks(0, maxM, 4).forEach(v => { const y = mapY(v); ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(w - pad.r, y); ctx.stroke(); ctx.fillText(v + "%", pad.l - 5, y + 4); });
        [[cMwr, C.muted, 1.7], [sMwr, C.success, 2.4]].forEach(([arr, col, lw]) => {
          ctx.beginPath(); ctx.strokeStyle = col; ctx.lineWidth = lw;
          arr.forEach((v, i) => { const x = mapX(i), y = mapY(v); if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); });
          ctx.stroke();
        });
        ctx.fillStyle = C.muted; ctx.textAlign = "center";
        yrs.forEach((y, i) => { if (y % 15 === 0) ctx.fillText(String(y), mapX(i), h - 8); });
      }

      const isZh = currentLang === "zh-CN";
      const jpm = [
        ["Foodies", "饮食型", "39%", "28% on food & beverage; mortgages paid off; spending declines with age", "支出最低，食品饮料占比28%，随年龄稳定下降，最适用微笑曲线"],
        ["Homebodies", "居家型", "29%", "High ongoing housing, taxes & maintenance outlays; tracks inflation", "住房税费与维护占比高，晚年仍需外包维修，随通胀同步"],
        ["Snowflakes", "杂项型", "24%", "Idiosyncratic / balanced categories without single dominant driver", "支出分布较均衡，无单一主导大项"],
        ["Globetrotters", "环球旅行型", "5% (13% of $1M+)", "Heavy travel outlays at age 75+; spending stays high with inflation", "高净值人群占比达13%，75岁后仍大量旅行，不宜套用递减曲线"],
        ["Health-Care Spenders", "医疗支出型", "4%", "28% of income on health care; real spending rises earlier than peers", "医疗占比达28%，实际支出更早迎来上拐点"],
      ];
      document.getElementById("jpmHead").innerHTML = `<tr><th>${isZh ? "家庭类型" : "Profile"}</th><th>${isZh ? "占比" : "Share"}</th><th>${isZh ? "支出特征与规划启示" : "Spending Behavior & Planning Implication"}</th></tr>`;
      document.getElementById("jpmBody").innerHTML = jpm.map(r => `<tr><td><strong>${isZh ? r[1] : r[0]}</strong></td><td>${r[2]}</td><td style="text-align:left;white-space:normal;font-family:var(--font);">${isZh ? r[4] : r[3]}</td></tr>`).join("");
    }

    function renderLegacyTab(H, presMode, hhMort, wr, eqN, bdN, infN) {
      const nC = NYU.length - H + 1;
      const rows = [];
      for (let i = 0; i < nC; i++) {
        const mDep = computeCohortMWR(eqN, bdN, infN, i, H, 0.50, { targetPreserveMode: "deplete" });
        const mNom = computeCohortMWR(eqN, bdN, infN, i, H, 0.50, { targetPreserveMode: "nominal", targetFrac: 1.0 });
        const mReal = computeCohortMWR(eqN, bdN, infN, i, H, 0.50, { targetPreserveMode: "real", targetFrac: 1.0 });
        let balNom = 100, cumInf = 1;
        for (let t = 0; t < H; t++) {
          const rp = 0.5 * eqN[i + t] + 0.5 * bdN[i + t];
          balNom = Math.max(0, balNom - wr * 100 * cumInf) * (1 + rp);
          cumInf *= (1 + infN[i + t]);
        }
        rows.push({ yr: NYU[i].Year, mDep, mNom, mReal, endNom: balNom, endReal: balNom / cumInf });
      }
      document.getElementById("klDep").textContent = Math.min(...rows.map(r => r.mDep)).toFixed(2) + "%";
      const minNom = Math.min(...rows.map(r => r.mNom)), minReal = Math.min(...rows.map(r => r.mReal));
      const fail4Real = rows.filter(r => r.mReal < 4.0).length;
      document.getElementById("klNom").textContent = minNom.toFixed(2) + "%";
      document.getElementById("klNomSub").textContent = `<4% in ${rows.filter(r => r.mNom < 4).length}/${rows.length} cohorts`;
      document.getElementById("klReal").textContent = minReal.toFixed(2) + "%";
      document.getElementById("klRealSub").textContent = `4% fails real in ${fail4Real}/${rows.length}`;

      // Horizon curve 5..40 vs IRS RMD
      const hGrid = [];
      const rmdByAge = {}; MORT.forEach(m => { if (m.IRS_RMD_Divisor_Pre2022) rmdByAge[m.Age] = m.IRS_RMD_Divisor_Pre2022; });
      for (let h = 5; h <= 40; h++) {
        const ncH = NYU.length - h + 1;
        const sf = wEq => { let mn = 999; for (let i = 0; i < ncH; i++) { const v = computeCohortMWR(eqN, bdN, infN, i, h, wEq); if (v < mn) mn = v; } return mn; };
        const ageMap = 100 - h;
        const rmdPct = rmdByAge[ageMap] ? (100 / rmdByAge[ageMap]) : null;
        hGrid.push({ h, s100: sf(1.0), s50: sf(0.5), s0: sf(0.0), rmdPct });
      }

      // Competing Risks MC (Market x SOA 2017 Death Age)
      const curve = buildSurvivalCurve(MORT, { table: "soa_2017", startAge: 65, household: hhMort });
      const rng = mulberry32(state.seed);
      const Nmc = 3000;
      const fixedRuin = new Array(50).fill(0), lifeRuin = new Array(50).fill(0);
      for (let r = 0; r < Nmc; r++) {
        // Sample age of death from curve.surv
        const u = rng();
        let deathT = 50;
        for (let k = 0; k < curve.surv.length - 1; k++) {
          if (curve.surv[k].p >= u && curve.surv[k + 1].p <= u) { deathT = k + 1; break; }
        }
        let bal = 1.0, depT = null;
        for (let t = 0; t < 50; t++) {
          const k = Math.floor(rng() * NYU.length);
          const rr = (1 + 0.5 * eqN[k] + 0.5 * bdN[k]) / (1 + infN[k]) - 1;
          bal = Math.max(0, bal - wr) * (1 + rr);
          if (bal <= 0 && depT === null) depT = t + 1;
          if (depT !== null && depT <= t + 1) {
            fixedRuin[t]++;
            if (depT <= deathT) lifeRuin[t]++;
          }
        }
      }
      document.getElementById("klComp").textContent = ((lifeRuin[29] / Nmc) * 100).toFixed(1) + "%";
      document.getElementById("klCompSub").textContent = `Fixed Yr-30 ruin: ${((fixedRuin[29] / Nmc) * 100).toFixed(1)}%`;

      const sc1 = setupCanvas(document.getElementById("horCanvas"));
      if (sc1) {
        const { ctx, w, h } = sc1; const C = getThemeColors(); ctx.clearRect(0, 0, w, h);
        const pad = { l: 42, r: 16, t: 18, b: 28 }, cw = w - pad.l - pad.r, ch = h - pad.t - pad.b;
        const mapX = i => pad.l + (i / (hGrid.length - 1)) * cw;
        const mapY = v => pad.t + ch - (Math.min(18, v) / 18) * ch;
        ctx.strokeStyle = C.grid; ctx.font = CANVAS_FONT; ctx.textAlign = "right"; ctx.fillStyle = C.muted;
        [0, 5, 10, 15].forEach(v => { const y = mapY(v); ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(w - pad.r, y); ctx.stroke(); ctx.fillText(v + "%", pad.l - 5, y + 4); });
        [["s100", C.equity, []], ["s50", C.port, []], ["s0", C.bond, []], ["rmdPct", C.danger, [4, 3]]].forEach(([k, col, dash]) => {
          ctx.beginPath(); ctx.strokeStyle = col; ctx.lineWidth = 2; ctx.setLineDash(dash);
          let st = false;
          hGrid.forEach((g, i) => { if (g[k] !== null) { const x = mapX(i), y = mapY(g[k]); if (!st) { ctx.moveTo(x, y); st = true; } else ctx.lineTo(x, y); } });
          ctx.stroke(); ctx.setLineDash([]);
        });
        ctx.fillStyle = C.muted; ctx.textAlign = "center";
        hGrid.forEach((g, i) => { if (g.h % 5 === 0) ctx.fillText(g.h + "y", mapX(i), h - 8); });
      }

      const sc2 = setupCanvas(document.getElementById("compCanvas"));
      if (sc2) {
        const { ctx, w, h } = sc2; const C = getThemeColors(); ctx.clearRect(0, 0, w, h);
        const pad = { l: 42, r: 16, t: 18, b: 28 }, cw = w - pad.l - pad.r, ch = h - pad.t - pad.b;
        const maxR = Math.max(20, (fixedRuin[49] / Nmc) * 100) * 1.1;
        const mapX = t => pad.l + (t / 49) * cw;
        const mapY = v => pad.t + ch - (v / maxR) * ch;
        ctx.strokeStyle = C.grid; ctx.font = CANVAS_FONT; ctx.textAlign = "right"; ctx.fillStyle = C.muted;
        computeNiceLinearTicks(0, maxR, 4).forEach(v => { const y = mapY(v); ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(w - pad.r, y); ctx.stroke(); ctx.fillText(v.toFixed(0) + "%", pad.l - 5, y + 4); });
        [[fixedRuin, C.muted], [lifeRuin, C.danger]].forEach(([arr, col]) => {
          ctx.beginPath(); ctx.strokeStyle = col; ctx.lineWidth = 2.3;
          arr.forEach((v, t) => { const x = mapX(t), y = mapY((v / Nmc) * 100); if (t === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); });
          ctx.stroke();
        });
        ctx.fillStyle = C.muted; ctx.textAlign = "center";
        [0, 14, 29, 44].forEach(t => ctx.fillText("Age " + (66 + t), mapX(t), h - 8));
      }

      const isZh = currentLang === "zh-CN";
      document.getElementById("legHead").innerHTML = `<tr><th>${isZh ? "年份" : "Year"}</th><th>0% Deplete</th><th>100% Nom</th><th>100% Real</th><th>${isZh ? "4%末名义" : "4% Nom End"}</th><th>${isZh ? "4%末实际" : "4% Real End"}</th></tr>`;
      document.getElementById("legBody").innerHTML = rows.map(r => `<tr>
        <td><strong>${r.yr}</strong></td><td>${r.mDep.toFixed(2)}%</td><td class="${r.mNom < 4 ? 'neg' : ''}">${r.mNom.toFixed(2)}%</td><td class="${r.mReal < 4 ? 'neg' : ''}">${r.mReal.toFixed(2)}%</td>
        <td>$${r.endNom.toFixed(1)}</td><td><strong>$${r.endReal.toFixed(1)}</strong></td>
      </tr>`).join("");
    }

    function renderTentTab(H, gpStart, gpEnd, wr, isCh3a, eqN, bdN, infN) {
      const N = 1500, rng = mulberry32(state.seed);
      const paths = [];
      for (let i = 0; i < N; i++) {
        if (isCh3a) paths.push(simulateCh3APath(CH3A_CAL, H, rng));
        else {
          const eq = new Float64Array(H), bd = new Float64Array(H), inf = new Float64Array(H);
          for (let t = 0; t < H; t++) { const k = Math.floor(rng() * NYU.length); eq[t] = eqN[k]; bd[t] = bdN[k]; inf[t] = infN[k]; }
          paths.push({ eq, bd, inf });
        }
      }
      const testSucc = (w0, w1) => {
        let ok = 0;
        for (let i = 0; i < N; i++) {
          let bal = 1.0;
          for (let t = 0; t < H; t++) {
            const wEq = w0 + (w1 - w0) * (t / Math.max(1, H - 1));
            const rr = (1 + wEq * paths[i].eq[t] + (1 - wEq) * paths[i].bd[t]) / (1 + paths[i].inf[t]) - 1;
            bal = Math.max(0, bal - wr) * (1 + rr);
            if (bal <= 0) break;
          }
          if (bal > 0) ok++;
        }
        return (ok / N) * 100;
      };
      const statSucc = testSucc(gpStart, gpStart);
      const glSucc = testSucc(gpStart, gpEnd);
      document.getElementById("ktStatic").textContent = statSucc.toFixed(1) + "%";
      document.getElementById("ktStaticSub").textContent = `Fixed ${Math.round(gpStart * 100)}% Eq`;
      document.getElementById("ktGlide").textContent = glSucc.toFixed(1) + "%";
      document.getElementById("ktGlideSub").textContent = `${Math.round(gpStart * 100)}% → ${Math.round(gpEnd * 100)}% Eq`;

      // 1966 stress run
      const idx66 = NYU.findIndex(r => r.Year === 1966);
      const sim66 = (w0, w1) => {
        const arr = [100]; let b = 100;
        for (let t = 0; t < Math.min(H, NYU.length - idx66); t++) {
          const wEq = w0 + (w1 - w0) * (t / Math.max(1, H - 1));
          const rr = (1 + wEq * eqN[idx66 + t] + (1 - wEq) * bdN[idx66 + t]) / (1 + infN[idx66 + t]) - 1;
          b = Math.max(0, b - wr * 100) * (1 + rr); arr.push(b);
        }
        return arr;
      };
      const p66Stat = sim66(gpStart, gpStart), p66Glide = sim66(gpStart, gpEnd);
      document.getElementById("kt1966").textContent = `$${p66Glide[p66Glide.length - 1].toFixed(1)} vs $${p66Stat[p66Stat.length - 1].toFixed(1)}`;
      document.getElementById("kt1966Sub").textContent = "Glidepath vs Static ($100 start)";

      const gridVals = [0, 20, 40, 60, 80, 100];
      let bestPair = { s: 0, e: 0, v: -1 };
      const isZh = currentLang === "zh-CN";
      document.getElementById("tentHead").innerHTML = `<tr><th>${isZh ? "期初股% \\ 期末股%" : "Start Eq \\ End Eq"}</th>${gridVals.map(e => `<th>${e}%</th>`).join("")}</tr>`;
      document.getElementById("tentBody").innerHTML = gridVals.map(s => {
        const tds = gridVals.map(e => {
          const v = testSucc(s / 100, e / 100);
          if (v > bestPair.v) bestPair = { s, e, v };
          const act = Math.abs(s - gpStart * 100) < 5 && Math.abs(e - gpEnd * 100) < 5;
          return `<td class="hm-cell${act ? " hm-active" : ""}">${v.toFixed(1)}%</td>`;
        }).join("");
        return `<tr><td><strong>${s}%</strong></td>${tds}</tr>`;
      }).join("");
      document.getElementById("ktBest").textContent = bestPair.v.toFixed(1) + "%";
      document.getElementById("ktBestSub").textContent = `${bestPair.s}% → ${bestPair.e}% Eq`;

      const sc = setupCanvas(document.getElementById("tentCanvas"));
      if (sc) {
        const { ctx, w, h } = sc; const C = getThemeColors(); ctx.clearRect(0, 0, w, h);
        const pad = { l: 44, r: 16, t: 18, b: 28 }, cw = w - pad.l - pad.r, ch = h - pad.t - pad.b;
        const maxV = Math.max(120, ...p66Glide, ...p66Stat) * 1.05;
        const mapX = t => pad.l + (t / (p66Glide.length - 1)) * cw;
        const mapY = v => pad.t + ch - (v / maxV) * ch;
        ctx.strokeStyle = C.grid; ctx.font = CANVAS_FONT; ctx.textAlign = "right"; ctx.fillStyle = C.muted;
        computeNiceLinearTicks(0, maxV, 4).forEach(v => { const y = mapY(v); ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(w - pad.r, y); ctx.stroke(); ctx.fillText("$" + v, pad.l - 5, y + 4); });
        [[p66Stat, C.muted], [p66Glide, C.success]].forEach(([arr, col]) => {
          ctx.beginPath(); ctx.strokeStyle = col; ctx.lineWidth = 2.4;
          arr.forEach((v, i) => { const x = mapX(i), y = mapY(v); if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y); });
          ctx.stroke();
        });
        ctx.fillStyle = C.muted; ctx.textAlign = "center";
        [0, 10, 20, 30].filter(t => t < p66Glide.length).forEach(t => ctx.fillText("Yr " + t, mapX(t), h - 8));
      }
    }

    function applyPreset(name) {
      document.querySelectorAll(".preset-btn").forEach(b => b.classList.toggle("active", b.dataset.preset === name));
      if (name === "smile") {
        document.getElementById("spendModel").value = "smile";
        document.querySelector('[data-tab="smile"]').click();
      } else if (name === "basu") {
        document.getElementById("spendModel").value = "basu";
        document.querySelector('[data-tab="smile"]').click();
      } else if (name === "preserve") {
        document.getElementById("preserveMode").value = "real";
        document.querySelector('[data-tab="legacy"]').click();
      } else if (name === "tent") {
        document.getElementById("gpStartEq").value = "30"; document.getElementById("gpEndEq").value = "70";
        document.querySelector('[data-tab="tent"]').click();
      }
      updateAll();
    }

    function onThemeOrLangChange() { updateAll(); }

    document.querySelectorAll(".tab-btn").forEach(b => {
      b.addEventListener("click", () => {
        state.tab = b.dataset.tab;
        document.querySelectorAll(".tab-btn").forEach(x => { x.classList.toggle("active", x === b); x.setAttribute("aria-selected", x === b ? "true" : "false"); });
        const map = { smile: "paneSmile", legacy: "paneLegacy", tent: "paneTent" };
        Object.entries(map).forEach(([k, id]) => document.getElementById(id).style.display = k === state.tab ? "block" : "none");
        updateAll();
      });
    });
    document.querySelectorAll(".preset-btn").forEach(b => b.addEventListener("click", () => applyPreset(b.dataset.preset)));
    document.getElementById("btnReset").addEventListener("click", () => applyPreset("smile"));
    document.getElementById("btnExportCsv").addEventListener("click", () => {
      downloadCsv("pfau_ch5b_smile_mwr.csv", ["Year", "Const_MWR_pct", "Selected_Pattern_MWR_pct"], state.lastExport);
    });
    ["spendModel", "initBudget", "horizonYrs", "hcInfPct", "cpiBasePct", "preserveMode", "hhMortality", "gpStartEq", "gpEndEq", "tentWrPct", "tentMcMode"].forEach(id => {
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
        slug="spending-smiles-glidepaths",
        title_en="Spending Smiles & Bond Tents",
        extra_css=".hm-active { outline: 2px solid var(--accent); outline-offset: -2px; font-weight: 700 !important; background: var(--accent-soft) !important; }",
        body_html=body_html,
        embedded_data_js=embedded,
        page_i18n=page_i18n,
        page_js=page_js,
    )


if __name__ == "__main__":
    build_ch5b()
