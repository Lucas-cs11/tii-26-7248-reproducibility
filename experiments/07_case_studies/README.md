# Experiment 07 — case studies

Independent evidence that the analysis and the firing-interval adjustment
generalize beyond the synthetic benchmark families.

| Folder | Study | Outcome |
|---|---|---|
| `illustrative/` | Illustrative Time Petri Net introducing the diagnosis and adjustment workflow | fixed net and recorded analysis/adjustment outputs |
| `published_cases/` | Literature-grounded evaluation: Wang/Mahulea/Silva, *IEEE TAC* 2015 (7P/7T); Basile et al., *IEEE TAC* 2015; manufacturing subnet | state-class graph equals TINA 4.0.0 `-W` (38 classes / 63 edges); published firing-domain example reproduced; manufacturing subnet imported read-only |
| `context_dataset/` | Public Kaupp et al. context dataset (Zenodo 4034867, CC BY-NC 4.0) | not sufficient for a data-grounded task-completion case (documented in `context_dataset/analysis_summary.md`); auxiliary timing/concurrency evidence retained |

## Reproduce

Each folder has its own README with commands. The published-case evaluation and
the context-dataset pipeline are driven by the scripts in `pipeline/` and
`scripts/`.

## Caveat

These are demonstrations and one negative feasibility study, not a
representative sample. They are reported separately from the 8,280-evaluation
scalability study and never pooled with it.
