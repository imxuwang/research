#!/usr/bin/env python3
"""Build Lab 8 (Chapters 1, 8, 9): Household Balance Sheet Funded Ratio, 13-Factor CARE Diagnostic & Morningstar Gamma."""

from shared_shell import dump_json_inline, load_csv_records, render_page
from shared_sim_js import SHARED_SIM_JS


def build_ch8_9():
    curves = load_csv_records("us_treasury_tips_yields.csv")
    mort = load_csv_records("mortality_and_rmd_tables.csv")

    body_html = """  <main class="layout">
    <aside class="sidebar" aria-label="Simulation parameters" data-i18n-aria-label="aria_sidebar">
      <div class="side-section">
        <div class="sec-head-static">
          <h2 class="sec-title" data-i18n="sec_presets">Household Plan Presets</h2>
          <button type="button" class="link-btn" id="btnReset" data-i18n="btn_reset">Reset</button>
        </div>
        <div class="preset-grid">
          <button type="button" class="preset-btn active" data-preset="balanced">
            <span class="p-title" data-i18n="pre_bal_t">Funded Couple (FR ~112%)</span>
            <span class="p-meta" data-i18n="pre_bal_m">$1.2M Port + SS67 @ $85k</span>
          </button>
          <button type="button" class="preset-btn" data-preset="safety">
            <span class="p-title" data-i18n="pre_saf_t">Safety-First (CARE)</span>
            <span class="p-meta" data-i18n="pre_saf_m">SS70 + SPIA Floor Coverage</span>
          </button>
          <button type="button" class="preset-btn" data-preset="under">
            <span class="p-title" data-i18n="pre_und_t">Constrained (FR &lt; 95%)</span>
            <span class="p-meta" data-i18n="pre_und_m">High Longevity / Low Floor</span>
          </button>
          <button type="button" class="preset-btn" data-preset="gamma">
            <span class="p-title" data-i18n="pre_gam_t">Ex. 9.1–9.2 · Gamma</span>
            <span class="p-meta" data-i18n="pre_gam_m">+2.3% Gamma-Equiv Alpha</span>
          </button>
        </div>
      </div>

      <div class="side-section">
        <div class="sec-head-static"><h2 class="sec-title" data-i18n="sec_assets">Household Assets &amp; Discount Curve</h2></div>
        <div class="control-group">
          <label for="tipsCurveSel"><span data-i18n="lbl_disc">TIPS Real Discount Curve</span></label>
          <select id="tipsCurveSel"></select>
        </div>
        <div class="control-group row-2">
          <div>
            <label for="hhType"><span data-i18n="lbl_hh">Household Mortality</span></label>
            <select id="hhType">
              <option value="couple" selected data-i18n="hh_cpl">Couple (SOA 2017)</option>
              <option value="female" data-i18n="hh_fem">Female (SOA 2017)</option>
              <option value="male" data-i18n="hh_mal">Male (SOA 2017)</option>
            </select>
          </div>
          <div>
            <label for="ssAge"><span data-i18n="lbl_ssage">SS Claim Age</span></label>
            <input type="number" id="ssAge" value="67" min="62" max="70" step="1" />
          </div>
        </div>
        <div class="control-group row-2">
          <div>
            <label for="finPort"><span data-i18n="lbl_port">Portfolio ($)</span></label>
            <div class="currency-field"><span class="currency-prefix">$</span><input type="text" id="finPort" value="1,200,000" inputmode="numeric" /></div>
          </div>
          <div>
            <label for="cashRes"><span data-i18n="lbl_res">Emergency Reserves ($)</span></label>
            <div class="currency-field"><span class="currency-prefix">$</span><input type="text" id="cashRes" value="100,000" inputmode="numeric" /></div>
          </div>
        </div>
        <div class="control-group row-2">
          <div>
            <label for="ssPia"><span data-i18n="lbl_pia">SS FRA-67 PIA ($/yr)</span></label>
            <div class="currency-field"><span class="currency-prefix">$</span><input type="text" id="ssPia" value="36,000" inputmode="numeric" /></div>
          </div>
          <div>
            <label for="spiaAlloc"><span data-i18n="lbl_spia">SPIA Purchase ($)</span></label>
            <div class="currency-field"><span class="currency-prefix">$</span><input type="text" id="spiaAlloc" value="0" inputmode="numeric" /></div>
          </div>
        </div>
      </div>

      <div class="side-section">
        <div class="sec-head-static"><h2 class="sec-title" data-i18n="sec_liab">Retirement Liabilities</h2></div>
        <div class="control-group row-2">
          <div>
            <label for="essSpend"><span data-i18n="lbl_ess">Essential Floor ($/yr)</span></label>
            <div class="currency-field"><span class="currency-prefix">$</span><input type="text" id="essSpend" value="55,000" inputmode="numeric" /></div>
          </div>
          <div>
            <label for="discSpend"><span data-i18n="lbl_dspend">Discretionary ($/yr)</span></label>
            <div class="currency-field"><span class="currency-prefix">$</span><input type="text" id="discSpend" value="30,000" inputmode="numeric" /></div>
          </div>
        </div>
        <div class="control-group row-2">
          <div>
            <label for="ltcRes"><span data-i18n="lbl_ltc">LTC / Contingency ($)</span></label>
            <div class="currency-field"><span class="currency-prefix">$</span><input type="text" id="ltcRes" value="200,000" inputmode="numeric" /></div>
          </div>
          <div>
            <label for="legGoal"><span data-i18n="lbl_leg">Legacy Goal PV ($)</span></label>
            <div class="currency-field"><span class="currency-prefix">$</span><input type="text" id="legGoal" value="150,000" inputmode="numeric" /></div>
          </div>
        </div>
      </div>
    </aside>

    <section class="workspace" aria-label="Simulation outputs" data-i18n-aria-label="aria_workspace">
      <div class="results-shell">
        <div class="tabs-bar">
          <div class="tab-strip" role="tablist">
            <button type="button" class="tab-btn active" role="tab" aria-selected="true" data-tab="funded" data-i18n="tab_funded">Funded Ratio &amp; Balance Sheet</button>
            <button type="button" class="tab-btn" role="tab" aria-selected="false" data-tab="care" data-i18n="tab_care">13-Factor CARE Diagnostic</button>
            <button type="button" class="tab-btn" role="tab" aria-selected="false" data-tab="gamma" data-i18n="tab_gamma">Morningstar Gamma &amp; Advisor Alpha</button>
          </div>
        </div>

        <div class="results-body">
          <div id="paneFunded" class="tab-pane">
            <div class="kpis kpis-4 kpis-flush-top">
              <div class="kpi"><div class="kpi-label" data-i18n="kf_fr">Aggregate Funded Ratio</div><div class="kpi-val pos" id="kfFr">—</div><div class="kpi-sub" id="kfFrSub">—</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="kf_floor">Reliable Floor Coverage</div><div class="kpi-val" id="kfFloor">—</div><div class="kpi-sub" id="kfFloorSub">—</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="kf_liq">True Liquidity (Assets − Floor Gap)</div><div class="kpi-val" id="kfLiq">—</div><div class="kpi-sub" id="kfLiqSub">—</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="kf_spia">Actuarial SPIA Payout Rate</div><div class="kpi-val" id="kfSpia">—</div><div class="kpi-sub" id="kfSpiaSub">—</div></div>
            </div>

            <div class="panel-block">
              <div class="legend"><strong data-i18n="ttl_bs">Economic Retirement Balance Sheet: Present Value of Assets vs. Liabilities (TIPS-Discounted)</strong></div>
              <div class="chart-wrap"><canvas id="bsCanvas" height="235"></canvas><div class="tooltip" id="bsTip"></div></div>
            </div>

            <div class="panel-block">
              <div class="card-title"><h3 class="sec-title" data-i18n="ttl_bs_tbl">Household Economic Balance Sheet Line Items</h3></div>
              <div class="table-container" style="max-height:none;"><table><thead id="bsHead"></thead><tbody id="bsBody"></tbody></table></div>
            </div>
          </div>

          <div id="paneCare" class="tab-pane" style="display:none;">
            <div class="kpis kpis-4 kpis-flush-top">
              <div class="kpi"><div class="kpi-label" data-i18n="kc_cap">Risk Capacity Score</div><div class="kpi-val" id="kcCap">—</div><div class="kpi-sub" id="kcCapSub">—</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="kc_com">Emotional Comfort Score</div><div class="kpi-val" id="kcCom">—</div><div class="kpi-sub" id="kcComSub">—</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="kc_style">Recommended Income School</div><div class="kpi-val pos" id="kcStyle">—</div><div class="kpi-sub" id="kcStyleSub">—</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="kc_band">Suggested Planning Age &amp; Equity</div><div class="kpi-val" id="kcBand">—</div><div class="kpi-sub" id="kcBandSub">—</div></div>
            </div>

            <div class="split-grid">
              <div class="grid-cell">
                <div class="card-title"><h3 class="sec-title" data-i18n="ttl_care_sliders">Interactive 13-Factor CARE Scorecard (1 = Low / Conservative, 5 = High / Growth)</h3></div>
                <div id="careSliders" style="display:grid;grid-template-columns:1fr;gap:8px;max-height:420px;overflow-y:auto;padding-right:4px;"></div>
              </div>
              <div class="grid-cell">
                <div class="legend"><strong data-i18n="ttl_care_quad">Retirement Income Style Quadrant (Capacity vs. Safety-First Orientation)</strong></div>
                <div class="chart-wrap"><canvas id="careCanvas" height="270"></canvas><div class="tooltip" id="careTip"></div></div>
                <div class="notice" id="careRecBox" style="margin-top:12px;"></div>
              </div>
            </div>
          </div>

          <div id="paneGamma" class="tab-pane" style="display:none;">
            <div class="kpis kpis-4 kpis-flush-top">
              <div class="kpi"><div class="kpi-label" data-i18n="kg_gross">Gross Gamma-Equiv Alpha</div><div class="kpi-val pos" id="kgGross">—</div><div class="kpi-sub" id="kgGrossSub">—</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="kg_net">Net Fee-Adjusted Alpha</div><div class="kpi-val" id="kgNet">—</div><div class="kpi-sub" id="kgNetSub">—</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="kg_ce">Certainty-Equiv Income Lift</div><div class="kpi-val pos" id="kgCe">—</div><div class="kpi-sub" id="kgCeSub">—</div></div>
              <div class="kpi"><div class="kpi-label" data-i18n="kg_van">Ex. 9.1 Net Portfolio Return</div><div class="kpi-val" id="kgVan">—</div><div class="kpi-sub" id="kgVanSub">—</div></div>
            </div>

            <div class="split-grid">
              <div class="grid-cell">
                <div class="legend"><strong data-i18n="ttl_gam_bar">Ex. 9.2: Blanchett &amp; Kaplan Morningstar Gamma Levers (Toggle to Simulate)</strong></div>
                <div id="gammaChecks" style="display:grid;gap:8px;margin-bottom:12px;"></div>
                <div class="control-group">
                  <label for="advFeeBps"><span data-i18n="lbl_fee">Advisory + Fund Fee Drag (bps / yr)</span></label>
                  <input type="number" id="advFeeBps" value="65" min="0" max="200" step="5" />
                </div>
              </div>
              <div class="grid-cell">
                <div class="legend"><strong data-i18n="ttl_gam_wf">Annual Gamma-Equivalent Alpha Attribution &amp; Fee Hurdle</strong></div>
                <div class="chart-wrap"><canvas id="gammaCanvas" height="265"></canvas><div class="tooltip" id="gammaTip"></div></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </main>
"""

    page_i18n = {
        "page_title": {"en-UK": "Funded Ratio, CARE & Advisor Gamma · Ch. 1, 8, 9", "zh-CN": "资金充足率、CARE 诊断与 Gamma 价值 · 第1/8/9章"},
        "app_title": {"en-UK": "Ch. 1, 8, 9 · Funded Ratio, CARE & Gamma", "zh-CN": "第1/8/9章 · 家庭资产负债表、CARE 与 Gamma"},
        "sec_presets": {"en-UK": "Household Plan Presets", "zh-CN": "家庭财务情境预设"},
        "pre_bal_t": {"en-UK": "Funded Couple (FR ~112%)", "zh-CN": "稳健充裕夫妻 (充足率 ~112%)"},
        "pre_bal_m": {"en-UK": "$1.2M Port + SS67 @ $85k", "zh-CN": "$1.2M 组合 + 67岁社保 @ $85k"},
        "pre_saf_t": {"en-UK": "Safety-First (CARE)", "zh-CN": "安全优先型 (CARE)"},
        "pre_saf_m": {"en-UK": "SS70 + SPIA Floor Coverage", "zh-CN": "70岁领社保 + 年金锁定底线"},
        "pre_und_t": {"en-UK": "Constrained (FR < 95%)", "zh-CN": "资金偏紧型 (充足率 < 95%)"},
        "pre_und_m": {"en-UK": "High Longevity / Low Floor", "zh-CN": "长寿风险高 / 刚性底线高"},
        "pre_gam_t": {"en-UK": "Ex. 9.1–9.2 · Gamma", "zh-CN": "第9章 · 顾问 Gamma 增值"},
        "pre_gam_m": {"en-UK": "+2.3% Gamma-Equiv Alpha", "zh-CN": "+2.3% 等效年化超额收益"},
        "sec_assets": {"en-UK": "Household Assets & Discount Curve", "zh-CN": "家庭经济资产与折现曲线"},
        "lbl_disc": {"en-UK": "TIPS Real Discount Curve", "zh-CN": "TIPS 真实折现曲线"},
        "lbl_hh": {"en-UK": "Household Mortality", "zh-CN": "家庭成员结构"},
        "hh_cpl": {"en-UK": "Couple (SOA 2017)", "zh-CN": "夫妻双人 (SOA 2017)"},
        "hh_fem": {"en-UK": "Female (SOA 2017)", "zh-CN": "单身女性 (SOA 2017)"},
        "hh_mal": {"en-UK": "Male (SOA 2017)", "zh-CN": "单身男性 (SOA 2017)"},
        "lbl_ssage": {"en-UK": "SS Claim Age", "zh-CN": "社保申领年龄"},
        "lbl_port": {"en-UK": "Portfolio ($)", "zh-CN": "金融投资组合 ($)"},
        "lbl_res": {"en-UK": "Emergency Reserves ($)", "zh-CN": "应急备用现金 ($)"},
        "lbl_pia": {"en-UK": "SS FRA-67 PIA ($/yr)", "zh-CN": "67岁全额社保基数 ($/年)"},
        "lbl_spia": {"en-UK": "SPIA Purchase ($)", "zh-CN": "即期终身年金配置 ($)"},
        "sec_liab": {"en-UK": "Retirement Liabilities", "zh-CN": "退休经济负债结构"},
        "lbl_ess": {"en-UK": "Essential Floor ($/yr)", "zh-CN": "刚性基本生活 ($/年)"},
        "lbl_dspend": {"en-UK": "Discretionary ($/yr)", "zh-CN": "弹性享乐支出 ($/年)"},
        "lbl_ltc": {"en-UK": "LTC / Contingency ($)", "zh-CN": "医疗长护应急储备 ($)"},
        "lbl_leg": {"en-UK": "Legacy Goal PV ($)", "zh-CN": "遗产传承现值目标 ($)"},
        "tab_funded": {"en-UK": "Funded Ratio & Balance Sheet", "zh-CN": "资金充足率与资产负债表"},
        "tab_care": {"en-UK": "13-Factor CARE Diagnostic", "zh-CN": "13因子 CARE 规划诊断"},
        "tab_gamma": {"en-UK": "Morningstar Gamma & Advisor Alpha", "zh-CN": "晨星 Gamma 与顾问 Alpha"},
        "kf_fr": {"en-UK": "Aggregate Funded Ratio", "zh-CN": "家庭总资金充足率 FR"},
        "kf_floor": {"en-UK": "Reliable Floor Coverage", "zh-CN": "可靠收入对刚性底线覆盖率"},
        "kf_liq": {"en-UK": "True Liquidity (Assets − Floor Gap)", "zh-CN": "真实自由流动性"},
        "kf_spia": {"en-UK": "Actuarial SPIA Payout Rate", "zh-CN": "精算 SPIA 终身派息率"},
        "ttl_bs": {"en-UK": "Economic Retirement Balance Sheet: PV of Assets vs. Liabilities (TIPS-Discounted)", "zh-CN": "退休经济资产负债表：TIPS 贴现资产现值 vs 负债现值"},
        "ttl_bs_tbl": {"en-UK": "Household Economic Balance Sheet Line Items", "zh-CN": "家庭资产负债表分项明细"},
        "kc_cap": {"en-UK": "Risk Capacity Score", "zh-CN": "客观风险承受力得分"},
        "kc_com": {"en-UK": "Emotional Comfort Score", "zh-CN": "心理波动舒适度得分"},
        "kc_style": {"en-UK": "Recommended Income School", "zh-CN": "匹配退休收入流派"},
        "kc_band": {"en-UK": "Suggested Planning Age & Equity", "zh-CN": "建议规划年龄与股债区间"},
        "ttl_care_sliders": {"en-UK": "Interactive 13-Factor CARE Scorecard (1 = Low / Safety, 5 = High / Growth)", "zh-CN": "13因子 CARE 评分卡 (1=安全优先, 5=概率进取)"},
        "ttl_care_quad": {"en-UK": "Retirement Income Style Quadrant (Capacity vs. Safety-First Orientation)", "zh-CN": "退休收入策略象限图（客观能力 vs 心理倾向）"},
        "kg_gross": {"en-UK": "Gross Gamma-Equiv Alpha", "zh-CN": "税前总 Gamma 等效 Alpha"},
        "kg_net": {"en-UK": "Net Fee-Adjusted Alpha", "zh-CN": "扣除顾问费净超额 Alpha"},
        "kg_ce": {"en-UK": "Certainty-Equiv Income Lift", "zh-CN": "确定性等值退休收入提升"},
        "kg_van": {"en-UK": "Ex. 9.1 Net Portfolio Return", "zh-CN": "图 9.1 净回报示例 (7%−费 vs 4%)"},
        "ttl_gam_bar": {"en-UK": "Ex. 9.2: Blanchett & Kaplan Morningstar Gamma Levers (Toggle to Simulate)", "zh-CN": "图 9.2：Blanchett & Kaplan 晨星 Gamma 六大来源开关"},
        "lbl_fee": {"en-UK": "Advisory + Fund Fee Drag (bps / yr)", "zh-CN": "年化顾问与基金总费率 (基点 bps)"},
        "ttl_gam_wf": {"en-UK": "Annual Gamma-Equivalent Alpha Attribution & Fee Hurdle", "zh-CN": "年度 Gamma 超额收益拆解与费率门槛"}
    }

    embedded = (
        f"    const CURVES = {dump_json_inline(curves)};\n"
        f"    const MORT = {dump_json_inline(mort)};\n"
        + SHARED_SIM_JS
    )

    page_js = r"""
    const CARE_FACTORS = [
      { id: "c_long", g: "C", val: 3, en: "Short-Horizon Willingness (vs Max Longevity Fear)", zh: "C1. 接受较短精算期限意愿 (非极度害怕长寿)" },
      { id: "c_floor", g: "C", val: 3, en: "Reliable Income Floor Adequacy", zh: "C2. 养老金/社保底线充足度" },
      { id: "c_flex", g: "C", val: 3, en: "Spending Flexibility (Ability to Trim Discretionary)", zh: "C3. 非必需消费削减弹性" },
      { id: "c_res", g: "C", val: 3, en: "Dedicated Contingency Reserves Buffer", zh: "C4. 医疗/突发备用金缓冲充足度" },
      { id: "a_leg", g: "A", val: 3, en: "Legacy Aspiration vs Lifetime Consumption", zh: "A1. 遗产目标优先级" },
      { id: "a_up", g: "A", val: 3, en: "Lifestyle Upside Priority (over Floor Certainty)", zh: "A2. 追求生活质量上行弹性" },
      { id: "r_val", g: "R", val: 3, en: "Confidence in Equity Risk Premium Realization", zh: "R1. 对股票长期风险溢价兑现信心" },
      { id: "e_vol", g: "E", val: 3, en: "Portfolio Volatility & Drawdown Comfort", zh: "E1. 市场剧烈回撤心理承受力" },
      { id: "e_comp", g: "E", val: 3, en: "Technical Strategy Complexity Comfort", zh: "E2. 对动态规则/资产配置复杂度接受度" },
      { id: "e_ann", g: "E", val: 3, en: "Discomfort with Irrevocable Annuities (vs Safety)", zh: "E3. 偏好保留资金流动性（不购买年金）" },
      { id: "e_disc", g: "E", val: 3, en: "Behavioral Discipline Against Panic Selling", zh: "E4. 熊市坚持再平衡纪律" },
      { id: "e_cog", g: "E", val: 3, en: "Desire for Self-Directed Oversight", zh: "E5. 自主管理而非完全外包意愿" },
      { id: "e_adv", g: "E", val: 3, en: "Comfort Relying on Market Returns over Guarantees", zh: "E6. 信任总回报组合而非保本承诺" }
    ];

    const GAMMA_LEVERS = [
      { id: "g_tw", on: true, bps: 44, ce: 5.8, en: "Total-Wealth Asset Allocation (Human + SS)", zh: "1. 全家庭经济总财富配置" },
      { id: "g_dyn", on: true, bps: 52, ce: 7.4, en: "Dynamic Withdrawal Rule (vs 4% Constant)", zh: "2. 动态护栏提取策略" },
      { id: "g_ann", on: true, bps: 31, ce: 4.5, en: "Partial Annuity / Longevity Risk Pooling", zh: "3. 年金与长寿风险共担工具" },
      { id: "g_tax", on: true, bps: 42, ce: 5.5, en: "Tax-Efficient Asset Location & Sequencing", zh: "4. 税务账户配置与取款顺序" },
      { id: "g_liab", on: true, bps: 28, ce: 4.1, en: "Liability-Relative TIPS Duration Matching", zh: "5. 负债匹配 TIPS 组合优化" },
      { id: "g_ss", on: true, bps: 37, ce: 4.5, en: "Optimal Social Security Delaying (Age 70)", zh: "6. 社保延迟至70岁申领优化" }
    ];

    const state = { tab: "funded", bsData: null, lastExport: [] };

    (function initSelects() {
      const sel = document.getElementById("tipsCurveSel");
      for (let i = CURVES.length - 1; i >= 0; i--) {
        const c = CURVES[i];
        const opt = document.createElement("option");
        opt.value = c.Date;
        opt.textContent = `${c.Label} (DFII 10Y: ${c.DFII10 ?? 0.5}% / 30Y: ${c.DFII30 ?? 1.0}%)`;
        sel.appendChild(opt);
      }
      sel.value = CURVES[CURVES.length - 1].Date;
    })();

    function ssFactor(age) {
      // Exact statutory FRA-67 PIA claiming factor (62..70)
      if (age <= 67) {
        const monthsEarly = (67 - age) * 12;
        return 1 - Math.min(36, monthsEarly) * (5 / 900) - Math.max(0, monthsEarly - 36) * (5 / 1200);
      }
      return 1 + (age - 67) * 0.08;
    }

    function computeFunded() {
      const cRow = CURVES.find(x => x.Date === document.getElementById("tipsCurveSel").value) || CURVES[CURVES.length - 1];
      const r10 = ((cRow.DFII10 ?? 1.5) / 100);
      const r20 = ((cRow.DFII20 ?? cRow.DFII10 ?? 1.8) / 100);
      const hh = document.getElementById("hhType").value;
      const surv = buildSurvivalCurve(MORT, { table: "soa_2017", startAge: 65, household: hh });

      const port = Math.max(0, parseMoney(document.getElementById("finPort")));
      const res = Math.max(0, parseMoney(document.getElementById("cashRes")));
      const pia = Math.max(0, parseMoney(document.getElementById("ssPia")));
      const ssAge = Math.min(70, Math.max(62, parseInt(document.getElementById("ssAge").value, 10) || 67));
      const spiaBuy = Math.min(port, Math.max(0, parseMoney(document.getElementById("spiaAlloc"))));
      const remPort = port - spiaBuy;

      const ess = Math.max(0, parseMoney(document.getElementById("essSpend")));
      const disc = Math.max(0, parseMoney(document.getElementById("discSpend")));
      const ltc = Math.max(0, parseMoney(document.getElementById("ltcRes")));
      const leg = Math.max(0, parseMoney(document.getElementById("legGoal")));

      // Mortality-weighted PV of $1 real annuity (using curve blend r10 -> r20)
      let axReal = 0;
      for (const pt of surv.surv) {
        const yRate = pt.k <= 10 ? r10 : r20;
        axReal += pt.p / Math.pow(1 + yRate, pt.k);
      }
      // SPIA actuarial payout rate (nominal-ish/real w/ 3% load)
      const spiaNomYield = ((cRow.DGS20 ?? cRow.DGS10 ?? 3.5) / 100);
      let axSpia = 0;
      for (const pt of surv.surv) axSpia += pt.p / Math.pow(1 + spiaNomYield, pt.k);
      const spiaPayoutRate = 1.0 / (axSpia * 1.03);
      const spiaAnnual = spiaBuy * spiaPayoutRate;

      // SS starts at ssAge (if ssAge > 65, starts at k = ssAge - 65)
      const ssAnnual = pia * ssFactor(ssAge);
      let ssPv = 0;
      for (const pt of surv.surv) {
        if (pt.age >= ssAge) {
          const yRate = pt.k <= 10 ? r10 : r20;
          ssPv += (ssAnnual * pt.p) / Math.pow(1 + yRate, pt.k);
        }
      }
      const spiaPv = spiaBuy / 1.03; // Fair economic PV net of load
      const pvEss = ess * axReal;
      const pvDisc = disc * axReal;
      const totalAssets = remPort + res + ssPv + spiaPv;
      const totalLiab = pvEss + pvDisc + ltc + leg;
      const fundedRatio = totalLiab > 0 ? (totalAssets / totalLiab) * 100 : 100;
      const reliablePv = ssPv + spiaPv;
      const floorCov = pvEss > 0 ? (reliablePv / pvEss) * 100 : 100;
      const trueLiq = remPort + res - Math.max(0, pvEss - reliablePv) - ltc;

      return {
        remPort, res, ssPv, spiaPv, spiaAnnual, spiaPayoutRate, ssAnnual,
        pvEss, pvDisc, ltc, leg, totalAssets, totalLiab, fundedRatio, floorCov, trueLiq, axReal, surv
      };
    }

    function renderCareUI() {
      const box = document.getElementById("careSliders");
      const isZh = currentLang === "zh-CN";
      box.innerHTML = CARE_FACTORS.map((f, idx) => `
        <div style="display:flex;justify-content:space-between;align-items:center;gap:10px;border-bottom:1px solid var(--border);padding-bottom:5px;">
          <span style="font-size:12px;color:var(--text-soft);">${isZh ? f.zh : f.en}</span>
          <div style="display:flex;align-items:center;gap:6px;flex-shrink:0;">
            <input type="range" min="1" max="5" step="1" value="${f.val}" data-cidx="${idx}" style="width:82px;" class="care-rng" />
            <span style="font-family:var(--mono);font-size:12px;font-weight:600;width:16px;text-align:right;">${f.val}</span>
          </div>
        </div>`).join("");
      box.querySelectorAll(".care-rng").forEach(el => {
        el.addEventListener("input", () => {
          CARE_FACTORS[parseInt(el.dataset.cidx, 10)].val = parseInt(el.value, 10);
          updateCareScores();
        });
      });
    }

    function updateCareScores() {
      const isZh = currentLang === "zh-CN";
      const capItems = CARE_FACTORS.slice(0, 7);
      const comItems = CARE_FACTORS.slice(7);
      const avgCap = capItems.reduce((a, b) => a + b.val, 0) / capItems.length;
      const avgCom = comItems.reduce((a, b) => a + b.val, 0) / comItems.length;
      const capScore = Math.round(((avgCap - 1) / 4) * 100);
      const comScore = Math.round(((avgCom - 1) / 4) * 100);

      let schoolEn = "", schoolZh = "", planAge = "", eqBand = "", targetLab = "";
      if (capScore >= 55 && comScore >= 55) {
        schoolEn = "Probability-Based Total Return"; schoolZh = "概率驱动 · 总回报型";
        planAge = "Age 90–92"; eqBand = "60%–75% Equity · Guyton-Klinger / PAY Rule";
        targetLab = "../variable-spending/";
      } else if (capScore < 50 && comScore < 50) {
        schoolEn = "Safety-First Income Floor"; schoolZh = "安全优先 · 收入底线型";
        planAge = "Age 95–100 (Lifetime Pool)"; eqBand = "25%–40% Equity · TIPS Ladder + SPIA";
        targetLab = "../bonds-and-buckets/";
      } else if (comScore < 50 && capScore >= 50) {
        schoolEn = "Time-Segmentation Buckets"; schoolZh = "时间分段 · 蓄水池型";
        planAge = "Age 95"; eqBand = "40%–55% Equity + 10Y Bond Ladder";
        targetLab = "../bonds-and-buckets/";
      } else {
        schoolEn = "Balanced Dynamic Guardrails"; schoolZh = "平衡混合 · 动态护栏型";
        planAge = "Age 95"; eqBand = "45%–60% Equity · Zolt / Bengen Rules";
        targetLab = "../variable-spending/";
      }

      document.getElementById("kcCap").textContent = `${capScore} / 100`;
      document.getElementById("kcCapSub").textContent = isZh ? "基于寿命、底线、弹性与储备" : "Longevity, floor & reserve capacity";
      document.getElementById("kcCom").textContent = `${comScore} / 100`;
      document.getElementById("kcComSub").textContent = isZh ? "波动耐受度与管理复杂度" : "Volatility & complexity tolerance";
      document.getElementById("kcStyle").textContent = isZh ? schoolZh : schoolEn;
      document.getElementById("kcStyleSub").textContent = isZh ? "Ex. 8.3–8.6 象限匹配" : "Ex. 8.3–8.6 Profile Match";
      document.getElementById("kcBand").textContent = planAge;
      document.getElementById("kcBandSub").textContent = eqBand;

      document.getElementById("careRecBox").innerHTML = isZh
        ? `<strong>执行方案建议：</strong>匹配流派为「${schoolZh}」，建议采用 <strong>${eqBand}</strong>，规划至 ${planAge}。<a href="${targetLab}" style="color:var(--accent);font-weight:600;margin-left:6px;">前往对应章节实验室验证 →</a>`
        : `<strong>Action Plan:</strong> Matched school is <strong>${schoolEn}</strong> with <strong>${eqBand}</strong> (${planAge}). <a href="${targetLab}" style="color:var(--accent);font-weight:600;margin-left:6px;">Open matching lab →</a>`;

      const sc = setupCanvas(document.getElementById("careCanvas"));
      if (sc) {
        const { ctx, w, h } = sc, C = getThemeColors(); ctx.clearRect(0, 0, w, h);
        const pad = { l: 42, r: 18, t: 18, b: 30 }, cw = w - pad.l - pad.r, ch = h - pad.t - pad.b;
        const mapX = v => pad.l + (v / 100) * cw;
        const mapY = v => pad.t + ch - (v / 100) * ch;
        ctx.strokeStyle = C.grid; ctx.lineWidth = 1;
        ctx.strokeRect(pad.l, pad.t, cw, ch);
        ctx.beginPath(); ctx.setLineDash([4, 4]);
        ctx.moveTo(mapX(50), pad.t); ctx.lineTo(mapX(50), pad.t + ch);
        ctx.moveTo(pad.l, mapY(50)); ctx.lineTo(pad.l + cw, mapY(50));
        ctx.stroke(); ctx.setLineDash([]);

        ctx.fillStyle = C.muted; ctx.font = CANVAS_FONT; ctx.textAlign = "center";
        ctx.fillText(isZh ? "安全优先底线" : "Safety-First", mapX(25), mapY(25));
        ctx.fillText(isZh ? "时间分段池" : "Time-Segmentation", mapX(75), mapY(25));
        ctx.fillText(isZh ? "动态护栏" : "Guardrails", mapX(25), mapY(75));
        ctx.fillText(isZh ? "总回报概率" : "Total Return", mapX(75), mapY(75));
        ctx.fillText(isZh ? "客观风险能力 (0–100) →" : "Risk Capacity (0–100) →", pad.l + cw * 0.5, h - 8);

        ctx.beginPath(); ctx.arc(mapX(capScore), mapY(comScore), 8, 0, Math.PI * 2);
        ctx.fillStyle = C.port; ctx.fill(); ctx.strokeStyle = C.panel; ctx.lineWidth = 2; ctx.stroke();
      }
    }

    function renderGammaUI() {
      const box = document.getElementById("gammaChecks");
      const isZh = currentLang === "zh-CN";
      box.innerHTML = GAMMA_LEVERS.map((g, i) => `
        <div class="switch-row" style="border-bottom:1px solid var(--border);padding-bottom:6px;">
          <label for="${g.id}" style="font-size:12.5px;">${isZh ? g.zh : g.en} <span style="font-family:var(--mono);color:var(--accent);">(+${g.bps} bps)</span></label>
          <input type="checkbox" id="${g.id}" class="switch gamma-sw" data-gidx="${i}" ${g.on ? "checked" : ""} />
        </div>`).join("");
      box.querySelectorAll(".gamma-sw").forEach(el => {
        el.addEventListener("change", () => {
          GAMMA_LEVERS[parseInt(el.dataset.gidx, 10)].on = el.checked;
          updateGamma();
        });
      });
    }

    function updateGamma() {
      const isZh = currentLang === "zh-CN";
      const feeBps = Math.max(0, parseFloat(document.getElementById("advFeeBps").value) || 0);
      const active = GAMMA_LEVERS.filter(g => g.on);
      const grossBps = active.reduce((a, b) => a + b.bps, 0);
      const ceLift = active.reduce((a, b) => a + b.ce, 0);
      const netBps = grossBps - feeBps;
      const vanNet = 7.0 - (feeBps / 100);

      document.getElementById("kgGross").textContent = `+${(grossBps / 100).toFixed(2)}%`;
      document.getElementById("kgGrossSub").textContent = `${grossBps} bps (${active.length} ${isZh ? "项启用" : "levers active"})`;
      document.getElementById("kgNet").textContent = fmtPct(netBps / 100, 2, true);
      document.getElementById("kgNet").className = "kpi-val " + (netBps >= 0 ? "pos" : "neg");
      document.getElementById("kgNetSub").textContent = isZh ? `扣除年费 ${feeBps} bps 后` : `Net of ${feeBps} bps annual fee`;
      document.getElementById("kgCe").textContent = `+${ceLift.toFixed(1)}%`;
      document.getElementById("kgCeSub").textContent = isZh ? "晨星 2013 基准满项约 +31.8%" : "Blanchett-Kaplan max ~+31.8%";
      document.getElementById("kgVan").textContent = `${vanNet.toFixed(2)}% vs 4.00%`;
      document.getElementById("kgVanSub").textContent = isZh ? "Ex. 9.1 顾问赋能净复合回报" : "Ex. 9.1 advisor-assisted vs DIY 4%";

      const sc = setupCanvas(document.getElementById("gammaCanvas"));
      if (sc) {
        const { ctx, w, h } = sc, C = getThemeColors(); ctx.clearRect(0, 0, w, h);
        const bars = GAMMA_LEVERS.map(g => ({ lbl: "#" + (GAMMA_LEVERS.indexOf(g) + 1), v: g.on ? g.bps : 0, col: C.accent }));
        bars.push({ lbl: isZh ? "年费" : "Fee", v: -feeBps, col: C.danger });
        bars.push({ lbl: isZh ? "净Gain" : "Net", v: netBps, col: netBps >= 0 ? C.success : C.danger });
        const minY = Math.min(-50, -feeBps - 20), maxY = Math.max(80, grossBps * 0.45, netBps + 30);
        const pad = { l: 48, r: 16, t: 18, b: 32 }, cw = w - pad.l - pad.r, ch = h - pad.t - pad.b;
        const mapY = v => pad.t + ch - ((v - minY) / Math.max(1, maxY - minY)) * ch;
        ctx.strokeStyle = C.grid; ctx.font = CANVAS_FONT; ctx.textAlign = "right";
        computeNiceLinearTicks(minY, maxY, 4).forEach(v => {
          const y = mapY(v); ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(w - pad.r, y); ctx.stroke();
          ctx.fillStyle = C.muted; ctx.fillText(v + "bps", pad.l - 4, y + 4);
        });
        const y0 = mapY(0), bw = cw / bars.length;
        bars.forEach((b, i) => {
          const x = pad.l + i * bw + bw * 0.18, ww = bw * 0.64, y = mapY(b.v);
          ctx.fillStyle = b.col;
          ctx.fillRect(x, Math.min(y, y0), ww, Math.abs(y - y0));
          ctx.fillStyle = C.text; ctx.textAlign = "center";
          ctx.fillText((b.v > 0 ? "+" : "") + b.v, x + ww * 0.5, b.v >= 0 ? y - 5 : y + 12);
          ctx.fillStyle = C.muted; ctx.fillText(b.lbl, x + ww * 0.5, h - 8);
        });
      }
    }

    function updateAll() {
      const isZh = currentLang === "zh-CN";
      const bs = computeFunded();
      state.bsData = bs;
      document.getElementById("kfFr").textContent = bs.fundedRatio.toFixed(1) + "%";
      document.getElementById("kfFr").className = "kpi-val " + (bs.fundedRatio >= 100 ? "pos" : "neg");
      document.getElementById("kfFrSub").textContent = `${fmtCompactMoney(bs.totalAssets)} vs ${fmtCompactMoney(bs.totalLiab)}`;
      document.getElementById("kfFloor").textContent = bs.floorCov.toFixed(1) + "%";
      document.getElementById("kfFloorSub").textContent = isZh ? `社保+年金 ${fmtCompactMoney(bs.ssPv + bs.spiaPv)}` : `Reliable PV ${fmtCompactMoney(bs.ssPv + bs.spiaPv)}`;
      document.getElementById("kfLiq").textContent = fmtCompactMoney(bs.trueLiq);
      document.getElementById("kfLiq").className = "kpi-val " + (bs.trueLiq >= 0 ? "pos" : "neg");
      document.getElementById("kfLiqSub").textContent = isZh ? `贴现年金因子 a_x = ${bs.axReal.toFixed(1)}` : `Real annuity factor = ${bs.axReal.toFixed(1)}`;
      document.getElementById("kfSpia").textContent = (bs.spiaPayoutRate * 100).toFixed(2) + "%";
      document.getElementById("kfSpiaSub").textContent = `${isZh ? "年派息" : "Annual"}: ${fmtExactMoney(bs.spiaAnnual)}`;

      document.getElementById("bsHead").innerHTML = isZh
        ? `<tr><th>资产负债表项目</th><th>分类</th><th>年现金流 / 基准</th><th>TIPS 折现现值 ($)</th><th>占总负债/资产比</th></tr>`
        : `<tr><th>Balance Sheet Item</th><th>Side</th><th>Annual Cash Flow</th><th>TIPS Present Value ($)</th><th>Share (%)</th></tr>`;

      const rows = [
        [isZh ? "可投资金融组合 (扣除SPIA)" : "Financial Portfolio (net of SPIA)", isZh ? "资产" : "Asset", "—", bs.remPort, (bs.remPort / bs.totalAssets) * 100],
        [isZh ? "专用应急现金储备" : "Dedicated Contingency Reserves", isZh ? "资产" : "Asset", "—", bs.res, (bs.res / bs.totalAssets) * 100],
        [isZh ? "社会保障养老金 (PV)" : "Social Security Present Value", isZh ? "资产" : "Asset", fmtExactMoney(bs.ssAnnual) + "/yr", bs.ssPv, (bs.ssPv / bs.totalAssets) * 100],
        [isZh ? "即期终身年金 (SPIA PV)" : "SPIA Lifetime Annuity PV", isZh ? "资产" : "Asset", fmtExactMoney(bs.spiaAnnual) + "/yr", bs.spiaPv, (bs.spiaPv / bs.totalAssets) * 100],
        [isZh ? "刚性基本生活底线 (PV)" : "Essential Spending Floor PV", isZh ? "负债" : "Liability", fmtExactMoney(parseMoney(document.getElementById("essSpend"))) + "/yr", bs.pvEss, (bs.pvEss / bs.totalLiab) * 100],
        [isZh ? "弹性享受型支出 (PV)" : "Discretionary Lifestyle PV", isZh ? "负债" : "Liability", fmtExactMoney(parseMoney(document.getElementById("discSpend"))) + "/yr", bs.pvDisc, (bs.pvDisc / bs.totalLiab) * 100],
        [isZh ? "医疗长护应急储备需求" : "Longevity / LTC Reserve Target", isZh ? "负债" : "Liability", "—", bs.ltc, (bs.ltc / bs.totalLiab) * 100],
        [isZh ? "遗产传承目标 (PV)" : "Legacy Aspiration Target PV", isZh ? "负债" : "Liability", "—", bs.leg, (bs.leg / bs.totalLiab) * 100]
      ];
      state.lastExport = rows.map(r => [r[0], r[1], r[2], Math.round(r[3]), r[4].toFixed(1)]);
      document.getElementById("bsBody").innerHTML = rows.map(r =>
        `<tr><td>${r[0]}</td><td><span class="year-pill">${r[1]}</span></td><td>${r[2]}</td><td><strong>${fmtExactMoney(r[3])}</strong></td><td>${r[4].toFixed(1)}%</td></tr>`
      ).join("");

      if (state.tab === "funded") {
        const sc = setupCanvas(document.getElementById("bsCanvas"));
        if (sc) {
          const { ctx, w, h } = sc, C = getThemeColors(); ctx.clearRect(0, 0, w, h);
          const maxV = Math.max(bs.totalAssets, bs.totalLiab) * 1.15;
          const pad = { l: 120, r: 30, t: 24, b: 28 }, cw = w - pad.l - pad.r;
          const mapX = v => pad.l + (v / Math.max(1, maxV)) * cw;
          ctx.strokeStyle = C.grid; ctx.font = CANVAS_FONT; ctx.textAlign = "center";
          computeNiceLinearTicks(0, maxV, 4).forEach(v => {
            const x = mapX(v); ctx.beginPath(); ctx.moveTo(x, pad.t); ctx.lineTo(x, h - pad.b); ctx.stroke();
            ctx.fillStyle = C.muted; ctx.fillText(fmtCompactMoney(v), x, h - 8);
          });
          const drawStack = (y, lbl, segs) => {
            let curX = pad.l;
            segs.forEach(([val, col]) => {
              const segW = (val / maxV) * cw;
              ctx.fillStyle = col; ctx.fillRect(curX, y, segW, 44);
              curX += segW;
            });
            ctx.fillStyle = C.text; ctx.textAlign = "right"; ctx.font = CANVAS_LABEL_FONT;
            ctx.fillText(lbl, pad.l - 10, y + 26);
          };
          drawStack(44, isZh ? "经济总资产" : "Total Assets", [[bs.remPort, C.equity], [bs.res, C.accent], [bs.ssPv, C.success], [bs.spiaPv, C.port]]);
          drawStack(120, isZh ? "经济总负债" : "Total Liab.", [[bs.pvEss, C.danger], [bs.pvDisc, C.inflation], [bs.ltc, C.bond], [bs.leg, C.muted]]);
        }
      } else if (state.tab === "care") {
        renderCareUI(); updateCareScores();
      } else if (state.tab === "gamma") {
        renderGammaUI(); updateGamma();
      }
    }

    function applyPreset(name) {
      document.querySelectorAll(".preset-btn").forEach(b => b.classList.toggle("active", b.dataset.preset === name));
      document.getElementById("finPort").value = "1,200,000";
      document.getElementById("cashRes").value = "100,000";
      document.getElementById("ssPia").value = "36,000";
      document.getElementById("ssAge").value = "67";
      document.getElementById("spiaAlloc").value = "0";
      document.getElementById("essSpend").value = "55,000";
      document.getElementById("discSpend").value = "30,000";
      document.getElementById("ltcRes").value = "200,000";
      document.getElementById("legGoal").value = "150,000";
      if (name === "safety") {
        document.getElementById("ssAge").value = "70";
        document.getElementById("spiaAlloc").value = "350,000";
        CARE_FACTORS.forEach(f => { f.val = f.id === "c_floor" ? 4 : 2; });
        document.querySelector('[data-tab="care"]').click();
      } else if (name === "under") {
        document.getElementById("finPort").value = "750,000";
        document.getElementById("essSpend").value = "68,000";
        document.querySelector('[data-tab="funded"]').click();
      } else if (name === "gamma") {
        GAMMA_LEVERS.forEach(g => { g.on = true; });
        document.querySelector('[data-tab="gamma"]').click();
      } else {
        CARE_FACTORS.forEach(f => { f.val = 3; });
        document.querySelector('[data-tab="funded"]').click();
      }
      updateAll();
    }

    function onThemeOrLangChange() { updateAll(); }

    document.querySelectorAll(".tab-btn").forEach(b => {
      b.addEventListener("click", () => {
        state.tab = b.dataset.tab;
        document.querySelectorAll(".tab-btn").forEach(x => { x.classList.toggle("active", x === b); x.setAttribute("aria-selected", x === b ? "true" : "false"); });
        const map = { funded: "paneFunded", care: "paneCare", gamma: "paneGamma" };
        Object.entries(map).forEach(([k, id]) => document.getElementById(id).style.display = k === state.tab ? "block" : "none");
        updateAll();
      });
    });
    document.querySelectorAll(".preset-btn").forEach(b => b.addEventListener("click", () => applyPreset(b.dataset.preset)));
    document.getElementById("btnReset").addEventListener("click", () => applyPreset("balanced"));
    document.getElementById("btnExportCsv").addEventListener("click", () => {
      downloadCsv("pfau_ch8_9_funded_ratio.csv", ["Item", "Side", "Annual_Flow", "TIPS_PV", "Share_pct"], state.lastExport);
    });
    ["tipsCurveSel", "hhType", "ssAge", "finPort", "cashRes", "ssPia", "spiaAlloc", "essSpend", "discSpend", "ltcRes", "legGoal", "advFeeBps"].forEach(id => {
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
        slug="funded-ratio-and-gamma",
        title_en="Funded Ratio, CARE & Advisor Gamma",
        extra_css="",
        body_html=body_html,
        embedded_data_js=embedded,
        page_i18n=page_i18n,
        page_js=page_js,
    )


if __name__ == "__main__":
    build_ch8_9()
