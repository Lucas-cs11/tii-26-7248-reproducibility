#!/usr/bin/env bash
set -euo pipefail
# Set these environment variables before running:
#   FROZEN_ENV_PYTHON = Python 3.11 with numpy 2.4.6 and scipy 1.16.2
#   FROZEN_ADJUSTMENT_ROOT = original firing_interval_adjustment directory
#   REPRO_REPO = tii-26-7248-reproducibility checkout
: "${FROZEN_ENV_PYTHON:?set FROZEN_ENV_PYTHON}"
: "${FROZEN_ADJUSTMENT_ROOT:?set FROZEN_ADJUSTMENT_ROOT}"
: "${REPRO_REPO:?set REPRO_REPO}"
P='{"n_machines":3,"n_parts":2,"ops_per_part":2,"wip_bound":2,"unobservable_ratio":0.5,"fault_locations":2,"interval_width_factor":0.5,"adjustable_ratio":0.1,"seed":6}'
E='fs_m3_j2_k2_w2_ur50_fl2_wf5_ar10_s6'
EXPECTED='{"status":"VERIFIED_SUCCESS","final_model_hash":"7868dcfd319e2666","modified_transition_count":2,"CI":"2.531250"}'
"$FROZEN_ENV_PYTHON" "$FROZEN_ADJUSTMENT_ROOT/tools/run_case.py" coquand "$E" "$P" 10 33.0
"$FROZEN_ENV_PYTHON" "$REPRO_REPO/experiments/08_task_preservation/code/run_case_audit.py" coquand "$E" "$P" 10 33.0 "$EXPECTED"
