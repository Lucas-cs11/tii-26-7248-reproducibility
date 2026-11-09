#!/usr/bin/env python3
import argparse,csv,hashlib,json,subprocess,sys
from collections import Counter
from pathlib import Path
AUDIT=Path(__file__).resolve().parents[1]
EXP=AUDIT.parents[1]
METHODS=('cpgld','coquand','exhaustive')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--check-manifest',action='store_true'); args=ap.parse_args()
    checks=[]
    def check(name,condition,detail=''):
        checks.append({'check':name,'pass':bool(condition),'detail':str(detail)})
    # Recompute, rather than trusting stored totals.
    for script in ('recompute_statistics.py','build_auxiliary_tables.py','analyze_performance.py'):
        proc=subprocess.run([sys.executable,str(AUDIT/'scripts'/script)],capture_output=True,text=True)
        check(f'{script}_exit_zero',proc.returncode==0,proc.stderr[-500:])
    stats=json.loads((AUDIT/'statistics.json').read_text())
    cov=stats['coverage']; all_stats=stats['all']; methods=stats['methods']
    check('record_count_identity',cov['records']==3*cov['pilot_evaluations'],cov)
    check('unique_records',cov['records']==cov['unique_evaluation_method'] and cov['duplicates']==0)
    for metric in ('fresh_successes','path_pass','psi0','psi5','psi10'):
        check(f'all_{metric}_sum',all_stats[metric]==sum(methods[m]['predicate_checked' if metric=='fresh_successes' else metric] for m in METHODS))
    check('fresh_cohort_partition',all_stats['fresh_successes']==stats['cohorts']['original_success_again']['n']+stats['cohorts']['flips']['n'])
    check('paired_common_original_subset',stats['paired']['common_original_success_evaluations']<=stats['paired']['common_evaluations'])
    check('paired_no_discordance',all(v==0 for v in stats['paired']['discordant_fresh_common'].values()))
    # Verify every CSV rate against its integer numerator and denominator.
    with (AUDIT/'FINAL_TASK_PRESERVATION_STATISTICS.csv').open() as handle:
        rows=list(csv.DictReader(handle))
    bad=[]
    for row in rows:
        n=int(row['numerator']); d=int(row['denominator']); r=float(row['rate'])
        if d<=0 or n<0 or n>d or abs(r-n/d)>1e-6: bad.append(row)
    check('final_csv_arithmetic',not bad,f'{len(rows)} rows; bad={bad[:2]}')
    with (AUDIT/'OUTCOME_FLIP_FINAL_CLASSIFICATION.csv').open() as handle:
        flips=list(csv.DictReader(handle))
    check('flip_row_count',len(flips)==stats['cohorts']['flips']['n'],len(flips))
    flip_status=Counter(r['original_status'] for r in flips)
    expected=Counter()
    for method in METHODS:
        expected.update(methods[method]['flips_by_original_status'])
    check('flip_status_reconciliation',flip_status==expected,dict(flip_status))
    with (AUDIT/'DECISION_STATUS_AUDIT.csv').open() as handle:
        decisions=list(csv.DictReader(handle))
    check('decision_audit_coverage',len(decisions)==cov['records'],len(decisions))
    check('path_fail_lp_caveat_present',all(r['lp_decision_interpretation']=='NONE_STATUS_CONFLATES_INFEASIBLE_AND_NUMERICAL_UNKNOWN'
          for r in decisions if r['path_pass']=='False'))
    # Representative cases.
    c1=AUDIT/'REPRESENTATIVE_EXACT_CERTIFICATES/fs_m2_j2_k4_w1_ur50_fl4_wf5_ar25_s1/certificate.json'
    c2=AUDIT/'REPRESENTATIVE_EXACT_CERTIFICATES/fs_m3_j1_k2_w2_ur50_fl1_wf15_ar50_s7/certificate.json'
    for label,path in (('case1',c1),('case2',c2)):
        check(f'{label}_certificate_exists',path.is_file(),path)
    if c1.is_file() and c2.is_file():
        d1=json.loads(c1.read_text()); d2=json.loads(c2.read_text())
        for label,d in (('case1',d1),('case2',d2)):
            rc=d['reconstruction']
            check(f'{label}_fresh_complete_ver',rc['fresh_verdict']=='VER' and rc['fresh_certificates']==0 and rc['fresh_enumeration_complete'] is True)
            check(f'{label}_hash_match',rc['hash_match'] is True)
            check(f'{label}_complete_models',bool(d['original_model']) and bool(d['candidate_model']))
        check('case1_path_fails',d1['predicate']['path_pass'] is False)
        lost_statuses=[v for v in d1['numeric_status_for_lost_words'].values()]
        check('case1_direct_infeasible_statuses',len(lost_statuses)==2 and all(v['min_status']=='INFEASIBLE' and v['max_status']=='INFEASIBLE' for v in lost_statuses))
        baseline_fault={tuple(w):iv for w,iv in d1['baseline_completion_intervals']['fault']}
        check('case1_lost_words_originally_feasible',all(tuple(v['word']) in baseline_fault for v in d1['predicate']['fault_rows'] if v['status']=='LOST'))
        check('case2_all_predicates_pass',d2['predicate']['path_pass'] and all(d2['predicate']['psi_pass'].values()))
        check('case2_zero_normal_degradation',all(row['delta']=='0' for row in d2['predicate']['normal_rows']))
    # Same-model alternative verified candidates under the performance predicate.
    alt_c=AUDIT/'ALTERNATIVE_CANDIDATE_AUDIT/cpgld/certificate.json'
    alt_q=AUDIT/'ALTERNATIVE_CANDIDATE_AUDIT/coquand_certificate.json'
    check('alternative_pair_exists',alt_c.is_file() and alt_q.is_file())
    if alt_c.is_file() and alt_q.is_file():
        ac=json.loads(alt_c.read_text()); aq=json.loads(alt_q.read_text())
        check('alternative_same_nominal_model',ac['initial_model_hash']==aq['initial_model_hash'])
        check('alternative_both_fresh_ver',all(d['reconstruction']['fresh_verdict']=='VER' and d['reconstruction']['fresh_certificates']==0 and d['reconstruction']['hash_match'] for d in (ac,aq)))
        check('alternative_predicate_discordance',not ac['predicate']['psi_pass']['0'] and not ac['predicate']['psi_pass']['5'] and ac['predicate']['psi_pass']['10'] and all(aq['predicate']['psi_pass'].values()))
        check('alternative_paths_retained',ac['predicate']['path_pass'] and aq['predicate']['path_pass'])

    # Targeted reruns: raw output, independent validation, and full adjusted model.
    for case in ('case_1','case_2'):
        root=AUDIT/'TARGETED_RERUN_CERTIFICATES'/case
        check(f'{case}_rerun_files',all((root/name).is_file() for name in ('raw_output.json','validation.json','command.txt','full_model_certificate.json')))
        if (root/'validation.json').is_file():
            v=json.loads((root/'validation.json').read_text()); check(f'{case}_rerun_pass',v['PASS'] is True,v)
    # Coquand: do not require the frozen mismatch to disappear; require honest evidence.
    cq=AUDIT/'COQUAND_CASE_RESOLUTION/validation.json'
    check('coquand_validation_exists',cq.is_file())
    if cq.is_file():
        v=json.loads(cq.read_text())
        check('coquand_current_runners_agree',v['runners_currently_agree'] and v['both_current_verified'])
        check('coquand_unresolved_not_hidden',v['current_original_runner_matches_frozen'] is False and v['not_equivalent_optimal_proof'])
    # Delivery text must not contain personal absolute paths or obvious credentials.
    personal=[]
    personal_marker='/'+'Users'+'/'
    for path in AUDIT.rglob('*'):
        if path.is_file() and path.suffix in ('.md','.py','.sh','.txt','.json','.csv'):
            try: text=path.read_text()
            except UnicodeDecodeError: continue
            if personal_marker in text: personal.append(str(path.relative_to(AUDIT)))
    check('no_personal_absolute_paths',not personal,personal)
    if args.check_manifest:
        manifest=AUDIT/'MANIFEST.sha256'
        check('manifest_exists',manifest.is_file())
        if manifest.is_file():
            listed={}; malformed=[]
            for line in manifest.read_text().splitlines():
                if not line.strip(): continue
                try: digest,name=line.split('  ',1); listed[name]=digest
                except ValueError: malformed.append(line)
            actual={str(p.relative_to(AUDIT)):p for p in AUDIT.rglob('*') if p.is_file() and p.name!='MANIFEST.sha256' and '__pycache__' not in p.parts}
            check('manifest_no_malformed',not malformed,malformed)
            check('manifest_complete',set(listed)==set(actual),{'missing':sorted(set(actual)-set(listed))[:10],'extra':sorted(set(listed)-set(actual))[:10]})
            bad=[name for name,digest in listed.items() if name in actual and name!='VALIDATION_REPORT.json' and hashlib.sha256(actual[name].read_bytes()).hexdigest()!=digest]
            check('manifest_hashes',not bad,bad[:10])
    report={'PASS':all(c['pass'] for c in checks),'checks':checks,
            'records':cov['records'],'primary_cohort_n':stats['cohorts']['exact_reconstruction']['n'],
            'all_fresh_success_n':all_stats['fresh_successes']}
    print(json.dumps(report,indent=2))
    return 0 if report['PASS'] else 1
if __name__=='__main__': sys.exit(main())
