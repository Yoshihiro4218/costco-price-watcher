import os
import json
from urllib.request import Request, urlopen



API_URL = "https://www.costco.co.jp/rest/v2/japan/metadata/productDetails"


def fetch_product_details(product_code: str) -> dict:
    url = f"{API_URL}?code={product_code}&lang=ja&curr=JPY"
    with urlopen(url) as resp:
        return json.loads(resp.read().decode("utf-8"))


def extract_price(data: dict) -> int:
    schema_raw = data.get("schemaOrgProduct")
    if not schema_raw:
        raise ValueError("schemaOrgProduct field is missing")

    try:
        schema = json.loads(schema_raw)
    except Exception as e:
        raise ValueError(f"schemaOrgProduct parse error: {e}")

    price_str = (
        schema.get("offers", {}).get("price")
        if isinstance(schema.get("offers"), dict)
        else None
    )
    if price_str is None:
        raise ValueError("price field is missing")

    try:
        return int(float(price_str))
    except Exception as e:
        raise ValueError(f"invalid price value: {price_str} ({e})")


def extract_product_url(data: dict) -> str:
    schema_raw = data.get("schemaOrgProduct")
    if not schema_raw:
        raise ValueError("schemaOrgProduct field is missing")

    try:
        schema = json.loads(schema_raw)
    except Exception as e:
        raise ValueError(f"schemaOrgProduct parse error: {e}")

    url = None
    offers = schema.get("offers")
    if isinstance(offers, dict):
        url = offers.get("url")
    if not url:
        url = schema.get("url") or schema.get("@id")
    if not url:
        raise ValueError("url field is missing")
    return url


def send_line_message(token: str, user_id: str, message: str) -> None:
    payload = json.dumps({
        "to": user_id,
        "messages": [{"type": "text", "text": message}]
    }).encode("utf-8")
    req = Request(
        "https://api.line.me/v2/bot/message/push",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    )
    try:
        with urlopen(req) as resp:
            status = resp.status
            body = resp.read().decode('utf-8')
            print(f"LINE API response: status={status}, body={body}")
            if status != 200:
                raise RuntimeError(f"LINE push failed: {body}")
    except Exception as e:
        print(f"LINE push exception: {e}")
        raise


def lambda_handler(event, context):
    targets_env = os.environ.get("TARGETS")
    line_token = os.environ.get("LINE_TOKEN")
    user_id = os.environ.get("LINE_USER_ID")
    if not targets_env or not line_token or not user_id:
        raise ValueError(
            "TARGETS, LINE_TOKEN and LINE_USER_ID env vars are required"
        )

    targets = json.loads(targets_env)
    results = []
    for item in targets:
        product_code = item["productCode"]
        threshold = int(item["threshold"])
        try:
            data = fetch_product_details(product_code)
            product_name = data.get("metaTitle", product_code)
        except Exception as e:
            error_msg = f"【エラー】{product_code} の取得失敗: {e}"
            print(error_msg)
            results.append({
                "productCode": product_code,
                "productName": None,
                "price": None,
                "notified": False,
                "error": error_msg
            })
            continue

        try:
            price = extract_price(data)
            if price is None:
                raise ValueError("価格を取得できませんでした。")
            product_url = extract_product_url(data)
        except Exception as e:
            error_msg = f"【エラー】{product_name} の価格取得失敗: {e}"
            print(error_msg)
            results.append({
                "productCode": product_code,
                "productName": product_name,
                "price": None,
                "productUrl": None,
                "notified": False,
                "error": error_msg
            })
            continue

        if price <= threshold:
            price_str = f"{price:,}"
            threshold_str = f"{threshold:,}"
            message = (
                f"{product_name} の価格が {price_str} 円になりました (指定価格 {threshold_str} 円)\n{product_url}"
            )
            send_line_message(line_token, user_id, message)
            print(
                f"【通知】{product_name} の価格: {price}円（閾値: {threshold}円）-> 通知を送信しました。"
            )
            results.append({
                "productCode": product_code,
                "productName": product_name,
                "price": price,
                "productUrl": product_url,
                "notified": True,
            })
        else:
            print(
                f"【未通知】{product_name} の価格: {price}円（閾値: {threshold}円）-> 通知は送信しません。"
            )
            results.append({
                "productCode": product_code,
                "productName": product_name,
                "price": price,
                "productUrl": product_url,
                "notified": False,
            })

    return {"results": results}
