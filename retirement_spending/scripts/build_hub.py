#!/usr/bin/env python3
"""Build docs/retirement-spending/index.html — Suite Overview Hub & Chapter 1 Interactive Primer."""

from shared_shell import dump_json_inline, render_page

EXTRA_CSS = """
    html { scroll-behavior: smooth; }
    @media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } }
    #ch1-calculator { scroll-margin-top: 18px; }

    .hub-wrap { max-width: 1080px; margin: 0 auto; padding: 28px 22px 56px; }
    .hub-intro { margin-bottom: 24px; max-width: 72ch; }
    .hub-intro h2 { margin: 0 0 8px; font-size: 22px; font-weight: 650; letter-spacing: -0.02em; text-wrap: balance; }
    .hub-intro p { margin: 0; color: var(--text-soft); font-size: 13.5px; line-height: 1.52; text-wrap: pretty; }

    .hub-actions { display: flex; align-items: center; flex-wrap: wrap; gap: 10px 14px; margin-top: 14px; }
    .cta-calc-link {
      display: inline-flex; align-items: center; gap: 7px;
      padding: 8px 14px; min-height: 36px; border-radius: 6px;
      background: var(--accent); color: #ffffff;
      font-size: 13px; font-weight: 600; text-decoration: none;
      transition: opacity 0.14s, transform 0.12s;
    }
    html[data-theme="dark"] .cta-calc-link { color: #0c0d0f; }
    .cta-calc-link:hover { opacity: 0.92; }
    .cta-calc-link:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
    .hub-dir-note { font-size: 12.5px; color: var(--muted); }

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
    .lab-question { margin: 7px 0 4px; font-size: 13.5px; font-weight: 560; color: var(--text); line-height: 1.42; text-wrap: pretty; }
    .lab-desc { margin: 0; font-size: 12.5px; color: var(--muted); line-height: 1.46; text-wrap: pretty; }
    .lab-meta { display: flex; align-items: center; justify-content: space-between; font-size: 12px; color: var(--text-soft); border-top: 1px solid var(--border); padding-top: 9px; }

    .primer-grid {
      display: grid; grid-template-columns: 320px minmax(0, 1fr); gap: 1px;
      background: var(--border); border: 1px solid var(--border); border-radius: 8px; overflow: hidden; margin-bottom: 24px;
    }
    @media (max-width: 900px) { .primer-grid { grid-template-columns: 1fr; } }
    .primer-controls { background: var(--panel); padding: 18px; }
    .primer-outputs { background: var(--panel); padding: 18px 20px; min-width: 0; }
    .primer-outputs .kpis { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    @media (max-width: 640px) { .primer-outputs .kpis { grid-template-columns: 1fr; } }
    .kpi-val.kpi-prose {
      font-family: var(--font); font-size: 14.5px; font-weight: 620;
      letter-spacing: -0.01em; line-height: 1.38; white-space: normal; color: var(--text);
    }
    .primer-outputs .kpi-sub { white-space: normal; text-wrap: pretty; }

    .primer-charts {
      display: grid; grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 18px; padding-top: 18px;
    }
    @media (max-width: 760px) { .primer-charts { grid-template-columns: 1fr; gap: 20px; } }
    .primer-chart-box { min-width: 0; display: flex; flex-direction: column; }
    .primer-chart-box .chart-wrap { margin-top: auto; }
    .chart-head {
      display: flex; align-items: baseline; justify-content: space-between;
      flex-wrap: wrap; gap: 4px 10px; margin-bottom: 10px;
    }
    .chart-title { margin: 0; font-size: 13px; font-weight: 620; color: var(--text); text-wrap: balance; }
    .chart-head .legend-items { gap: 10px; font-size: 11.5px; color: var(--text-soft); }

    .matrix-panel {
      background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 16px 20px;
    }
    .matrix-panel th { white-space: normal; line-height: 1.35; }

    @media (max-width: 480px) {
      .hub-wrap { padding: 18px 12px 42px; }
      .primer-controls { padding: 14px; }
      .primer-outputs { padding: 14px; --body-px: 14px; --body-py: 14px; }
      .matrix-panel { padding: 14px; }
      .chapter-jump { max-width: 100%; }
    }
    @media (pointer: coarse) {
      .cta-calc-link { min-height: 42px; padding: 9px 15px; }
    }
"""

