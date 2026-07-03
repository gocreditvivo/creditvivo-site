# Credit Vivo Parser/Scanner v16 — Proprietary Engine Upgrade

## Main upgrade

Replaced the basic native parser with a stronger proprietary architecture:

- Normalized tradeline schema
- Evidence snippets
- Confidence scoring
- Cross-bureau matching
- Issue detection engine
- Customer-friendly summaries
- Admin-ready review output
- CSV/JSON output files

## Still no paid AI

No Anthropic, Claude, OpenAI, or paid AI API is required.

## Still no public layout change

This package does not redesign the approved public website.

## Backend outputs

For each scan job, the backend saves:

- `scan_result_summary.json`
- `credit_vivo_parser_result.json`
- `tradelines.csv`
- `review_issues.csv`
- raw text files

## Local run

```powershell
cd scanner_backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8080
```

Health check:

```text
http://localhost:8080/health
```
