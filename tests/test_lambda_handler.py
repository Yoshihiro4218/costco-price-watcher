import json
import builtins
from lambda_function import lambda_handler

class DummyResponse:
    def __init__(self, data):
        self.data = data.encode('utf-8')
    def read(self):
        return self.data
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        pass

def test_lambda_handler(monkeypatch):
    data = {"schemaOrgProduct": '{"offers": {"price": "1000.0"}}'}

    def fake_urlopen(req, *args, **kwargs):
        return DummyResponse(json.dumps(data))

    monkeypatch.setattr('lambda_function.urlopen', fake_urlopen)
    targets = [{'productCode': '12345', 'threshold': 2000}]
    monkeypatch.setitem(
        lambda_handler.__globals__['os'].environ,
        'TARGETS',
        json.dumps(targets)
    )
    monkeypatch.setitem(lambda_handler.__globals__['os'].environ, 'LINE_TOKEN', 'dummy')
    monkeypatch.setitem(lambda_handler.__globals__['os'].environ, 'LINE_USER_ID', 'U1234567890')
    result = lambda_handler({}, {})
    assert result['results'][0]['notified']
