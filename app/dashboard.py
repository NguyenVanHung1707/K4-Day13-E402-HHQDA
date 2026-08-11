import json
from collections import Counter
from pathlib import Path
from statistics import mean
import yaml
from .metrics import percentile

ROOT = Path(__file__).resolve().parents[1]

def aggregate(rows, minutes=60):
    responses = [r for r in rows if r.get('event') == 'response_sent']
    received = sum(r.get('event') == 'request_received' for r in rows)
    failed = [r for r in rows if r.get('event') == 'request_failed']
    nums = lambda f: [r[f] for r in responses if isinstance(r.get(f), (int, float))]
    latency, cost, tin, tout, quality = map(nums, ('latency_ms','cost_usd','tokens_in','tokens_out','quality_score'))
    return {'latency':[percentile(latency,p) for p in (50,95,99)], 'traffic':[received,received/minutes], 'errors':[len(failed)/received*100 if received else 0,dict(Counter(r.get('error_type','Unknown') for r in failed))], 'cost':sum(cost), 'tokens':[sum(tin),sum(tout)], 'quality':mean(quality) if quality else 0}

def dashboard_html():
    cfg=yaml.safe_load((ROOT/'config/dashboard.yaml').read_text(encoding='utf-8'))['dashboard']
    path=ROOT/'data/logs.jsonl'; rows=[]
    if path.exists():
        for line in path.read_text(encoding='utf-8').splitlines():
            try: rows.append(json.loads(line))
            except json.JSONDecodeError: pass
    m=aggregate(rows,cfg['time_range_minutes'])
    values={'latency':f"P50 {m['latency'][0]:.0f} | P95 {m['latency'][1]:.0f} | P99 {m['latency'][2]:.0f}",'traffic':f"{m['traffic'][0]} requests | {m['traffic'][1]:.2f}/min",'errors':f"{m['errors'][0]:.2f}% | {m['errors'][1]}",'cost':f"USD {m['cost']:.4f}",'tokens':f"In {m['tokens'][0]} | Out {m['tokens'][1]}",'quality':f"{m['quality']:.3f}"}
    cards=[]
    for p in cfg['panels']:
        t=p['threshold']; sign='&lt;=' if t['operator']=='lte' else '&gt;='
        cards.append(f'<section><h2>{p["title"]}</h2><b>{values[p["id"]]}</b><p>Unit: {p["unit"]}</p><footer>SLO {t["aggregation"]} {sign} {t["value"]}</footer></section>')
    return f'''<html><head><meta http-equiv="refresh" content="{cfg['refresh_seconds']}"><style>body{{background:#07111f;color:#eef;font:15px system-ui;padding:30px}}header{{display:flex;justify-content:space-between}}main{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}}section{{background:#142236;padding:20px;border-radius:12px}}b{{font-size:24px}}footer{{border-top:1px solid #456;padding-top:10px}}</style></head><body><header><h1>{cfg['title']}</h1><p>Time range: last {cfg['time_range_minutes']}m | Refresh: {cfg['refresh_seconds']}s | data/logs.jsonl</p></header><main>{''.join(cards)}</main></body></html>'''
