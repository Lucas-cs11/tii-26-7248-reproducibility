#!/usr/bin/env python3
"""S5 industrial-case regression: rebuild the reference execution set (distinct
certificate normal/fault words) from the frozen complete-set enumeration and
compare with the stored evidence (87 / 88)."""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
CERTS = ROOT/"protocol"/"s5"/"before_complete_set.json"
STORED = ROOT/"protocol"/"s5"/"exact_sequence_preservation.json"
def main():
    d = json.loads(CERTS.read_text()); certs = d.get("certificates") or []
    normal = {tuple(c["N"]) for c in certs if "N" in c}; fault = {tuple(c["F"]) for c in certs if "F" in c}
    st = json.loads(STORED.read_text())
    out = {"certificates": len(certs), "distinct_normal": len(normal), "distinct_fault": len(fault),
           "stored_normal": st.get("reference_normal_sequences"), "stored_fault": st.get("reference_fault_sequences"),
           "normal_match": len(normal)==st.get("reference_normal_sequences"),
           "fault_match": len(fault)==st.get("reference_fault_sequences"),
           "stored_flags": [st.get("normal_reference_pass"), st.get("fault_reference_pass")]}
    out["PASS"] = bool(out["normal_match"] and out["fault_match"] and out["stored_flags"]==[True,True] and len(certs)>0)
    print(json.dumps(out, indent=2)); return 0 if out["PASS"] else 1
if __name__=="__main__": sys.exit(main())
