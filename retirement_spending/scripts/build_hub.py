#!/usr/bin/env python3
"""Build docs/retirement-spending/index.html — Suite Overview Hub & Chapter 1 Interactive Primer."""

from shared_shell import CHAPTER_NAV, dump_json_inline, render_page

EXTRA_CSS = """
    .hub-wrap { max-width: 1080px; margin: 0 auto; padding: 28px 22px 56px; }
    .hub-intro { margin-bottom: 24px; max-width: 72ch; }
    .hub-intro h2 { margin: 0 0 6px; font-size: 21px; font-weight: 650; letter-spacing: -0.02em; text-wrap: balance; }
    .hub-intro p { margin: 0; color: var(--text-soft); font-size: 13.5px; text-wrap: pretty; }

    .lab-grid {
      display: grid; grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px; margin-bottom: 26px;
    }
    @media (max-width: 760px) { .lab-grid { grid-template-columns: 1fr; } }
    a.lab-link {
      display: flex; flex-direction: column; justify-content: space-between; gap: 10px;
      padding: 15px 17px; background: var(--panel); border: 1px solid var(--border);
      border-radius: 8px; text-decoration: none; color: inherit;
      transition: border-color 0.14s, background 0.14s;
    }
    a.lab-link:hover { border-color: var(--border-hover); background: var(--bg-subtle); }
    .lab-top { display: flex; align-items: baseline; justify-content: space-between; gap: 10px; }
    .lab-ch {
      font-family: var(--mono); font-size: 11.5px; font-weight: 600;
      color: var(--accent); background: var(--accent-soft); border: 1px solid var(--accent-border);
      padding: 2px 7px; border-radius: 4px; flex-shrink: 0;
    }
    .lab-title { margin: 0; font-size: 15px; font-weight: 620; text-wrap: balance; }
    .lab-desc { margin: 5px 0 0; font-size: 12.8px; color: var(--muted); line-height: 1.48; text-wrap: pretty; }
    .lab-meta { display: flex; align-items: center; justify-content: space-between; font-size: 12px; color: var(--text-soft); border-top: 1px solid var(--border); padding-top: 9px; }

    .primer-grid {
      display: grid; grid-template-columns: 330px minmax(0, 1fr); gap: 1px;
      background: var(--border); border: 1px solid var(--border); border-radius: 8px; overflow: hidden; margin-bottom: 24px;
    }
    @media (max-width: 900px) { .primer-grid { grid-template-columns: 1fr; } }
    .primer-controls { background: var(--panel); padding: 18px; }
    .primer-outputs { background: var(--panel); padding: 18px 20px; min-width: 0; }

    .matrix-panel {
      background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 16px 20px;
    }
"""

