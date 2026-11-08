# Experiment 07 — case studies

Independent evidence that the analysis and the firing-interval adjustment
generalize beyond the synthetic benchmark families.

| Folder | Study | Key files |
|---|---|---|
| `illustrative/` | Illustrative Time Petri Net used to introduce the diagnosis and adjustment workflow | `model/`, `src/`, `scripts/`, `results/`, `fig/`, `MANIFEST.sha256` |
| `published_cases/` | Literature-grounded evaluation: Wang/Mahulea/Silva, *IEEE TAC* 2015 (7P/7T); Basile et al., *IEEE TAC* 2015; manufacturing subnet; state-class result checked against TINA 4.0.0 `-W` | `README.md`, `PROTOCOL.md`, `CASE_COMPARISON_README.md`, `models/`, `pipeline/`, `literature/`, `manufacturing/`, `figures/`, `MANIFEST.sha256` |
| `context_dataset/` | Public Kaupp et al. context dataset (Zenodo 4034867, CC BY-NC 4.0): integrity verification, cycle reconstruction, event recovery, concurrency reclassification, timing semantics | `scripts/`, `MANIFEST.sha256` |

## Headline results

* **Published net (Wang/Mahulea/Silva, *IEEE TAC* 2015):** the independent
  state-class graph equals TINA 4.0.0 `-W` (38 classes / 63 edges), and the
  reproduced firing-domain result matches the published example.
* **Manufacturing subnet:** imported read-only and analysed without modifying
  the published model.
* **Context dataset:** archive downloaded from Zenodo, MD5-verified
  (`ca10ec210b91159811f72959a868bade`), analysed read-only; the dataset is not
  redistributed here because its license is CC BY-NC 4.0.

## Reproduce

Each subfolder has its own README or protocol document. The published-case
evaluation and the context-dataset pipeline are driven by the scripts in
`pipeline/` and `scripts/`; the illustrative case ships its driver scripts and
results.

## Caveat

These are demonstrations, not a representative sample. They are reported
separately from the 8,280-evaluation scalability study and never pooled with it.
