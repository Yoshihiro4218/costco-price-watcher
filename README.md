# costco-price-watcher

AWS Lambda function that watches Costco product pages and sends a LINE notification when a price drops below a configured threshold. The notification message includes the product name taken from the API's `metaTitle` field and the product URL extracted from the API response.

## Environment variables

- `TARGETS` – JSON array of objects containing `productCode` and `threshold` keys. Example:
  ```json
  [
    {"productCode": "74333", "threshold": 2000},
    {"productCode": "12345", "threshold": 1500}
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
