from lambda_function import extract_price

HTML = '<span class="product-price-amount"><span class="notranslate">¥1,848</span></span>'

def test_extract_price():
    assert extract_price(HTML) == 1848
