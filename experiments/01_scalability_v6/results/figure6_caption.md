**Figure 6. Structural scalability of the bounded ambiguity analysis on the v6 matrix.**
(a) Per-cell analysis time (SCG construction plus verification) against model
size, measured as places + transitions, for the pre-registered structural grid
(600 cells: 600 completed, 0 right-censored, 50 INC); the rank correlation on completed cells is Spearman
$\rho = 0.60$. (b) Paired WIP sensitivity for 360 base
models that differ only in the WIP bound (1080 cells: 628 completed, 452 right-censored, 30 INC): thin grey segments are
per-model trajectories through completed cells and the black line is the median
of completed cells at each WIP. Where both the WIP-1 reference and the WIP-$k$
cell completed, the median paired growth is 84$\times$ for WIP 2/WIP 1
($n = 171$ pairs) and 114$\times$ for WIP 3/WIP 1
($n = 97$ pairs); a pair with a censored WIP-2/3 cell only provides a
lower bound and is never treated as a measured ratio. (c) Depth-limit $L$
sensitivity at fixed model and horizon $H$ for 300 sweeps
(5400 cells: 3249 completed, 2151 right-censored, 0 INC); filled markers flag cells whose depth-limited synchronizer
produced candidate histories, i.e. cells that actually reached L-sensitive work,
which happens in 192 of the 300 sweeps at some
$L$. Time axes are logarithmic.

Right-censoring and inconclusive cells are shown explicitly in every panel. A
TIMEOUT cell is an observation right-censored at the 60 s cell cap: it is
drawn as an open triangle on the dashed ceiling line, is never plotted at its
wall-clock value as if it were a completion time, and is never imputed. INC
denotes a completed but inconclusive analysis (e.g. the SCG state-space limit);
it is drawn as a hollow diamond at its measured — non-zero — analysis time and
is counted separately from VER and AMB rather than being folded into them. All
P50/P90/P95 statistics and all medians are computed over COMPLETED cells only;
each panel reports the total $n$, the number of completed, censored and INC
cells. At the full 8,280-cell scale panels (b) and (c) switch to median + IQR of
completed cells together with an explicit censored-share line, so censored cells
contribute to the figure without being imputed as times. Cell analysis time is
an implementation- and runner-dependent measurement, used only for within-run
paired contrasts and never as an intrinsic model property. Data: protocol
v6-formal-1; all plotted values are distributed as `normalized_tasks.csv` /
`figure6_data.csv` and every statistic in the figure is recomputable from
`statistics.json`.
