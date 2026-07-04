# Credit Vivo Credit Comeback Simulator

## Purpose
Customer-facing score impact dashboard tied directly to the Credit Vivo scanner.

## Core flow
Upload report -> CV Scanner finds negative accounts -> CV Brain ranks blockers -> Score Impact Engine estimates possible movement -> Customer sees possible FICO path -> Customer-approved dispute prep is prioritized from the highest-impact items first.

## What it does
- Tracks starting, current, and goal score
- Shows score movement
- Ranks top credit blockers
- Estimates possible score impact by account
- Lets the customer simulate selected items corrected/updated/removed
- Shows a possible 100-point credit comeback path
- Exposes `POST /api/score-simulator/estimate` for scanner-connected estimates
- Maps CV Brain negative tradelines into simulator accounts with `scannerTradelinesToSimulatorAccounts`

## What it avoids
- Does not claim to reproduce the exact FICO formula
- Does not guarantee score increases
- Does not guarantee deletions or approvals
- Does not automatically send disputes, complaints, mail, or attorney referrals
- Does not provide legal advice

## Install
Integrated files:

- components/dashboard/CreditComebackSimulator.tsx
- components/dashboard/demo-data.ts
- lib/score-impact-engine.ts
- types/score-simulator.ts
- app/api/score-simulator/estimate/route.ts
- docs/scanner/README_CREDIT_COMEBACK_SIMULATOR.md
- supabase/schema.sql score simulator tables
- supabase/score_simulator_schema.sql

## Example usage

```tsx
import { CreditComebackSimulator } from '@/components/dashboard/CreditComebackSimulator';
import { demoNegativeAccounts, demoScoreProfile } from '@/components/dashboard/demo-data';

export default function Page() {
  return <CreditComebackSimulator profile={demoScoreProfile} accounts={demoNegativeAccounts} />;
}
```

## Scanner API bridge

The estimate route accepts either simulator-ready `accounts` or CV Brain scanner objects:

```json
{
  "profile": {
    "startingScore": 552,
    "currentScore": 579,
    "goalScore": 680,
    "scoreSource": "UserEntered"
  },
  "tradelines": [],
  "issues": [],
  "selectedAccountIds": []
}
```

The response includes:

- profile
- accounts
- impacts
- summary
- scenario
- compliance flags

## Model notes

The model is an estimated score-impact guide. It uses:

- negative account type
- severity
- recency
- bureau coverage
- balance and utilization where available
- dispute strength score
- duplicate risk
- possible scanner issue findings
- diminishing returns across multiple selected items

It is not a FICO clone and does not promise a specific result.

## Customer language
- Your credit comeback starts here.
- See what may be holding your FICO score back.
- Find errors. Build disputes. See results.
- Possible 100-point credit comeback.
- Move toward a stronger FICO score.
- AI Credit Boost + Attorney Support.