LAB_CARDS = [
    ("fixed-returns-longevity", "Ch. 2", "第2章",
     "Fixed Returns & Longevity Risk", "固定收益与长寿风险",
     "Deterministic PMT / NPER / RATE solvers, Exhibit 2.1 return waterfall, SOA 2012 IAM vs. SSA mortality survival curves, and Exhibits 2.8–2.10 Horizon × Return matrices.",
     "第2章：确定性 PMT/NPER/RATE 求解、收益拆解瀑布图、SOA 与 SSA 生存曲线对比，以及退休年限 × 收益率支出矩阵。"),
    ("sequence-of-returns-risk", "Ch. 3", "第3章",
     "Sequence-of-Returns Risk", "收益率顺序风险",
     "Wealth glide paths and >10% withdrawal spirals (Ex. 3.1–3.3), Adam's 60-year lifecycle & regression R² attribution (Ex. 3.4–3.6), and reverse-engineered IRR percentiles (Ex. 3.7–3.9).",
     "第3章：资产下滑路径与 >10% 提取率螺旋、60年全生命周期顺序风险归因（回归 R²），以及反推固定收益率分位数（10,000次蒙特卡洛）。"),
    ("safe-withdrawal-rates", "Ch. 4", "第4章",
     "Safe Withdrawal Rates & Trinity Study", "安全提取率与 Trinity 研究",
     "Bengen SAFEMAX across 1871–2025 / 1928–2025 (Ex. 4.1–4.4), full Trinity Study success grid (Ex. 4.5), historical overlap bias vs. Monte Carlo (Ex. 4.6), and Markowitz SWR isoquants (Ex. 4.7–4.8).",
     "第4章：Bengen 历史最差安全提取率 (SAFEMAX)、完整 Trinity 研究成功率矩阵、历史窗口重叠偏差对比，以及均值-方差有效前沿与等提取率曲线。"),
    ("valuations-and-savings", "Ch. 5A", "第5章上",
     "Valuations, Safe Savings & Drag", "市场估值、安全储蓄率与损耗",
     "Shiller PE10 & 10Y yield MWR regression (Ex. 5.4–5.8), Safe Savings Rate SAFEMIN lifecycle (Ex. 5.9–5.11), 20-country DMS & 5-asset optimization (Ex. 5.2–5.3, 5.26–5.28), and fee/tax/mistiming drag (Ex. 5.12–5.13).",
     "第5章上：席勒 PE10 与美债利率回归预测、安全储蓄率 (SAFEMIN) 全周期模拟、20国历史与5资产配置优化，以及费用/税负/择时失误损耗。"),
    ("spending-smiles-glidepaths", "Ch. 5B", "第5章下",
     "Spending Smiles & Bond Tents", "支出微笑曲线与动态股债滑道",
     "Blanchett HRS Spending Smile & Basu 4-category Age-Banding (Ex. 5.16–5.21), nominal/real legacy targets & competing mortality ruin (Ex. 5.14–5.15, 5.22–5.25), and Rising Equity Glidepath 2D heatmap (Ex. 5.29).",
     "第5章下：Blanchett 退休支出微笑曲线与 Basu 分年龄段通胀模型、本金/购买力留存与寿命竞争风险、以及“债券帐篷”递增股票滑道热力图。"),
    ("variable-spending", "Ch. 6", "第6章",
     "Variable Spending & PAY Rule™", "可变支出策略与 PAY 准则",
     "All 10 variable rules (Constant, Fixed %, Hybrid, 3Y MA, Bengen F/C, Vanguard F/C, Kitces Ratchet, Guyton-Klinger 2006, Zolt Glidepath, Modified RMD), PAY Rule™ auto-calibration, and 1966/1982/1946 head-to-head.",
     "第6章：完整实现全书 10 种动态支出规则、PAY 准则自动校准器（保守/稳健/进取），以及 1966 滞胀/1982 牛市/1946 高通胀年份正面交锋。"),
    ("bonds-and-buckets", "Ch. 7", "第7章",
     "Bond Ladders & Time Segmentation", "债券阶梯与时间分段策略",
     "Forward 30-yr Treasury STRIPS & backward-induction TIPS ladders (Ex. 7.11–7.12), bond duration/convexity/pull-to-par (Ex. 7.1–7.9), and 7-way Time Segmentation MC simulator (Ex. 7.13–7.21).",
     "第7章：30年期零息国债 STRIPS 与抗通胀债券 TIPS 反向归纳阶梯、久期/凸性/回面值演示，以及 7 种时间分段桶策略与动态总收益对比。"),
    ("funded-ratio-and-gamma", "Ch. 8–9", "第8–9章",
     "Funded Ratio, CARE & Advisor Gamma", "资金充足率、CARE 与规划 Gamma",
     "Risk-free TIPS Funded Ratio & Essential Floor balance sheet (Ex. 1.2, 8.2), interactive 13-factor CARE diagnostic (Ex. 8.6), and Morningstar Gamma / Vanguard Advisor Alpha simulator (Ex. 9.1–9.2).",
     "第8–9章：基于 TIPS 贴现的无风险资金充足率资产负债表、13因子 CARE 财务诊断评估，以及晨星 Gamma 六大维度与先锋顾问 Alpha 量化模拟器。"),
]


