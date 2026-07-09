# Credit Vivo Forensic Benchmark + Bank-Grade QA Plan

## Executive Benchmark

Credit Vivo should not compete as a cheaper credit repair company. It should compete as a **credit readiness fintech**:

**AI Precision. Attorney Authority.**

| Area | Dovly | Lexington Law | Credit Saint | Credit Vivo Target |
|---|---|---|---|---|
| Core model | AI app, free-first, build/fix/protect | Attorney-backed credit repair | Traditional credit repair packages | Hybrid SaaS: AI + builder + protection + attorney-supported escalation |
| Pricing signal | Low-cost/free, Premium around $39.99/mo or annual value pricing | Premium legal-backed price around $139.95/mo | $79.99-$109.99+/mo plus initial work fee | $0 Free Review, $59 Plus, $99 Pro, Legal+ eligibility |
| Trust signal | App simplicity, score-lift claims, large download/user proof | Law firm authority, history, removals proof | Ranking/reputation, 90-day guarantee language, package clarity | Clean fintech trust, security posture, evidence-driven workflows, attorney-supported review |
| Customer model | DIY-light, app-first, mass-market | High-intent repair customer | High-intent repair customer comparing packages | Approval-ready customer: auto, mortgage, apartment, credit, loan, job |
| Retention | Monitoring, builder tradeline, identity protection | Monthly case work and legal positioning | Monthly package/service cycle | Monitoring, builder tools, identity protection, readiness roadmap, attorney escalation |
| Risk exposure | Bold score claims need substantiation | Regulatory history shows advance-fee/bait-switch risk in category | Guarantee language needs careful substantiation | Avoid guarantees, document-first workflows, compliant billing, controlled claims |

## Forensic Findings

- **Dovly wins on simplicity.** Its page/app promise is easy: build, fix, monitor, protect, free to start.
- **Lexington wins on authority.** Its legal positioning creates trust and premium willingness to pay.
- **Credit Saint wins on package clarity.** Customers can compare tiers and understand service depth.
- **Credit Vivo’s lane is the hybrid:** Dovly’s ease, Lexington’s authority, Credit Saint’s package clarity, with stronger fintech security and lifecycle retention.

## Architecture Target

Current build:

- Static landing page
- Node HTTP backend
- Lead API
- Token-protected admin view
- Local JSON storage
- Basic security headers, validation, spam trap, rate limiting

Bank-grade target:

- Frontend: Next.js or equivalent production app with SSR-safe pages, design system, accessibility tests, analytics events.
- API: versioned service layer with typed validation, request IDs, structured logs, rate limits, WAF, and abuse detection.
- Auth: customer auth, admin auth, MFA, RBAC, session expiry, device/session management.
- Data: encrypted managed database, field-level encryption for sensitive records, audit tables, immutable event log.
- AI: private credit-review pipeline, prompt/version governance, human review for high-risk actions, no unsupported legal conclusions.
- Workflow: intake, credit data import, issue queue, document vault, dispute tracker, attorney escalation packet, support inbox.
- Compliance: CROA/FCRA review, state-law matrix, billing controls, cancellation flow, consent records, marketing claim approval.
- Security: NIST CSF 2.0 aligned controls, GLBA Safeguards program, incident response, vendor risk, retention/deletion.

## Layout + Customer Experience Standard

- First screen must answer: who it helps, what happens next, why it is safe.
- Copy must stay short, plain-English, and action-oriented.
- Dashboard must show real status, not fake certainty: Review, Organize, Track, Build, Protect, Escalate.
- Pricing should feel premium but not predatory: $59 Plus, $99 Pro, Legal+ after eligibility.
- Never collect SSN, bureau credentials, full DOB, IDs, signatures, or credit report uploads in the public form.

## Revised Product Roadmap

1. **Foundation:** keep current lead API, protected admin, production docs, smoke tests.
2. **Auth + CRM:** add real admin login, MFA, lead statuses, notes, assignment, export, audit log.
3. **Customer portal:** account creation, consent, goal profile, readiness dashboard.
4. **Secure vault:** document upload with encryption, malware scan, retention controls.
5. **Credit engine:** report parser, issue detection, score-factor explanation, review queue.
6. **Workflow engine:** dispute packets, bureau/furnisher response tracking, customer tasks.
7. **Partner layer:** credit builder, identity protection, monitoring, payments.
8. **Attorney layer:** eligibility rules, evidence packet, attorney portal, referral logs.
9. **Scale layer:** observability, queue workers, data warehouse, marketing attribution, partner APIs.

## 120 Bank-Grade Test Scenarios

### Public Website

1. Home page returns 200.
2. Admin page returns 200.
3. Missing route returns 404.
4. Static JS returns correct content type.
5. HTML includes hero slogan.
6. Pricing includes $59/mo.
7. Pricing includes $99/mo.
8. Rejected guarantee phrases are absent.
9. Footer uses neutral compliance language.
10. Mobile viewport has no horizontal overflow.
11. Desktop viewport has no horizontal overflow.
12. CTA scrolls to form.
13. Form fields have labels.
14. Form works without JavaScript fallback message planned.
15. Sensitive-data warning is visible.
16. Color contrast passes WCAG AA.
17. Keyboard tab order reaches all fields.
18. Focus states are visible.
19. Admin route does not expose leads in HTML source.
20. Browser title and meta description are present.

