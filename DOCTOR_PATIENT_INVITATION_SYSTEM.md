# Doctor-Patient Invitation System 🔗

## Overview
Realistic telemedicine approach for linking doctors and patients using invitation codes. Patient controls privacy, doctor approves access.

---

## 🎯 How It Works

### Complete Flow:

```
1. DOCTOR generates invitation code
   ↓
2. DOCTOR shares code/link with patient
   ↓
3. PATIENT enters code in dashboard
   ↓
4. Status = PENDING (waiting for approval)
   ↓
5. DOCTOR reviews and approves/rejects
   ↓
6. If APPROVED → Access granted
   If REJECTED → Patient can try another code
```

---

## 👨‍⚕️ Doctor Side

### 1. Generate Invitation Code

**Endpoint:** `POST /api/v1/invitation/doctor/generate-code`

**Request:**
```json
{
  "max_uses": 5,
  "expires_in_days": 30,
  "description": "For new patients - December 2025"
}
```

**Response:**
```json
{
  "invitation_id": "uuid",
  "invitation_code": "ABCD-1234",
  "invitation_link": "http://localhost:3000/link-doctor?code=ABCD-1234",
  "max_uses": 5,
  "current_uses": 0,
  "expires_at": "2026-01-17T00:00:00Z",
  "is_active": true,
  "description": "For new patients - December 2025",
  "created_at": "2025-12-18T00:00:00Z"
}
```

**Features:**
- ✅ Unique 8-character code (XXXX-XXXX format)
- ✅ Easy to type and share
- ✅ Single-use or multi-use (configurable)
- ✅ Optional expiration (default 30 days)
- ✅ Optional description for tracking

**Share Options:**
1. **Share code directly:** "ABCD-1234"
2. **Share link:** `http://localhost:3000/link-doctor?code=ABCD-1234`
3. **Generate QR code** (frontend can implement)

---

### 2. View My Invitation Codes

**Endpoint:** `GET /api/v1/invitation/doctor/my-codes?active_only=true`

**Response:**
```json
[
  {
    "invitation_id": "uuid",
    "invitation_code": "ABCD-1234",
    "invitation_link": "http://localhost:3000/link-doctor?code=ABCD-1234",
    "max_uses": 5,
    "current_uses": 2,
    "expires_at": "2026-01-17T00:00:00Z",
    "is_active": true,
    "description": "For new patients",
    "created_at": "2025-12-18T00:00:00Z"
  }
]
```

**Shows:**
- All generated codes
- Usage statistics (2 out of 5 uses)
- Expiration status
- Active/inactive status

---

### 3. View Pending Requests

**Endpoint:** `GET /api/v1/invitation/doctor/pending-requests`

**Response:**
```json
[
  {
    "request_id": "uuid",
    "patient_name": "John Doe",
    "patient_email": "john@example.com",
    "doctor_name": "Dr. Sarah Johnson",
    "status": "pending",
    "patient_message": "Hello, I'd like to be your patient for Parkinson's monitoring.",
    "requested_at": "2025-12-18T10:30:00Z"
  }
]
```

**Shows:**
- All patients waiting for approval
- Patient details (name, email)
- Optional message from patient
- Request timestamp

---

### 4. Approve Patient Request

**Endpoint:** `POST /api/v1/invitation/doctor/approve-request`

**Request:**
```json
{
  "request_id": "uuid",
  "response_message": "Welcome! I'll be monitoring your progress."
}
```

**Response:**
```json
{
  "success": true,
  "message": "Patient link request approved",
  "patient_name": "John Doe",
  "assignment_id": "uuid"
}
```

**What Happens:**
1. ✅ Request status → APPROVED
2. ✅ Creates `DoctorPatientAssignment`
3. ✅ Patient can now see this doctor in "My Doctors"
4. ✅ Doctor can see patient in assigned patient list
5. ✅ Doctor can access patient's reports

---

### 5. Reject Patient Request

**Endpoint:** `POST /api/v1/invitation/doctor/reject-request`

**Request:**
```json
{
  "request_id": "uuid",
  "response_message": "Sorry, my patient list is currently full."
}
```

