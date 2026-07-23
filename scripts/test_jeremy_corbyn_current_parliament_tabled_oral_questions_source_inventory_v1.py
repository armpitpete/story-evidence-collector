#!/usr/bin/env python3
"""Validate the fixed Jeremy Corbyn tabled oral-question source inventory."""
from __future__ import annotations
import argparse, base64, gzip, hashlib, json, urllib.error, urllib.request
from datetime import date
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1]
PACKET=ROOT/'research/complete-mp-reports/jeremy-corbyn/current-parliament-tabled-oral-questions-source-inventory-v1.json'
NOTE=ROOT/'docs/jeremy-corbyn-current-parliament-tabled-oral-questions-source-note-v1.md'
URL='https://oralquestionsandmotions-api.parliament.uk/oralquestions/list?parameters.askingMemberIds=185&parameters.skip=0&parameters.take=100'
BASE='6e65e5ccd70bbed91f678e067105933ec049f17b'
ALL=[122465,127241,271822,271823,287272,319088,319553,332039,373735,374007,404663,411372]
CURRENT=[319088,319553,332039,373735,374007,404663,411372]
EXCLUDED=[122465,127241,271822,271823,287272]
def canonical(v:Any)->bytes:return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
def digest_bytes(v:bytes)->str:return hashlib.sha256(v).hexdigest()
def digest(v:Any)->str:return digest_bytes(canonical(v))
def member(m):
    if m is None:return None
    return {'mnis_id':m.get('MnisId'),'pims_id':m.get('PimsId'),'name':m.get('Name'),'list_as':m.get('ListAs'),'constituency':m.get('Constituency'),'status':m.get('Status'),'party':m.get('Party'),'party_id':m.get('PartyId'),'party_colour':m.get('PartyColour'),'photo_url':m.get('PhotoUrl')}
def norm(r):
    return {'api_id':r.get('Id'),'question_type_value':r.get('QuestionType'),'question_type_label':None,'question_text':r.get('QuestionText'),'status_value':r.get('Status'),'status_label':None,'number':r.get('Number'),'tabled_when':r.get('TabledWhen'),'removed_from_to_be_asked_when':r.get('RemovedFromToBeAskedWhen'),'declarable_interest_detail':r.get('DeclarableInterestDetail'),'hansard_link':r.get('HansardLink'),'uin':r.get('UIN'),'answering_when':r.get('AnsweringWhen'),'answering_body_id':r.get('AnsweringBodyId'),'answering_body':r.get('AnsweringBody'),'answering_minister_title':r.get('AnsweringMinisterTitle'),'asking_member':member(r.get('AskingMember')),'answering_minister':member(r.get('AnsweringMinister')),'asking_member_id':r.get('AskingMemberId'),'answering_minister_id':r.get('AnsweringMinisterId')}
def validate():
    p=json.loads(PACKET.read_text(encoding='utf-8'))
    assert p['authority_base']==BASE and p['schema_version']=='1'
    assert p['inventory_id']=='jeremy-corbyn-current-parliament-tabled-oral-questions-source-inventory-v1'
    c=p['capture']; assert c['captured_at_utc']=='2026-07-23T17:27:27Z' and c['source']['official_url']==URL
    gz=base64.b64decode(c['raw_response_gzip_base64']); raw=gzip.decompress(gz)
    assert digest_bytes(raw)==p['checksums']['raw_response_sha256']=='9d3b31f77d8e53c018039713fad830bc1e99b73bc5ca7c6a7bd0d67603cd35f9'
    assert digest_bytes(gz)==p['checksums']['gzip_response_sha256']=='b7126e70594e3d4ce468e00f26dddb13ca5606de9dd1fed26ac138a5d6071a7f'
    api=json.loads(raw); expected={'Skip':0,'Take':100,'Total':12,'GlobalTotal':12,'StatusCounts':[],'GlobalStatusCounts':[]}
    assert api['PagingInfo']==c['paging']==expected and api['StatusCode']==200 and api['Success'] is True and api['Errors']==[]
    records=[norm(r) for r in api['Response']]; assert [r['api_id'] for r in records]==ALL and len(set(ALL))==12
    u=p['member_query_universe']; assert u['record_count']==12 and u['api_ids']==ALL and u['records_sha256']==digest(records)
    for r in records:
        assert r['asking_member_id']==185 and r['asking_member']['mnis_id']==185 and r['asking_member']['name']=='Jeremy Corbyn'
        assert r['question_text'].strip() and r['question_type_label'] is None and r['status_label'] is None
        assert u['record_sha256'][str(r['api_id'])]==digest(r)
    current=[r for r in records if date(2024,7,4)<=date.fromisoformat(r['tabled_when'][:10])<=date(2026,7,23)]
    excluded=[r for r in records if r not in current]; s=p['current_parliament_selection']
    assert [r['api_id'] for r in current]==s['included_api_ids']==CURRENT
    assert [r['api_id'] for r in excluded]==s['excluded_pre_current_parliament_api_ids']==EXCLUDED
    assert s['accepted_record_count']==7 and s['excluded_record_count']==5 and s['selected_records_sha256']==digest(current)
    payload={k:v for k,v in p.items() if k!='checksums'}; assert p['checksums']['canonical_payload_sha256']==digest(payload)=='13c94b8044c54415e6f04c307f79f5a5a0935afe8240121caef3c805eb194fb5'
    text=NOTE.read_text(encoding='utf-8')
    for h in ('## Authority and fixed capture','## Source-interface continuity','## Complete member-query universe','## Current-Parliament selection','## Source controls','## Drift reconciliation','## What this proves','## What this does not prove','## Explicit boundary','## Validation contract'):assert text.count(h)==1,h
    for phrase in ('seven included records and five explicit pre-current-Parliament exclusions','Their labels remain unresolved rather than inferred.','A question asked is recorded only as a question asked.','does not authorise canonical Complete MP fixture integration'):assert phrase in text,phrase
    return p,records
def live(p,records):
    req=urllib.request.Request(URL,headers={'Accept':'application/json','User-Agent':'story-evidence-collector/1.0'})
    try:
        with urllib.request.urlopen(req,timeout=60) as response:raw=response.read();assert response.status==200
    except (urllib.error.URLError,TimeoutError,OSError) as exc:
        print(f'LIVE_REPLAY_UNAVAILABLE: {type(exc).__name__}: {exc}');return 0
    api=json.loads(raw);assert api['PagingInfo']==p['capture']['paging'];assert [norm(r) for r in api['Response']]==records,'stable-field drift requires separate reconciliation'
    print('LIVE_REPLAY_MATCH' if digest_bytes(raw)==p['checksums']['raw_response_sha256'] else 'LIVE_REPLAY_RAW_DRIFT_WITH_STABLE_RECORDS');return 0
def main():
    a=argparse.ArgumentParser();a.add_argument('--live-replay',action='store_true');args=a.parse_args();p,r=validate()
    if args.live_replay:return live(p,r)
    print('PASS: fixed oral-question inventory and current-Parliament selection are reproducible');return 0
if __name__=='__main__':raise SystemExit(main())