### Lead API

21. Health route returns ok.
22. Lead POST accepts valid payload.
23. Lead POST rejects missing name.
24. Lead POST rejects short name.
25. Lead POST rejects invalid email.
26. Lead POST rejects missing goal.
27. Lead POST rejects invalid goal.
28. Lead POST rejects missing score range.
29. Lead POST rejects invalid score range.
30. Lead POST rejects missing plan.
31. Lead POST rejects invalid plan.
32. Lead POST rejects invalid contact preference.
33. Lead POST accepts optional phone.
34. Lead POST sanitizes phone characters.
35. Lead POST truncates long notes.
36. Lead POST trims whitespace.
37. Lead POST lowercases email.
38. Lead POST rejects honeypot.
39. Lead POST rejects wrong content type.
40. Lead POST rejects malformed JSON.
41. Lead POST rejects oversized payload.
42. Lead POST returns generic error for parsing failures.
43. Lead POST returns no IP hash to public response.
44. Lead IDs are unique.
45. Created timestamps are ISO strings.

### Admin API

46. GET leads without token returns 401.
47. GET leads with wrong token returns 401.
48. GET leads with valid token returns 200.
49. GET leads never returns ipHash.
50. GET leads returns newest first.
51. Admin token uses timing-safe comparison.
52. Empty lead list returns count 0.
53. Admin page shows locked state without token.
54. Admin page stores token only in sessionStorage.
55. Clear token relocks admin page.
56. Bad token shows locked/error state.
57. Valid token shows live state.
58. Admin table escapes HTML.
59. Admin table handles empty phone.
60. Admin table handles many rows.

### Security Headers

61. CSP header exists.
62. X-Frame-Options is DENY.
63. X-Content-Type-Options is nosniff.
64. Referrer-Policy is strict.
65. Permissions-Policy disables camera.
66. Permissions-Policy disables microphone.
67. Permissions-Policy disables geolocation.
68. API responses are no-store.
69. Static responses have safe cache policy.
70. Data directory is not web-accessible.
71. Path traversal attempt is blocked.
72. Unknown binary files use safe content type.
73. Admin token is not printed in UI.
74. Production mode fails without ADMIN_TOKEN.
75. Production mode accepts long ADMIN_TOKEN.

### Abuse + Reliability

76. Rate limit blocks rapid repeated POSTs.
77. Rate limit does not block first valid POST.
78. Rate limit key does not expose raw IP.
79. Simultaneous valid POSTs do not corrupt JSON.
80. Atomic write temp file is removed or renamed.
81. Corrupted leads file fails closed to empty list.
82. Server continues after invalid request.
83. Server handles request body stream errors.
84. Server handles missing data directory.
85. Server creates data directory automatically.
86. Server binds only to 127.0.0.1 in local mode.
87. Server does not log sensitive payloads.
88. Test runner restores existing leads after test.
89. Test runner works on a separate port.
90. Server process exits cleanly on test completion.

### Compliance

91. No guaranteed score increase language.
92. No guaranteed deletion language.
93. No guaranteed approval language.
94. No guaranteed timeline language.
95. No “remove accurate negatives” claim.
96. Attorney language says eligible cases.
97. Legal+ language does not imply automatic representation.
98. Pricing language avoids pay-for-deletion framing.
99. Intake warning blocks SSN/bureau credentials.
100. Footer says education/report review/guided support.
101. Future signup includes written agreement.
102. Future signup includes cancellation rights.
103. Future billing avoids advance-fee risk.
104. Testimonials require substantiation.
105. AI outputs require compliance review before customer action.

### Customer Model + Business

106. Free Review captures goal and score range.
107. Plus maps to repair/build/track value.
108. Pro maps to protect/priority/readiness value.
109. Legal+ appears after eligibility, not hard-sold.
110. Auto-ready funnel tags lead source.
111. Mortgage-ready funnel tags lead source.
112. Apartment-ready funnel tags lead source.
113. Identity-theft funnel routes to protection workflow.
114. Thin-file customer routes to builder tools.
115. High-utilization customer routes to score-factor education.
116. Denial-event customer routes to readiness workflow.
117. Partner referral source is captured.
118. Admin can triage leads by goal.
119. Lifecycle messages can be triggered by status.
120. Investor KPI report can calculate lead count, plan interest, and goal mix.

## Current Automated Coverage

`npm run test:smoke` currently verifies the backend foundation:

- Health route
- Home/admin pages
- Security headers
- Locked admin API
- Content-type validation
- Invalid email
- Invalid enum
- Honeypot
- Valid lead creation
- Authenticated admin read
- No `ipHash` leakage
- Data directory blocking
- Oversized payload handling

## Sources Used

- Dovly official pricing and app pages
- Dovly how-it-works page
- Lexington Law official site and FAQ
- CFPB Lexington Law / CreditRepair.com case page
- Credit Saint official packages and home page
- FTC Credit Repair Organizations Act
- FTC Safeguards Rule
- NIST CSF 2.0
