# Invitation System - Quick Reference Card

## 🚀 Quick Start (2 Minutes)

### Setup & Test:
```bash
cd /home/hari/Downloads/parkinson/parkinson-app

# 1. Create test accounts
python setup_invitation_test_users.py

# 2. Run complete test
python test_invitation_system.py

# Expected: ✅ ALL TESTS PASSED!
```

---

## 📋 API Endpoints Cheat Sheet

### Doctor Endpoints

| Action | Endpoint | Method |
|--------|----------|--------|
| Generate code | `/api/v1/invitation/doctor/generate-code` | POST |
| View my codes | `/api/v1/invitation/doctor/my-codes` | GET |
| View pending | `/api/v1/invitation/doctor/pending-requests` | GET |
| Approve | `/api/v1/invitation/doctor/approve-request` | POST |
| Reject | `/api/v1/invitation/doctor/reject-request` | POST |
| Deactivate | `/api/v1/invitation/doctor/code/{id}` | DELETE |

### Patient Endpoints

| Action | Endpoint | Method |
|--------|----------|--------|
| Use code | `/api/v1/invitation/patient/use-code` | POST |
| View requests | `/api/v1/invitation/patient/my-requests` | GET |
| View doctors | `/api/v1/invitation/patient/my-doctors` | GET |
| Unlink | `/api/v1/invitation/patient/unlink-doctor/{id}` | DELETE |

### Public

| Action | Endpoint | Method |
|--------|----------|--------|
| Validate code | `/api/v1/invitation/validate-code/{code}` | GET |

---

## 💻 Code Examples

### Doctor: Generate Code
```bash
curl -X POST http://localhost:8000/api/v1/invitation/doctor/generate-code \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "max_uses": 5,
    "expires_in_days": 30,
    "description": "For new patients"
  }'

# Response: {"invitation_code": "ABCD-1234", ...}
```

### Patient: Use Code
```bash
curl -X POST http://localhost:8000/api/v1/invitation/patient/use-code \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "invitation_code": "ABCD-1234",
    "message": "Hello doctor!"
  }'

# Response: {"status": "pending", ...}
```

### Doctor: Approve
```bash
curl -X POST http://localhost:8000/api/v1/invitation/doctor/approve-request \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "uuid",
    "response_message": "Welcome!"
  }'

# Response: {"success": true, ...}
```

---

## 🔄 Complete Workflow

```
1. DOCTOR                        2. PATIENT
   ↓                               ↓
   Generate Code              Enter Code
   "ABCD-1234"                "ABCD-1234"
   ↓                               ↓
   Share with                 Submit Request
   Patient                    (Status: PENDING)
                                   ↓
3. DOCTOR                    4. PATIENT
   ↓                               ↓
   View Pending              Wait for
   Requests                  Approval
   ↓                               ↓
   Approve                   Receives
   Request                   Notification
   ↓                               ↓
   ✅ LINKED!                ✅ LINKED!
```

---

## 🗄️ Database Tables

### doctor_invitations
- `invitation_code` - Unique code (XXXX-XXXX)
- `max_uses` - Maximum uses
- `current_uses` - Current usage count
- `expires_at` - Expiration date
- `is_active` - Active status

### doctor_patient_link_requests
- `status` - pending/approved/rejected
- `patient_message` - Optional message
- `doctor_response` - Optional response
- `approved_at` - Approval timestamp

### doctor_patient_assignments
- `link_request_id` - Links to request
- `is_active` - Active status
- `assigned_at` - Assignment timestamp

---

## 🔐 Test Accounts

| Role | Email | Password |
|------|-------|----------|
| Doctor | test_doctor@example.com | Doctor123! |
| Patient | test_patient@example.com | Patient123! |

---

## ✅ Feature Checklist

- ✅ Code generation (XXXX-XXXX format)
- ✅ Multi-use codes (1-∞ uses)
- ✅ Code expiration (1-365 days)
- ✅ Public validation (no auth)
- ✅ Patient requests (with message)
- ✅ Doctor approval (with response)
- ✅ Doctor rejection (patient can retry)
- ✅ Patient unlink (privacy control)
- ✅ Usage tracking (X/Y uses)
- ✅ Status tracking (pending/approved/rejected)
- ✅ Code deactivation
- ✅ Audit trail (link_request_id)

---

## 🎯 Viva Talking Points

**Q: Why invitation codes?**  
A: Industry standard (Teladoc, Doctor on Demand use this)

**Q: How is privacy maintained?**  
A: Patient controls access, can unlink anytime

**Q: How is security ensured?**  
A: JWT auth, role-based access, code expiration, usage limits

**Q: What happens if code is compromised?**  
A: Doctor can deactivate code, existing links unaffected

**Q: Can a patient have multiple doctors?**  
A: Yes! Use multiple codes, patient sees all doctors

**Q: Can a doctor reject a patient?**  
A: Yes! Request stays pending until approved/rejected

---

## 📁 Documentation Files

1. **INVITATION_SYSTEM_COMPLETE.md** - Full implementation summary
2. **DOCTOR_PATIENT_INVITATION_SYSTEM.md** - Complete API reference
3. **This file** - Quick reference card

---

## 🐛 Troubleshooting

### Issue: "Only doctors can access this endpoint"
**Solution:** Check user role in database
```bash
cd backend
python -c "from app.db.database import SessionLocal; from app.db.models import User; db = SessionLocal(); user = db.query(User).filter(User.email=='test_doctor@example.com').first(); print(f'Role: {user.role}')"
```

### Issue: "Invalid invitation code"
**Solution:** Check code exists and is active
```bash
curl http://localhost:8000/api/v1/invitation/validate-code/YOUR-CODE
```

### Issue: "No such column: link_request_id"
**Solution:** Recreate tables
```bash
cd backend
python -c "from sqlalchemy import text; from app.db.database import engine; from app.db.models import Base; [engine.execute(text(f'DROP TABLE IF EXISTS {t}')) for t in ['doctor_patient_link_requests','doctor_invitations','doctor_patient_assignments']]; Base.metadata.create_all(bind=engine)"
```

---

## 📞 Support

- **Documentation:** See DOCTOR_PATIENT_INVITATION_SYSTEM.md
- **API Reference:** Check `/docs` endpoint (Swagger UI)
- **Test Script:** Run `test_invitation_system.py`

---

**Status:** 🟢 OPERATIONAL  
**Last Tested:** December 18, 2025  
**Test Result:** ✅ ALL TESTS PASSED
