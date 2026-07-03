# Credit Vivo Proprietary Scanner Backend v18.1.7

This scanner is redesigned to avoid paid AI APIs and avoid PyMuPDF.

## Removed

- Anthropic / Claude API dependency
- `ANTHROPIC_API_KEY`
- PyMuPDF dependency

## Uses

- Credit Vivo native rule-based parser
- pypdf for basic PDF text extraction
- FastAPI for backend API
- v18.1.7 decision-readiness mapping for auto loan, mortgage, apartment, collection, charge-off, late-payment, and bureau mismatch review
- raw-exact field display in the 3-bureau comparison workbook
- CFPB-style packet checklist, document vault manifest, and Lob tracking placeholders
- founder/admin backend hub with local login for testing
- production-readiness gates for auth, storage, encryption, audit logging, and approval controls

## Local setup

```powershell
cd scanner_backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8080
```

Check:

```text
http://localhost:8080/health
```

## Important

This parser is proprietary to Credit Vivo, but it still uses permissive open-source libraries. Keep license notices in the package.

No customer letters or disputes should be sent automatically from parser output. Admin/customer approval is required.

## Free beta production notes

Set these environment variables on the backend host:

```text
CREDIT_VIVO_ALLOWED_ORIGINS=https://www.creditvivo.com,https://creditvivo.com
SCANNER_ENVIRONMENT=production
SCANNER_MAX_FILES=3
SCANNER_MAX_FILE_MB=25
SCANNER_RETAIN_UPLOADS=false
SCANNER_WRITE_RAW_TEXT=false
SCANNER_STORAGE_DIR=/var/data/creditvivo-scanner
CREDITVIVO_ADMIN_USERNAME=founder@creditvivo.com
CREDITVIVO_ADMIN_PASSWORD=use-a-long-random-secret
ADMIN_SESSION_SECRET=use-a-different-long-random-secret
ADMIN_SETUP_TOKEN=use-a-long-random-owner-only-token
CREDITVIVO_AUTH_PROVIDER=local-dev-until-supabase-auth0-or-clerk
CREDITVIVO_STORAGE_ENCRYPTION_KEY=use-a-long-random-encryption-secret
```

Default beta behavior:

- PDF uploads only.
- Maximum 3 files per request.
- Maximum 25 MB per file.
- Uploaded PDFs are deleted after parsing unless `SCANNER_RETAIN_UPLOADS=true`.
- Full raw extracted text files are not written unless `SCANNER_WRITE_RAW_TEXT=true`.
- Parser results still contain draft evidence snippets for customer/admin review.
- Founder/admin routes are protected by a signed session cookie in local/test mode.
- Production should replace local login with Supabase, Auth0, Clerk, or another secure auth provider with 2FA.

Use a private backend host, HTTPS, restrictive CORS, and secure retention rules before accepting real customer reports.

## Render deployment

This repo includes `render.yaml` for deploying the scanner as a Render web service.

Recommended Render service:

- Service type: Web Service
- Runtime: Python
- Python version: `python-3.12.8` from root `runtime.txt`
- Build command: `pip install -r scanner_backend/requirements.txt`
- Start command: `cd scanner_backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
- Health check path: `/health`

Production environment variables:

```text
CREDIT_VIVO_ALLOWED_ORIGINS=https://www.creditvivo.com,https://creditvivo.com
SCANNER_ENVIRONMENT=production
SCANNER_MAX_FILES=3
SCANNER_MAX_FILE_MB=25
SCANNER_RETAIN_UPLOADS=false
SCANNER_WRITE_RAW_TEXT=false
SCANNER_STORAGE_DIR=/var/data/creditvivo-scanner
CREDITVIVO_ADMIN_USERNAME=founder@creditvivo.com
CREDITVIVO_ADMIN_PASSWORD=use-a-long-random-secret
ADMIN_SESSION_SECRET=use-a-different-long-random-secret
ADMIN_SETUP_TOKEN=use-a-long-random-owner-only-token
CREDITVIVO_AUTH_PROVIDER=local-dev-until-supabase-auth0-or-clerk
CREDITVIVO_STORAGE_ENCRYPTION_KEY=use-a-long-random-encryption-secret
```

Founder backend paths:

```text
/founder-login
/founder
/admin/production-readiness
```

After Render deploys, verify:

```text
https://YOUR-RENDER-SERVICE.onrender.com/health
```

Expected response includes:

```json
{
  "ok": true,
  "service": "credit-vivo-proprietary-scanner-api"
}
```

## v18.1.3 Decision-Readiness Layer

The v18.1.3 parser maps scanner issues to customer situations without promising results:

- Auto loan or refinance review
- Mortgage readiness
- Apartment application review
- Collection account review
- Charge-off or late-payment review
- Bureau mismatch review

These cards are educational next-step guidance only. They do not guarantee approvals, score increases, removals, or legal outcomes.

## Owner-only user provisioning

The backend includes setup endpoints for creating demo/provisioned users while full production auth is being connected.

Required environment variable:

```text
ADMIN_SETUP_TOKEN=use-a-long-random-owner-only-token
```

Setup info:

```text
GET /api/admin/users/setup
```

Create user:

```text
POST /api/admin/users/create
Header: X-Credit-Vivo-Admin-Setup-Token: YOUR_ADMIN_SETUP_TOKEN
```

Example body:

```json
{
  "email": "owner@creditvivo.com",
  "display_name": "Owner",
  "role": "owner_admin"
}
```

Roles:

- `owner_admin`: all privileges
- `partner_reviewer`: partner review access
- `technical_reviewer`: technical review access
- `demo_customer`: customer demo access

Important:
This provisioning endpoint does not replace a full production auth provider. It creates secure setup records and one-time temporary passwords. Connect Supabase, Auth0, Clerk, or another auth provider before public launch.
