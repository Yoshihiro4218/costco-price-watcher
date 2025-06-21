from lambda_function import extract_price, extract_product_url

DATA = {"schemaOrgProduct": '{"offers": {"price": "1848.0", "url": "https://example.com/product"}}'}


def test_extract_price():
    assert extract_price(DATA) == 1848


def test_extract_product_url():
    assert extract_product_url(DATA) == "https://example.com/product"
