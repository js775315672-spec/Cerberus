"""Independently regrade public D3 evidence; never authorize promotion."""
import hashlib
import json
import math
import os
from pathlib import Path
import statistics
import zipfile
from agent.d2_public_audit import open_archive, regrade, CYCLE, CANDIDATE, ARCHIVE, SOURCE

F_RUN = "45915066932"
F_COMMIT = "4265f7812ad3bd43da4841628f19f4c6c55122e0"
C_RUN = "45914645339"
C_COMMIT = "308d0b808c20ae02350facc6eb419642b3bc037e"
C_ZIP = "c23d35a420805dc4071eec54a07035b256c6188727773ae3c4c91f038c2d2ce7"
C_REPORT = "3483230a90529e6f1642d015e5eb868cadb9942ae7dea763b72800c928db2e10"
SIZES = ("0.5b","1.5b","3b")
MODES = ("direct","hybrid")
KNOWN = {frozenset((11+3*i,2+i%7)) for i in range(30)}

def check(ok, msg):
    if not ok: raise ValueError(msg)

def hash_bytes(data):
    return hashlib.sha256(data).hexdigest()

def read(data):
    def pairs(values):
        out={}
        for key,value in values:
            check(key not in out,"duplicate key")
            out[key]=value
        return out
    return json.loads(data,object_pairs_hook=pairs,parse_constant=lambda v:(_ for _ in ()).throw(ValueError("nonfinite")))

def canonical(x):
    return json.dumps(x,sort_keys=True,ensure_ascii=False,allow_nan=False).encode()

def evidence_cases(ab):
    correct=[]; wrong=[]
    for i,row in enumerate(ab["rows"]):
        a,b=11+3*i,2+i%7
        seen=next(x["output"].strip() for x in row["observations"] if x["variant"]=="compact")
        case=dict(id=row["group_id"],a=a,b=b,observed=seen)
        (correct if seen==str(a+b) else wrong).append(case)
    check(len(correct)>=3 and len(wrong)>=3,"insufficient balanced set")
    return [s for pair in zip(correct[:3],wrong[:3]) for s in pair]

def independent_grade(row,case):
    mode=row["mode"]; exp=str(case["a"]+case["b"]); obs=case["observed"]
    mismatch=(exp!=obs)
    try:
        x=read(row["raw"])
        names={"risk","test_a","test_b","rationale"}
        if mode=="direct": names|={"expected","observed","mismatch","test_expected"}
        check(type(x) is dict and set(x)==names,"schema")
        risk="possible_digit_integer_conflict" if mismatch else "no_mismatch_in_this_case"
        check(x["risk"]==risk,"risk")
        a,b=x["test_a"],x["test_b"]
        check(type(a) is int and type(b) is int and 10<=a<=90 and 1<=b<=9 and frozenset((a,b)) not in KNOWN,"novel test")
        h=x["rationale"]
        check(type(h) is str and 12<=len(h.strip())<=1200,"rationale length")
        lower=h.lower()
        check(("digit" in lower or "integer" in lower) if mismatch else any(w in lower for w in ("correct","match","equal","no error","no discrepancy")),"rationale topic")
        if mode=="direct":
            check(x["expected"]==exp and x["observed"].strip()==obs and type(x["mismatch"]) is bool and x["mismatch"]==mismatch,"arithmetic")
            check(x["test_expected"]==str(a+b),"test arithmetic")
        return dict(pass_=True, expected=exp,mismatch=mismatch,risk=risk,test_a=a,test_b=b,test_expected=str(a+b),rationale=h)
    except (ValueError,KeyError,TypeError,AttributeError):
        return {"pass_":False}

def audit(obj,samples,model,run,commit,attempt):
    check(obj["model"]==model and len(obj["model_digest"])==64 and all(c in "0123456789abcdef" for c in obj["model_digest"]),"model identity")
    check(obj["cycle_id"]==CYCLE and obj["candidate_sha256"]==CANDIDATE and obj["archive_sha256"]==ARCHIVE and obj["cases"]==samples,"candidate drift")
    check(obj["run_id"]==run and obj["commit"]==commit and obj["run_attempt"]==attempt,"run identity")
    check(obj["status"]=="UNVERIFIED" and obj["promotion_allowed"] is False and len(obj["rows"])==12,"false approval or missing calls")
    stats={};results={}
    for mode in MODES:
        rs=[r for r in obj["rows"] if r["mode"]==mode]
        check([r["id"] for r in rs]==[c["id"] for c in samples],"sample order")
        graded=[]
        for r,c in zip(rs,samples):
            g=independent_grade(r,c)
            check(type(r["result"]["pass"]) is bool and g["pass_"]==r["result"]["pass"],"self-grade differs")
            if g["pass_"]:
                check({k:v for k,v in g.items() if k!="pass_"}=={k:v for k,v in r["result"].items() if k!="pass"},"derived finding differs")
            check(type(r["eval_count"]) is int and r["eval_count"]>0 and type(r["wall_seconds"]) in (int,float) and math.isfinite(r["wall_seconds"]) and r["wall_seconds"]>0 and r["model_vram_bytes"]==0,"measurement invalid")
            check(type(r["rss_sample_mib"]) in (int,float) and math.isfinite(r["rss_sample_mib"]) and r["rss_sample_mib"]>=0 and type(r["model_loaded_bytes"]) is int and r["model_loaded_bytes"]>0,"memory measurement invalid")
            graded.append(g)
        stats[mode]=dict(passed=sum(g["pass_"] for g in graded),total=6,median_seconds=round(statistics.median(r["wall_seconds"] for r in rs),4),max_sampled_rss_mib=round(max(r["rss_sample_mib"] for r in rs),2),model_loaded_mib=round(max(r["model_loaded_bytes"] for r in rs)/1048576,2))
        results[mode]=graded
    return stats,results