# (slug, ch_en, ch_zh, t_en, t_zh, q_en, q_zh, d_en, d_zh)
LAB_CARDS = [
    ("fixed-returns-longevity", "Ch. 2", "第2章",
     "Fixed Returns & Longevity Risk", "固定收益与长寿风险",
     "How long might my retirement last, and what can I spend if returns are steady?",
     "退休可能持续多少年？如果投资收益稳定，每年可以花多少钱？",
     "Compare steady-return spending schedules with single and couple survival odds.",
     "结合单人与夫妻生存概率曲线，测算稳定回报下的可持续支出与规划年限。"),
    ("sequence-of-returns-risk", "Ch. 3", "第3章",
     "Sequence-of-Returns Risk", "收益率顺序风险",
     "What happens if my worst investment years come first?",
     "如果最差的投资年份恰好出现在刚退休时，会发生什么？",
     "See how early downturns drain a portfolio under withdrawals even when average returns look fine.",
     "观察早期市场下跌叠加持续取款如何加速消耗本金，即便长期平均回报并不低。"),
    ("safe-withdrawal-rates", "Ch. 4", "第4章",
     "Safe Withdrawal Rates & Trinity Study", "安全提取率与 Trinity 研究",
     "Where does the 4% rule come from, and how often has a fixed budget survived?",
     "“4% 法则”从何而来？按通胀调整的固定预算在历史上有多稳妥？",
     "Test historical US retirements since 1871 and low-yield simulations across stock-bond mixes.",
     "跨越 1871 年以来的历史退休队列与低利率模拟，检验不同股债配比的成功率。"),
    ("valuations-and-savings", "Ch. 5A", "第5章上",
     "Valuations, Safe Savings & Drag", "市场估值、安全储蓄率与损耗",
     "How do high market prices, global history, and fees change a safe spending rate?",
     "偏高的市场估值、海外历史经验与投资费用，会如何改变安全提取率？",
     "Explore valuation-based forecasts, career savings rates, 20-country history, and fee drag.",
     "结合市场估值预测、工作期储蓄率、20 国历史数据以及费用与税负损耗进行评估。"),
    ("spending-smiles-glidepaths", "Ch. 5B", "第5章下",
     "Spending Smiles & Bond Tents", "支出微笑曲线与动态股债滑道",
     "Do retirees spend the same real amount every year, and can a bond tent help?",
     "退休后每年的真实开销固定不变吗？阶段性增配债券能否降低风险？",
     "Model age-related spending changes, legacy goals, lifetime mortality, and rising-equity paths.",
     "模拟随年龄变化的支出微笑曲线、遗产目标、寿命竞争风险与递增股票滑道。"),
    ("variable-spending", "Ch. 6", "第6章",
     "Variable Spending & PAY Rule™", "可变支出策略与 PAY 准则",
     "How much more can I start with if I adjust spending after good and bad years?",
     "如果愿意随市场好坏灵活调整开销，起步时能多花多少钱？",
     "Compare ten flexible withdrawal rules for income stability, upside, and remaining wealth.",
     "横向对比十种可变提取规则在支出稳定性、上行空间与剩余资产之间的权衡。"),
    ("bonds-and-buckets", "Ch. 7", "第7章",
     "Bond Ladders & Time Segmentation", "债券阶梯与时间分段策略",
     "Should I lock in upcoming years of spending with individual bonds instead of a fund?",
     "是否应该用单只到期国债锁定未来几年的开销，而不是依赖债券基金？",
     "Build year-by-year Treasury and inflation-protected bond ladders, and test bucket strategies.",
     "构建逐年到期的零息与抗通胀国债阶梯，并对比时间分段策略与总回报组合。"),
    ("funded-ratio-and-gamma", "Ch. 8–9", "第8–9章",
     "Funded Ratio, CARE & Advisor Gamma", "资金充足率、CARE 与规划 Gamma",
     "Are my total resources enough for essentials, and which income style fits me?",
     "我的家庭总资源足以覆盖基本开支吗？哪种退休收入风格更适合我？",
     "Measure your household funded ratio, score planning preferences, and estimate tax and claiming gains.",
     "测算家庭资产负债充足率，完成规划偏好评估，并估算社保与税务筹划的增益。"),
]


