# Historical Annual Total Return Datasets for Portfolio Backtesting

All values in the CSV files are expressed as **annual percentage total returns** (e.g., `17.88` means `+17.88%`, `-13.0` means `-13.00%`), inclusive of reinvested dividends and bond coupons, measured in **USD**.

---

## 1. Files Overview

| File | Period | Years | Primary Use Case |
| :--- | :--- | :---: | :--- |
| `backtest_1988_2025_all_country.csv` | **1988–2025** | 38 | **All-Country Modern Era**: S&P 500, Bloomberg US Aggregate Bond, MSCI ACWI (Developed + Emerging), MSCI World, MSCI World ex-USA, MSCI Emerging Markets, Bloomberg Global Aggregate Bond (from 1990), and NYU Stern series. |
| `backtest_1976_2025_world.csv` | **1976–2025** | 50 | **Modern Broad Bond + Developed World Era**: S&P 500, Bloomberg US Aggregate Bond, MSCI World (23 Developed Markets), MSCI World ex-USA, Bloomberg Global Aggregate Bond (from 1990), and NYU Stern series. |
| `nyu_stern_1928_2025_full.csv` | **1928–2025** | 98 | **Full NYU Stern (Aswath Damodaran) Reference**: Nominal and Real (inflation-adjusted) annual returns for US Large Cap, Small Cap, 3M T-Bills, 10Y T-Bonds, Baa Corporate Bonds, Real Estate, Gold, and US CPI Inflation. |

---

## 2. Column Definitions & Sources

### Equity & Broad Bond Index Columns
* **`SP500_Official_TR_pct`** *(1926–2025)*: Official **S&P 500 Total Return Index** (reinvested monthly/daily dividends). Sourced from S&P Dow Jones Indices / Dimensional Matrix Book (1926–2023) and S&P / Callan institutional benchmark reports (2024–2025).
* **`Bloomberg_US_Agg_Bond_pct`** *(1976–2025)*: **Bloomberg US Aggregate Bond Index** (`LBUSTRUU`, USD Total Return). Broad US investment-grade Treasuries, agencies, corporate bonds, MBS, and ABS. Inception: January 1, 1976.
* **`MSCI_ACWI_Gross_USD_pct`** *(1988–2025)*: **MSCI All Country World Index** (Gross Dividends Reinvested, USD). Covers 23 Developed + 24 Emerging Markets (~85% of global investable equities). Launched May 1990; officially backfilled by MSCI to January 1, 1988.
* **`MSCI_World_Gross_USD_pct`** *(1970–2025)*: **MSCI World Index** (Gross Dividends Reinvested, USD). Covers 23 Developed Markets (including the US, which represents ~60–72% of index cap in recent decades).
* **`MSCI_World_ex_USA_Gross_USD_pct`** *(1970–2025)*: **MSCI World ex USA Index** (Gross Dividends Reinvested, USD). Covers 22 Developed Markets excluding the US—ideal when pairing directly with S&P 500 to avoid double-counting US equities.
* **`MSCI_EM_Gross_USD_pct`** *(1988–2025)*: **MSCI Emerging Markets Index** (Gross Dividends Reinvested, USD). Inception: January 1, 1988.
* **`Bloomberg_Global_Agg_USD_Hedged_pct`** *(1990–2025; blank for pre-1990)*: **Bloomberg Global Aggregate Bond Index (Hedged to USD)** (`LEGATRUH`). Flagship multi-currency global investment-grade bond benchmark (sovereign, government-related, corporate, and securitized debt across developed and emerging markets) hedged back to USD via 1-month FX forwards. Officially launched December 1998 and backfilled by Bloomberg to **January 1, 1990** (no index history exists prior to 1990).
* **`Bloomberg_Global_Agg_ex_USD_Hedged_pct`** *(1990–2025; blank for pre-1990)*: **Bloomberg Global Aggregate ex-USD Bond Index (Hedged to USD)** (`LG38TRUH`). Non-USD global investment-grade bonds hedged to USD (the institutional counterpart to Vanguard `BNDX`)—ideal when pairing with Bloomberg US Aggregate Bond to avoid double-counting USD bonds.

### NYU Stern (Aswath Damodaran) Columns (`histretSP.xls`, 1928–2025)
* **`NYU_SP500_pct`**: S&P 500 including year-end dividend yield approximation (`(P_t - P_{t-1} + D_t) / P_{t-1}`). Differs slightly (~0.1–0.3%/yr) from `SP500_Official_TR_pct` due to intra-year dividend reinvestment timing.
* **`NYU_US_Small_Cap_pct`**: US Small Cap stocks (bottom decile of NYSE/US market cap).
* **`NYU_US_3M_TBill_pct`**: 3-Month US Treasury Bills (average annual rate / cash return).
* **`NYU_US_10Y_TBond_pct`**: Constant-maturity 10-Year US Treasury Bond total return (coupon + price change).
* **`NYU_US_Baa_Corp_Bond_pct`**: Moody's Baa-rated US Corporate Bond total return.
* **`NYU_US_Real_Estate_pct`**: Case-Shiller US Residential Real Estate price index return.
* **`NYU_Gold_pct`**: Gold spot price annual return in USD.
* **`NYU_US_CPI_Inflation_pct`**: US Consumer Price Index (CPI-U) annual inflation rate (December-to-December).
* **`*_Real_pct`** *(in `nyu_stern_1928_2025_full.csv`)*: Exact Fisher-adjusted real return `((1 + r_nominal) / (1 + cpi) - 1)`.

---

## 3. Handling Pre-1990 Years for Global Aggregate Bond

Because Bloomberg's Global Aggregate Bond Index begins on **January 1, 1990**, rows for `1988–1989` (in the 1988–2025 file) and `1976–1989` (in the 1976–2025 file) are intentionally left blank (`""`) rather than fabricated. For backtests starting in 1988 or 1976 that include a Global Bond sleeve, standard institutional practice (e.g., Dimensional Fund Advisors' Core Allocations) is one of:
1. Start the Global Bond allocation test in **1990–2025** (36 years), or
2. Proxy pre-1990 Global Aggregate Hedged USD returns (`1976–1989`) using `Bloomberg_US_Agg_Bond_pct` (since FX-hedged global sovereign/aggregate bond returns converge closely to domestic USD interest-rate carry plus global term premium).
