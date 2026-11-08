**Figure 6. Structural scalability of the bounded ambiguity analysis.**
(a) Per-evaluation analysis time (state-class construction plus verification)
against model size, measured as places + transitions, for the pre-registered
structural grid (600 evaluations: 600 completed, 0 wall-clock-capped, 50 INC);
the rank correlation on completed evaluations is Spearman rho = 0.60.
(b) Paired work-in-process sensitivity for 360 base models that differ only in
the work-in-process bound (1,080 evaluations: 628 completed, 452
wall-clock-capped, 30 INC): thin grey segments are per-model trajectories
through completed evaluations and the black line is the median of completed
evaluations at each bound. Where both the bound-1 reference and the bound-k
evaluation completed, the median paired growth is 84x for bound 2 over bound 1
(n = 171 pairs) and 114x for bound 3 over bound 1 (n = 97 pairs); a pair with a
capped member only provides a lower bound and is never treated as a measured
ratio. (c) Observable-history bound L on fixed models: filled markers mark the
evaluations that genuinely become L-sensitive (the candidate-word set appears);
the panel shows the onset and plateau of the retained-history workload.
Capped evaluations are drawn at the cap and are not treated as completions.
