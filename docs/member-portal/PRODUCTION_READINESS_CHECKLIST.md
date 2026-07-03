# Production Readiness Checklist — Member Portal

## Front-end defaults

- [x] Demo/mock mode off by default
- [x] Customer findings blocked without backend production gates
- [x] Draft letters blocked without backend production gates
- [x] Secure upload disabled until backend connected
- [x] No real credit data in code
- [x] No full SSN/DOB/account numbers
- [x] No auto-send
- [x] Draft-only language
- [x] Customer approval UI prepared
- [x] Production gate banner

## Still required before live launch

- [ ] Real auth/session provider
- [ ] Role-based access control
- [ ] Approved scanner API
- [ ] Encrypted file storage
- [ ] Audit logs
- [ ] Health check backend
- [ ] Ground-truth validation backend
- [ ] QA verification backend
- [ ] Security audit backend
- [ ] Production gate backend
- [ ] Legal/compliance review
- [ ] Privacy/terms/disclosure pages
- [ ] Incident response plan
- [ ] Vendor/API risk review
- [ ] Payment/CROA review before billing
