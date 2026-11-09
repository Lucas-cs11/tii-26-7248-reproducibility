#!/usr/bin/env python3
import json
from fractions import Fraction
from pathlib import Path
EXP=Path(__file__).resolve().parents[3]
records=[json.loads(line) for path in sorted((EXP/'results/pilot_full').glob('shard_*.jsonl'))
         for line in path.read_text().splitlines() if line.strip()]
summary={}
for scope, rows in (
    ('all_path_pass', [r for r in records if r.get('fresh_success') and r.get('predicate',{}).get('path_pass')]),
    ('all_retained_normal_rows', [r for r in records if r.get('fresh_success') and 'predicate' in r]),
):
    comparisons=positive=over5=over10=zero_baseline=negative=0
    max_ratio=Fraction(-10**9); max_case=None
    for r in rows:
        for row in r['predicate']['normal_rows']:
            if row.get('status')!='RETAINED': continue
            if scope=='all_retained_normal_rows' and not r['predicate']['path_pass']:
                # Include retained normal rows in path-failing cases only in this scope.
                pass
            comparisons+=1
            base=Fraction(row['t_min_base']); new=Fraction(row['t_min']); delta=new-base
            if base==0:
                zero_baseline+=1
                ratio=Fraction(0) if delta==0 else None
            else:
                ratio=delta/base
            if delta<0: negative+=1
            if delta>0:
                positive+=1
                if ratio is not None and ratio>Fraction(5,100): over5+=1
                if ratio is not None and ratio>Fraction(10,100): over10+=1
                if ratio is not None and ratio>max_ratio:
                    max_ratio=ratio; max_case={'evaluation_id':r['evaluation_id'],'method':r['method'],
                                               't_min_base':str(base),'t_min':str(new),'relative_delta':str(ratio)}
    summary[scope]={'retained_normal_comparisons':comparisons,'positive_delta':positive,
        'negative_delta':negative,'zero_baseline':zero_baseline,'relative_delta_over_5pct':over5,
        'relative_delta_over_10pct':over10,'max_positive_relative_delta':str(max_ratio) if comparisons else None,
        'max_case':max_case}
(EXP/'results/writing_readiness_audit/performance_analysis.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
