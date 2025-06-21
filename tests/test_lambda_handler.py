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
    data = {
        "metaTitle": "テスト商品",
        "schemaOrgProduct": '{"offers": {"price": "1000.0", "url": "https://example.com/product"}}'
    }

    def fake_urlopen(req, *args, **kwargs):
        return DummyResponse(json.dumps(data))

    monkeypatch.setattr('lambda_function.urlopen', fake_urlopen)

    sent_messages = []

    def fake_send_line_message(token, user_id, message):
        sent_messages.append(message)

    monkeypatch.setattr('lambda_function.send_line_message', fake_send_line_message)
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
    assert 'テスト商品' in sent_messages[0]
    assert 'https://example.com/product' in sent_messages[0]