**Response:**
```json
{
  "success": true,
  "message": "Patient link request rejected",
  "patient_name": "John Doe"
}
```

**What Happens:**
1. ✅ Request status → REJECTED
2. ✅ Patient is notified
3. ✅ Patient can try with another doctor's code

---

### 6. Deactivate Invitation Code

**Endpoint:** `DELETE /api/v1/invitation/doctor/code/{invitation_id}`

**Response:**
```json
{
  "success": true,
  "message": "Invitation code deactivated"
}
```

**Use Cases:**
- Code was shared publicly by mistake
- No longer accepting new patients
- Code security compromised

---

## 👤 Patient Side

### 1. Enter Invitation Code

**Endpoint:** `POST /api/v1/invitation/patient/use-code`

**Request:**
```json
{
  "invitation_code": "ABCD-1234",
  "message": "Hello Dr. Johnson, I'd like to be your patient for Parkinson's monitoring."
}
```

**Response:**
```json
{
  "success": true,
  "message": "Link request sent to doctor",
  "request_id": "uuid",
  "doctor_name": "Dr. Sarah Johnson",
  "status": "pending",
  "next_step": "Wait for doctor approval. You will be notified once approved."
}
```

**Validations:**
- ✅ Code must exist
- ✅ Code must be active
- ✅ Code must not be expired
- ✅ Code must have uses remaining
- ✅ Patient can't have duplicate pending requests with same doctor

---

### 2. View My Link Requests

**Endpoint:** `GET /api/v1/invitation/patient/my-requests`

**Response:**
```json
[
  {
    "request_id": "uuid",
    "patient_name": "John Doe",
    "patient_email": "john@example.com",
    "doctor_name": "Dr. Sarah Johnson",
    "status": "pending",
    "patient_message": "Hello, I'd like to be your patient.",
    "requested_at": "2025-12-18T10:30:00Z"
  },
  {
    "request_id": "uuid2",
    "patient_name": "John Doe",
    "patient_email": "john@example.com",
    "doctor_name": "Dr. Michael Smith",
    "status": "approved",
    "patient_message": null,
    "requested_at": "2025-12-15T09:00:00Z"
  }
]
```

**Shows:**
- All requests (pending, approved, rejected)
- Doctor names
- Status of each request
- Timestamps

---

### 3. View My Doctors

**Endpoint:** `GET /api/v1/invitation/patient/my-doctors`

**Response:**
```json
{
  "success": true,
  "count": 2,
  "doctors": [
    {
      "doctor_id": "uuid",
      "doctor_name": "Dr. Sarah Johnson",
      "email": "doctor@example.com",
      "specialization": "Neurology",
      "hospital": "Parkinson Research Hospital",
      "linked_since": "2025-12-15T10:00:00Z",
      "assignment_id": "uuid"
    }
  ]
}
```

**Shows:**
- All approved doctors
- Doctor specialization
- Hospital affiliation
- Link date

---

### 4. Unlink from Doctor

**Endpoint:** `DELETE /api/v1/invitation/patient/unlink-doctor/{assignment_id}`

**Response:**
```json
{
  "success": true,
  "message": "Successfully unlinked from Dr. Johnson",
  "doctor_name": "Dr. Sarah Johnson"
}
```

**Patient Privacy:**
- ✅ Patient controls who has access
- ✅ Can revoke access anytime
- ✅ Doctor loses access to reports immediately

---

## 🌐 Public Endpoints

### Validate Invitation Code (No Auth Required)

**Endpoint:** `GET /api/v1/invitation/validate-code/{code}`

**Example:** `GET /api/v1/invitation/validate-code/ABCD-1234`

**Response:**
```json
{
  "valid": true,
  "invitation_code": "ABCD-1234",
  "doctor_name": "Dr. Sarah Johnson",
  "specialization": "Neurology",
  "hospital": "Parkinson Research Hospital",
  "description": "For new patients - December 2025",
  "expires_at": "2026-01-17T00:00:00Z",
  "uses_remaining": 3
}
```

**Use Case:**
- Display doctor info before patient logs in
- Validate code in real-time as user types
- Show expiration warning

