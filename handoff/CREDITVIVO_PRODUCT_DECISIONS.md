# CreditVivo Product Decisions

Created: 2026-07-18

Use this file to prevent the AIs from re-litigating settled product direction.

## Decided

| Decision | Status | Reason |
|---|---|---|
| CreditVivo customer side should be simple and confidence-building | Decided | Customers want a clear path, not technical clutter. |
| Founder/admin side should be an operator dashboard | Decided | Tim needs scanner queues, deadlines, letters, compliance, and Mini Tim. |
| Mini Tim is backend-only for now | Decided | Do not market it as a customer chatbot yet. |
| Scanner outputs must preserve raw evidence | Decided | The scanner cannot alter bureau/report values. |
| Findings must say possible issue | Decided | Compliance-safe language avoids unsupported legal conclusions. |
| No guaranteed score increase, deletion, approval, or timeline | Decided | Required compliance guardrail. |
| Vendor tools can be used only as lawful validators/references | Decided | Do not copy vendor code or private logic. |
| BureauRelay/SwitchLabs waits until company is formed | Decided | Tim could not buy as an individual; do not misrepresent. |

## Product Shape

Customer flow:

1. Start credit path.
2. Give low-risk intake details.
3. Upload/report import only after secure production vault exists.
4. See simple progress and required next steps.
5. Approve draft actions.
6. Track results and next review dates.

Founder/admin flow:

1. Review new scans.
2. Inspect 3-bureau comparison.
3. Review possible issues and raw evidence.
4. Approve/reject draft letters.
5. Track 30/45-day timelines.
6. Escalate to collector, furnisher, CFPB, or attorney review when supported.

## Open Product Questions

| Question | Owner | Needed Before |
|---|---|---|
| What is the first paid offer after waitlist? | Tim | Paid launch |
| Which attorney referral/legal partner model is real? | Tim | Attorney Authority public claims |
| Which credit-builder partner is real? | Tim | Credit builder advertising |
| Which report provider will be used first? | Tim + Codex | Automated report import |
| What customer data is allowed in MVP? | Tim + compliance | Production onboarding |

## ChatGPT Lane

- Customer flow
- CRC-style workflow notes
- Homepage copy
- FAQ and sales scripts
- Onboarding questions
- Customer education
- Compliance-friendly wording suggestions

## Codex Lane

- Scanner/parser
- Metro 2-style field audit
- Backend routes
- Data model
- Tests
- Deployment health
- Security controls
- Mini Tim backend logic
