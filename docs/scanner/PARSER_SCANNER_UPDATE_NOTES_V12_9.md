# Credit Vivo Parser/Scanner v12.9 Integration Notes

## What this update adds

This package connects the v12.8 AI second-pass scanner to the Bolt/Vite frontend in a layout-safe way.

## Included

- Current approved Bolt build v15.1
- Credit Vivo scanner v12.8 AI second-pass engine
- FastAPI scanner backend adapter
- Frontend scanner API client
- Environment examples
- Bolt integration prompt
- API contract
- Layout-safe instructions

## What did not change

The approved public page layout was not changed.

## Recommended deployment

- Public website/app frontend: Vercel
- Scanner backend API: Render, Railway, Fly.io, or private server
- API keys: backend environment variables only

## Environment variables

Frontend:

```env
VITE_SCANNER_API_URL=https://your-scanner-api.example.com
```

Backend:

```env
ANTHROPIC_API_KEY=your_anthropic_key_here
CREDIT_VIVO_ALLOWED_ORIGINS=https://your-vercel-domain.vercel.app,https://creditvivo.com
```

## Important

AI parser output should be treated as draft review data. It should not automatically generate or send disputes. Customer approval and admin review are required.
