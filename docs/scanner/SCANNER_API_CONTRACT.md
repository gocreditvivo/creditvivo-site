# Credit Vivo Scanner API Contract v16

## Health check

GET `/health`

Response:

```json
{
  "ok": true,
  "service": "credit-vivo-proprietary-scanner-api",
  "version": "16.0",
  "paid_ai_used": false,
  "parser_engine": "Credit Vivo Proprietary Parser Engine"
}
```

## Parse reports

POST `/api/scanner/parse`

Form data:
- `files`: one or more PDF files
- `use_ai_second_pass`: accepted for compatibility but ignored

Response includes:
- `job_id`
- `files`
- `review_items_count`
- `review_items_preview`
- `issues_count`
- `issues_preview`
- `cross_bureau_groups`
- `customer_summary`
- `admin_summary`

## Get summary result

GET `/api/scanner/result/:job_id`

## Get full result

GET `/api/scanner/result/:job_id/full`

## Security

Never expose secrets in frontend. This v16 parser does not need paid AI keys.
