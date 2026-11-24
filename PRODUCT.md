# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

- **Primary user (owner):** The site author making personal retirement and portfolio planning decisions, who wants fast, trustworthy scenario analysis and side-by-side parameter testing.
- **Secondary audience (public readers):** Individual investors and family/friends evaluating retirement or portfolio strategies in either English or Chinese, who need self-explanatory, reliable tools without sign-up friction.

## Product Purpose

Provide interactive, transparent research tools—currently centered on historical retirement portfolio simulation—that let users stress-test asset allocation, withdrawal rates, and bad-year spending adjustments against real market and inflation history. Success means a user can test assumptions quickly, compare alternatives fairly without simulation noise, and trust the calculations and underlying numbers without exposing personal financial inputs to a server.

## Positioning

- **Paired Monte Carlo parameter sweeps:** Compares configurations (equity allocation, initial expense rate, bad-year expense floor) across identical 1,000-run market year sequences so differences reflect strategy rather than sampling noise.
- **Private, offline-capable single-file tools:** 100% client-side execution with zero tracking, no accounts, and no external runtime dependencies—users can save or run the page locally without sending financial data anywhere.
- **Equal-footing bilingual experience:** Full English (`en-UK`) and Chinese (`zh-CN`) support across the site, sharing persisted language preference seamlessly rather than treating either language as a secondary translation.

## Operating Context

- Published statically via GitHub Pages from `docs/` to `https://research.cxfamily.eu/` (`docs/CNAME`, `docs/.nojekyll`), with no build pipeline required.
- Current surfaces:
  - `docs/index.html` — directory landing page linking to published tools.
  - `docs/retirement-simulation/index.html` — interactive Retirement Simulation SPA with four views: Sequential historical backtest, 1,000-run Random Monte Carlo, Compare parameter sweeps, and Market & CPI Data inspection/export.
- Settings and language preferences persist locally in browser `localStorage` (`site_lang_v1`, `retirement_sim_settings_v1`), and results export directly to CSV.

## Capabilities and Constraints

- **Single-file self-contained architecture:** Each web tool under `docs/` is a standalone HTML file with embedded historical data (`RAW_DATA`, 1928–2025) and zero external JS, CSS, font, or API fetches.
- **Bilingual i18n contract:** Every UI string across both pages is mapped in a `key -> { "en-UK": "...", "zh-CN": "..." }` dictionary and kept 100% synchronized between English and Chinese.
- **Statistical integrity:** Random and Compare expense metrics distinguish surviving-at-step trajectories from full-horizon survivor totals; historical gaps (e.g., pre-1990 Global Aggregate Bond rows in source CSVs) are kept blank rather than fabricated.
- **Undecided product facts:**
  - Whether additional research tools or written notes beyond retirement simulation will be added to `docs/index.html` is currently open.
  - No formal accessibility compliance standard (e.g., WCAG AA/AAA certification target) has been established beyond general readability and usability.
  - Note: Repository root `README.md` currently documents an unrelated Co-Scientist CLI skill workflow rather than the `docs/` web product.

## Brand Commitments

- **Site name:** `Research` (English) / `研究与工具` (Chinese).
- **Voice and tone:** Neutral, analytical, and strictly non-advisory—present historical data, formulas, and simulation mechanics plainly without making financial-advice claims or promotional promises.

## Evidence on Hand

- `data/nyu_stern_1928_2025_full.csv` — NYU Stern (Aswath Damodaran) 1928–2025 nominal and real US equity, small cap, T-Bill, 10Y T-Bond, Baa corporate bond, real estate, gold, and US CPI series (98 annual rows).
- `data/backtest_1976_2025_world.csv` — 1976–2025 developed world equity and broad bond total return series (50 annual rows).
- `data/backtest_1988_2025_all_country.csv` — 1988–2025 all-country equity (S&P 500, MSCI ACWI, MSCI World, MSCI World ex-USA, MSCI EM) and US/Global Aggregate Bond series (38 annual rows).
- `data/DATA_DICTIONARY.md` — Column definitions, index inception dates, and source attributions (including explicit handling of pre-1990 Global Aggregate Bond blanks).
- `docs/retirement-simulation/index.html` — Embeds the 1928–2025 dataset directly in `RAW_DATA`.
- **Absences not to fabricate:** No user testimonials, press mentions, institutional endorsements, live market feeds, or third-party benchmarks exist; do not invent any.

## Product Principles

1. **Owner-grade utility, public-grade clarity:** Optimize for real analytical decisions first, while keeping controls, metrics, and caveats clear enough for any public reader to understand without guesswork.
2. **Apples-to-apples transparency:** Make comparison mechanics fair (e.g., paired random sequences) and keep underlying historical data and methodology inspectable and exportable rather than hidden behind black-box outputs.
3. **Zero-friction privacy by construction:** Keep tools 100% client-side, offline-capable, and free of accounts, trackers, or external runtime dependencies.
4. **First-class bilingual parity:** Treat English (`en-UK`) and Chinese (`zh-CN`) as co-equal experiences for every label, chart, export, and explanation.
5. **Analytical neutrality over persuasion:** Communicate with calm precision and never frame historical simulations as personalized financial advice or guaranteed future outcomes.