def build_hub():
    cards_html = []
    for slug, ch_en, ch_zh, t_en, t_zh, d_en, d_zh in LAB_CARDS:
        key_t = f"card_t_{slug.replace('-', '_')}"
        key_d = f"card_d_{slug.replace('-', '_')}"
        key_ch = f"card_ch_{slug.replace('-', '_')}"
        cards_html.append(f"""      <a class="lab-link" href="./{slug}/">
        <div>
          <div class="lab-top">
            <h3 class="lab-title" data-i18n="{key_t}">{t_en}</h3>
            <span class="lab-ch" data-i18n="{key_ch}">{ch_en}</span>
          </div>
          <p class="lab-desc" data-i18n="{key_d}">{d_en}</p>
        </div>
        <div class="lab-meta">
          <span data-i18n="open_lab">Open interactive lab</span>
          <span aria-hidden="true">&rarr;</span>
        </div>
      </a>""")

    body_html = f"""  <main class="hub-wrap">
    <div class="hub-intro">
      <h2 data-i18n="hub_heading">How Much Can I Spend in Retirement? — Interactive Quantitative Suite</h2>
      <p data-i18n="hub_sub">Eight self-contained interactive laboratories implementing the historical simulations, 10,000-run stochastic models, variable spending rules, bond ladders, and balance-sheet diagnostics from Wade D. Pfau’s book.</p>
    </div>

    <div class="lab-grid">
{chr(10).join(cards_html)}
    </div>

    <section class="primer-grid" aria-label="Chapter 1 Liquidity & Safe Spending Calculator" data-i18n-aria-label="aria_ch1_calc">
      <div class="primer-controls">
        <div class="sec-head-static">
          <h3 class="sec-title" data-i18n="ch1_calc_title">Chapter 1: Nest Egg, Inflation &amp; True Liquidity</h3>
        </div>
        <div class="control-group">
          <label for="ch1Portfolio"><span data-i18n="lbl_total_assets">Total financial assets</span></label>
          <div class="currency-field"><span class="currency-prefix">$</span><input type="text" id="ch1Portfolio" value="1,500,000" inputmode="numeric" /></div>
        </div>
        <div class="control-group">
          <label for="ch1Spend"><span data-i18n="lbl_target_spend">Target annual spending (S₁)</span></label>
          <div class="currency-field"><span class="currency-prefix">$</span><input type="text" id="ch1Spend" value="40,000" inputmode="numeric" /></div>
        </div>
        <div class="control-group row-2">
          <div>
            <label for="ch1Swr"><span data-i18n="lbl_swr_pct">Safe WR (%)</span></label>
            <input type="number" id="ch1Swr" value="4.0" min="1.5" max="10" step="0.1" />
          </div>
          <div>
            <label for="ch1Inf"><span data-i18n="lbl_inf_pct">Inflation (%/yr)</span></label>
            <input type="number" id="ch1Inf" value="3.0" min="0" max="12" step="0.1" />
          </div>
        </div>
        <div class="control-group row-2">
          <div>
            <label for="ch1InfYrs"><span data-i18n="lbl_inf_yrs">Horizon (yrs)</span></label>
            <input type="number" id="ch1InfYrs" value="25" min="5" max="50" step="1" />
          </div>
          <div>
            <label for="ch1AnnuityPct"><span data-i18n="lbl_spia_rate">SPIA Payout (%)</span></label>
            <input type="number" id="ch1AnnuityPct" value="5.0" min="3" max="12" step="0.1" />
          </div>
        </div>
      </div>
      <div class="primer-outputs">
        <div class="kpis kpis-4 kpis-flush-top">
          <div class="kpi">
            <div class="kpi-label" data-i18n="kpi_nest_egg">Target Portfolio (W₀)</div>
            <div class="kpi-val" id="ch1NestEgg">—</div>
            <div class="kpi-sub" id="ch1NestSub">—</div>
          </div>
          <div class="kpi">
            <div class="kpi-label" data-i18n="kpi_purch_power">$1 Real Power Left</div>
            <div class="kpi-val neg" id="ch1RealVal">—</div>
            <div class="kpi-sub" id="ch1PriceMult">—</div>
          </div>
          <div class="kpi">
            <div class="kpi-label" data-i18n="kpi_true_liq_self">True Liquidity (Self-Fund)</div>
            <div class="kpi-val" id="ch1LiqSelf">—</div>
            <div class="kpi-sub" id="ch1LiqSelfSub">—</div>
          </div>
          <div class="kpi">
            <div class="kpi-label" data-i18n="kpi_true_liq_spia">True Liquidity (SPIA Pool)</div>
            <div class="kpi-val pos" id="ch1LiqSpia">—</div>
            <div class="kpi-sub" id="ch1LiqSpiaSub">—</div>
          </div>
        </div>
        <div style="padding-top:16px;">
          <div class="legend">
            <div class="legend-items">
              <div class="legend-item"><span class="swatch" style="background:var(--port);height:8px;"></span><span data-i18n="leg_earmarked">Earmarked Capital (Technical Liquidity Only)</span></div>
              <div class="legend-item"><span class="swatch" style="background:var(--success);height:8px;"></span><span data-i18n="leg_true_liq">Unencumbered True Liquidity</span></div>
              <div class="legend-item"><span class="swatch" style="background:var(--inflation);height:3px;"></span><span data-i18n="leg_inf_erosion">Purchasing Power Curve</span></div>
            </div>
          </div>
          <div class="chart-wrap">
            <canvas id="ch1Canvas" height="235"></canvas>
            <div class="tooltip" id="ch1Tip"></div>
          </div>
        </div>
      </div>
    </section>

    <section class="matrix-panel">
      <div class="card-title" style="margin-bottom:8px;">
        <h3 class="sec-title" data-i18n="ch1_schools_title">Chapter 1: Probability-Based vs. Safety-First Frameworks (Exhibits 1.2–1.6)</h3>
      </div>
      <div class="table-container" style="max-height:none;">
        <table>
          <thead>
            <tr>
              <th data-i18n="th_dim">Dimension</th>
              <th data-i18n="th_prob">Probability-Based (Investments / Total Return)</th>
              <th data-i18n="th_safe">Safety-First (Insurance / Asset-Liability Match)</th>
            </tr>
          </thead>
          <tbody id="ch1MatrixBody"></tbody>
        </table>
      </div>
    </section>
  </main>"""

    page_i18n = {
        "page_title": {"en-UK": "Retirement Spending Strategies (Pfau)", "zh-CN": "退休支出策略分析（Pfau）"},
        "app_title": {"en-UK": "Retirement Spending Strategies (Pfau)", "zh-CN": "退休支出策略分析（Pfau）"},
        "hub_heading": {
            "en-UK": "How Much Can I Spend in Retirement? — Quantitative Labs",
            "zh-CN": "《退休后我能花多少钱？》—— 量化分析交互实验室",
        },
        "hub_sub": {
            "en-UK": "Eight self-contained interactive tools implementing the historical simulations, 10,000-run Monte Carlo engines, variable spending rules, bond ladders, and balance-sheet models across Chapters 1–9 of Wade D. Pfau's guide.",
            "zh-CN": "全套 8 个纯本地单文件交互实验室，完整复现 Wade D. Pfau 专著第 1–9 章的历史回测、万次蒙特卡洛模拟、动态支出规则、债券阶梯与家庭资产负债表模型。",
        },
        "open_lab": {"en-UK": "Open interactive lab", "zh-CN": "进入交互实验室"},
        "aria_ch1_calc": {"en-UK": "Chapter 1 Liquidity and Inflation Calculator", "zh-CN": "第1章流动性与通胀计算器"},
        "ch1_calc_title": {"en-UK": "Ch. 1: Nest Egg, Inflation & True Liquidity", "zh-CN": "第1章：目标本金、通胀侵蚀与真实流动性"},
        "lbl_total_assets": {"en-UK": "Total financial assets", "zh-CN": "家庭总金融资产"},
        "lbl_target_spend": {"en-UK": "Target annual spending (S₁)", "zh-CN": "目标首年支出 (S₁)"},
        "lbl_swr_pct": {"en-UK": "Safe WR (%)", "zh-CN": "安全提取率 (%)"},
        "lbl_inf_pct": {"en-UK": "Inflation (%/yr)", "zh-CN": "年通胀率 (%/年)"},
        "lbl_inf_yrs": {"en-UK": "Horizon (yrs)", "zh-CN": "年数 (年)"},
        "lbl_spia_rate": {"en-UK": "SPIA Payout (%)", "zh-CN": "即期年金给付率 (%)"},
        "kpi_nest_egg": {"en-UK": "Self-Fund Target (W₀)", "zh-CN": "自筹目标本金 (W₀)"},
        "kpi_purch_power": {"en-UK": "$1 Real Power Left", "zh-CN": "$1 剩余购买力"},
        "kpi_true_liq_self": {"en-UK": "True Liquidity (Self-Fund)", "zh-CN": "真实流动性（纯自筹）"},
        "kpi_true_liq_spia": {"en-UK": "True Liquidity (Annuity Pool)", "zh-CN": "真实流动性（年金池）"},
        "leg_earmarked": {"en-UK": "Earmarked Capital (Allocation Liquidity Only)", "zh-CN": "专款占用本金（仅配置流动性）"},
        "leg_true_liq": {"en-UK": "Unencumbered True Liquidity", "zh-CN": "可自由支配真实流动性"},
        "leg_inf_erosion": {"en-UK": "$1 Purchasing Power Over Horizon", "zh-CN": "$1 购买力随时间衰减曲线"},
        "ch1_schools_title": {"en-UK": "Ch. 1: Probability-Based vs. Safety-First Schools (Exhibits 1.2–1.6)", "zh-CN": "第1章：概率学派 vs 安全优先学派框架对比（图 1.2–1.6）"},
        "th_dim": {"en-UK": "Dimension", "zh-CN": "对比维度"},
        "th_prob": {"en-UK": "Probability-Based (Investments / Total Return)", "zh-CN": "概率学派（投资组合 / 总收益）"},
        "th_safe": {"en-UK": "Safety-First (Insurance / Liability Matching)", "zh-CN": "安全优先学派（保险 / 资产负债匹配）"},
        "sub_mult": {"en-UK": "{x}× annual spending", "zh-CN": "年支出的 {x} 倍"},
        "sub_price_mult": {"en-UK": "Price level: {m}× in {y} yrs", "zh-CN": "{y} 年后物价倍数为 {m}×"},
        "sub_spia_cost": {"en-UK": "Annuity cost: {c} ({x}×)", "zh-CN": "年金所需本金：{c}（{x}×）"},
        "sub_self_cost": {"en-UK": "Earmarked: {c}", "zh-CN": "专款锁定：{c}"},
    }
    for slug, ch_en, ch_zh, t_en, t_zh, d_en, d_zh in LAB_CARDS:
        s_u = slug.replace("-", "_")
        page_i18n[f"card_t_{s_u}"] = {"en-UK": t_en, "zh-CN": t_zh}
        page_i18n[f"card_ch_{s_u}"] = {"en-UK": ch_en, "zh-CN": ch_zh}
        page_i18n[f"card_d_{s_u}"] = {"en-UK": d_en, "zh-CN": d_zh}

    matrix_rows = [
        ("Monte Carlo 90% Success", "90% 成功率标准",
         "Acceptable baseline; relies on ability to adjust later", "可接受基准；依赖后期动态削减支出的弹性",
         "Rejected for essentials; 10% ruin risk is unacceptable for core needs", "基本生活开支不接受 10% 失败概率"),
        ("Objective Function", "优化目标函数",
         "Minimize depletion probability for unified lifestyle spending", "最小化统一生活预算的资产耗尽概率",
         "Maximize expected lifetime utility; separate essentials from discretionary", "最大化终身效用；严格区分刚性开支与弹性开支"),
        ("Goal Hierarchy (4 Ls)", "目标层级（4L 模型）",
         "Single pooled lifestyle budget; precautionary leftovers for contingencies", "单一汇总预算；靠剩余资金充当应急缓冲",
         "1. Longevity floor (SS/TIPS/SPIA) → 2. Liquidity reserves → 3. Lifestyle → 4. Legacy", "1.长寿底线（社保/TIPS/年金）→ 2.流动性储备 → 3.品质生活 → 4.遗产"),
        ("True vs. Technical Liquidity", "真实流动性 vs 配置流动性",
         "High allocation liquidity, but capital earmarked for spending cannot be freely spent", "账面均可调仓，但锁定用于未来支出的资金并无真实支配自由",
         "Risk pooling (mortality credits) lowers floor cost (~20× vs ~25–35×), freeing true liquidity", "长寿风险池降低刚性底线资金占用，反而释放更多可自由支配流动性"),
    ]

    page_js = f"""
    const MATRIX_ROWS = {dump_json_inline(matrix_rows)};

    function updateCh1() {{
      const assets = Math.max(0, parseMoney(document.getElementById("ch1Portfolio")));
      const spend = Math.max(0, parseMoney(document.getElementById("ch1Spend")));
      const swr = Math.max(0.5, parseFloat(document.getElementById("ch1Swr").value) || 4.0) / 100;
      const inf = Math.max(-5, parseFloat(document.getElementById("ch1Inf").value) || 3.0) / 100;
      const yrs = Math.max(1, Math.min(60, parseInt(document.getElementById("ch1InfYrs").value, 10) || 25));
      const spiaRate = Math.max(1, parseFloat(document.getElementById("ch1AnnuityPct").value) || 5.0) / 100;

      const w0Self = spend / swr;
      const w0Spia = spend / spiaRate;
      const realDollar = Math.pow(1 + inf, -yrs);
      const priceMult = Math.pow(1 + inf, yrs);
      const liqSelf = assets - w0Self;
      const liqSpia = assets - w0Spia;

      document.getElementById("ch1NestEgg").textContent = fmtExactMoney(w0Self);
      document.getElementById("ch1NestSub").textContent = t("sub_mult", {{ x: (1 / swr).toFixed(1) }});
      document.getElementById("ch1RealVal").textContent = "$" + realDollar.toFixed(3);
      document.getElementById("ch1PriceMult").textContent = t("sub_price_mult", {{ m: priceMult.toFixed(2), y: yrs }});
      document.getElementById("ch1LiqSelf").textContent = fmtExactMoney(liqSelf);
      document.getElementById("ch1LiqSelf").className = "kpi-val " + (liqSelf >= 0 ? "" : "neg");
      document.getElementById("ch1LiqSelfSub").textContent = t("sub_self_cost", {{ c: fmtCompactMoney(w0Self) }});
      document.getElementById("ch1LiqSpia").textContent = fmtExactMoney(liqSpia);
      document.getElementById("ch1LiqSpia").className = "kpi-val " + (liqSpia >= 0 ? "pos" : "neg");
      document.getElementById("ch1LiqSpiaSub").textContent = t("sub_spia_cost", {{ c: fmtCompactMoney(w0Spia), x: (1 / spiaRate).toFixed(1) }});

      // Render Matrix
      const tbody = document.getElementById("ch1MatrixBody");
      const isZh = currentLang === "zh-CN";
      tbody.innerHTML = MATRIX_ROWS.map(r => `
        <tr>
          <td style="white-space:normal;font-family:var(--font);font-weight:600;">${{isZh ? r[1] : r[0]}}</td>
          <td style="text-align:left;white-space:normal;font-family:var(--font);">${{isZh ? r[3] : r[2]}}</td>
          <td style="text-align:left;white-space:normal;font-family:var(--font);">${{isZh ? r[5] : r[4]}}</td>
        </tr>
      `).join("");

      drawCh1Chart({{ assets, w0Self, w0Spia, inf, yrs }});
    }}

    function drawCh1Chart(m) {{
      const canvas = document.getElementById("ch1Canvas");
      const sc = setupCanvas(canvas);
      if (!sc) return;
      const {{ ctx, w, h }} = sc;
      const C = getThemeColors();
      ctx.clearRect(0, 0, w, h);

      // Left half: Capital Earmarked vs True Liquidity stacked bars; Right half: $1 Real Purchasing Power decay
      const midX = w * 0.48;
      const padL = 58, padR = 24, padT = 22, padB = 30;
      const ch = h - padT - padB;

      // Left panel
      const maxCap = Math.max(m.assets, m.w0Self, m.w0Spia, 100000) * 1.1;
      const yMapCap = v => padT + ch - (v / maxCap) * ch;
      ctx.strokeStyle = C.grid; ctx.lineWidth = 1; ctx.fillStyle = C.muted; ctx.font = CANVAS_FONT; ctx.textAlign = "right";
      computeNiceLinearTicks(0, maxCap, 4).forEach(v => {{
        const y = yMapCap(v);
        ctx.beginPath(); ctx.moveTo(padL, y); ctx.lineTo(midX - 24, y); ctx.stroke();
        ctx.fillText(fmtCompactMoney(v), padL - 6, y + 4);
      }});

      const bars = [
        {{ lbl: currentLang === "zh-CN" ? "纯自筹组合" : "Self-Fund", ear: Math.min(m.assets, m.w0Self), free: Math.max(0, m.assets - m.w0Self) }},
        {{ lbl: currentLang === "zh-CN" ? "年金风险池" : "SPIA Pool", ear: Math.min(m.assets, m.w0Spia), free: Math.max(0, m.assets - m.w0Spia) }}
      ];
      const lw = midX - 24 - padL;
      const bw = Math.min(48, lw * 0.28);
      bars.forEach((b, idx) => {{
        const cx = padL + ((idx + 0.5) / 2) * lw;
        const y0 = yMapCap(0), yEar = yMapCap(b.ear), yTot = yMapCap(b.ear + b.free);
        ctx.fillStyle = C.port;
        ctx.fillRect(cx - bw / 2, yEar, bw, y0 - yEar);
        if (b.free > 0) {{
          ctx.fillStyle = C.success;
          ctx.fillRect(cx - bw / 2, yTot, bw, yEar - yTot);
        }}
        ctx.fillStyle = C.muted; ctx.textAlign = "center";
        ctx.fillText(b.lbl, cx, h - 9);
      }});

      // Right panel: Purchasing power curve
      const rx0 = midX + 34, rx1 = w - padR, rw = rx1 - rx0;
      const mapX = yr => rx0 + (yr / m.yrs) * rw;
      const mapYP = v => padT + ch - v * ch;
      ctx.textAlign = "right";
      [0, 0.25, 0.5, 0.75, 1.0].forEach(v => {{
        const y = mapYP(v);
        ctx.strokeStyle = C.grid;
        ctx.beginPath(); ctx.moveTo(rx0, y); ctx.lineTo(rx1, y); ctx.stroke();
        ctx.fillStyle = C.muted;
        ctx.fillText("$" + v.toFixed(2), rx0 - 6, y + 4);
      }});
      ctx.beginPath();
      ctx.strokeStyle = C.inflation; ctx.lineWidth = 2.4;
      for (let yr = 0; yr <= m.yrs; yr++) {{
        const px = mapX(yr), py = mapYP(Math.min(1.05, Math.pow(1 + m.inf, -yr)));
        if (yr === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
      }}
      ctx.stroke();
      ctx.fillStyle = C.muted; ctx.textAlign = "center";
      [0, Math.round(m.yrs / 2), m.yrs].forEach(yr => {{
        ctx.fillText((currentLang === "zh-CN" ? "第" + yr + "年" : "Yr " + yr), mapX(yr), h - 9);
      }});
    }}

    function onThemeOrLangChange() {{ updateCh1(); }}

    ["ch1Portfolio", "ch1Spend"].forEach(id => {{
      const el = document.getElementById(id);
      el.addEventListener("input", updateCh1);
      el.addEventListener("blur", () => formatMoneyEl(el, parseMoney(el)));
    }});
    ["ch1Swr", "ch1Inf", "ch1InfYrs", "ch1AnnuityPct"].forEach(id => {{
      document.getElementById(id).addEventListener("input", updateCh1);
    }});
    window.addEventListener("resize", () => requestAnimationFrame(updateCh1));

    initSharedControls();
    applyStaticI18n();
    updateCh1();
"""
    render_page(
        slug="",
        title_en="Retirement Spending Strategies (Pfau)",
        extra_css=EXTRA_CSS,
        body_html=body_html,
        embedded_data_js="",
        page_i18n=page_i18n,
        page_js=page_js,
        is_app_shell=False,
        show_csv=False,
    )


if __name__ == "__main__":
    build_hub()