def build_hub():
    cards_html = []
    for slug, ch_en, ch_zh, t_en, t_zh, q_en, q_zh, d_en, d_zh in LAB_CARDS:
        su = slug.replace("-", "_")
        key_t = f"card_t_{su}"
        key_q = f"card_q_{su}"
        key_d = f"card_d_{su}"
        key_ch = f"card_ch_{su}"
        cards_html.append(f"""      <a class="lab-link" href="./{slug}/">
        <div>
          <div class="lab-top">
            <h3 class="lab-title" data-i18n="{key_t}">{t_en}</h3>
            <span class="lab-ch" data-i18n="{key_ch}">{ch_en}</span>
          </div>
          <p class="lab-question" data-i18n="{key_q}">{q_en}</p>
          <p class="lab-desc" data-i18n="{key_d}">{d_en}</p>
        </div>
        <div class="lab-meta">
          <span data-i18n="open_lab">Open interactive lab</span>
          <span aria-hidden="true">&rarr;</span>
        </div>
      </a>""")

    body_html = f"""  <main class="hub-wrap">
    <div class="hub-intro">
      <h2 data-i18n="hub_heading">How Much Can I Spend in Retirement? Quantitative Labs</h2>
      <p data-i18n="hub_sub">Eight self-contained interactive tools implementing the historical simulations, 10,000-run Monte Carlo engines, variable spending rules, bond ladders, and balance-sheet models across Chapters 1–9 of Wade D. Pfau's guide.</p>
      <div class="hub-actions">
        <a class="cta-calc-link" href="#ch1-calculator">
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M8 3v10M4 9l4 4 4-4"/></svg>
          <span data-i18n="cta_try_ch1">Try the Chapter 1 calculator</span>
        </a>
        <span class="hub-dir-note" data-i18n="cta_or_browse">or choose a chapter lab below</span>
      </div>
    </div>

    <div class="lab-grid">
{chr(10).join(cards_html)}
    </div>

    <section id="ch1-calculator" class="primer-grid" aria-label="Chapter 1 Liquidity and Inflation Calculator" data-i18n-aria-label="aria_ch1_calc">
      <div class="primer-controls">
        <div class="sec-head-static">
          <h3 class="sec-title" data-i18n="ch1_calc_title">Chapter 1: Nest Egg, Inflation &amp; True Liquidity</h3>
        </div>
        <div class="control-group">
          <label for="ch1Portfolio"><span data-i18n="lbl_total_assets">Total retirement savings</span></label>
          <div class="currency-field"><span class="currency-prefix">$</span><input type="text" id="ch1Portfolio" value="1,500,000" inputmode="numeric" /></div>
        </div>
        <div class="control-group">
          <label for="ch1Spend"><span data-i18n="lbl_target_spend">First-year annual spending</span></label>
          <div class="currency-field"><span class="currency-prefix">$</span><input type="text" id="ch1Spend" value="40,000" inputmode="numeric" /></div>
        </div>
        <div class="control-group">
          <label for="ch1Swr"><span data-i18n="lbl_swr_pct">Withdrawal rate (%/yr)</span></label>
          <input type="number" id="ch1Swr" value="4.0" min="1.5" max="10" step="0.1" />
        </div>
        <div class="control-group">
          <label for="ch1AnnuityPct"><span data-i18n="lbl_spia_rate">Income annuity payout rate (%/yr)</span></label>
          <input type="number" id="ch1AnnuityPct" value="5.0" min="3" max="12" step="0.1" />
        </div>
        <div class="control-group">
          <label for="ch1Inf"><span data-i18n="lbl_inf_pct">Annual inflation rate (%/yr)</span></label>
          <input type="number" id="ch1Inf" value="3.0" min="0" max="12" step="0.1" />
        </div>
        <div class="control-group">
          <label for="ch1InfYrs"><span data-i18n="lbl_inf_yrs">Time horizon (years)</span></label>
          <input type="number" id="ch1InfYrs" value="25" min="5" max="50" step="1" />
        </div>
      </div>

      <div class="primer-outputs">
        <div class="kpis kpis-flush-top">
          <div class="kpi">
            <div class="kpi-label" data-i18n="kpi_nest_egg">Savings needed to self-fund</div>
            <div class="kpi-val" id="ch1NestEgg">--</div>
            <div class="kpi-sub" id="ch1NestSub">--</div>
          </div>
          <div class="kpi">
            <div class="kpi-label" data-i18n="kpi_purch_power">Purchasing power of $1</div>
            <div class="kpi-val kpi-prose" id="ch1RealVal">--</div>
            <div class="kpi-sub" id="ch1PriceMult">--</div>
          </div>
          <div class="kpi">
            <div class="kpi-label" data-i18n="kpi_true_liq_self">Available after self-funding</div>
            <div class="kpi-val" id="ch1LiqSelf">--</div>
            <div class="kpi-sub" id="ch1LiqSelfSub">--</div>
          </div>
          <div class="kpi">
            <div class="kpi-label" data-i18n="kpi_true_liq_spia">Available with an income annuity</div>
            <div class="kpi-val pos" id="ch1LiqSpia">--</div>
            <div class="kpi-sub" id="ch1LiqSpiaSub">--</div>
          </div>
        </div>

        <div class="primer-charts">
          <div class="primer-chart-box">
            <div class="chart-head">
              <div class="chart-title" data-i18n="ch1_avail_heading">How much money stays available?</div>
              <div class="legend-items">
                <div class="legend-item"><span class="swatch" style="background:var(--port);height:8px;"></span><span data-i18n="leg_earmarked">Set aside</span></div>
                <div class="legend-item"><span class="swatch" style="background:var(--success);height:8px;"></span><span data-i18n="leg_true_liq">Available</span></div>
              </div>
            </div>
            <div class="chart-wrap">
              <canvas id="ch1AvailCanvas" height="220"></canvas>
              <div class="tooltip" id="ch1AvailTip"></div>
            </div>
          </div>

          <div class="primer-chart-box">
            <div class="chart-head">
              <div class="chart-title" data-i18n="ch1_power_heading">What will $1 buy over time?</div>
              <div class="legend-items">
                <div class="legend-item"><span class="swatch" style="background:var(--inflation);height:3px;"></span><span data-i18n="leg_inf_erosion">Today's prices</span></div>
              </div>
            </div>
            <div class="chart-wrap">
              <canvas id="ch1PowerCanvas" height="220"></canvas>
              <div class="tooltip" id="ch1PowerTip"></div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="matrix-panel">
      <div class="card-title" style="margin-bottom:8px;">
        <h3 class="sec-title" data-i18n="ch1_schools_title">Chapter 1: Probability-Based vs. Safety-First Frameworks</h3>
      </div>
      <div class="table-container" style="max-height:none;">
        <table>
          <thead>
            <tr>
              <th data-i18n="th_dim">Dimension</th>
              <th data-i18n="th_prob">Probability-Based (Investments / Total Return)</th>
              <th data-i18n="th_safe">Safety-First (Insurance / Liability Matching)</th>
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
            "en-UK": "How Much Can I Spend in Retirement? Quantitative Labs",
            "zh-CN": "《退休后我能花多少钱？》量化分析交互实验室",
        },
        "hub_sub": {
            "en-UK": "Eight self-contained interactive tools implementing the historical simulations, 10,000-run Monte Carlo engines, variable spending rules, bond ladders, and balance-sheet models across Chapters 1–9 of Wade D. Pfau's guide.",
            "zh-CN": "全套 8 个纯本地单文件交互实验室，完整复现 Wade D. Pfau 专著第 1–9 章的历史回测、万次蒙特卡洛模拟、动态支出规则、债券阶梯与家庭资产负债表模型。",
        },
        "cta_try_ch1": {"en-UK": "Try the Chapter 1 calculator", "zh-CN": "体验第 1 章快速测算器"},
        "cta_or_browse": {"en-UK": "or choose a chapter lab below", "zh-CN": "或直接选择下方章节实验室"},
        "open_lab": {"en-UK": "Open interactive lab", "zh-CN": "进入交互实验室"},
        "aria_ch1_calc": {"en-UK": "Chapter 1 Liquidity and Inflation Calculator", "zh-CN": "第1章流动性与通胀计算器"},
        "ch1_calc_title": {"en-UK": "Chapter 1: Nest Egg, Inflation & True Liquidity", "zh-CN": "第 1 章：目标本金、通胀侵蚀与真实流动性"},
        "lbl_total_assets": {"en-UK": "Total retirement savings", "zh-CN": "退休储蓄总额"},
        "lbl_target_spend": {"en-UK": "First-year annual spending", "zh-CN": "首年计划支出"},
        "lbl_swr_pct": {"en-UK": "Withdrawal rate (%/yr)", "zh-CN": "初始提取率 (%/年)"},
        "lbl_spia_rate": {"en-UK": "Income annuity payout rate (%/yr)", "zh-CN": "终身年金给付率 (%/年)"},
        "lbl_inf_pct": {"en-UK": "Annual inflation rate (%/yr)", "zh-CN": "年通胀率 (%/年)"},
        "lbl_inf_yrs": {"en-UK": "Time horizon (years)", "zh-CN": "时间跨度 (年)"},
        "kpi_nest_egg": {"en-UK": "Savings needed to self-fund", "zh-CN": "纯自筹所需本金"},
        "kpi_purch_power": {"en-UK": "Purchasing power of $1", "zh-CN": "$1 的实际购买力"},
        "kpi_true_liq_self": {"en-UK": "Available after self-funding", "zh-CN": "纯自筹后可支配资金"},
        "kpi_true_liq_spia": {"en-UK": "Available with an income annuity", "zh-CN": "配终身年金后可支配资金"},
        "ch1_avail_heading": {"en-UK": "How much money stays available?", "zh-CN": "有多少资金仍可自由支配？"},
        "ch1_power_heading": {"en-UK": "What will $1 buy over time?", "zh-CN": "$1 的购买力随时间如何变化？"},
        "leg_earmarked": {"en-UK": "Set aside", "zh-CN": "专款支应开销"},
        "leg_true_liq": {"en-UK": "Available", "zh-CN": "可自由支配"},
        "leg_inf_erosion": {"en-UK": "Today's prices", "zh-CN": "按今日物价折算"},
        "ch1_schools_title": {"en-UK": "Chapter 1: Probability-Based vs. Safety-First Frameworks", "zh-CN": "第 1 章：概率学派 vs 安全优先学派框架对比"},
        "th_dim": {"en-UK": "Dimension", "zh-CN": "对比维度"},
        "th_prob": {"en-UK": "Probability-Based (Investments / Total Return)", "zh-CN": "概率学派（投资组合 / 总收益）"},
        "th_safe": {"en-UK": "Safety-First (Insurance / Liability Matching)", "zh-CN": "安全优先学派（保险 / 资产负债匹配）"},
        "sub_nest": {"en-UK": "Covers {s}/yr at a {w} withdrawal rate ({x}× annual spending).", "zh-CN": "按 {w} 提取率满足 {s}/年支出（年支出的 {x} 倍）。"},
        "prose_real_power": {"en-UK": "In {y} {yw}, $1 will buy about {amt} worth of goods at today's prices.", "zh-CN": "{y}年后，$1 大约能买到相当于今天{amt}的商品。"},
        "sub_price_mult": {"en-UK": "Assumes {r} annual inflation (prices reach {m}× today's level).", "zh-CN": "假设年通胀率 {r}（物价升至今日的 {m} 倍）。"},
        "sub_liq_self_ok": {"en-UK": "After setting aside {c} for spending, {f} stays uncommitted.", "zh-CN": "扣除用于支出的专款 {c} 后，剩余 {f} 可自由支配。"},
        "sub_liq_self_gap": {"en-UK": "Self-funding needs {c}, leaving a {g} shortfall.", "zh-CN": "纯自筹需本金 {c}，当前资金尚有 {g} 缺口。"},
        "sub_liq_spia_ok": {"en-UK": "An annuity paying {r} costs {c} for {s}/yr, freeing {f}.", "zh-CN": "按 {r} 给付率购买年金仅需 {c} 即可锁定 {s}/年，可释放 {f}。"},
        "sub_liq_spia_gap": {"en-UK": "An annuity paying {r} costs {c}, leaving a {g} shortfall.", "zh-CN": "按 {r} 给付率购买年金需本金 {c}，当前资金尚有 {g} 缺口。"},
        "bar_self": {"en-UK": "Self-funded", "zh-CN": "纯自筹"},
        "bar_annuity": {"en-UK": "With annuity", "zh-CN": "配年金"},
        "lbl_today": {"en-UK": "Today", "zh-CN": "今天"},
    }
    for slug, ch_en, ch_zh, t_en, t_zh, q_en, q_zh, d_en, d_zh in LAB_CARDS:
        su = slug.replace("-", "_")
        page_i18n[f"card_t_{su}"] = {"en-UK": t_en, "zh-CN": t_zh}
        page_i18n[f"card_ch_{su}"] = {"en-UK": ch_en, "zh-CN": ch_zh}
        page_i18n[f"card_q_{su}"] = {"en-UK": q_en, "zh-CN": q_zh}
        page_i18n[f"card_d_{su}"] = {"en-UK": d_en, "zh-CN": d_zh}

    matrix_rows = [
        ("Monte Carlo 90% Success", "90% 成功率标准",
         "Acceptable baseline; relies on ability to adjust later", "可接受基准；依赖后期动态削减支出的弹性",
         "Rejected for essentials; 10% ruin risk is unacceptable for core needs", "基本生活开支不接受 10% 失败概率"),
        ("Objective Function", "优化目标函数",
         "Minimize depletion probability for unified lifestyle spending", "最小化统一生活预算的资产耗尽概率",
         "Maximize expected lifetime utility; separate essentials from discretionary", "最大化终身效用；严格区分刚性开支与弹性开支"),
        ("Goal Hierarchy (4 Ls)", "目标层级（4L 模型）",
         "Single pooled lifestyle budget; precautionary leftovers for contingencies", "单一汇总预算；靠剩余资金充当应急缓冲",
         "1. Longevity floor (Social Security / TIPS / annuity) → 2. Reserves → 3. Lifestyle → 4. Legacy", "1.长寿底线（社保/TIPS/年金）→ 2.储备金 → 3.品质生活 → 4.遗产"),
        ("True vs. Technical Liquidity", "真实流动性 vs 配置流动性",
         "High allocation liquidity, but capital earmarked for spending cannot be freely spent", "账面均可调仓，但锁定用于未来支出的资金并无真实支配自由",
         "Risk pooling (mortality credits) lowers floor cost (~20× vs ~25–35×), freeing true liquidity", "长寿风险池降低刚性底线资金占用，反而释放更多可自由支配流动性"),
    ]

    page_js = f"""
    const MATRIX_ROWS = {dump_json_inline(matrix_rows)};
    const state = {{ bars: null, powerPts: null }};

    function fmtRateStr(pct) {{
      const rounded = Math.round(pct * 10) / 10;
      return (Math.abs(rounded - Math.round(rounded)) < 0.05 ? String(Math.round(rounded)) : rounded.toFixed(1)) + "%";
    }}

    function fmtDollarFraction(val, isZh) {{
      if (val >= 0.995) return "$" + val.toFixed(2);
      const cents = Math.round(val * 100);
      if (cents < 1) return isZh ? "不足1美分" : "<1¢";
      return isZh ? (cents + "美分") : (cents + "¢");
    }}

    function updateCh1() {{
      const assets = Math.max(0, parseMoney(document.getElementById("ch1Portfolio")));
      const spend = Math.max(0, parseMoney(document.getElementById("ch1Spend")));
      const swrPct = Math.max(0.5, parseFloat(document.getElementById("ch1Swr").value) || 4.0);
      const infRaw = parseFloat(document.getElementById("ch1Inf").value);
      const infPct = isFinite(infRaw) ? Math.max(-5, Math.min(20, infRaw)) : 3.0;
      const yrs = Math.max(1, Math.min(60, parseInt(document.getElementById("ch1InfYrs").value, 10) || 25));
      const spiaPct = Math.max(1, parseFloat(document.getElementById("ch1AnnuityPct").value) || 5.0);

      const swr = swrPct / 100;
      const inf = infPct / 100;
      const spiaRate = spiaPct / 100;

      const w0Self = spend / swr;
      const w0Spia = spend / spiaRate;
      const realDollar = Math.pow(1 + inf, -yrs);
      const priceMult = Math.pow(1 + inf, yrs);
      const liqSelf = assets - w0Self;
      const liqSpia = assets - w0Spia;
      const isZh = currentLang === "zh-CN";

      document.getElementById("ch1NestEgg").textContent = fmtExactMoney(w0Self);
      document.getElementById("ch1NestSub").textContent = t("sub_nest", {{
        s: fmtExactMoney(spend), w: fmtRateStr(swrPct), x: (1 / swr).toFixed(1)
      }});

      document.getElementById("ch1RealVal").textContent = t("prose_real_power", {{
        y: yrs, yw: yrs === 1 ? "year" : "years", amt: fmtDollarFraction(realDollar, isZh)
      }});
      document.getElementById("ch1PriceMult").textContent = t("sub_price_mult", {{
        r: fmtRateStr(infPct), m: priceMult.toFixed(2)
      }});

      document.getElementById("ch1LiqSelf").textContent = fmtExactMoney(liqSelf);
      document.getElementById("ch1LiqSelf").className = "kpi-val " + (liqSelf >= 0 ? "" : "neg");
      document.getElementById("ch1LiqSelfSub").textContent = liqSelf >= 0
        ? t("sub_liq_self_ok", {{ c: fmtExactMoney(w0Self), f: fmtExactMoney(liqSelf) }})
        : t("sub_liq_self_gap", {{ c: fmtExactMoney(w0Self), g: fmtExactMoney(Math.abs(liqSelf)) }});

      document.getElementById("ch1LiqSpia").textContent = fmtExactMoney(liqSpia);
      document.getElementById("ch1LiqSpia").className = "kpi-val " + (liqSpia >= 0 ? "pos" : "neg");
      document.getElementById("ch1LiqSpiaSub").textContent = liqSpia >= 0
        ? t("sub_liq_spia_ok", {{ r: fmtRateStr(spiaPct), c: fmtExactMoney(w0Spia), s: fmtExactMoney(spend), f: fmtExactMoney(liqSpia) }})
        : t("sub_liq_spia_gap", {{ r: fmtRateStr(spiaPct), c: fmtExactMoney(w0Spia), g: fmtExactMoney(Math.abs(liqSpia)) }});

      const tbody = document.getElementById("ch1MatrixBody");
      tbody.innerHTML = MATRIX_ROWS.map(r => `
        <tr>
          <td style="white-space:normal;font-family:var(--font);font-weight:600;">${{isZh ? r[1] : r[0]}}</td>
          <td style="text-align:left;white-space:normal;font-family:var(--font);">${{isZh ? r[3] : r[2]}}</td>
          <td style="text-align:left;white-space:normal;font-family:var(--font);">${{isZh ? r[5] : r[4]}}</td>
        </tr>
      `).join("");

      drawAvailChart({{ assets, w0Self, w0Spia }});
      drawPowerChart({{ inf, yrs, infPct }});
    }}

    function drawAvailChart(m) {{
      const canvas = document.getElementById("ch1AvailCanvas");
      const sc = setupCanvas(canvas);
      if (!sc) return;
      const {{ ctx, w, h }} = sc;
      const C = getThemeColors();
      ctx.clearRect(0, 0, w, h);

      const padL = 54, padR = 14, padT = 18, padB = 30;
      const cw = w - padL - padR, ch = h - padT - padB;
      const maxCap = Math.max(m.assets, m.w0Self, m.w0Spia, 100000) * 1.12;
      const yMap = v => padT + ch - (v / maxCap) * ch;

      ctx.strokeStyle = C.grid; ctx.lineWidth = 1; ctx.fillStyle = C.muted; ctx.font = CANVAS_FONT; ctx.textAlign = "right";
      computeNiceLinearTicks(0, maxCap, 4).forEach(v => {{
        const y = yMap(v);
        ctx.beginPath(); ctx.moveTo(padL, y); ctx.lineTo(w - padR, y); ctx.stroke();
        ctx.fillText(fmtCompactMoney(v), padL - 6, y + 4);
      }});

      const bars = [
        {{ lbl: t("bar_self"), need: m.w0Self, ear: Math.min(m.assets, m.w0Self), free: Math.max(0, m.assets - m.w0Self) }},
        {{ lbl: t("bar_annuity"), need: m.w0Spia, ear: Math.min(m.assets, m.w0Spia), free: Math.max(0, m.assets - m.w0Spia) }}
      ];
      const bw = Math.min(64, cw * 0.26);
      const hitBars = [];
      bars.forEach((b, idx) => {{
        const cx = padL + ((idx + 0.5) / 2) * cw;
        const y0 = yMap(0), yEar = yMap(b.ear), yTot = yMap(b.ear + b.free);
        ctx.fillStyle = C.port;
        ctx.fillRect(cx - bw / 2, yEar, bw, y0 - yEar);
        if (b.free > 0) {{
          ctx.fillStyle = C.success;
          ctx.fillRect(cx - bw / 2, yTot, bw, yEar - yTot);
        }}
        if (b.need > m.assets) {{
          const yNeed = yMap(b.need);
          ctx.save();
          ctx.setLineDash([4, 3]);
          ctx.strokeStyle = C.danger;
          ctx.lineWidth = 1.6;
          ctx.strokeRect(cx - bw / 2, yNeed, bw, yEar - yNeed);
          ctx.restore();
        }}
        ctx.fillStyle = C.text; ctx.textAlign = "center"; ctx.font = CANVAS_LABEL_FONT;
        const topVal = b.free > 0 ? b.free : (m.assets - b.need);
        ctx.fillText(fmtCompactMoney(topVal), cx, Math.max(12, Math.min(yTot, yMap(b.need)) - 6));
        ctx.fillStyle = C.muted; ctx.font = CANVAS_FONT;
        ctx.fillText(b.lbl, cx, h - 10);
        hitBars.push({{ ...b, x0: cx - bw / 2, x1: cx + bw / 2, cx }});
      }});
      state.bars = hitBars;
    }}

    function drawPowerChart(m) {{
      const canvas = document.getElementById("ch1PowerCanvas");
      const sc = setupCanvas(canvas);
      if (!sc) return;
      const {{ ctx, w, h }} = sc;
      const C = getThemeColors();
      const isZh = currentLang === "zh-CN";
      ctx.clearRect(0, 0, w, h);

      const padL = 46, padR = 16, padT = 18, padB = 30;
      const cw = w - padL - padR, ch = h - padT - padB;
      let maxVal = 1.0;
      for (let yr = 0; yr <= m.yrs; yr++) maxVal = Math.max(maxVal, Math.pow(1 + m.inf, -yr));
      maxVal = Math.max(1.0, Math.ceil(maxVal * 4) / 4);

      const mapX = yr => padL + (yr / m.yrs) * cw;
      const mapY = v => padT + ch - (v / maxVal) * ch;

      ctx.textAlign = "right"; ctx.font = CANVAS_FONT;
      [0, 0.25, 0.5, 0.75, 1.0].concat(maxVal > 1.05 ? [maxVal] : []).forEach(v => {{
        const y = mapY(v);
        ctx.strokeStyle = C.grid; ctx.lineWidth = 1;
        ctx.beginPath(); ctx.moveTo(padL, y); ctx.lineTo(w - padR, y); ctx.stroke();
        ctx.fillStyle = C.muted;
        ctx.fillText("$" + v.toFixed(2), padL - 6, y + 4);
      }});

      const pts = [];
      ctx.beginPath();
      ctx.strokeStyle = C.inflation; ctx.lineWidth = 2.6;
      for (let yr = 0; yr <= m.yrs; yr++) {{
        const v = Math.pow(1 + m.inf, -yr);
        const px = mapX(yr), py = mapY(v);
        pts.push({{ yr, v, px, py }});
        if (yr === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
      }}
      ctx.stroke();

      const lastPt = pts[pts.length - 1];
      ctx.beginPath(); ctx.arc(lastPt.px, lastPt.py, 4.5, 0, Math.PI * 2);
      ctx.fillStyle = C.inflation; ctx.fill();
      ctx.fillStyle = C.text; ctx.textAlign = "right"; ctx.font = CANVAS_LABEL_FONT;
      ctx.fillText(fmtDollarFraction(lastPt.v, isZh), lastPt.px - 2, Math.max(14, lastPt.py - 8));

      ctx.fillStyle = C.muted; ctx.textAlign = "center"; ctx.font = CANVAS_FONT;
      const midYr = Math.round(m.yrs / 2);
      ctx.fillText(t("lbl_today"), mapX(0) + 12, h - 10);
      if (m.yrs >= 6) ctx.fillText(isZh ? (midYr + "年") : ("Yr " + midYr), mapX(midYr), h - 10);
      ctx.fillText(isZh ? (m.yrs + "年") : ("Yr " + m.yrs), mapX(m.yrs) - 10, h - 10);
      state.powerPts = pts;
    }}

    attachCanvasHover(document.getElementById("ch1AvailCanvas"), document.getElementById("ch1AvailTip"), (e, canvas, tip) => {{
      if (!e || !state.bars) return;
      const rect = canvas.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const bar = Math.abs(mx - state.bars[0].cx) <= Math.abs(mx - state.bars[1].cx) ? state.bars[0] : state.bars[1];
      tip.innerHTML = `<strong>${{bar.lbl}}</strong>` +
        `<div class="tip-row"><span>${{t("leg_earmarked")}}</span><span>${{fmtExactMoney(bar.need)}}</span></div>` +
        `<div class="tip-row"><span>${{t("leg_true_liq")}}</span><span>${{fmtExactMoney(bar.free)}}</span></div>`;
      placeTooltip(tip, canvas, e.clientX, e.clientY);
    }});

    attachCanvasHover(document.getElementById("ch1PowerCanvas"), document.getElementById("ch1PowerTip"), (e, canvas, tip) => {{
      if (!e || !state.powerPts || !state.powerPts.length) return;
      const rect = canvas.getBoundingClientRect();
      const padL = 46, padR = 16, cw = rect.width - padL - padR;
      const ratio = Math.max(0, Math.min(1, (e.clientX - rect.left - padL) / Math.max(1, cw)));
      const idx = Math.round(ratio * (state.powerPts.length - 1));
      const pt = state.powerPts[idx];
      const isZh = currentLang === "zh-CN";
      tip.innerHTML = `<strong>${{pt.yr === 0 ? t("lbl_today") : (isZh ? ("第 " + pt.yr + " 年") : ("Year " + pt.yr))}}</strong>` +
        `<div class="tip-row"><span>${{t("kpi_purch_power")}}</span><span>${{fmtDollarFraction(pt.v, isZh)}} ($${{pt.v.toFixed(3)}})</span></div>`;
      placeTooltip(tip, canvas, e.clientX, e.clientY);
    }});

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
