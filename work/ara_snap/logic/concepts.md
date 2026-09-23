# Concepts

Notation follows Table 4 of the paper (Appendix A.2): c, r, j, i index configuration, replicate run, benchmark and item; N, R, K are configuration, replicate and benchmark counts, with values 125, 3 and 10 on DataDecide.

## SNAP (Seed Noise Across Phenotypes)
- **Notation**: $\widehat\Lambda=\sqrt{\sum_c T_c/\sum_c U_c}$
- **Definition**: The paper's cross-half moment estimator of item-general run covariance between benchmark scores, adapted from repeated-measurement constructions; "phenotype" names what the paper calls a trait. Algorithm 1 gives the measurement recipe.
- **Boundary conditions**: The name is kept although DataDecide replicates differ in checkpoint step, training budget and seed, so the empirical target is run covariance rather than seed-only covariance.
- **Related concepts**: Cross-half statistics, Inflation factor, Trait

## Trait
- **Notation**: $y^{\mathrm{marg}}_{crj}$, $y^{\mathrm{acc}}_{crj}$
- **Definition**: A benchmark-level score for run r of configuration c on benchmark j: the item average of per-byte margins or of correctness indicators, with MMLU macro-averaged over its 57 subjects.
- **Boundary conditions**: Defined per item set (half A, half B, or bank); a trait with negative estimated run variance is retained in the primary estimand but dropped from standardised diagnostics.
- **Related concepts**: Per-byte margin, SNAP

## Per-byte margin
- **Notation**: $m_{crji}=\ell(\mathrm{gold}_i)/\mathrm{bytes}(\mathrm{gold}_i)-\max_{v\ne \mathrm{gold}_i}\ell(v_i)/\mathrm{bytes}(v_i)$; $a_{crji}=\mathbf 1\{m_{crji}>0\}$
- **Definition**: Summed answer log-likelihood per byte of the gold answer minus the largest per-byte log-likelihood among alternatives (Equation 1); accuracy thresholds this margin at zero, with a zero margin treated as incorrect.
- **Boundary conditions**: Multiplying every margin by ten leaves Lambda unchanged to nine decimal places; bounded or standardised transforms of the margin change the benchmark weights and the estimate (supplement Table 7).
- **Related concepts**: Trait, Information ratio

## Half-score measurement model
- **Notation**: $y^H_{crj}=\mu^H_{cj}+E_{crj}+\varepsilon^H_{crj}$, $H\in\{A,B\}$
- **Definition**: Each half score is a half-specific mean plus a run deviation shared by both item populations plus item-dependent error.
- **Boundary conditions**: Unbiasedness assumes i.i.d. run effects within a configuration and item errors with zero cross-half covariance; shared passages, duplicate content and item effects shared across benchmarks violate the second condition.
- **Related concepts**: Run covariance, Item-general versus fixed-bank run variance

## Run covariance
- **Notation**: $\Sigma_{E,c}$, $\Sigma_E=N^{-1}\sum_c\Sigma_{E,c}$
- **Definition**: Covariance matrix of run deviations E_crj across benchmarks within configuration c, averaged across configurations.
- **Boundary conditions**: The finite-sample moment estimate is symmetric but need not be positive semidefinite; the accuracy correlation estimate has an entry of 1.296 and an eigenvalue of -0.55.
- **Related concepts**: Cross-half statistics, Effective covariance coefficient

## Centred half score
- **Notation**: $d^H_{crj}=y^H_{crj}-R^{-1}\sum_s y^H_{csj}$, $g^H_{cr}=K^{-1}\sum_j d^H_{crj}$
- **Definition**: Half score centred across the R replicate runs of its configuration, and its battery average.
- **Boundary conditions**: Implemented as a projection onto an orthonormal basis of mean-zero run contrasts (Appendix D.7); without centring, raw products include squared configuration means.
- **Related concepts**: Cross-half statistics

## Cross-half statistics
- **Notation**: $T_c=\frac{1}{R-1}\sum_r g^A_{cr}g^B_{cr}$, $U_c=\frac{1}{K^2(R-1)}\sum_{j,r}d^A_{crj}d^B_{crj}$
- **Definition**: T_c estimates $K^{-2}\mathbf 1^{\mathsf T}\Sigma_{E,c}\mathbf 1$ (aggregate covariance) and U_c estimates $K^{-2}\operatorname{tr}\Sigma_{E,c}$ (diagonal-only contribution).
- **Boundary conditions**: Each configuration's U_c uses two replicate degrees of freedom and can be near zero or negative, which is why sums are pooled before the ratio.
- **Related concepts**: Inflation factor, Centred half score

