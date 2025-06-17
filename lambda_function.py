import os
import json
import re
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

PRICE_RE = re.compile(r"¥([\d,]+)")


def fetch_page(url: str) -> str:
    with urlopen(url) as resp:
        return resp.read().decode("utf-8")


def extract_price(html: str) -> int:
    soup = BeautifulSoup(html, 'html.parser')

    # ① セール後の最終価格を優先
    sale_elem = soup.select_one('.you-pay-value')
    if sale_elem and sale_elem.get_text(strip=True):
        price_text = sale_elem.get_text()
    else:
        # ② 通常時の価格
        norm_elem = soup.select_one('.product-price-amount')  # or '.price-value' 両方試す場合も
        if not norm_elem:
            raise ValueError('価格要素が見つかりませんでした')
        price_text = norm_elem.get_text()

    # 「¥」「,」を取り除き、数字のみを抽出して整数に変換
    digits = re.sub(r'\D', '', price_text)
    if not digits:
        raise ValueError(f'価格のパースに失敗しました: {price_text}')
    return int(digits)


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
        try:
            html = fetch_page(url)
        except Exception as e:
            error_msg = f"【エラー】{url} へのアクセス失敗: {e}"
            print(error_msg)
            results.append({
                "url": url,
                "price": None,
                "notified": False,
                "error": error_msg
            })
            continue

        try:
            price = extract_price(html)
            if price is None:
                raise ValueError("価格を取得できませんでした。")
        except Exception as e:
            error_msg = f"【エラー】{url} の価格取得失敗: {e}"
            print(error_msg)
            results.append({
                "url": url,
                "price": None,
                "notified": False,
                "error": error_msg
            })
            continue

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
