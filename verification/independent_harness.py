#!/usr/bin/env python3
"""EIL-001 independent verification harness.

This harness is intentionally separate from the candidate's pytest suite.
It verifies candidate identity first, then performs independent behavioral
probes through public interfaces. Failures become findings; the candidate is
never modified.
"""
from __future__ import annotations
import argparse, hashlib, json, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

EXPECTED = "f4f1e93db44fd1cb9c4834ba4973f7834e3972f832c547437627db7ab176f62b"

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def run(cmd, cwd: Path) -> dict:
    p=subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    return {"command":cmd, "returncode":p.returncode, "stdout":p.stdout, "stderr":p.stderr}

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("candidate", type=Path, help="Frozen EIL-001 implementation-candidate ZIP")
    ap.add_argument("--out", type=Path, default=Path("verification/runs"))
    args=ap.parse_args()

    candidate=args.candidate.resolve()
    out=args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    observed=sha256(candidate)
    identity={"expected_sha256":EXPECTED,"observed_sha256":observed,"hash_match":observed==EXPECTED}
    (out/"SOURCE-IDENTITY.json").write_text(json.dumps(identity,indent=2)+"\n")
    if observed != EXPECTED:
        (out/"FINDING-SOURCE-HASH-MISMATCH.json").write_text(json.dumps({
            "finding":"SOURCE_HASH_MISMATCH",
            "expected":EXPECTED,
            "observed":observed,
            "action":"ABORT",
            "qualification_effect":"NONE"
        },indent=2)+"\n")
        return 2

    work=Path(tempfile.mkdtemp(prefix="eil-independent-"))
    try:
        with zipfile.ZipFile(candidate) as z:
            z.extractall(work)
        roots=[p for p in work.iterdir() if p.is_dir()]
        root=work/"EIL-001-v0.2" if (work/"EIL-001-v0.2").is_dir() else (roots[0] if len(roots)==1 else work)

        pytest_result=run([sys.executable,"-m","pytest","-q"],root)
        (out/"pytest.stdout").write_text(pytest_result["stdout"])
        (out/"pytest.stderr").write_text(pytest_result["stderr"])

        probe=root/"_eil_independent_probe.py"
        probe.write_text(r'''
import json, sys
from eil.core.models import Evidence, Qualification, EpistemicState, EvidenceLevel, Disposition
from eil.core.transition_engine import authorize_transition, TransitionRequest, TransitionRejected

def ev(cid,eid,prov): return Evidence(evidence_id=eid, claim_id=cid, description="independent", provenance_ref=prov)
def reject(name, req, results):
    try:
        authorize_transition(req); results.append({"claim":name,"result":"FAIL","reason":"unexpected authorization"})
    except TransitionRejected as e: results.append({"claim":name,"result":"PASS","observation":str(e)})
def accept(name, req, results):
    try: authorize_transition(req); results.append({"claim":name,"result":"PASS"})
    except Exception as e: results.append({"claim":name,"result":"FAIL","reason":type(e).__name__+":"+str(e)})

r=[]
s1=EpistemicState(EvidenceLevel.E1,Disposition.UNRESOLVED)
common=dict(subject_id="independent-c1",current_state=s1,
 requested_state=EpistemicState(EvidenceLevel.E2,Disposition.SUPPORTED),
 evidence=(ev("independent-c1","e1","source-A"),),
 required_conditions=("CRIT-E2-INDEPENDENT-REQUIREMENT","CRIT-E2-CONTROL-OR-COMPARISON"),
 alternatives_addressed=True,failure_conditions_present=True,provenance_intact=True)
accept("EIL-C-004-valid-transition-control",TransitionRequest(**common),r)
reject("EIL-C-003-wrong-claim",TransitionRequest(**{**common,"evidence":(ev("other-claim","e2","source-A"),)}),r)
reject("EIL-C-003-missing-provenance",TransitionRequest(**{**common,"evidence":(ev("independent-c1","e3",""),)}),r)
reject("EIL-C-006-qualification-is-not-evidence",TransitionRequest(**{**common,"evidence":(Qualification("q1","independent-c1",(),(),"QUALIFIED"),)}),r)
reject("EIL-C-004-generic-conditions",TransitionRequest(**{**common,"required_conditions":("arbitrary-condition",)}),r)

s2=EpistemicState(EvidenceLevel.E2,Disposition.SUPPORTED)
e3=dict(subject_id="independent-c1",current_state=s2,
 requested_state=EpistemicState(EvidenceLevel.E3,Disposition.SUPPORTED),
 evidence=(ev("independent-c1","e4","source-A"),ev("independent-c1","e5","source-A")),
 required_conditions=("CRIT-E3-REPLICATION-OR-INDEPENDENT-CONFIRMATION","CRIT-E3-PROVENANCE-TRACE"),
 alternatives_addressed=True,failure_conditions_present=True,provenance_intact=True)
reject("EIL-C-003-duplicate-provenance",TransitionRequest(**e3),r)
reject("EIL-C-007-ai-confidence",TransitionRequest(**{**e3,"evidence":(ev("independent-c1","e6","source-A"),ev("independent-c1","e7","source-B")),"authorization_basis":("AI_CONFIDENCE",)}),r)
print(json.dumps(r,indent=2))
sys.exit(0 if all(x["result"]=="PASS" for x in r) else 1)
''')
        probe_result=run([sys.executable,str(probe)],root)
        (out/"independent-probe.stdout").write_text(probe_result["stdout"])
        (out/"independent-probe.stderr").write_text(probe_result["stderr"])
        probe.unlink(missing_ok=True)

        result={
          "candidate_sha256":observed,
          "pytest_pass":pytest_result["returncode"]==0,
          "independent_probe_pass":probe_result["returncode"]==0,
          "claims_registered":["EIL-C-001","EIL-C-002","EIL-C-003","EIL-C-004","EIL-C-005","EIL-C-006","EIL-C-007","EIL-C-008"],
          "claims_proven_by_this_harness":["EIL-C-003","EIL-C-004","EIL-C-006","EIL-C-007"],
          "claims_not_yet_proven":["EIL-C-001","EIL-C-002","EIL-C-005","EIL-C-008"],
          "qualification":"NOT_ESTABLISHED",
          "human_ratification":"NOT_ESTABLISHED",
          "authority":"HUMAN_ONLY"
        }
        (out/"RUN-RESULT.json").write_text(json.dumps(result,indent=2)+"\n")
        return 0 if result["pytest_pass"] and result["independent_probe_pass"] else 1
    finally:
        shutil.rmtree(work,ignore_errors=True)

if __name__=="__main__":
    raise SystemExit(main())