## Inflation factor
- **Notation**: $\Lambda^2=\mathbf 1^{\mathsf T}\Sigma_E\mathbf 1/\operatorname{tr}\Sigma_E=1+(K-1)\bar r_E$; $\Lambda_M$, $\Lambda_A$ on margins and accuracy
- **Definition**: Ratio of the standard deviation of the battery average under the full covariance to its value under independent deviations at the same average variance, $\Lambda=\sigma_{\mathrm{agg}}/\sigma_{\mathrm{indep}}$.
- **Boundary conditions**: A property of a fixed battery and weighting; a single positive-variance benchmark has Lambda = 1; the ratio and its square root are not unbiased; a negative lower squared endpoint leaves the square-root endpoint undefined.
- **Related concepts**: Effective covariance coefficient, Effective benchmark count

## Effective covariance coefficient
- **Notation**: $\bar r_E=\sum_{j\ne k}\Sigma_E(j,k)/((K-1)\operatorname{tr}\Sigma_E)$
- **Definition**: Off-diagonal covariance normalised by the trace (Equation 6); equals the mean off-diagonal correlation when marginal variances are equal, and $\bar r_E=a_\sigma\bar r_{\mathrm{weighted}}$ with $a_\sigma\in[0,1]$ otherwise.
- **Boundary conditions**: Two perfectly correlated traits with standard deviations one and two give 0.8 against a weighted mean correlation of one; undefined for K = 1.
- **Related concepts**: Inflation factor

## Effective benchmark count
- **Notation**: $K_{\mathrm{eff}}=K/\Lambda^2$
- **Definition**: Number of independent benchmarks with the same marginal RMS deviation whose average would be as variable as the measured battery average.
- **Boundary conditions**: Can exceed K when aggregate off-diagonal covariance is negative; does not count independent information sources and differs from the spectral participation ratio (3.57 on nine margin traits, 3.62 on eight accuracy traits after clipping).
- **Related concepts**: Inflation factor, Spectral participation ratio

## Aggregate standard deviation
- **Notation**: $\sigma^2_{\mathrm{agg}}=\bar\sigma^2_E[1/K+(K-1)\bar r_E/K]$, $\sigma^2_{\mathrm{indep}}=\bar\sigma^2_E/K$
- **Definition**: Run standard deviation of the battery mean under the fitted covariance, in margin units for margins and fractions for accuracy.
- **Boundary conditions**: A larger Lambda can accompany a smaller sigma_agg, as BoolQ removal shows.
- **Related concepts**: Inflation factor, Flip probability

## Reliability (cross-half, per trait)
- **Notation**: $\widehat\sigma^2_E/(\widehat\sigma^2_E+\widehat\sigma^2_{\mathrm{noise}})$; aggregate $\rho_g=\Lambda^2/(\Lambda^2+\bar v)$
- **Definition**: Share of a trait's half-score variance attributable to run deviations; negative when the estimated run component is negative.
- **Boundary conditions**: Reliability means do not estimate inflation; diagnostics only, not inputs to the headline ratio.
- **Related concepts**: Trait, Information ratio

## Item-general versus fixed-bank run variance
- **Notation**: none
- **Definition**: SNAP targets run deviations that generalise across item halves; the run variance of a fixed evaluation bank can additionally retain run-by-item variation that enters the item error in the measurement model.
- **Boundary conditions**: Bounding fixed-battery inflation by the item-general factor requires a diagonal additional covariance D with $\Lambda^2_D=(\mathbf 1^{\mathsf T}\Sigma_E\mathbf 1+\operatorname{tr}D)/(\operatorname{tr}\Sigma_E+\operatorname{tr}D)$.
- **Related concepts**: Half-score measurement model, Cross-bank estimate

## Auxiliary-run contrast
- **Notation**: contrast between the two auxiliary runs of a configuration
- **Definition**: Estimate that uses only the auxiliary-two-versus-auxiliary-three contrast, removing the default-versus-auxiliary batch component that the three-run estimate carries.
- **Boundary conditions**: Does not remove differences shared with checkpoint schedules; has fewer degrees of freedom and wider intervals.
- **Related concepts**: Run covariance

## Wild cluster bootstrap-t
- **Notation**: $\psi_g=\sum_{c\in g}(T_c-\widehat\theta U_c)/\sum_c U_c$; $T^*_c=\widehat\theta U_c+v_{bg(c)}(T_c-\widehat\theta U_c)$, $v\in\{-1,+1\}$
- **Definition**: Studentised bootstrap on the squared ratio theta with Rademacher signs per recipe cluster, fixed observed denominator, 4,999 draws, seed zero; endpoints square-rooted.
- **Boundary conditions**: Coverage 0.928 to 0.954 across twelve simulated populations; falls under band-shared run effects; requires at least max(100, 0.9B) finite draws.
- **Related concepts**: Centred cluster test inversion, Delete-one-seed jackknife

