import os
import json
import re
from urllib.request import Request, urlopen

PRICE_RE = re.compile(r"¥([\d,]+)")


def fetch_page(url: str) -> str:
    with urlopen(url) as resp:
        return resp.read().decode("utf-8")


def extract_price(html: str) -> int:
    match = PRICE_RE.search(html)
    if not match:
        raise ValueError("Price not found")
    price_str = match.group(1).replace(",", "")
    return int(price_str)


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
    with urlopen(req) as resp:
        resp.read()


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
        url = item["url"]
        threshold = int(item["threshold"])
        html = fetch_page(url)
        price = extract_price(html)
        if price <= threshold:
            message = (
                f"{url} の価格が {price} 円になりました (指定価格 {threshold} 円)"
            )
            send_line_message(line_token, user_id, message)
            print(f"【通知】{url} の価格: {price}円（閾値: {threshold}円）-> 通知を送信しました。")
            results.append({"url": url, "price": price, "notified": True})
        else:
            print(f"【未通知】{url} の価格: {price}円（閾値: {threshold}円）-> 通知は送信しません。")
            results.append({"url": url, "price": price, "notified": False})
    return {"results": results}
