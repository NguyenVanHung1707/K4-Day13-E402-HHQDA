from app.dashboard import aggregate, dashboard_html

def test_dashboard_runtime():
    rows=[{'event':'request_received'},{'event':'request_received'},{'event':'response_sent','latency_ms':100,'cost_usd':.1,'tokens_in':10,'tokens_out':20,'quality_score':.8},{'event':'request_failed','error_type':'TimeoutError'}]
    result=aggregate(rows)
    assert result['errors'][0] == 50
    assert sum(result['tokens']) == 30
    page=dashboard_html()
    assert page.count('<section>') == 6
    assert 'Time range: last 60m' in page
