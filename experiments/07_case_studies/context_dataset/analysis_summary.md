# Public context dataset — analysis summary

## Source and integrity

* Kaupp et al., Zenodo record 4034867 (DOI 10.5281/zenodo.4034867), archive
  `kaupp_context_dataset.zip`, 23,474,033 bytes, MD5
  `ca10ec210b91159811f72959a868bade`, license **CC BY-NC 4.0**.
* The archive is downloaded from its original source and never redistributed
  here. It contains 29 members: four scenario directories with 24 CSV files and
  five further files.

## What the data contain

* Four scenarios of asynchronous PLC value changes: 377k–454k rows per
  scenario, 33,056 distinct NodeIds, of which only 2,694–2,710 change state
  during the recorded window; the rest are static configuration variables.
* Five equipment logs per scenario are **sensor logger** files (temperature,
  pressure, light, acceleration, gyroscope, magnetic field); they carry no
  product, order or shuttle identifier and no discrete event labels.

## Outcome (reported honestly)

**The archive is not sufficient to construct a data-grounded task-completion
Time Petri Net case:**

* no product/order/pallet/shuttle identity in any log, so a first-entry task
  completion cannot be defined (the recording interval is not a task boundary);
* the press step alternates long/short modes, so treating it as a single
  physical operation would be an unverified modelling assumption;
* all recovered events are internal PLC step states — there is no observable
  alphabet that would define which events are observable versus unobservable
  for the paper's formulation;
* no PLC symbol documentation, engineering range or safety limit is
  distributed, so firing-interval adjustment authority cannot be established.

## Evidence retained as auxiliary results

* measured activity durations per node (median/P5/P95 over fully observed
  windows), as measured durations, not calibrated firing intervals;
* genuine between-part production loops (relay mount 15×, protection module
  15×, robot program 31×, press chains 15–31×);
* observed controller-state overlap and station concurrency between robot, press
  and shuttle controllers (e.g. 43 overlapping press/robot pairs, max 31.5 s);
* 12 anonymous assembly units, each with one relay mount and one protection
  module.

## Files

`results/` — summary tables and JSON inventories used above (activity windows,
cycle summary, concurrency overlaps, node activity inventory, signal
classification, dataset metadata). The analysis scripts are in `scripts/`; the
complete raw tables remain in the archived companion repository.