---

## 🗄️ Database Tables

### 1. doctor_invitations
Stores invitation codes generated by doctors.

**Fields:**
- `id` - Primary key
- `doctor_id` - FK to users (doctor)
- `invitation_code` - Unique code (XXXX-XXXX)
- `max_uses` - Maximum uses allowed
- `current_uses` - Current usage count
- `expires_at` - Expiration datetime (nullable)
- `is_active` - Active status
- `description` - Optional description
- `created_at` - Creation timestamp

**Indexes:**
- `invitation_code` (unique)
- `doctor_id`

---

### 2. doctor_patient_link_requests
Stores patient requests to link with doctors.

**Fields:**
- `id` - Primary key
- `patient_id` - FK to users (patient)
- `doctor_id` - FK to users (doctor)
- `invitation_id` - FK to doctor_invitations
- `status` - Enum (pending, approved, rejected, expired)
- `patient_message` - Optional message from patient
- `doctor_response` - Optional response from doctor
- `approved_at` - Approval timestamp
- `rejected_at` - Rejection timestamp
- `requested_at` - Request timestamp
- `updated_at` - Update timestamp

**Status Flow:**
```
PENDING → APPROVED (creates assignment)
PENDING → REJECTED (patient can try again)
```

---

### 3. doctor_patient_assignments (Updated)
Links approved doctor-patient relationships.

**New Field:**
- `link_request_id` - FK to doctor_patient_link_requests (nullable)

**Purpose:**
- Track how assignment was created (via invitation vs admin)
- Maintain audit trail

---

## 📱 Frontend Integration

### Doctor Dashboard Pages

#### 1. Invitation Codes Page
```typescript
// /doctor/invitations

Features:
- Button: "Generate New Code"
- List of all codes with:
  * Code display (ABCD-1234)
  * Copy button
  * QR code generator
  * Usage: "2/5 uses"
  * Expires: "15 days left"
  * Deactivate button

- Pending requests section:
  * Patient cards with approve/reject buttons
  * Patient info display
  * Message from patient
```

#### 2. Generate Code Modal
```typescript
interface GenerateCodeForm {
  maxUses: number;
  expiresInDays: number;
  description: string;
}

onSubmit() {
  axios.post('/api/v1/invitation/doctor/generate-code', form)
    .then(response => {
      // Show code + shareable link
      displayCode(response.data.invitation_code);
      displayLink(response.data.invitation_link);
      showCopyButton();
      showQRCode();
    });
}
```

### Patient Dashboard Pages

#### 1. Link Doctor Page
```typescript
// /link-doctor or /link-doctor?code=ABCD-1234

Features:
- Input field: "Enter invitation code"
- Auto-fill from URL parameter if present
- Validate button
- Shows doctor info after validation
- Optional message textarea
- Submit button: "Send Link Request"

Flow:
1. User enters code
2. Validate code (public API)
3. Display doctor details
4. User confirms and submits
5. Request sent, status = pending
```

#### 2. My Doctors Page
```typescript
// /patient/my-doctors

Features:
- List of linked doctors
- Each card shows:
  * Doctor name
  * Specialization
  * Hospital
  * Linked since date
  * View reports button
  * Unlink button (with confirmation)

- Pending requests section:
  * Status indicators
  * "Waiting for approval" message
```

---

## 🔒 Security Features

### Authentication
- ✅ All endpoints require JWT token (except validate-code)
- ✅ Role-based access (doctor vs patient)
- ✅ Patient assignment verification

### Privacy
- ✅ Patient controls access
- ✅ Can unlink anytime
- ✅ Doctor can reject requests
- ✅ Codes can be deactivated

### Validation
- ✅ Code expiration checking
- ✅ Usage limit enforcement
- ✅ Duplicate request prevention
- ✅ Active status verification

---

## 💡 Use Cases

### Use Case 1: Doctor Onboards New Patients
```
1. Doctor generates code: "XYZ5-7890"
2. Doctor shares in clinic: "Enter this code in the app"
3. 5 patients use the code
4. Doctor reviews pending requests
5. Doctor approves all 5 patients
6. Patients now linked
```

