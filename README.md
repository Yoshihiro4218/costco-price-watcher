# costco-price-watcher

AWS Lambda function that watches Costco product pages and sends a LINE notification when a price drops below a configured threshold.

## Environment variables

- `TARGETS` – JSON array of objects containing `url` and `threshold` keys. Example:
  ```json
  [
    {"url": "https://www.costco.co.jp/Example-Item", "threshold": 2000},
    {"url": "https://www.costco.co.jp/Another", "threshold": 1500}
  ]
  ```
- `LINE_TOKEN` – Channel access token for the LINE Messaging API.
- `LINE_USER_ID` – User ID to send notifications to.

## Handler

The Lambda entry point is `lambda_function.lambda_handler`.

## Development

Tests can be run with:

```bash
pytest
```
