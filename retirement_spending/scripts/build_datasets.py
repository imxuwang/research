#!/usr/bin/env python3
"""Fetch, build, and verify historical, yield-curve, and actuarial datasets in data/."""

import csv
import datetime
import io
import math
import os
import re
import subprocess
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(ROOT, "data")
CACHE_DIR = os.path.join(os.path.dirname(__file__), "_cache")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)


def curl_fetch(url: str, cache_name: str, max_age_hours: int = 24) -> bytes:
    cache_path = os.path.join(CACHE_DIR, cache_name)
    if os.path.exists(cache_path):
        age_sec = datetime.datetime.now().timestamp() - os.path.getmtime(cache_path)
        if age_sec < max_age_hours * 3600 and os.path.getsize(cache_path) > 100:
            with open(cache_path, "rb") as f:
                return f.read()
    cmd = ["curl", "-4", "-fsSL", "--retry", "3", "--retry-delay", "1", "--max-time", "20"]
    if "mort.soa.org" in url or "web.archive.org" in url:
        cmd.extend(["-A", "Mozilla/5.0"])
    cmd.append(url)
    raw = subprocess.check_output(cmd)
    with open(cache_path, "wb") as f:
        f.write(raw)
    return raw


def load_xlsx_sheet_rows(xlsx_path: str, sheet_xml: str = "xl/worksheets/sheet5.xml"):
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with zipfile.ZipFile(xlsx_path, "r") as z:
        strings = []
        if "xl/sharedStrings.xml" in z.namelist():
            ss = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in ss.findall("m:si", ns):
                strings.append("".join(t.text or "" for t in si.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t")))
        root = ET.fromstring(z.read(sheet_xml))
        out = []
        for row in root.findall(".//m:row", ns):
            vals = {}
            for c in row.findall("m:c", ns):
                ref = c.attrib.get("r", "")
                m = re.match(r"([A-Z]+)", ref)
                if not m:
                    continue
                col = m.group(1)
                t = c.attrib.get("t")
                v_el = c.find("m:v", ns)
                if v_el is None or v_el.text is None:
                    continue
                val = v_el.text
                if t == "s":
                    val = strings[int(val)]
                vals[col] = val
            if vals:
                out.append(vals)
        return out


def parse_fred_csv(sid: str, cosd: str = "") -> dict[str, float]:
    extra = f"&cosd={cosd}" if cosd else ""
    raw = curl_fetch(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}{extra}", f"fred_{sid}.csv").decode("utf-8")
    out = {}
    for line in raw.splitlines()[1:]:
        if "," not in line:
            continue
        d, v = line.split(",", 1)
        v = v.strip()
        if v and v != ".":
            try:
                out[d.strip()] = float(v)
            except ValueError:
                pass
    return out


def build_shiller_dataset():
    xls_url = "https://img1.wsimg.com/blobby/go/e5e77e0b-59d1-44d9-ab25-4763ac982e53/downloads/ie_data.xls"
    xls_bytes = curl_fetch(xls_url, "shiller_ie_data.xls")
    xls_path = os.path.join(CACHE_DIR, "shiller_ie_data.xls")
    xlsx_path = os.path.join(CACHE_DIR, "shiller_ie_data.xlsx")
    if not os.path.exists(xlsx_path) or os.path.getmtime(xlsx_path) < os.path.getmtime(xls_path):
        subprocess.check_call(
            ["libreoffice", "--headless", "--convert-to", "xlsx", "--outdir", CACHE_DIR, xls_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    sheet_rows = load_xlsx_sheet_rows(xlsx_path, "xl/worksheets/sheet5.xml")
    # Parse monthly Shiller records: key = (year, month)
    monthly = {}
    for vals in sheet_rows:
        dt = vals.get("A", "").strip()
        m = re.match(r"^(\d{4})\.(\d{1,2})$", dt)
        if not m:
            continue
        yr = int(m.group(1))
        # Note: in Shiller xls, 2023.10 becomes string "2023.1" because float! Check column F (Date Fraction)
        frac_str = vals.get("F", "")
        if frac_str:
            try:
                frac = float(frac_str)
                yr = int(math.floor(frac + 1e-6))
                mo = int(round((frac - yr - 1.0 / 24.0) * 12)) + 1
                if mo < 1:
                    mo = 1
                if mo > 12:
                    mo = 12
            except ValueError:
                mo = int(m.group(2))
        else:
            mo = int(m.group(2))

        def fget(col):
            v = vals.get(col)
            if v is None or v in ("NA", "", "."):
                return None
            try:
                return float(v)
            except ValueError:
                return None

        monthly[(yr, mo)] = {
            "P": fget("B"),
            "D": fget("C"),
            "E": fget("D"),
            "CPI": fget("E"),
            "GS10": fget("G"),
            "RealP": fget("H"),
            "RealTR_P": fget("J"),
            "PE10": fget("M"),
            "RealBondTR_Idx": fget("S"),
        }

    # Load NYU Stern 1928-2025 and FRED CPI/GS10/TB3MS and datasets/s-and-p-500 for 2024-2026 prices
    nyu = {}
    with open(os.path.join(DATA_DIR, "nyu_stern_1928_2025_full.csv"), "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            nyu[int(row["Year"])] = {k: float(v) for k, v in row.items() if k != "Year" and v != ""}

    sp_gh_raw = curl_fetch(
        "https://raw.githubusercontent.com/datasets/s-and-p-500/main/data/data.csv",
        "datasets_sp500.csv",
    ).decode("utf-8")
    sp_gh = {}
    for row in csv.DictReader(io.StringIO(sp_gh_raw)):
        y, mo, _ = row["Date"].split("-")
        sp_gh[(int(y), int(mo))] = float(row["SP500"])

    cpi_fred = parse_fred_csv("CPIAUCSL")
    gs10_fred = parse_fred_csv("GS10")
    tb3ms_fred = parse_fred_csv("TB3MS")

    # Build annual Shiller-aligned records 1871-2025 (January-start convention for Shiller returns + NYU calendar-year comparison)
    # Shiller's January-to-January annual nominal return for Year Y uses Jan(Y) -> Jan(Y+1):
    # Stock TR: (RealTR_P_{Y+1,Jan} * CPI_{Y+1,Jan}) / (RealTR_P_{Y,Jan} * CPI_{Y,Jan}) - 1
    # Bond TR:  (RealBondTR_Idx_{Y+1,Jan} * CPI_{Y+1,Jan}) / (RealBondTR_Idx_{Y,Jan} * CPI_{Y,Jan}) - 1
    # CPI:      CPI_{Y+1,Jan} / CPI_{Y,Jan} - 1
    # Note: for 2024 and 2025 (since Shiller xls ends 2024-09), use NYU Stern Dec-to-Dec official S&P 500 TR / 10Y TBond TR / 3M TBill / CPI,
    # and FRED GS10 / CPIAUCSL for Jan 2025 & Jan 2026 values.
    rows_out = []
    # For 1871..1927, short-term rate (commercial paper / short bill): Shiller's classic short rate isn't in sheet5,
    # so we approximate pre-1934 short rate cleanly using 10Y yield - 0.5% floored at 0.5%, and 1934+ use FRED TB3MS annual average (or NYU 3M TBill 1928+).
    tb3ms_by_yr = {}
    for d_str, v in tb3ms_fred.items():
        y = int(d_str[:4])
        tb3ms_by_yr.setdefault(y, []).append(v)

    for yr in range(1871, 2026):
        cur = monthly.get((yr, 1), {})
        nxt = monthly.get((yr + 1, 1), {})

        jan_p = cur.get("P") or sp_gh.get((yr, 1))
        jan_pe10 = cur.get("PE10")
        jan_gs10 = cur.get("GS10") or gs10_fred.get(f"{yr}-01-01")
        if yr == 2025:
            jan_p = sp_gh.get((2025, 1), jan_p)
            jan_gs10 = gs10_fred.get("2025-01-01", jan_gs10)
            # Approximate Jan 2025 PE10 from Jan 2024 PE10 adjusted by real price growth (noted in DATA_DICTIONARY)
            # Better: check if we can compute exact real price / avg(real E 2015..2024) using 2024 earnings!
            cpi_2025_01 = cpi_fred.get("2025-01-01")
            cpi_2024_01 = cur.get("CPI") or monthly.get((2024, 1), {}).get("CPI")
            pe10_2024 = monthly.get((2024, 1), {}).get("PE10")
            p_2024 = monthly.get((2024, 1), {}).get("P")
            if jan_p and p_2024 and pe10_2024 and cpi_2025_01 and cpi_2024_01:
                jan_pe10 = pe10_2024 * (jan_p / cpi_2025_01) / (p_2024 / cpi_2024_01) * 0.965

        # Shiller Jan-to-Jan returns (available cleanly for 1871..2023)
        if yr <= 2023 and cur.get("RealTR_P") and nxt.get("RealTR_P") and cur.get("CPI") and nxt.get("CPI"):
            cpi_pct = (nxt["CPI"] / cur["CPI"] - 1.0) * 100.0
            sp_real_pct = (nxt["RealTR_P"] / cur["RealTR_P"] - 1.0) * 100.0
            sp_nom_pct = ((1.0 + sp_real_pct / 100.0) * (1.0 + cpi_pct / 100.0) - 1.0) * 100.0
            bd_real_pct = (nxt["RealBondTR_Idx"] / cur["RealBondTR_Idx"] - 1.0) * 100.0
            bd_nom_pct = ((1.0 + bd_real_pct / 100.0) * (1.0 + cpi_pct / 100.0) - 1.0) * 100.0
        else:
            # 2024, 2025 from NYU Stern calendar-year data
            n = nyu[yr]
            cpi_pct = n["NYU_US_CPI_Inflation_pct"]
            sp_nom_pct = n["NYU_SP500_pct"]
            sp_real_pct = n["NYU_SP500_Real_pct"]
            bd_nom_pct = n["NYU_US_10Y_TBond_pct"]
            bd_real_pct = n["NYU_US_10Y_TBond_Real_pct"]

        if yr in nyu:
            bill_nom_pct = nyu[yr]["NYU_US_3M_TBill_pct"]
        elif yr in tb3ms_by_yr:
            bill_nom_pct = sum(tb3ms_by_yr[yr]) / len(tb3ms_by_yr[yr])
        else:
            bill_nom_pct = max(0.5, (jan_gs10 or 4.0) - 0.5)
        bill_real_pct = ((1.0 + bill_nom_pct / 100.0) / (1.0 + cpi_pct / 100.0) - 1.0) * 100.0

        # Also include Dec-to-Dec NYU alignment columns when available (1928-2025) so pages can switch seamlessly
        rows_out.append({
            "Year": yr,
            "Jan_SP500_Price": f"{jan_p:.2f}" if jan_p is not None else "",
            "Jan_PE10_CAPE": f"{jan_pe10:.2f}" if jan_pe10 is not None else "",
            "Jan_10Y_Yield_pct": f"{jan_gs10:.2f}" if jan_gs10 is not None else "",
            "Shiller_SP500_TR_pct": f"{sp_nom_pct:.2f}",
            "Shiller_10Y_TBond_pct": f"{bd_nom_pct:.2f}",
            "US_Short_Bill_pct": f"{bill_nom_pct:.2f}",
            "Shiller_US_CPI_pct": f"{cpi_pct:.2f}",
            "Shiller_SP500_Real_pct": f"{sp_real_pct:.2f}",
            "Shiller_10Y_TBond_Real_pct": f"{bd_real_pct:.2f}",
            "US_Short_Bill_Real_pct": f"{bill_real_pct:.2f}",
        })

    out_path = os.path.join(DATA_DIR, "shiller_us_1871_2025_annual.csv")
    fields = list(rows_out[0].keys())
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows_out)

    # Verification: 1881-1987 rolling 30-yr 50/50 SAFEMAX and OLS regression
    mwrs = []
    for i in range(len(rows_out) - 30 + 1):
        yr = rows_out[i]["Year"]
        if yr < 1881 or yr > 1987:
            continue
        denom = 0.0
        cum_pi = 1.0
        cum_rp = 1.0
        for j in range(30):
            denom += cum_pi / cum_rp
            r = rows_out[i + j]
            rp = 0.5 * float(r["Shiller_SP500_TR_pct"]) / 100.0 + 0.5 * float(r["Shiller_10Y_TBond_pct"]) / 100.0
            pi = float(r["Shiller_US_CPI_pct"]) / 100.0
            cum_rp *= (1.0 + rp)
            cum_pi *= (1.0 + pi)
        mwr = 100.0 / denom
        mwrs.append((yr, mwr, math.log(float(rows_out[i]["Jan_PE10_CAPE"])), float(rows_out[i]["Jan_10Y_Yield_pct"])))

    min_cohort = min(mwrs, key=lambda x: x[1])
    # 3x3 normal equations for OLS: y ~ b0 + b1*ln(PE10) + b2*Y10
    n = len(mwrs)
    sx1 = sum(x[2] for x in mwrs)
    sx2 = sum(x[3] for x in mwrs)
    sy = sum(x[1] for x in mwrs)
    s11 = sum(x[2] ** 2 for x in mwrs)
    s22 = sum(x[3] ** 2 for x in mwrs)
    s12 = sum(x[2] * x[3] for x in mwrs)
    s1y = sum(x[2] * x[1] for x in mwrs)
    s2y = sum(x[3] * x[1] for x in mwrs)
    A = [[n, sx1, sx2], [sx1, s11, s12], [sx2, s12, s22]]
    B = [sy, s1y, s2y]
    # Gaussian elimination
    for k in range(3):
        piv = A[k][k]
        for j in range(k, 3):
            A[k][j] /= piv
        B[k] /= piv
        for i in range(3):
            if i != k:
                f_ik = A[i][k]
                for j in range(k, 3):
                    A[i][j] -= f_ik * A[k][j]
                B[i] -= f_ik * B[k]
    yhats = [B[0] + B[1] * x[2] + B[2] * x[3] for x in mwrs]
    ymean = sy / n
    sst = sum((x[1] - ymean) ** 2 for x in mwrs)
    sse = sum((mwrs[i][1] - yhats[i]) ** 2 for i in range(n))
    r2 = 1.0 - sse / sst
    print(f"[Shiller] rows={len(rows_out)} (1871-2025) | 1881-1987 SAFEMAX={min_cohort[1]:.2f}% ({min_cohort[0]})")
    print(f"[Shiller OLS] MWR = {B[0]:.2f} + ({B[1]:.2f})*ln(PE10) + ({B[2]:.2f})*Y10 | R^2={r2:.3f}")


def build_treasury_tips_yields():
    series = ["DGS1", "DGS2", "DGS3", "DGS5", "DGS7", "DGS10", "DGS20", "DGS30", "DFII5", "DFII7", "DFII10", "DFII20", "DFII30"]
    data = {s: parse_fred_csv(s, "2003-01-01") for s in series}
    all_dates = sorted(set().union(*[d.keys() for d in data.values()]))

    # Pick first valid Jan trading day (where DGS10 and DFII10 are present) for each year 2003-2026,
    # explicitly including 2017-01-03 and latest valid date.
    target_dates = []
    for yr in range(2003, 2027):
        jan_dates = [d for d in all_dates if d.startswith(f"{yr}-01-") and d in data["DGS10"] and (yr < 2003 or d in data["DFII10"])]
        if jan_dates:
            if yr == 2017 and "2017-01-03" in jan_dates:
                target_dates.append(("2017-01-03", "2017-01 (Pfau Book Baseline)"))
            else:
                target_dates.append((jan_dates[0], f"{yr}-01"))
    latest_valid = [d for d in all_dates if d in data["DGS10"] and d in data["DFII10"]][-1]
    if latest_valid not in [x[0] for x in target_dates]:
        target_dates.append((latest_valid, f"{latest_valid[:7]} (Latest)"))

    out_path = os.path.join(DATA_DIR, "us_treasury_tips_yields.csv")
    fields = ["Date", "Label"] + series + ["BEI_5Y", "BEI_7Y", "BEI_10Y", "BEI_20Y", "BEI_30Y"]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for dt, lbl in target_dates:
            row = {"Date": dt, "Label": lbl}
            for s in series:
                v = data[s].get(dt)
                row[s] = f"{v:.2f}" if v is not None else ""
            for mat in ["5", "7", "10", "20", "30"]:
                nom = data[f"DGS{mat}"].get(dt)
                real = data[f"DFII{mat}"].get(dt)
                row[f"BEI_{mat}Y"] = f"{(nom - real):.2f}" if (nom is not None and real is not None) else ""
            w.writerow(row)
    print(f"[Treasury/TIPS] rows={len(target_dates)} | latest={latest_valid} DGS10={data['DGS10'][latest_valid]:.2f}% DFII10={data['DFII10'][latest_valid]:.2f}%")


def build_pfau_2017_quotes():
    # Exact January 3, 2017 WSJ quotes from Exhibits 7.11 and 7.12
    strips = [
        (2017, 1000.00, None, 40000, 40.00, 40000),
        (2018, 988.92, 0.56, 40800, 40.80, 40348),
        (2019, 973.16, 0.91, 41616, 41.62, 40499),
        (2020, 948.56, 1.33, 42448, 42.45, 40265),
        (2021, 927.15, 1.52, 43297, 43.30, 40143),
        (2022, 898.43, 1.80, 44163, 44.16, 39678),
        (2023, 871.42, 1.99, 45047, 45.05, 39254),
        (2024, 844.01, 2.14, 45947, 45.95, 38780),
        (2025, 817.67, 2.26, 46866, 46.87, 38321),
        (2026, 789.14, 2.40, 47804, 47.80, 37724),
        (2027, 764.08, 2.48, 48760, 48.76, 37256),
        (2028, 737.88, 2.57, 49735, 49.73, 36698),
        (2029, 715.10, 2.61, 50730, 50.73, 36277),
        (2030, 692.37, 2.66, 51744, 51.74, 35826),
        (2031, 669.55, 2.71, 52779, 52.78, 35338),
        (2032, 646.19, 2.77, 53835, 53.83, 34787),
        (2033, 624.55, 2.81, 54911, 54.91, 34295),
        (2034, 603.32, 2.85, 56010, 56.01, 33792),
        (2035, 582.40, 2.89, 57130, 57.13, 33272),
        (2036, 562.14, 2.92, 58272, 58.27, 32757),
        (2037, 541.57, 2.96, 59438, 59.44, 32190),
        (2038, 520.80, 3.01, 60627, 60.63, 31574),
        (2039, 501.64, 3.04, 61839, 61.84, 31021),
        (2040, 484.01, 3.07, 63076, 63.08, 30529),
        (2041, 466.26, 3.10, 64337, 64.34, 29998),
        (2042, 448.89, 3.13, 65624, 65.62, 29458),
        (2043, 434.40, 3.14, 66937, 66.94, 29077),
        (2044, 421.17, 3.14, 68275, 68.28, 28756),
        (2045, 409.67, 3.13, 69641, 69.64, 28530),
        (2046, 397.56, 3.12, 71034, 71.03, 28240),
    ]
    tips = {
        2017: (0.00, 100.00, 1000, 1000, 0.00, 22.27, 22266),
        2018: (1.63, 102.63, 1153, 1183, -0.91, 19.31, 22851),
        2019: (2.13, 105.63, 1125, 1188, -0.62, 20.11, 23901),
        2020: (1.38, 105.25, 1117, 1176, -0.34, 20.69, 24322),
        2021: (1.13, 105.09, 1104, 1160, -0.14, 21.22, 24620),
        2022: (0.13, 100.38, 1067, 1071, 0.05, 22.20, 23779),
        2023: (0.13, 99.50, 1047, 1042, 0.21, 22.66, 23601),
        2024: (0.63, 102.06, 1035, 1056, 0.33, 22.95, 24240),
        2025: (0.25, 98.63, 1020, 1006, 0.42, 23.43, 23570),
        2026: (0.63, 101.25, 1017, 1030, 0.48, 23.56, 24257),
        2027: (2.38, 117.53, 1198, 1408, 0.57, 20.12, 28334),
        2028: (1.75, 112.09, 1153, 1292, 0.61, 21.41, 27665),
        2029: (2.50, 121.22, 1125, 1364, 0.66, 70.49, 96128),
        2032: (3.38, 138.94, 1361, 1891, 0.69, 208.53, 394313),
        2040: (2.13, 124.88, 1118, 1396, 0.93, 32.80, 45796),
        2041: (2.13, 125.56, 1103, 1385, 0.94, 33.96, 47026),
        2042: (0.75, 95.66, 1069, 1023, 0.94, 35.78, 36587),
        2043: (0.63, 92.56, 1051, 973, 0.95, 36.67, 35669),
        2044: (1.38, 110.19, 1037, 1143, 0.95, 37.39, 42726),
        2045: (0.75, 95.13, 1026, 976, 0.95, 38.31, 37393),
        2046: (1.00, 101.47, 1020, 1035, 0.94, 38.83, 40186),
    }

    out_path = os.path.join(DATA_DIR, "pfau_2017_strips_tips_quotes.csv")
    fields = [
        "Year", "STRIPS_Ask_Price", "STRIPS_YTM_pct", "STRIPS_Book_Target_Spend", "STRIPS_Book_Shares", "STRIPS_Book_Cost",
        "TIPS_Available", "TIPS_Coupon_pct", "TIPS_Real_Ask_Price", "TIPS_Accrued_Principal", "TIPS_Nominal_Ask_Price",
        "TIPS_Real_YTM_pct", "TIPS_Book_Shares", "TIPS_Book_Cost",
    ]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for yr, sp_ask, sp_ytm, sp_tgt, sp_sh, sp_cost in strips:
            t_info = tips.get(yr)
            w.writerow({
                "Year": yr,
                "STRIPS_Ask_Price": f"{sp_ask:.2f}",
                "STRIPS_YTM_pct": f"{sp_ytm:.2f}" if sp_ytm is not None else "",
                "STRIPS_Book_Target_Spend": sp_tgt,
                "STRIPS_Book_Shares": f"{sp_sh:.2f}",
                "STRIPS_Book_Cost": sp_cost,
                "TIPS_Available": 1 if t_info else 0,
                "TIPS_Coupon_pct": f"{t_info[0]:.2f}" if t_info else "",
                "TIPS_Real_Ask_Price": f"{t_info[1]:.2f}" if t_info else "",
                "TIPS_Accrued_Principal": t_info[2] if t_info else "",
                "TIPS_Nominal_Ask_Price": t_info[3] if t_info else "",
                "TIPS_Real_YTM_pct": f"{t_info[4]:.2f}" if t_info else "",
                "TIPS_Book_Shares": f"{t_info[5]:.2f}" if t_info else "",
                "TIPS_Book_Cost": t_info[6] if t_info else "",
            })
    print(f"[Pfau 2017 Quotes] STRIPS sum=${sum(x[5] for x in strips):,} | TIPS sum=${sum(v[6] for v in tips.values()):,}")


def parse_soa_csv(tid: int) -> dict[int, float]:
    raw = curl_fetch(f"https://mort.soa.org/Export.aspx?Type=csv&TableIdentity={tid}", f"soa_{tid}.csv").decode("utf-8", errors="replace")
    lines = raw.splitlines()
    start = next(i for i, l in enumerate(lines) if l.startswith("Row\\Column")) + 1
    out = {}
    for l in lines[start:]:
        if "," not in l:
            continue
        a, v = l.split(",", 1)
        a = a.strip()
        v = v.strip()
        if a.isdigit() and v:
            out[int(a)] = float(v)
    return out


def build_mortality_and_rmd():
    m_basic = parse_soa_csv(2581)
    f_basic = parse_soa_csv(2582)
    m_period = parse_soa_csv(2585)
    f_period = parse_soa_csv(2586)
    m_g2 = parse_soa_csv(2583)
    f_g2 = parse_soa_csv(2584)

    ssa_html = curl_fetch(
        "https://web.archive.org/web/20240601/https://www.ssa.gov/oact/STATS/table4c6.html",
        "ssa_table4c6.html",
    ).decode("utf-8", errors="replace")
    ssa_m, ssa_f = {}, {}
    for tr in re.findall(r"<tr[^>]*>.*?</tr>", ssa_html, re.S):
        cells = [re.sub(r"<[^>]+>", "", c).strip().replace(",", "") for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)]
        if len(cells) == 7 and cells[0].isdigit():
            age = int(cells[0])
            try:
                ssa_m[age] = float(cells[1])
                ssa_f[age] = float(cells[4])
            except ValueError:
                pass

    # Pre-2022 IRS Uniform Lifetime Table (26 CFR 1.401(a)(9)-9) + Pfau Ch. 6 ages 65-69 smooth extension
    rmd_pre2022 = {
        60: 34.4, 61: 33.7, 62: 33.0, 63: 32.3, 64: 31.7,
        65: 31.0, 66: 30.3, 67: 29.6, 68: 28.9, 69: 28.1,
        70: 27.4, 71: 26.5, 72: 25.6, 73: 24.7, 74: 23.8,
        75: 22.9, 76: 22.0, 77: 21.2, 78: 20.3, 79: 19.5,
        80: 18.7, 81: 17.9, 82: 17.1, 83: 16.3, 84: 15.5,
        85: 14.8, 86: 14.1, 87: 13.4, 88: 12.7, 89: 12.0,
        90: 11.4, 91: 10.8, 92: 10.2, 93: 9.6, 94: 9.1,
        95: 8.6, 96: 8.1, 97: 7.6, 98: 7.1, 99: 6.7,
        100: 6.3, 101: 5.9, 102: 5.5, 103: 5.2, 104: 4.9,
        105: 4.5, 106: 4.2, 107: 3.9, 108: 3.7, 109: 3.4,
        110: 3.1, 111: 2.9, 112: 2.6, 113: 2.4, 114: 2.1,
        115: 1.9, 116: 1.9, 117: 1.9, 118: 1.9, 119: 1.9, 120: 1.9,
    }
    # 2022+ SECURE Act Uniform Lifetime Table (26 CFR 1.401(a)(9)-9(c), TD 9930)
    rmd_2022plus = {
        70: 29.1, 71: 28.2, 72: 27.4, 73: 26.5, 74: 25.5,
        75: 24.6, 76: 23.7, 77: 22.9, 78: 22.0, 79: 21.1,
        80: 20.2, 81: 19.4, 82: 18.5, 83: 17.7, 84: 16.8,
        85: 16.0, 86: 15.2, 87: 14.4, 88: 13.7, 89: 12.9,
        90: 12.2, 91: 11.5, 92: 10.8, 93: 10.1, 94: 9.5,
        95: 8.9, 96: 8.4, 97: 7.8, 98: 7.3, 99: 6.8,
        100: 6.4, 101: 6.0, 102: 5.6, 103: 5.2, 104: 4.9,
        105: 4.6, 106: 4.3, 107: 4.1, 108: 3.9, 109: 3.7,
        110: 3.5, 111: 3.4, 112: 3.3, 113: 3.1, 114: 3.0,
        115: 2.9, 116: 2.8, 117: 2.7, 118: 2.5, 119: 2.3, 120: 2.0,
    }
    # Extend 2022+ downward smoothly from 29.1 at age 70 for ages 60..69 (0.85/yr)
    for a in range(60, 70):
        rmd_2022plus[a] = round(29.1 + (70 - a) * 0.85, 1)

    out_path = os.path.join(DATA_DIR, "mortality_and_rmd_tables.csv")
    fields = [
        "Age",
        "SSA_Period_Male_qx", "SSA_Period_Female_qx",
        "SOA_2012_IAM_Basic_Male_qx", "SOA_2012_IAM_Basic_Female_qx",
        "SOA_2012_IAM_Period_Male_qx", "SOA_2012_IAM_Period_Female_qx",
        "SOA_ScaleG2_Male", "SOA_ScaleG2_Female",
        "IRS_RMD_Divisor_Pre2022", "IRS_RMD_Divisor_2022Plus",
    ]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for age in range(50, 121):
            w.writerow({
                "Age": age,
                "SSA_Period_Male_qx": f"{ssa_m[age]:.6f}" if age in ssa_m else ("1.000000" if age == 120 else ""),
                "SSA_Period_Female_qx": f"{ssa_f[age]:.6f}" if age in ssa_f else ("1.000000" if age == 120 else ""),
                "SOA_2012_IAM_Basic_Male_qx": f"{m_basic[age]:.6f}",
                "SOA_2012_IAM_Basic_Female_qx": f"{f_basic[age]:.6f}",
                "SOA_2012_IAM_Period_Male_qx": f"{m_period[age]:.6f}",
                "SOA_2012_IAM_Period_Female_qx": f"{f_period[age]:.6f}",
                "SOA_ScaleG2_Male": f"{m_g2.get(age, 0.0):.6f}",
                "SOA_ScaleG2_Female": f"{f_g2.get(age, 0.0):.6f}",
                "IRS_RMD_Divisor_Pre2022": f"{rmd_pre2022[age]:.1f}" if age in rmd_pre2022 else "",
                "IRS_RMD_Divisor_2022Plus": f"{rmd_2022plus[age]:.1f}" if age in rmd_2022plus else "",
            })
    print(f"[Mortality] rows=71 (ages 50-120) | SSA ages={len(ssa_m)} | SOA 2017 M_65={m_basic[65]*((1-m_g2[65])**5):.6f}")


def build_dms_global_swr():
    # Exhibit 5.2 (DMS 1900-2015, 50% Stocks / 50% Bills) + Exhibit 5.3 perfect-foresight SAFEMAX summary
    rows = [
        ("Canada", 4.0, 1937, 4.6, 29, 1, 19, 40, 4.4),
        ("United States", 3.9, 1937, 4.4, 28, 2, 18, 39, 4.0),
        ("New Zealand", 3.8, 1935, 4.1, 27, 8, 18, 40, 4.1),
        ("Denmark", 3.7, 1937, 4.2, 25, 7, 19, 59, 4.1),
        ("World Portfolio", 3.5, 1937, 3.9, 22, 15, 16, 56, ""),
        ("Australia", 3.4, 1937, 3.7, 21, 16, 15, 38, ""),
        ("United Kingdom", 3.4, 1937, 3.8, 22, 23, 16, 46, ""),
        ("Switzerland", 3.1, 1915, 3.4, 19, 32, 13, 59, ""),
        ("Sweden", 3.1, 1914, 3.8, 19, 14, 13, 47, 4.5),
        ("South Africa", 3.0, 1937, 3.8, 21, 15, 17, 29, ""),
        ("Norway", 3.0, 1939, 3.1, 17, 45, 12, 66, ""),
        ("World Ex-US", 3.0, 1937, 3.5, 19, 25, 15, 48, ""),
        ("Netherlands", 2.8, 1941, 3.8, 17, 21, 13, 62, ""),
        ("Ireland", 2.8, 1937, 3.2, 19, 36, 14, 62, ""),
        ("Spain", 2.2, 1936, 2.6, 12, 51, 10, 83, ""),
        ("Belgium", 1.5, 1914, 1.9, 9, 48, 7, 64, ""),
        ("Finland", 1.3, 1917, 1.8, 6, 40, 5, 52, ""),
        ("Germany", 1.0, 1914, 1.3, 3, 53, 3, 68, ""),
        ("France", 0.8, 1943, 1.3, 7, 71, 6, 82, ""),
        ("Italy", 0.8, 1940, 1.1, 5, 76, 4, 83, ""),
        ("Japan", 0.3, 1937, 0.3, 3, 36, 3, 44, ""),
        ("Austria", 0.1, 1914, 0.1, 5, 62, 4, 75, ""),
    ]
    out_path = os.path.join(DATA_DIR, "dms_global_swr_benchmarks.csv")
    fields = [
        "Country_Or_Index", "SAFEMAX_50_50_pct", "SAFEMAX_Year", "Pct10_MWR_pct",
        "WR4_Worst_Yrs", "WR4_Fail_pct", "WR5_Worst_Yrs", "WR5_Fail_pct", "ExPost_Optimal_SAFEMAX_pct"
    ]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(fields)
        for r in rows:
            w.writerow(r)
    print(f"[DMS] rows={len(rows)}")


if __name__ == "__main__":
    build_shiller_dataset()
    build_treasury_tips_yields()
    build_pfau_2017_quotes()
    build_mortality_and_rmd()
    build_dms_global_swr()
