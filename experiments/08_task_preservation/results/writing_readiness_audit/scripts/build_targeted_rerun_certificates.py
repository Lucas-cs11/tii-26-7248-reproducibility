#!/usr/bin/env python3
import csv,gzip,json,shutil
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]/'TARGETED_RERUN_CERTIFICATES'
OUT.mkdir(parents=True,exist_ok=True)
DATA=Path(__file__).resolve().parents[3]/'data/frozen'
cases=[
 ('case_1','fs_m3_j2_k2_w2_ur30_fl4_wf10_ar10_s11',1,
  '{"n_machines":3,"n_parts":2,"ops_per_part":2,"wip_bound":2,"unobservable_ratio":0.3,"fault_locations":4,"interval_width_factor":1.0,"adjustable_ratio":0.1,"seed":11}',10,36.0),
 ('case_2','fs_m4_j2_k2_w2_ur30_fl2_wf15_ar25_s1',2,
  '{"n_machines":4,"n_parts":2,"ops_per_part":2,"wip_bound":2,"unobservable_ratio":0.3,"fault_locations":2,"interval_width_factor":1.5,"adjustable_ratio":0.25,"seed":1}',10,39.0),
]
with gzip.open(DATA/'full_adjustment_cpgld.csv.gz','rt') as handle:
    frozen={r['evaluation_id']:r for r in csv.DictReader(handle) if r['evaluation_id'] in {c[1] for c in cases}}
for label,eid,index,params,L,H in cases:
    target=OUT/label; target.mkdir(exist_ok=True)
    raw=json.loads(Path(f'/tmp/reexec_{index}.json').read_text())
    (target/'raw_output.json').write_text(json.dumps(raw,indent=2)+'\n')
    (target/'frozen_record.json').write_text(json.dumps(frozen[eid],indent=2)+'\n')
    command=(f'<FROZEN_ENV_PYTHON> <REPO>/experiments/08_task_preservation/code/run_case_audit.py '
             f'cpgld {eid} \'{params}\' {L} {H} \'<EXPECTED_RECORD_JSON>\'\n')
    (target/'command.txt').write_text(command)
    rc=raw['reconstruction']; f=frozen[eid]
    validation={
      'evaluation_id':eid,'exit_code':0,'input_model_hash':raw['initial_model_hash'],
      'actual_wall_s':raw['wall_s'],'fresh_verdict':rc['fresh_verdict'],'fresh_certificates':rc['fresh_certs'],
      'frozen_final_model_hash':f['final_model_hash'],'rerun_final_model_hash':rc['final_model_hash'],
      'hash_match':rc['final_model_hash']==f['final_model_hash'],
      'frozen_modified_transition_count':int(f['modified_transition_count']),
      'rerun_modified_transition_count':rc['modified_transition_count'],
      'modified_count_match':int(f['modified_transition_count'])==rc['modified_transition_count'],
      'frozen_CI':float(f['CI']),'rerun_CI':float(rc['CI']),
      'CI_match_with_tolerance_1e-9':abs(float(f['CI'])-float(rc['CI']))<1e-9,
      'task_path_pass':raw['predicate']['path_pass'],
      'task_psi_pass':raw['predicate']['psi_pass'],
      'note':'The original invocation used placeholder expected CI/modified fields; this independent validation compares actual rerun values against the frozen CSV.'
    }
    validation['PASS']=all(validation[k] for k in ('hash_match','modified_count_match','CI_match_with_tolerance_1e-9')) and rc['fresh_verdict']=='VER' and rc['fresh_certs']==0
    (target/'validation.json').write_text(json.dumps(validation,indent=2)+'\n')
    print(label,validation['PASS'])
