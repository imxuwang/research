#!/usr/bin/env python3
"""Shared quantitative JS simulation engines (PMT/NPER/RATE, OLS, Markowitz QP, Ch.3A MC, Mortality, Ch.6 10 Strategies + PAY Rule)."""

SHARED_SIM_JS = r"""
    // ---- 1. Deterministic Time-Value-of-Money (Excel-compatible PMT / NPER / RATE) ----
    function calcPMT(rate, nper, pv, fv = 0, type = 1) {
      if (nper <= 0) return 0;
      if (Math.abs(rate) < 1e-10) return -(pv + fv) / nper;
      const pvif = Math.pow(1 + rate, nper);
      let pmt = (rate / (pvif - 1)) * -(pv * pvif + fv);
      if (type === 1) pmt /= (1 + rate);
      return pmt;
    }

    function calcNPER(rate, pmt, pv, fv = 0, type = 1) {
      if (Math.abs(rate) < 1e-10) {
        if (Math.abs(pmt) < 1e-12) return Infinity;
        return -(pv + fv) / pmt;
      }
      const pmtAdj = pmt * (1 + rate * type);
      const num = pmtAdj - fv * rate;
      const den = pv * rate + pmtAdj;
      if (Math.abs(den) < 1e-12 || !isFinite(num / den) || num / den <= 0) return Infinity;
      return Math.log(num / den) / Math.log(1 + rate);
    }

    function calcRATE(nper, pmt, pv, fv = 0, type = 1) {
      if (nper <= 0) return NaN;
      let lo = -0.5, hi = 1.0;
      const f = r => {
        if (Math.abs(r) < 1e-9) return pv + pmt * nper + fv;
        const g = Math.pow(1 + r, nper);
        return pv * g + pmt * (1 + r * type) * ((g - 1) / r) + fv;
      };
      let flo = f(lo), fhi = f(hi);
      if (flo * fhi > 0) return NaN;
      for (let it = 0; it < 90; it++) {
        const mid = 0.5 * (lo + hi);
        const fmid = f(mid);
        if (Math.abs(fmid) < 1e-9) return mid;
        if (flo * fmid <= 0) { hi = mid; fhi = fmid; } else { lo = mid; flo = fmid; }
      }
      return 0.5 * (lo + hi);
    }

    // ---- 2. Closed-Form & Sequential MWR (Maximum Sustainable Withdrawal Rate) ----
    // eqRets, bdRets, infs are decimal arrays (e.g. 0.08, 0.03) of length >= horizon
    function computeCohortMWR(eqRets, bdRets, infs, startIdx, horizon, eqWeight, {
      timing = "start", feeDec = 0, taxEff = 0, targetPreserveMode = "deplete", targetFrac = 0,
      realSpendMultipliers = null, eqGlideWeights = null
    } = {}) {
      let denom = 0.0, cumInf = 1.0, cumPort = 1.0;
      for (let t = 0; t < horizon; t++) {
        const idx = startIdx + t;
        const wEq = eqGlideWeights ? eqGlideWeights[t] : eqWeight;
        const grossR = wEq * eqRets[idx] + (1 - wEq) * bdRets[idx];
        const netR = grossR * (1 - taxEff) - feeDec;
        const pi = infs[idx];
        const spendMult = realSpendMultipliers ? realSpendMultipliers[t] : 1.0;
        if (timing === "start") {
          denom += (cumInf * spendMult) / cumPort;
        }
        cumPort *= (1 + netR);
        cumInf *= (1 + pi);
        if (timing === "end") {
          denom += (cumInf * spendMult) / cumPort;
        }
      }
      if (denom <= 0 || cumPort <= 0) return 0;
      let numer = 1.0;
      if (targetPreserveMode === "nominal") numer = Math.max(0, 1.0 - targetFrac / cumPort);
      else if (targetPreserveMode === "real") numer = Math.max(0, 1.0 - (targetFrac * cumInf) / cumPort);
      return Math.max(0, (numer / denom) * 100.0);
    }

    // ---- 3. Multi-Variable OLS Regression (Gaussian Elimination) ----
    function solveLinearSystem(A_in, b_in) {
      const n = b_in.length;
      const A = A_in.map(row => row.slice());
      const b = b_in.slice();
      for (let k = 0; k < n; k++) {
        let maxR = k;
        for (let r = k + 1; r < n; r++) {
          if (Math.abs(A[r][k]) > Math.abs(A[maxR][k])) maxR = r;
        }
        if (maxR !== k) {
          [A[k], A[maxR]] = [A[maxR], A[k]];
          [b[k], b[maxR]] = [b[maxR], b[k]];
        }
        const piv = A[k][k];
        if (Math.abs(piv) < 1e-12) return null;
        for (let j = k; j < n; j++) A[k][j] /= piv;
        b[k] /= piv;
        for (let i = 0; i < n; i++) {
          if (i === k) continue;
          const f = A[i][k];
          for (let j = k; j < n; j++) A[i][j] -= f * A[k][j];
          b[i] -= f * b[k];
        }
      }
      return b;
    }

    function fitOLS(yArr, XMat) {
      const n = yArr.length, p = XMat[0].length;
      const XtX = Array.from({ length: p }, () => new Array(p).fill(0));
      const Xty = new Array(p).fill(0);
      for (let i = 0; i < n; i++) {
        const xi = XMat[i], yi = yArr[i];
        for (let j = 0; j < p; j++) {
          Xty[j] += xi[j] * yi;
          for (let k = 0; k < p; k++) XtX[j][k] += xi[j] * xi[k];
        }
      }
      const beta = solveLinearSystem(XtX, Xty);
      if (!beta) return null;
      const yMean = meanArr(yArr);
      let sst = 0, sse = 0;
      const preds = new Array(n);
      for (let i = 0; i < n; i++) {
        let yh = 0;
        for (let j = 0; j < p; j++) yh += beta[j] * XMat[i][j];
        preds[i] = yh;
        sst += (yArr[i] - yMean) ** 2;
        sse += (yArr[i] - yh) ** 2;
      }
      const r2 = sst > 1e-12 ? 1 - sse / sst : 0;
      const rmse = Math.sqrt(sse / Math.max(1, n - p));
      return { beta, r2, rmse, preds };
    }

    // ---- 4. Long-Only Markowitz Efficient Frontier (Projected Gradient Descent on Simplex) ----
    function projectSimplex(v) {
      const n = v.length;
      const u = v.slice().sort((a, b) => b - a);
      let cssv = 0, rho = -1;
      for (let i = 0; i < n; i++) {
        cssv += u[i];
        if (u[i] + (1 - cssv) / (i + 1) > 0) rho = i;
      }
      const theta = (1 - u.slice(0, rho + 1).reduce((a, b) => a + b, 0)) / (rho + 1);
      return v.map(x => Math.max(0, x + theta));
    }

    function solveEfficientFrontier(means, stds, corr, numPoints = 41) {
      const n = means.length;
      const cov = Array.from({ length: n }, (_, i) =>
        Array.from({ length: n }, (__, j) => stds[i] * stds[j] * corr[i][j])
      );
      const minMu = Math.min(...means), maxMu = Math.max(...means);
      const frontier = [];
      for (let p = 0; p < numPoints; p++) {
        const targetMu = minMu + (p / (numPoints - 1)) * (maxMu - minMu);
        // Minimize 0.5 * w' Cov w + lambda * (w' mu - targetMu)^2 via projected gradient
        let w = new Array(n).fill(1 / n);
        const lam = 60.0;
        const lr = 0.25;
        for (let it = 0; it < 700; it++) {
          let curMu = 0;
          for (let i = 0; i < n; i++) curMu += w[i] * means[i];
          const grad = new Array(n).fill(0);
          for (let i = 0; i < n; i++) {
            let cw = 0;
            for (let j = 0; j < n; j++) cw += cov[i][j] * w[j];
            grad[i] = cw + 2 * lam * (curMu - targetMu) * means[i];
          }
          const step = lr / (1 + it * 0.008);
          const next = w.map((wi, i) => wi - step * grad[i]);
          w = projectSimplex(next);
        }
        let mu = 0, v = 0;
        for (let i = 0; i < n; i++) {
          mu += w[i] * means[i];
          for (let j = 0; j < n; j++) v += w[i] * w[j] * cov[i][j];
        }
        frontier.push({ weights: w, mean: mu, std: Math.sqrt(Math.max(0, v)) });
      }
      // Keep upper (non-dominated) portion of frontier above min-variance portfolio
      let minStdIdx = 0;
      for (let i = 1; i < frontier.length; i++) {
        if (frontier[i].std < frontier[minStdIdx].std) minStdIdx = i;
      }
      return frontier.slice(minStdIdx);
    }

    // ---- 5. Ch. 3A Correlated AR(1) Low-Yield Stochastic Return Engine ----
    // Calibrates directly to historical Shiller data (or Ch. 3A defaults) with initial seed y0, pi0
    function calibrateCh3AEngine(shillerRows) {
      const valid = shillerRows.filter(r => r.Year >= 1890 && r.Year <= 2023 && r.Jan_10Y_Yield_pct !== null);
      const n = valid.length;
      const infs = [], ylds = [], erps = [];
      for (let i = 0; i < n; i++) {
        const pi = valid[i].Shiller_US_CPI_pct / 100.0;
        const y = valid[i].Jan_10Y_Yield_pct / 100.0;
        const rs = valid[i].Shiller_SP500_TR_pct / 100.0;
        infs.push(pi);
        ylds.push(y);
        erps.push(rs - y);
      }
      const stats = arr => {
        const m = meanArr(arr);
        let s2 = 0;
        for (const x of arr) s2 += (x - m) ** 2;
        const sd = Math.sqrt(s2 / Math.max(1, arr.length - 1));
        return { m, sd };
      };
      const stInf = stats(infs), stY = stats(ylds), stErp = stats(erps);
      // AR(1) phi for inflation and yields
      const fitAR1 = (arr, m) => {
        let num = 0, den = 0;
        for (let t = 1; t < arr.length; t++) {
          num += (arr[t] - m) * (arr[t - 1] - m);
          den += (arr[t - 1] - m) ** 2;
        }
        const phi = Math.max(0.1, Math.min(0.96, den > 0 ? num / den : 0.5));
        const res = [];
        for (let t = 1; t < arr.length; t++) res.push((arr[t] - m) - phi * (arr[t - 1] - m));
        return { phi, sig: stats(res).sd };
      };
      const arInf = fitAR1(infs, stInf.m);
      const arY = fitAR1(ylds, stY.m);
      // Residuals for ERP (i.i.d.) and AR(1) innovations for Yield & Inflation
      const rErp = [], rY = [], rInf = [];
      for (let t = 1; t < n; t++) {
        rErp.push((erps[t] - stErp.m) / (stErp.sd || 1));
        rY.push(((ylds[t] - stY.m) - arY.phi * (ylds[t - 1] - stY.m)) / (arY.sig || 1));
        rInf.push(((infs[t] - stInf.m) - arInf.phi * (infs[t - 1] - stInf.m)) / (arInf.sig || 1));
      }
      const corr2 = (a, b) => {
        let s = 0;
        for (let i = 0; i < a.length; i++) s += a[i] * b[i];
        return Math.max(-0.85, Math.min(0.85, s / Math.max(1, a.length - 1)));
      };
      const c12 = corr2(rErp, rY), c13 = corr2(rErp, rInf), c23 = corr2(rY, rInf);
      // 3x3 Cholesky lower triangular L
      const l11 = 1.0, l21 = c12, l31 = c13;
      const l22 = Math.sqrt(Math.max(1e-6, 1 - l21 * l21));
      const l32 = (c23 - l31 * l21) / l22;
      const l33 = Math.sqrt(Math.max(1e-6, 1 - l31 * l31 - l32 * l32));
      return {
        muErp: stErp.m, sdErp: stErp.sd,
        muY: stY.m, phiY: arY.phi, sigY: arY.sig,
        muInf: stInf.m, phiInf: arInf.phi, sigInf: arInf.sig,
        L: [l11, l21, l22, l31, l32, l33]
      };
    }

    function simulateCh3APath(cal, horizon, rng, y0 = 0.0245, pi0 = 0.017) {
      const [l11, l21, l22, l31, l32, l33] = cal.L;
      const eq = new Float64Array(horizon);
      const bd = new Float64Array(horizon);
      const inf = new Float64Array(horizon);
      const yld = new Float64Array(horizon);
      let yPrev = y0, piPrev = pi0;
      for (let t = 0; t < horizon; t++) {
        const z1 = randNormal(rng), z2 = randNormal(rng), z3 = randNormal(rng);
        const eErp = l11 * z1;
        const eY = l21 * z1 + l22 * z2;
        const eInf = l31 * z1 + l32 * z2 + l33 * z3;
        const yCur = Math.max(0.001, Math.min(0.20, cal.muY + cal.phiY * (yPrev - cal.muY) + cal.sigY * eY));
        const piCur = Math.max(-0.12, Math.min(0.25, cal.muInf + cal.phiInf * (piPrev - cal.muInf) + cal.sigInf * eInf));
        const erpCur = cal.muErp + cal.sdErp * eErp;
        const rStock = Math.max(-0.80, Math.min(1.20, yPrev + erpCur));
        // Constant-maturity 10Y bond fund approximation (average coupon yield ~yPrev, duration ~7.5 yrs)
        const dur = yCur > 0.005 ? (1 - Math.pow(1 + yCur, -9)) / yCur : 8.5;
        const rBond = Math.max(-0.50, Math.min(0.60, yPrev - dur * (yCur - yPrev) * 0.85));
        eq[t] = rStock;
        bd[t] = rBond;
        inf[t] = piCur;
        yld[t] = yCur;
        yPrev = yCur;
        piPrev = piCur;
      }
      return { eq, bd, inf, yld };
    }

    // ---- 6. Mortality Survival Curve Helper ----
    function buildSurvivalCurve(mortRows, { table = "soa_2017", startAge = 65, household = "male", healthMult = 1.0 } = {}) {
      const byAge = {};
      for (const r of mortRows) byAge[r.Age] = r;
      const getQx = (age, sex, yrIdx) => {
        const r = byAge[Math.min(120, Math.max(50, age))];
        if (!r || age >= 120) return 1.0;
        let q = 0;
        if (table === "ssa") {
          q = sex === "F" ? r.SSA_Period_Female_qx : r.SSA_Period_Male_qx;
        } else if (table === "soa_period") {
          q = sex === "F" ? r.SOA_2012_IAM_Period_Female_qx : r.SOA_2012_IAM_Period_Male_qx;
        } else {
          const baseYear = table === "soa_2026" ? 2026 : 2017;
          const qBase = sex === "F" ? r.SOA_2012_IAM_Basic_Female_qx : r.SOA_2012_IAM_Basic_Male_qx;
          const g2 = sex === "F" ? r.SOA_ScaleG2_Female : r.SOA_ScaleG2_Male;
          q = qBase * Math.pow(1 - g2, baseYear + yrIdx - 2012);
        }
        return Math.max(0, Math.min(1.0, (q || 0) * healthMult));
      };

      const maxK = 120 - startAge;
      const pM = [1.0], pF = [1.0];
      for (let k = 0; k < maxK; k++) {
        pM.push(pM[k] * (1 - getQx(startAge + k, "M", k)));
        pF.push(pF[k] * (1 - getQx(startAge + k, "F", k)));
      }
      const surv = [];
      for (let k = 0; k <= maxK; k++) {
        let p = 1;
        if (household === "male") p = pM[k];
        else if (household === "female") p = pF[k];
        else if (household === "couple") p = 1 - (1 - pM[k]) * (1 - pF[k]);
        else if (household === "two_males") p = 1 - (1 - pM[k]) * (1 - pM[k]);
        else if (household === "two_females") p = 1 - (1 - pF[k]) * (1 - pF[k]);
        surv.push({ age: startAge + k, k, p });
      }
      // Death probabilities q_death[k] = surv[k].p - surv[k+1].p
      const pdf = [];
      let meanAge = startAge;
      for (let k = 0; k < maxK; k++) {
        const d = surv[k].p - surv[k + 1].p;
        pdf.push({ age: startAge + k, k, prob: d });
        meanAge += surv[k + 1].p;
      }
      const ageAtSurv = targetP => {
        for (let k = 0; k < maxK; k++) {
          if (surv[k].p >= targetP && surv[k + 1].p <= targetP) {
            const span = surv[k].p - surv[k + 1].p;
            return startAge + k + (span > 1e-9 ? (surv[k].p - targetP) / span : 0);
          }
        }
        return 120;
      };
      return { surv, pdf, meanAge, p50Age: ageAtSurv(0.5), p10Age: ageAtSurv(0.1), p90Age: ageAtSurv(0.9), p25Age: ageAtSurv(0.25) };
    }

    // ---- 7. Chapter 6: Exact 10 Variable Spending Strategies + PAY Rule Calibrator ----
    function computeZoltGlidePath(V0, w0, horizonGP = 45, piGP = 0.03) {
      // Solve sum_{k=0}^{H-1} q^k = 1 / w0 where q = (1 + piGP)/(1 + rReq)
      const invW = 1.0 / Math.max(1e-6, w0);
      let lo = 0.5, hi = 1.3;
      const sumQ = q => Math.abs(q - 1) < 1e-8 ? horizonGP : (1 - Math.pow(q, horizonGP)) / (1 - q);
      for (let it = 0; it < 70; it++) {
        const mid = 0.5 * (lo + hi);
        if (sumQ(mid) < invW) lo = mid; else hi = mid;
      }
      const q = 0.5 * (lo + hi);
      const rReq = (1 + piGP) / q - 1;
      const path = new Float64Array(horizonGP + 1);
      path[0] = V0;
      let wNom = w0 * V0;
      for (let t = 0; t < horizonGP; t++) {
        path[t + 1] = Math.max(0, (path[t] - wNom) * (1 + rReq));
        wNom *= (1 + piGP);
      }
      return { path, rReq };
    }

    function simulateCh6Strategy(stratId, w0, eqRets, bdRets, infs, {
      V0 = 100000, eqWeight = 0.50, horizon = 30, startAge = 65, rmdByAge = null,
      hybridAlpha = 0.50, maN = 3, bengenFloor = 0.85, bengenCeil = 1.20,
      vgFloor = 0.975, vgCeil = 1.05, vgNominal = true,
      kitcesThresh = 1.50, kitcesRaise = 1.10, kitcesCooldown = 3,
      gkGuardrail = 0.20, gkCut = 0.90, gkRaise = 1.10, gkCutoffRem = 15,
      zoltH = 45, zoltPi = 0.03
    } = {}) {
      let kMult = 1.0;
      if (stratId === 10 && rmdByAge) {
        const base65 = 1.0 / (rmdByAge[startAge] || 31.0);
        kMult = w0 / base65;
      }
      const zoltGP = stratId === 9 ? computeZoltGlidePath(V0, w0, Math.max(zoltH, horizon + 5), zoltPi).path : null;

      let vNom = V0, cumInf = 1.0;
      let wPrevNom = w0 * V0;
      let wInitReal = w0 * V0;
      let lastRatchetT = 1;
      const vHistNom = [V0];

      const spendReal = new Float64Array(horizon);
      const wealthReal = new Float64Array(horizon + 1);
      wealthReal[0] = V0;

      let dsvSum = 0;
      let depleted = false;

      for (let t = 1; t <= horizon; t++) {
        const piPrev = t >= 2 ? infs[t - 2] : 0;
        const rPrevPort = t >= 2 ? (eqWeight * eqRets[t - 2] + (1 - eqWeight) * bdRets[t - 2]) : 0;
        const prevCumInf = cumInf;
        let wTargetNom = 0;

        if (t === 1) {
          wTargetNom = w0 * V0;
        } else if (vNom <= 0) {
          wTargetNom = 0;
        } else {
          switch (stratId) {
            case 1: // Constant Real
              wTargetNom = wInitReal * prevCumInf;
              break;
            case 2: // Fixed %
              wTargetNom = w0 * vNom;
              break;
            case 3: // Endowment Hybrid (static convex combination of Strat 1 & Strat 2)
              wTargetNom = hybridAlpha * (wInitReal * prevCumInf) + (1 - hybridAlpha) * (w0 * vNom);
              break;
            case 4: { // Endowment N-Yr Moving Average (nominal balances)
              const startK = Math.max(0, vHistNom.length - maN);
              let sumV = 0;
              for (let k = startK; k < vHistNom.length; k++) sumV += vHistNom[k];
              wTargetNom = w0 * (sumV / (vHistNom.length - startK));
              break;
            }
            case 5: { // Bengen Hard-Dollar Real Floor/Ceiling
              const rawReal = w0 * (vNom / prevCumInf);
              const clamped = Math.max(bengenFloor * wInitReal, Math.min(bengenCeil * wInitReal, rawReal));
              wTargetNom = clamped * prevCumInf;
              break;
            }
            case 6: { // Vanguard % Floor/Ceiling (Pfau nominal or inflation-adjusted)
              const basePrev = vgNominal ? wPrevNom : wPrevNom * (1 + piPrev);
              wTargetNom = Math.max(vgFloor * basePrev, Math.min(vgCeil * basePrev, w0 * vNom));
              break;
            }
            case 7: { // Kitces Ratcheting
              let wBase = wPrevNom * (1 + piPrev);
              if (vNom > kitcesThresh * V0 && (t - lastRatchetT) >= kitcesCooldown) {
                wBase *= kitcesRaise;
                lastRatchetT = t;
              }
              wTargetNom = wBase;
              break;
            }
            case 8: { // Guyton-Klinger (2006)
              const infFreez = (rPrevPort < 0 && piPrev > 0 && (wPrevNom * (1 + piPrev) / vNom) > w0);
              const wStep1 = infFreez ? wPrevNom : wPrevNom * (1 + piPrev);
              const curWr = wStep1 / vNom;
              const remYrs = horizon - t + 1;
              if (remYrs > gkCutoffRem && curWr > w0 * (1 + gkGuardrail)) wTargetNom = wStep1 * gkCut;
              else if (curWr < w0 * (1 - gkGuardrail)) wTargetNom = wStep1 * gkRaise;
              else wTargetNom = wStep1;
              break;
            }
            case 9: { // Zolt Glide Path (TPA)
              const gpTarget = zoltGP[Math.min(t - 1, zoltGP.length - 1)];
              wTargetNom = (vNom < gpTarget && piPrev > 0) ? wPrevNom : wPrevNom * (1 + piPrev);
              break;
            }
            case 10: { // Modified RMD
              const div = (rmdByAge && rmdByAge[Math.min(120, startAge + t - 1)]) || Math.max(1.9, 31 - (startAge + t - 1 - 65) * 0.72);
              const rPct = Math.min(1.0, kMult / div);
              wTargetNom = rPct * vNom;
              break;
            }
            default:
              wTargetNom = wInitReal * prevCumInf;
          }
        }

        const wActualNom = Math.max(0, Math.min(vNom, wTargetNom));
        const wActualReal = wActualNom / prevCumInf;
        spendReal[t - 1] = wActualReal;

        if (t >= 2) {
          if (wActualReal <= 1e-9 || spendReal[t - 2] <= 1e-9) {
            dsvSum += -1.0;
          } else {
            const chg = (wActualReal - spendReal[t - 2]) / spendReal[t - 2];
            if (chg < 0) dsvSum += chg;
          }
        }

        wPrevNom = wActualNom;
        const remNom = Math.max(0, vNom - wActualNom);
        if (remNom <= 1e-9) depleted = true;

        const rPort = eqWeight * eqRets[t - 1] + (1 - eqWeight) * bdRets[t - 1];
        const piCur = infs[t - 1];
        vNom = remNom * (1 + rPort);
        cumInf *= (1 + piCur);
        vHistNom.push(vNom);
        wealthReal[t] = vNom / cumInf;
      }

      return {
        spendReal,
        wealthReal,
        endWealthReal: wealthReal[horizon],
        dsvPct: (dsvSum / horizon) * 100.0,
        depleted
      };
    }

    function calibratePayRuleW0(stratId, paths, targetXpct, targetYamt, horizon, simOpts) {
      // Find max w0 (to 1 bp = 0.0001) such that Q_{X%}(endWealthReal) >= targetYamt
      const N = paths.length;
      const qFrac = targetXpct / 100.0;
      const buf = new Float64Array(N);
      const evalQ = w0 => {
        for (let i = 0; i < N; i++) {
          const res = simulateCh6Strategy(stratId, w0, paths[i].eq, paths[i].bd, paths[i].inf, { ...simOpts, horizon });
          buf[i] = res.endWealthReal;
        }
        buf.sort();
        return quantileSorted(buf, qFrac);
      };
      let lo = 0.005, hi = 0.16;
      for (let it = 0; it < 22; it++) {
        const mid = 0.5 * (lo + hi);
        if (evalQ(mid) >= targetYamt) lo = mid; else hi = mid;
      }
      return Math.round(lo * 10000) / 10000;
    }
"""
