#!/usr/bin/env python3
"""Validate the fixed tabled oral questions source-interface proof."""
from __future__ import annotations
import hashlib, json, re
from datetime import date
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1]
NOTE=ROOT/"research"/"complete-mp-reports"/"jeremy-corbyn"/"current-parliament-tabled-oral-questions-source-interface-v1.md"
EXPECTED_SHA="25cd378069d42a50c1a4c36d514f188767c4f2721cf95f6c8c5d2c3a48a40a5b"
BASE_IDS=[122465,127241,271822,271823,287272,319088,319553,332039,373735,374007,404663,411372]
CURRENT_IDS=[319088,319553,332039,373735,374007,404663,411372]
PARAMETERS=["parameters.answeringDateStart","parameters.answeringDateEnd","parameters.questionType","parameters.oralQuestionTimeId","parameters.statuses","parameters.askingMemberIds","parameters.uINs","parameters.answeringBodyIds","parameters.skip","parameters.take"]
STATUSES=["Submitted","Carded","Unsaved","ReadyForShuffle","ToBeAsked","ShuffleUnsuccessful","Withdrawn","Unstarred","Draft","ForReview","Unasked","Transferred"]

def canonical(v:Any)->bytes:
    return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()

def extract(text:str)->dict[str,Any]:
    m=re.search(r"<!-- BEGIN SOURCE_INTERFACE_EVIDENCE_V1 -->\s*```json\s*(.*?)\s*```\s*<!-- END SOURCE_INTERFACE_EVIDENCE_V1 -->",text,re.S)
    assert m,"fixed evidence block missing"
    v=json.loads(m.group(1)); assert isinstance(v,dict); return v

def paging(v,total,take,skip):
    assert v=={"GlobalStatusCounts":[],"GlobalTotal":total,"Skip":skip,"StatusCounts":[],"Take":take,"Total":total}

def main()->int:
    text=NOTE.read_text(encoding="utf-8")
    for h in ("## Conclusion","## Confirmed interface behaviour","## Confirmed limitations","## Explicit exclusions","## Fixed evidence"):
        assert text.count(h)==1,h
    for phrase in (
        "A complete reproducible fixed inventory is possible for the oral-question records exposed by the official UK Parliament API at a fixed capture time.",
        "The current-Parliament boundary must therefore be applied locally to `TabledWhen`.",
        "There is no supported tabled-date filter.",
        "not a canonical Complete MP inventory",
        "does not authorise a fixed canonical oral-question inventory",
    ): assert phrase in text,phrase
    e=extract(text)
    assert hashlib.sha256(canonical(e)).hexdigest()==EXPECTED_SHA
    assert set(e)=={"answering_date_window","base_main","capture_date","member_query","pagination","probe","spec","unsupported_tabled_parameters","wrong_member"}
    assert e["capture_date"]=="2026-07-22" and e["base_main"]=="ddaa729a9deeaec7392a89e95e9dadaa5282bd67"
    assert e["probe"]=={"artifact_digest":"sha256:ca8cb8c5eddee9d364cde740d5c2be686fceeef3a79f549e18dc7d41d83f2ea3","artifact_id":8542430328,"head":"1cb7be10a70c140689087698adf342b2bec8a1e5","run_id":29951838611}
    s=e["spec"]
    assert s["url"]=="https://oralquestionsandmotions-api.parliament.uk/swagger/docs/v1"
    assert s["sha256"]=="bde894ce32092579b52cc419f36a5ee65a45260664fa5f89d9f78db01d65df6f"
    assert s["summary"]=="Returns a list of oral questions" and s["description"]=="A list of oral questions meeting the specified criteria."
    assert s["parameters"]==PARAMETERS and s["statuses"]==STATUSES
    assert not {"parameters.tabledStartDate","parameters.tabledEndDate","parameters.session"} & set(PARAMETERS)
    q=e["member_query"]
    assert q["url"]=="https://oralquestionsandmotions-api.parliament.uk/oralquestions/list?parameters.askingMemberIds=185&parameters.skip=0&parameters.take=100"
    assert q["raw_sha256"]=="f47822206b73bbac2fc557f6911750eda5165376905e3651323e59ccf02c94aa"; paging(q["paging"],12,100,0)
    assert [r["id"] for r in q["records"]]==BASE_IDS and len({r["id"] for r in q["records"]})==12
    for r in q["records"]:
        assert set(r)=={"answering","answering_body","answering_body_id","asking_member_id","asking_member_mnis_id","asking_member_name","id","question_type","status","tabled","uin"}
        assert (r["asking_member_id"],r["asking_member_mnis_id"],r["asking_member_name"])==(185,185,"Jeremy Corbyn")
        date.fromisoformat(r["tabled"]); date.fromisoformat(r["answering"])
    dates=[date.fromisoformat(r["tabled"]) for r in q["records"]]; assert dates==sorted(dates)
    current=[r["id"] for r in q["records"] if date(2024,7,4)<=date.fromisoformat(r["tabled"])<=date(2026,7,22)]
    assert current==CURRENT_IDS and len(q["records"])-len(current)==5
    d=e["answering_date_window"]; paging(d["paging"],7,100,0); assert d["ids"]==CURRENT_IDS
    assert d["raw_sha256"]=="4a4616b5a7427706c58c2856fc036b5420aa12177e24e8252f883fc056f4652f"
    u=e["unsupported_tabled_parameters"]; assert u["equals_base"] is True and u["sha256"]==q["raw_sha256"] and u["paging"]==q["paging"]
    assert "parameters.tabledStartDate=2024-07-04" in u["url"] and "parameters.tabledEndDate=2026-07-22" in u["url"]
    assert [p["id"] for p in e["pagination"]]==BASE_IDS[:3]
    for i,p in enumerate(e["pagination"]): paging(p["paging"],12,1,i); assert p["skip"]==i and re.fullmatch(r"[0-9a-f]{64}",p["raw_sha256"])
    w=e["wrong_member"]; paging(w["paging"],0,100,0); assert w["record_count"]==0 and "parameters.askingMemberIds=999999" in w["url"]
    assert w["raw_sha256"]=="25768e961931ac09314cd527d46efb316e4aec23613f96379d8e9327e3b2e515"
    print("PASS: bounded capture-time oral-question inventory is reproducible with local TabledWhen filtering")
    return 0
if __name__=="__main__": raise SystemExit(main())