### Use Case 2: Patient Finds Doctor
```
1. Patient gets referral to Dr. Johnson
2. Doctor gives patient code: "ABCD-1234"
3. Patient enters code in app
4. Sees Dr. Johnson's profile
5. Sends request with message
6. Waits for approval
7. Receives notification when approved
8. Can now share reports with doctor
```

### Use Case 3: Patient Controls Privacy
```
1. Patient linked to 2 doctors
2. Wants to switch to new doctor
3. Unlinks from Doctor A
4. Uses new code from Doctor B
5. Sends request to Doctor B
6. Gets approved
7. Now only Doctor B has access
```

### Use Case 4: Doctor Manages Codes
```
1. Doctor has 3 active codes:
   - Code A: For clinic patients (10 uses)
   - Code B: For referrals (5 uses)
   - Code C: For VIP patients (1 use)
2. Code A gets shared publicly by accident
3. Doctor deactivates Code A
4. Generates new Code D for clinic
5. Existing patients unaffected
```

---

## ✅ Benefits

### For Patients:
- ✅ Privacy control
- ✅ Easy to understand
- ✅ Can link multiple doctors
- ✅ Can unlink anytime
- ✅ No complex forms

### For Doctors:
- ✅ Control over patient list
- ✅ Approve/reject requests
- ✅ Track code usage
- ✅ Revoke codes if needed
- ✅ Professional workflow

### For System:
- ✅ Audit trail
- ✅ Scalable
- ✅ Secure
- ✅ Easy to explain in viva
- ✅ Industry standard approach

---

## 🧪 Testing

### Test Flow 1: Happy Path
```bash
# 1. Doctor generates code
curl -X POST http://localhost:8000/api/v1/invitation/doctor/generate-code \
  -H "Authorization: Bearer DOCTOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"max_uses": 5, "expires_in_days": 30}'

# Response: {"invitation_code": "ABCD-1234", ...}

# 2. Patient uses code
curl -X POST http://localhost:8000/api/v1/invitation/patient/use-code \
  -H "Authorization: Bearer PATIENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"invitation_code": "ABCD-1234", "message": "Hello doctor"}'

# 3. Doctor gets pending requests
curl http://localhost:8000/api/v1/invitation/doctor/pending-requests \
  -H "Authorization: Bearer DOCTOR_TOKEN"

# 4. Doctor approves
curl -X POST http://localhost:8000/api/v1/invitation/doctor/approve-request \
  -H "Authorization: Bearer DOCTOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"request_id": "REQUEST_UUID"}'

# 5. Verify assignment
curl http://localhost:8000/api/v1/doctor/patients \
  -H "Authorization: Bearer DOCTOR_TOKEN"
```

---

## 📊 API Summary

### Doctor Endpoints (5)
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/invitation/doctor/generate-code` | POST | Generate invitation code |
| `/invitation/doctor/my-codes` | GET | View all codes |
| `/invitation/doctor/pending-requests` | GET | View pending requests |
| `/invitation/doctor/approve-request` | POST | Approve patient |
| `/invitation/doctor/reject-request` | POST | Reject patient |
| `/invitation/doctor/code/{id}` | DELETE | Deactivate code |

### Patient Endpoints (4)
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/invitation/patient/use-code` | POST | Use invitation code |
| `/invitation/patient/my-requests` | GET | View my requests |
| `/invitation/patient/my-doctors` | GET | View linked doctors |
| `/invitation/patient/unlink-doctor/{id}` | DELETE | Unlink from doctor |

### Public Endpoints (1)
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/invitation/validate-code/{code}` | GET | Validate code (no auth) |

---

## 🎉 Implementation Complete!

✅ **Backend:** Fully implemented and ready
✅ **Database:** 3 new tables with relationships
✅ **Security:** Authentication and authorization
✅ **Privacy:** Patient controls access
✅ **Realistic:** Used in real telemedicine apps
✅ **Viva-Ready:** Easy to explain and demonstrate

**The invitation system is production-ready!** 🚀

Next step: Build frontend UI to display and use these features.
