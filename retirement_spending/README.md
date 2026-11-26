# Interactive Quantitative Suite — *How Much Can I Spend in Retirement?* (Chapters 1–9)

Self-contained, offline-capable HTML + JavaScript interactive research labs implementing the core quantitative models, historical cohort analyses, Monte Carlo simulations, bond ladders, and financial planning frameworks from Wade D. Pfau's *How Much Can I Spend in Retirement?: A Guide to Investment-Based Retirement Income Strategies*.

All 9 generated static pages live under [`docs/retirement-spending/`](../docs/retirement-spending/) and are linked from [`docs/index.html`](../docs/index.html). Each HTML file embeds all required datasets, stylesheets, and simulation engines directly inline — zero runtime CDN calls, external scripts, or `fetch()` requests — so every lab runs identically via GitHub Pages (`https://`) or directly via local `file://`.

## Generated Interactive Labs

| Page | Chapter(s) | Output File | Core Quantitative Models |
| :--- | :--- | :--- | :--- |
| **Suite Hub & Overview** | Ch. 1–9 | `docs/retirement-spending/index.html` | Quick Sustainable Spending Snapshot, Ch. 1 overview, direct cards to all 8 Labs |
| **Lab 1: Fixed Returns & Longevity** | Ch. 2 | `docs/retirement-spending/fixed-returns-longevity/index.html` | Deterministic `PMT`/`NPER`/`RATE` amortisation, SOA 2012 IAM + Scale G2 & SSA survival curves (Male/Female/Couple), stochastic longevity Monte Carlo |
| **Lab 2: Sequence-of-Returns Risk** | Ch. 3, 3A | `docs/retirement-spending/sequence-of-returns-risk/index.html` | Mirror-return reversal, bear-market timing shock, spending-weighted IRR, Ch. 3A AR(1) + 3×3 Cholesky low-yield Monte Carlo |
| **Lab 3: Historical Safe Withdrawal Rates** | Ch. 4 | `docs/retirement-spending/safe-withdrawal-rates/index.html` | Closed-form rolling cohort `MWR` across NYU (1928–2025) & Shiller (1871–2025), 50/50 Bengen `SAFEMAX`, fee/tax/rebalancing/international diversification attribution |
| **Lab 4: Valuations & Savings-Rate Framing** | Ch. 5 (Part I) | `docs/retirement-spending/valuations-and-savings/index.html` | CAPE (`ln(PE10)`) + 10Y yield OLS MWR forecasting, `4%` rule vs CAPE-adjusted rule, 5-asset Markowitz efficient frontier QP (`Ex. 5.5`), accumulation savings-rate `SAFESAVINGS` |
| **Lab 5: Spending Smiles & Bond Tents** | Ch. 5 (Part II) | `docs/retirement-spending/spending-smiles-glidepaths/index.html` | Blanchett HRS Spending Smile & Basu Age-Banding, J.P. Morgan household profiles, legacy preservation `MWR`, competing mortality ruin, rising equity glidepath (`Ex. 5.29`) |
| **Lab 6: Variable Spending & PAY Rule™** | Ch. 6 | `docs/retirement-spending/variable-spending/index.html` | All 10 Chapter 6 dynamic spending rules (`Ex. 6.16–6.24`), Zolt 45-yr nominal glidepath (`Ex. 6.13`), Downside Spending Volatility (`DSV`), PAY Rule™ bisection calibrator |
| **Lab 7: Bond Ladders & Time Segmentation** | Ch. 7 | `docs/retirement-spending/bonds-and-buckets/index.html` | WSJ Jan 3, 2017 Forward STRIPS & Backward-Induction TIPS ladders (`Ex. 7.11–7.12`), live FRED 2003–2026 Treasury/TIPS curves, duration/convexity/pull-to-par, `Ex. 7.13` crossover & 7-strategy bucket MC |
| **Lab 8: Funded Ratio, CARE & Advisor Gamma** | Ch. 1, 8, 9 | `docs/retirement-spending/funded-ratio-and-gamma/index.html` | TIPS-discounted Household Economic Balance Sheet & Funded Ratio, 13-Factor CARE Diagnostic scorecard, Blanchett & Kaplan Morningstar Gamma & Vanguard Advisor Alpha |

## Embedded Datasets (`data/`)

See [`data/DATA_DICTIONARY.md`](../data/DATA_DICTIONARY.md) for full column schemas, sources, and methodological notes:
- `data/nyu_stern_1928_2025_full.csv` (1928–2025 US stocks, Treasuries, corporate bonds, bills, CPI)
- `data/backtest_1976_2025_world.csv` & `data/backtest_1988_2025_all_country.csv`
- `data/shiller_us_1871_2025_annual.csv` (1871–2025 S&P, 10Y Treasury TR, CPI, CAPE/PE10)
- `data/us_treasury_tips_yields.csv` (FRED Treasury & TIPS curves 2003–2026, incl. `2017-01-03` baseline and `2026-11-24`)
- `data/pfau_2017_strips_tips_quotes.csv` (WSJ Jan 3, 2017 30-year STRIPS & TIPS quotes)
- `data/mortality_and_rmd_tables.csv` (SSA Period, SOA 2012 IAM Basic/Period + Scale G2, IRS Uniform Lifetime RMD divisors)
- `data/dms_global_swr_benchmarks.csv` (22 international Dimson-Marsh-Staunton `Ex. 5.2` safe withdrawal rate benchmarks)

## Regenerating & Testing

```bash
# Refresh/recreate derived CSV datasets in data/ (if rebuilding from upstream sources)
python3 retirement_spending/scripts/build_datasets.py

# Regenerate all 9 static HTML pages under docs/retirement-spending/
python3 retirement_spending/scripts/build_all_pages.py

# Run JS syntax, quantitative parity, i18n completeness, and offline self-containment verification
python3 retirement_spending/scripts/verify_suite.py
```

All existing functionality under [`docs/retirement-simulation/`](../docs/retirement-simulation/) remains separate and untouched.