## Centred cluster test inversion
- **Notation**: accepted set of Lambda values not rejected by a centred cluster test
- **Definition**: Interval added later; covers 0.935 to 0.956 in a 10,000-replicate repeat; gives [1.095, 1.323] for margins and [0.995, 1.162] for accuracy on the observed data.
- **Boundary conditions**: The accepted set can be unbounded (bounded in 23,999 of 24,000 simulated datasets); unbounded for PolyPythias accuracy.
- **Related concepts**: Wild cluster bootstrap-t

## Delete-one-seed jackknife
- **Notation**: $\widehat{\mathrm{se}}^2=\frac{R-1}{R}\sum_r(\widehat\theta_{(-r)}-\bar\theta)^2$, critical value $t_{0.975}(R-1)$
- **Definition**: Primary interval for PolyPythias rules R1 and R2, where nine seeds are the replicate unit and five size clusters are too few for the wild bootstrap; formed on theta and square-rooted, eight degrees of freedom.
- **Boundary conditions**: Requires the run index to mean the same seed in every configuration.
- **Related concepts**: Registered reading rule, Cross-bank estimate

## Cross-bank estimate and within-minus-cross difference
- **Notation**: half A = all bank-one items, half B = all bank-two items; $\log\widehat\theta_{\mathrm{within}}-\log\widehat\theta_{\mathrm{cross}}$
- **Definition**: Inflation computed with halves drawn from two disjoint item banks on the same runs, removing any component the halves share only because they come from one item set; the within-minus-cross log difference is read with a delete-one-seed jackknife.
- **Boundary conditions**: The banks also differ in split, item count (6,808 against 37,682) and exemplar overlap, which enters the cross-bank estimate; results pending.
- **Related concepts**: Item-general versus fixed-bank run variance, Registered reading rule

## Cross-format diagnostic
- **Notation**: masked sum retaining the diagonal and only off-diagonal pairs in different formats (54 of 90 ordered pairs)
- **Definition**: Diagnostic inflation with within-format off-diagonal covariance removed; null reference one when retained covariances vanish.
- **Boundary conditions**: The masked matrix need not be positive semidefinite or represent a realisable average; format and content are confounded since each benchmark has one format.
- **Related concepts**: Run covariance, Inflation factor

## Registered reading rule
- **Notation**: pass iff lower 95% interval limit > 1
- **Definition**: A decision rule fixed before scoring: the held-out test (four tasks, wild recipe-cluster interval, 530M/750M/1B scope) and R1/R2 for PolyPythias (jackknife intervals). Registration timestamps are not independently corroborated.
- **Boundary conditions**: The held-out rule reads interval width through the lower limit, so wide intervals fail it even with point estimates near the original.
- **Related concepts**: Delete-one-seed jackknife, Cross-bank estimate

## Information ratio
- **Notation**: $p(1-p)/\phi(z_0)^2$, $z_0=\Phi^{-1}(1-p)$
- **Definition**: Ratio of accuracy to margin item-noise variance per unit squared sensitivity to an infinitesimal additive shift in Gaussian item margins (Equation 7); about 1.66 at p = 0.35, minimum pi/2.
- **Boundary conditions**: Describes only the Gaussian location model; the planned lower threshold of 1.4 lies below the pi/2 floor and can't falsify the model.
- **Related concepts**: Per-byte margin, Reliability

## Flip probability
- **Notation**: $P_{\mathrm{flip}}$ under a Gaussian comparison model at aggregate noise sigma_agg
- **Definition**: Probability that a noisy aggregate gap has the opposite sign of the true gap; with accuracy sigma_agg 0.00514, $P_{\mathrm{flip}}>0.05$ for a true gap below 0.01196.
- **Boundary conditions**: Observed gaps are noisy, so counts of observed gaps below the threshold do not bound the fraction of small true gaps.
- **Related concepts**: Aggregate standard deviation

## Spectral participation ratio
- **Notation**: $(\sum\lambda_i)^2/\sum\lambda_i^2$ over eigenvalues of the correlation estimate; recipe-influence participation ratio over squared influences
- **Definition**: Eigenvalue-spread summary (3.57 margins, 3.62 accuracy after clipping) and, separately, a concentration summary of recipe influence (3.08 margins, 9.02 accuracy).
- **Boundary conditions**: Not a count of independent clusters or population directions; undefined as a validated count for the indefinite accuracy matrix.
- **Related concepts**: Effective benchmark count
