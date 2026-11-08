# Experiment 07 — case studies

Independent evidence that the verifier and the firing-interval adjustment
generalize beyond the synthetic benchmark families.

## Contents

| Folder | Study | Key files |
|---|---|---|
| `illustrative/` | Illustrative TPN case used to introduce the diagnosis/adjustment workflow | `model/`, `src/`, `scripts/`, `results/`, `fig/`, `MANIFEST.sha256` |
| `published_cases/` | Literature-grounded evaluation: Wang/Mahulea/Silva TAC 2015 (7P/7T), Basile TAC 2015, JAS 2026 manufacturing subnet; independent SCG checked against TINA 4.0.0 `-W` | `README.md`, `PROTOCOL.md`, `CASE_COMPARISON_README.md`, `models/`, `pipeline/`, `literature/`, `manufacturing/`, `figures/`, `reports/`, `MANIFEST.sha256` |
| `context_dataset/` | Public Kaupp et al. context dataset (Zenodo 4034867, CC BY-NC 4.0): authenticity check, cycle reconstruction, event recovery, concurrency reclassification, timing semantics, go/no-go | `scripts/`, `results/*.md`, `MANIFEST.sha256` |

## Headline claims

* **Published cases:** for the Wang/Mahulea/Silva TAC 2015 net, the independent
  SCG equals TINA 4.0.0 `-W` (38 classes / 63 edges), and the reproduced
  firing-domain result matches Table 4.1 of the published example.
* **Manufacturing subnet:** the JAS 2026 manufacturing subnet is imported
  read-only and analyzed without modifying the published model.
* **Context dataset:** the archive is downloaded from Zenodo, MD5-verified
  (`ca10ec210b91159811f72959a868bade`), and analyzed read-only; the dataset is
  **not redistributed** here (its license is CC BY-NC 4.0).

## Reproduce

Each subfolder has its own README or protocol document. The published-case
evaluation and the context-dataset pipeline are driven by the scripts in their
`pipeline/`/`scripts/` folders and were executed on GitHub Actions; the
illustrative case has `scripts/` and `results/` checked in.

## Caveat

These are case-study demonstrations, not a representative sample: they are
reported separately from the 8,280-cell matrix and never pooled with it.