def zip_files(path,expected_names):
    with zipfile.ZipFile(path) as z:
        check(len(z.infolist())==len(expected_names) and set(z.namelist())==set(expected_names) and all(i.file_size<2_000_000 for i in z.infolist()),"archive member mismatch")
        return {name:z.read(name) for name in expected_names}

def main():
    candidate,ab,aa=open_archive(Path("d2-raw.zip"))
    _,_,metrics=regrade(ab,aa)
    samples=evidence_cases(ab)
    names=["summary.json","FENRIR_REPORT.json"]+[f"bench-{s}.json" for s in SIZES]
    fpath=Path("fenrir.zip")
    check(hash_bytes(fpath.read_bytes())==os.environ["F_ZIP_SHA256"],"Fenrir zip digest")
    payload=zip_files(fpath,names)
    report=read(payload["FENRIR_REPORT.json"]); summary=read(payload["summary.json"])
    check(report["run_id"]==F_RUN and report["reviewer_commit"]==F_COMMIT and report["run_attempt"]==os.environ["F_ATTEMPT"],"Fenrir report provenance")
    for key,val in (("cycle_id",CYCLE),("candidate_sha256",CANDIDATE),("archive_sha256",ARCHIVE),("source_commit",SOURCE),("status","UNVERIFIED"),("protected_grade","pending"),("promotion_allowed",False)):
        check(report[key]==val,"report identity "+key)
    check(report["summary_sha256"]==hash_bytes(payload["summary.json"]),"summary digest")
    check(summary["actual_calls"]==36 and summary["promotion_allowed"] is False and summary["candidate_sha256"]==CANDIDATE and summary["cycle_id"]==CYCLE,"summary identity")
    stats={};grades={};objects={}
    for size in SIZES:
        o=read(payload[f"bench-{size}.json"])
        objects[size]=o
        stats[size],grades[size]=audit(o,samples,"qwen2.5:"+size,F_RUN,F_COMMIT,os.environ["F_ATTEMPT"])
    check(stats==summary["stats"],"summary statistics differ")
    eligible=[(s,m) for s in SIZES for m in MODES if stats[s][m]["passed"]==6]
    check(bool(eligible),"no configuration passed")
    size,mode=min(eligible,key=lambda x:(SIZES.index(x[0]),stats[x[0]][x[1]]["median_seconds"],x[1]))
    check(summary["selected"]==[size,mode] and report["model"]=="qwen2.5:"+size and report["mode"]==mode and report["selected_stats"]==stats[size][mode] and report["model_digest"]==objects[size]["model_digest"],"selection mismatch")
    check(report["benchmark_sha256"]==hash_bytes(payload[f"bench-{size}.json"]),"benchmark digest")
    findings=[]
    for case,g in zip(samples,grades[size][mode]):
        check(g["pass_"],"failed selected case")
        findings.append(dict(group_id=case["id"],measured_expected=str(case["a"]+case["b"]),measured_observed=case["observed"],classification="hypothesis" if g["mismatch"] else "no_mismatch_observed",model_rationale=g["rationale"],proposed_test=[g["test_a"],g["test_b"],g["test_expected"]],test_executed=False))
    check(report["findings"]==findings,"findings mismatch")
    cpath=Path("cerberus.zip")
    check(hash_bytes(cpath.read_bytes())==C_ZIP,"prior replay ZIP digest")
    prior=zip_files(cpath,["CERBERUS_PUBLIC_REPLAY.json"])["CERBERUS_PUBLIC_REPLAY.json"]
    check(hash_bytes(prior)==C_REPORT,"prior replay report digest")
    replay=read(prior)
    check(replay["cycle_id"]==CYCLE and replay["candidate_sha256"]==CANDIDATE and replay["archive_sha256"]==ARCHIVE and replay["source_commit"]==SOURCE and replay["cerberus_run"]==C_RUN and replay["cerberus_commit"]==C_COMMIT,"prior replay provenance")
    check(replay["verdict"]=="PUBLIC_REPLAY_MATCH" and replay["exact_replay_matches"]==30 and replay["actual_replay_calls"]==30 and replay["promotion_allowed"] is False and replay["regrade"]==metrics,"prior replay inconsistency")
    check(os.environ["ATTESTATIONS_VERIFIED"]=="true","attestation gate missing")
    out=Path("out");out.mkdir(exist_ok=True)
    receipt={"cycle_id":CYCLE,"candidate_sha256":CANDIDATE,"source_commit":SOURCE,"fenrir_run":F_RUN,"fenrir_commit":F_COMMIT,"fenrir_report_sha256":hash_bytes(payload["FENRIR_REPORT.json"]),"fenrir_zip_sha256":os.environ["F_ZIP_SHA256"],"prior_replay_run":C_RUN,"prior_replay_report_sha256":C_REPORT,"cerberus_run":os.environ["GITHUB_RUN_ID"],"cerberus_commit":os.environ["GITHUB_SHA"],"selected":[size,mode],"independent_regrade_calls":36,"public_replay_matches":30,"findings":findings,"verdict":"PUBLIC_HANDOFF_VERIFIED","scope":"public artifact identity, benchmark rule and prior replay only; model hypotheses not confirmed","protected_grade":"pending","promotion_allowed":False}
    (out/"CERBERUS_D3_RECEIPT.json").write_bytes(canonical(receipt))
    print(json.dumps(receipt,ensure_ascii=False),flush=True)

if __name__=="__main__": main()
