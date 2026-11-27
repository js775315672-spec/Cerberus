"""Independent public evidence regrade and actual CPU replay; no admission."""
import hashlib
import json
import math
import os
from pathlib import Path
import statistics
import time
import zipfile

ARCHIVE = "10c9873b297f795df130de2f30b6618b5ed081c5f073193aa615d2bf659e0297"
CANDIDATE = "d6f516b6fea97f30441bf96c9051835a81b5b924d5315a3fba485456000c89ba"
SOURCE = "5c5b4a93be07e7dc39f355c1f6bbf2e978dafd50"
CYCLE = "45913964999-1"
MODEL = "Qwen/Qwen2.5-0.5B-Instruct"
REV = "7ae557604adf67be50417f59c2c2f167def9a775"
WEIGHT = "fdf756fa7fcbe7404d5c60e26bff1a0c8b8aa1f72ced49e7dd0210fe288fb7fe"

def require(ok, message):
    if not ok:
        raise ValueError(message)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def read_json(data):
    def unique(items):
        d = {}
        for k, v in items:
            require(k not in d, "duplicate JSON key")
            d[k] = v
        return d
    return json.loads(data, object_pairs_hook=unique,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite JSON")))

def open_archive(path):
    require(sha(path.read_bytes()) == ARCHIVE, "archive digest")
    with zipfile.ZipFile(path) as z:
        names = {"candidate/candidate.json", "candidate/ab.json", "candidate/aa.json", "input/public_30_pairs.json"}
        require(set(z.namelist()) == names and len(z.infolist()) == 4 and all(i.file_size < 2_000_000 for i in z.infolist()), "archive members")
        b = z.read("candidate/candidate.json")
        c = read_json(b)
        require(sha(b) == CANDIDATE and c["implementation_sha"] == SOURCE and c["cycle_id"] == CYCLE, "candidate identity")
        require(sha(c["prompt"].encode()) == c["candidate_sha"], "prompt digest")
        require(sha(z.read("input/public_30_pairs.json")) == c["parent_evidence_sha256"], "seed digest")
        reports = []
        for n in ("ab.json","aa.json"):
            b = z.read("candidate/"+n)
            require(sha(b) == c["raw_sha256"][n], "raw digest")
            reports.append(read_json(b))
    return c, *reports

def regrade(ab, aa):
    tasks = [{"group_id":f"public-arithmetic-{i+1:02d}", "question":f"What is {11+3*i} plus {2+i%7}? Answer with only the integer.", "expected":str(13+3*i+i%7)} for i in range(30)]
    task_hash = sha(json.dumps(tasks, sort_keys=True).encode())
    hits = {"verbose":0,"compact":0}
    tokens = {"verbose":0,"compact":0}
    latency = {"verbose":[],"compact":[]}
    new_errors = 0
    compact = {}
    aa_hits = [0,0]
    aa_drift = []
    for report, kind in ((ab,"ab"),(aa,"aa")):
        require(report["model_id"] == MODEL and report["resolved_revision"] == REV and report["weight_files"][0]["sha256"] == WEIGHT, "model identity")
        require(report["public_tasks_sha256"] == task_hash and len(report["rows"]) == 30, "task identity")
        require(report["pretrained_checkpoint_loaded"] is True and all(report[k] is False for k in ("weights_trained_this_run","gpu_lora_training_proven","independent_heldout_accuracy_proven")) and report["quality_gain"] is None and report["speed_gain"] is None, "false claims")
        for i,(task,row) in enumerate(zip(tasks,report["rows"])):
            require(all(row[k] == v for k,v in task.items()), "task drift")
            order = (["verbose","compact"] if i%2==0 else ["compact","verbose"]) if kind=="ab" else ["compact","compact"]
            obs = row["observations"]
            require(len(obs)==2 and [x["variant"] for x in obs]==order and (kind!="ab" or row["execution_order"]==order), "order")
            correct = {}
            for j,o in enumerate(obs):
                v=o["variant"]
                require(type(o["output"]) is str and bool(o["output"].strip()) and o["attention_mask_explicit"] is True, "output or mask")
                require(type(o["input_tokens"]) is int and o["input_tokens"]>0 and type(o["generated_tokens"]) is int and 1<=o["generated_tokens"]<=16, "tokens")
                require(type(o["elapsed_seconds"]) in (int,float) and math.isfinite(o["elapsed_seconds"]) and o["elapsed_seconds"]>0, "latency")
                match=o["output"].strip()==task["expected"]
                require(type(o["exact_public_answer_match"]) is bool and match==o["exact_public_answer_match"], "forged answer label")
                if kind=="ab":
                    hits[v]+=int(match); tokens[v]+=o["input_tokens"]; latency[v].append(o["elapsed_seconds"]); correct[v]=match
                    if v=="compact": compact[task["group_id"]]=o
                else: aa_hits[j]+=int(match)
            if kind=="ab": new_errors+=int(correct["verbose"] and not correct["compact"])
            else:
                require(obs[0]["input_tokens"]==obs[1]["input_tokens"],"AA token drift")
                aa_drift.append(abs(obs[1]["elapsed_seconds"]-obs[0]["elapsed_seconds"]))
    savings=round(100*(1-tokens["compact"]/tokens["verbose"]),3)
    medians={k:round(statistics.median(v),6) for k,v in latency.items()}
    require(ab["summary"]["public_exact_matches"]==hits and ab["summary"]["input_tokens"]==tokens and ab["summary"]["input_token_saving_pct_descriptive"]==savings and ab["summary"]["latency_median_seconds"]==medians,"AB summary mismatch")
    require(aa["summary"]["median_absolute_pair_drift_seconds"]==round(statistics.median(aa_drift),6),"AA summary mismatch")
    return tasks, compact, {"raw_calls":120,"public_matches":hits,"new_public_errors":new_errors,"input_tokens":tokens,"token_saving_pct":savings,"latency_medians":medians,"aa_matches":aa_hits}

def actual_replay(c,tasks,compact):
    import torch
    from huggingface_hub import snapshot_download
    from transformers import AutoTokenizer, AutoModelForCausalLM
    torch.set_num_threads(2)
    torch.manual_seed(42)
    require(torch.version.cuda is None,"CPU only")
    p=Path(snapshot_download(MODEL, revision=REV, allow_patterns=["*.json","*.safetensors","*.txt"]))
    with (p/"model.safetensors").open("rb") as f:
        actual=hashlib.file_digest(f,"sha256").hexdigest()
    require(actual==WEIGHT,"actual model weight digest")
    tok=AutoTokenizer.from_pretrained(p,local_files_only=True)
    engine=AutoModelForCausalLM.from_pretrained(p,local_files_only=True,torch_dtype=torch.float32).eval()
    rows=[]
    start=time.monotonic()
    for task in tasks:
        ids=tok.apply_chat_template([{"role":"system","content":c["prompt"]},{"role":"user","content":task["question"]}],tokenize=True,add_generation_prompt=True,return_tensors="pt")
        with torch.inference_mode():
            out=engine.generate(input_ids=ids,attention_mask=torch.ones_like(ids),do_sample=False,max_new_tokens=16,pad_token_id=tok.eos_token_id)
        decoded=tok.decode(out[0,ids.shape[1]:],skip_special_tokens=True)
        prior=compact[task["group_id"]]
        rows.append(dict(task,observed=decoded,prior_output=prior["output"],same_output=decoded==prior["output"],same_input_tokens=ids.shape[1]==prior["input_tokens"],correct=decoded.strip()==task["expected"]))
    return rows,time.monotonic()-start,actual

def main():
    c,ab,aa=open_archive(Path("d2-raw.zip"))
    tasks,compact,metrics=regrade(ab,aa)
    rows,seconds,weight=actual_replay(c,tasks,compact)
    equal=sum(x["same_output"] and x["same_input_tokens"] for x in rows)
    report={"cycle_id":CYCLE,"candidate_sha256":CANDIDATE,"archive_sha256":ARCHIVE,"source_commit":SOURCE,
            "cerberus_run":os.environ["GITHUB_RUN_ID"],"cerberus_commit":os.environ["GITHUB_SHA"],
            "model_weight_sha256":weight,"regrade":metrics,"actual_replay_calls":len(rows),
            "actual_replay_correct":sum(x["correct"] for x in rows),"exact_replay_matches":equal,
            "actual_replay_seconds":seconds,"rows":rows,"fenrir_admission":"NOT_EVALUATED",
            "protected_grade":"pending","promotion_allowed":False,
            "verdict":"PUBLIC_REPLAY_MATCH" if equal==30 else "PUBLIC_REPLAY_MISMATCH"}
    Path("out").mkdir(exist_ok=True)
    Path("out/CERBERUS_PUBLIC_REPLAY.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k!="rows"},ensure_ascii=False))
    require(equal==30,"actual replay differs; do not admit")

if __name__=="__main__":
    main()
