# Algorithm

## Mathematical formulation

Scores (Equation 1):
$$m_{crji}=\frac{\ell(\mathrm{gold}_i)}{\mathrm{bytes}(\mathrm{gold}_i)}-\max_{v\ne\mathrm{gold}_i}\frac{\ell(v_i)}{\mathrm{bytes}(v_i)},\qquad a_{crji}=\mathbf 1\{m_{crji}>0\}.$$

Measurement model (Equation 2): $y^H_{crj}=\mu^H_{cj}+E_{crj}+\varepsilon^H_{crj}$, $H\in\{A,B\}$.

Centring: $d^H_{crj}=y^H_{crj}-R^{-1}\sum_s y^H_{csj}$.

Identity (Equation 3), under zero-mean item errors uncorrelated across halves and i.i.d. run effects:
$$\mathbb E[d^A_{crj}d^B_{crk}]=(1-1/R)\,\Sigma_{E,c}(j,k).$$

Statistics (Equation 4), with $g^H_{cr}=K^{-1}\sum_j d^H_{crj}$:
$$T_c=\frac{1}{R-1}\sum_r g^A_{cr}g^B_{cr},\qquad U_c=\frac{1}{K^2(R-1)}\sum_{j,r}d^A_{crj}d^B_{crj}.$$

Estimator (Equation 5):
$$\widehat\Lambda=\sqrt{\frac{\sum_cT_c}{\sum_cU_c}},\quad \Lambda^2=\frac{\mathbf 1^{\mathsf T}\Sigma_E\mathbf 1}{\operatorname{tr}\Sigma_E}=1+(K-1)\bar r_E,\quad K_{\mathrm{eff}}=K/\Lambda^2.$$

Symmetrised matrix estimate (Appendix A.3):
$$\widehat\Sigma_E(j,k)=\frac{1}{2N(R-1)}\sum_{c,r}\left(d^A_{crj}d^B_{crk}+d^A_{crk}d^B_{crj}\right).$$

Wild cluster bootstrap-t on $\theta=\Lambda^2$ (Appendix D.2, Equation 18): recipe residuals $\psi_g=\sum_{c\in g}(T_c-\widehat\theta U_c)/\sum_cU_c$, $\widehat{\mathrm{SE}}=(\sum_g\psi_g^2)^{1/2}$; draw $v_{bg}\in\{\pm1\}$, $T^*_c=\widehat\theta U_c+v_{bg(c)}(T_c-\widehat\theta U_c)$ with denominator fixed at $\sum_cU_c$; $t^*_b=(\widehat\theta^*_b-\widehat\theta)/\widehat{\mathrm{SE}}^*_b$; interval $[\widehat\theta-q_{0.975}\widehat{\mathrm{SE}},\ \widehat\theta-q_{0.025}\widehat{\mathrm{SE}}]$, square-rooted when nonnegative.

Delete-one-seed jackknife (PolyPythias, from `compute2/analysis/estimates.py`): $\widehat\theta_{(-r)}$ for each seed $r$, $\widehat{\mathrm{se}}=\sqrt{\frac{R-1}{R}\sum_r(\widehat\theta_{(-r)}-\bar\theta)^2}$, interval $\widehat\theta\pm t_{0.975}(R-1)\widehat{\mathrm{se}}$, square-rooted.

Information ratio (Equation 7): $p(1-p)/\phi(z_0)^2$, $z_0=\Phi^{-1}(1-p)$.

Attenuation by diagonal extra covariance $D$: $\Lambda^2_D=(\mathbf 1^{\mathsf T}\Sigma_E\mathbf 1+\operatorname{tr}D)/(\operatorname{tr}\Sigma_E+\operatorname{tr}D)$, between $\Lambda^2$ and one when denominators are positive.

Aggregate variance: $\sigma^2_{\mathrm{agg}}=\bar\sigma^2_E[1/K+(K-1)\bar r_E/K]$.

## Pseudocode (Algorithm 1 of the paper, with inference and rules)

```
input: per-item scores for runs r=1..R of configurations c=1..N on K benchmarks
1  mask_A <- balanced within-trait permutation(seed=20260101)   # frozen, reused for all runs
2  for each c, r, j: y^A_crj, y^B_crj <- item means on each half (MMLU macro-averaged)
3  d^H_c <- project y^H_c onto mean-zero run contrasts            # centring
4  g^H_cr <- mean_j d^H_crj
5  T_c <- sum_r g^A_cr g^B_cr / (R-1);  U_c <- sum_{j,r} d^A_crj d^B_crj / (K^2 (R-1))
6  theta <- sum_c T_c / sum_c U_c;  Lambda <- sqrt(theta);  K_eff <- K / theta
7  interval <- wild_cluster_bootstrap_t(T, U, recipe, B=4999, seed=0)    # DataDecide
   or       <- seed_jackknife(population, t(R-1))                         # PolyPythias
8  repeat 5-7 after deleting each benchmark, recipe, recipe pair, size band; report spread
9  registered test: pass iff interval.lo > 1 (held-out margin, 530M/750M/1B)
   R1: pass iff jackknife.lo > 1 (PolyPythias bank 1 margin)
   R2: A = all bank-1 items, B = all bank-2 items; cross <- steps 3-7
       diff <- jackknife of log theta_within - log theta_cross
       if cross.lo > 1 and diff.lo <= 0 <= diff.hi: "shared-item explanation not supported"
       elif diff.lo > 0 and cross.hi >= 1 and not cross.lo > 1: "supported"
       else: "undecided"
```

## Step-by-step explanation
1. The half assignment is fixed once so that every run is scored on the same item sets; per-trait splitting keeps both halves covering every benchmark.
2. Centring within configuration removes the configuration mean (competence), which with three runs would otherwise dominate raw products.
3. Cross-half products cancel item noise in expectation because the halves contain disjoint items with independent errors (under A2).
4. T_c captures the full aggregate covariance and U_c its diagonal; both are pooled before division.
5. The interval treats recipes as clusters because a recipe's five sizes can share run structure; a band-shared effect is bounded separately.
6. Deletions report how much the factor depends on the battery, since the estimand is fixed-battery.

## Complexity
- Reduction: one sequential pass over 122.9 GB of compressed data (18 CPU hours budgeted).
- Estimation: O(N R K) for T and U after reduction; 37,682 items per run are averaged in O(items).
- Wild bootstrap: O(B N) with B = 4,999; test inversion and prepivoting multiply this (1,999 x 1,999 for Beran prepivoting).
- Subset enumeration: 1,081,575 seventeen-recipe sets (thirteen seconds reported); 1,013 benchmark subsets each with 4,999 draws.
- Jackknife: R + 1 estimator evaluations (R = 9).
- Scoring (registered test): pilot timing projected 66.0 session hours for all 375 runs and 54.9 for the 225 in scope.
