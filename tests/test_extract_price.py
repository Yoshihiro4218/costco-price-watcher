from lambda_function import extract_price

DATA = {"schemaOrgProduct": '{"offers": {"price": "1848.0"}}'}


def test_extract_price():
    assert extract_price(DATA) == 1848
