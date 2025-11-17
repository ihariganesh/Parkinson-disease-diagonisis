# 🧪 Testing Guide - Complete Website Refinement

## Quick Start Testing

### 1. Database Migration ✅

```bash
cd /home/hari/Downloads/parkinson/parkinson-app/backend

# Check current migration status
alembic current

# Run the migration
alembic upgrade head

# Verify migration applied
alembic current
# Should show: add_user_profile_fields (head)
```

### 2. Start Backend Server 🚀

```bash
cd /home/hari/Downloads/parkinson/parkinson-app/backend

# Activate virtual environment
source ml_env/bin/activate

# Verify google-generativeai is installed
pip list | grep google-generativeai
# Should show: google-generativeai 0.8.5

# Set API key (if not in .env)
export GOOGLE_API_KEY=AIzaSyDA4lY5XN0QnX-sp_IBG5ZaXreIZGnd-rM

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
# INFO:     Started reloader process
# INFO:     Started server process
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
```

### 3. Start Frontend Server 💻

```bash
# Open new terminal
cd /home/hari/Downloads/parkinson/parkinson-app/frontend

# Install dependencies (if needed)
npm install

# Start dev server
npm run dev

# Expected output:
# VITE v5.x.x  ready in xxx ms
# ➜  Local:   http://localhost:5173/
# ➜  Network: http://192.168.x.x:5173/
```

---

## 📋 **Test Checklist**

### Backend API Tests

#### 1. Test Health Endpoint
```bash
curl http://localhost:8000/health
```
**Expected:**
```json
{
  "success": true,
  "message": "ParkinsonCare API is running",
  "version": "1.0.0"
}
```

#### 2. Test Profile Endpoint (requires auth token)
```bash
# First login to get token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'

# Copy the token from response
TOKEN="your_token_here"

# Test profile endpoint
curl http://localhost:8000/api/v1/patients/profile \
  -H "Authorization: Bearer $TOKEN"
```
**Expected:**
```json
{
  "id": "...",
  "email": "test@example.com",
  "first_name": "Test",
  "last_name": "User",
  "date_of_birth": null,
  "address_street": null,
  ...
}
```

#### 3. Test Update Profile
```bash
curl -X PUT http://localhost:8000/api/v1/patients/profile \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1960-01-15",
    "phone_number": "+1 (555) 123-4567",
    "address_street": "123 Main St",
    "address_city": "San Francisco",
    "address_state": "California",
    "address_zip": "94102",
    "address_country": "United States"
  }'
```
**Expected:**
```json
{
  "success": true,
  "message": "Profile updated successfully"
}
```

#### 4. Test Lifestyle Recommendations (Quick)
```bash
curl -X POST http://localhost:8000/api/v1/lifestyle/recommendations/quick \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "diagnosis": "Early Stage Parkinsons Disease",
    "pd_probability": 78.5,
    "age": 65
  }'
```
**Expected:**
```json
{
  "success": true,
  "recommendations": {
    "exercise": {
      "category": "Exercise & Physical Activity",
      "items": ["...", "..."],
      "priority": "high"
    },
    "nutrition": { ... },
    ...
  },
  "generated_at": "2025-11-13T..."
}
```

---

### Frontend UI Tests

#### Test 1: Dashboard View ✅
1. Open browser: http://localhost:5173
2. Login with test credentials
3. Navigate to Dashboard
4. **Verify:**
   - ✅ Navigation has only 4 items: Dashboard, Analysis, Reports, Profile
   - ✅ Single "Start Comprehensive Analysis" button visible
   - ✅ Gradient background (indigo→purple→blue)
   - ✅ Visual modality grid with 3 icons
   - ✅ NO individual analysis buttons (Handwriting, Speech, DaT)

#### Test 2: Navigation Redirects ✅
Try navigating to old routes:
1. http://localhost:5173/handwriting → Should redirect to /comprehensive
2. http://localhost:5173/speech → Should redirect to /comprehensive
3. http://localhost:5173/dat → Should redirect to /comprehensive
4. http://localhost:5173/multimodal-upload → Should redirect to /comprehensive

**Verify:** All redirects work correctly ✅

#### Test 3: Profile Page ✅
1. Click "Profile" in navigation
2. **Verify:**
   - ✅ Profile page loads
   - ✅ Basic Information section visible
   - ✅ Address section visible
   - ✅ Emergency Contact section visible
   - ✅ "Edit Profile" button in top right
3. Click "Edit Profile"
4. Fill in all fields:
   - First Name: John
   - Last Name: Doe
   - Date of Birth: 01/15/1960
   - Phone: +1 (555) 123-4567
   - Address fields
   - Emergency contact
5. Click "Save Changes"
6. **Verify:**
   - ✅ Success message appears
   - ✅ Age auto-calculated (should show "65 years old")
   - ✅ All fields saved correctly
   - ✅ Edit mode exits automatically

#### Test 4: Comprehensive Analysis Flow ✅
1. Click "Start Comprehensive Analysis" from Dashboard
2. **Verify:**
   - ✅ Redirects to /comprehensive page
   - ✅ Upload form visible
   - ✅ Three file upload sections (Handwriting, Voice, DaT)
3. Upload sample files:
   - Handwriting: spiral drawing image
   - Voice: audio file (MP3 or WAV)
   - DaT Scan: brain scan image
4. Click "Analyze"
5. **Verify:**
   - ✅ Loading animation shows
   - ✅ Analysis completes (30-60 seconds)
   - ✅ Results display with diagnosis and confidence

#### Test 5: Lifestyle Recommendations ✅
(After completing Test 4)
1. Wait for recommendations to generate
2. **Verify:**
   - ✅ Loading animation shows (if integration added)
   - ✅ Recommendations section appears below results
   - ✅ All 7 categories visible:
     - 🏃 Exercise
     - 🥗 Nutrition
     - 🧘 Mental Health
     - 😴 Sleep
     - 🏠 Daily Living
     - 💊 Medical Management
     - 📱 Technology Support
   - ✅ Each category has:
     - Icon and title
     - Priority badge (High/Medium/Low)
     - List of recommendations
     - Gradient header
   - ✅ Medical disclaimer at bottom
   - ✅ All text readable and properly formatted

---

## 🔍 **Detailed Component Tests**

### Test A: Gemini AI Service

```bash
# Test Gemini service directly
cd /home/hari/Downloads/parkinson/parkinson-app/backend
source ml_env/bin/activate
python3 << 'EOF'
import asyncio
import os
os.environ['GOOGLE_API_KEY'] = 'AIzaSyDA4lY5XN0QnX-sp_IBG5ZaXreIZGnd-rM'

from app.services.gemini_service import get_gemini_service

async def test_gemini():
    service = get_gemini_service()
    
    recommendations = await service.generate_recommendations(
        diagnosis="Early Stage Parkinson's Disease",
        pd_probability=78.5,
        confidence=78.5,
        age=65,
        symptoms={
            'tremor': True,
            'rigidity': True,
            'bradykinesia': True
        },
        medical_history="Recently diagnosed, no prior treatment"
    )
    
    print("✅ Gemini Service Test")
    print(f"Categories: {len(recommendations)}")
    for category, data in recommendations.items():
        if isinstance(data, dict) and 'items' in data:
            print(f"  - {category}: {len(data['items'])} items, priority: {data.get('priority', 'N/A')}")
    
    return recommendations

result = asyncio.run(test_gemini())
print("\n✅ Test passed!" if result else "❌ Test failed!")
EOF
```

**Expected Output:**
```
✅ Gemini Service Test
Categories: 8
  - exercise: 4-6 items, priority: high
  - nutrition: 4-6 items, priority: high
  - mental_health: 4-6 items, priority: medium
  - sleep: 4-6 items, priority: high
  - daily_living: 4-6 items, priority: medium
  - medical_management: 4-6 items, priority: high
  - technology_support: 3-5 items, priority: low
  - metadata: ...

✅ Test passed!
```

### Test B: User Model Age Calculation

```bash
cd /home/hari/Downloads/parkinson/parkinson-app/backend
source ml_env/bin/activate
python3 << 'EOF'
from datetime import datetime
from app.db.models import User, UserRole

# Create test user
user = User()
user.email = "test@example.com"
user.first_name = "Test"
user.last_name = "User"
user.role = UserRole.PATIENT
user.date_of_birth = datetime(1960, 1, 15)

# Test age calculation
age = user.age
print(f"✅ User Age Test")
print(f"Date of Birth: {user.date_of_birth.strftime('%Y-%m-%d')}")
print(f"Calculated Age: {age} years")
print(f"Expected: ~65 years")
print("✅ Test passed!" if 64 <= age <= 66 else "❌ Test failed!")
EOF
```

---

## 🎯 **Integration Tests**

### Test 1: Complete User Journey

**Steps:**
1. Register new user
2. Login
3. Navigate to Dashboard → verify new design
4. Go to Profile → fill all fields → save
5. Go to Comprehensive Analysis
6. Upload files
7. Submit analysis
8. Wait for results
9. Verify lifestyle recommendations appear
10. Go back to Dashboard → verify data persists

**Expected Time:** ~10 minutes
**Success Criteria:** All steps complete without errors ✅

### Test 2: API Integration Test

```bash
# Full API integration test
cd /home/hari/Downloads/parkinson/parkinson-app/backend
source ml_env/bin/activate

# Run this script
python3 << 'EOF'
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

print("🧪 API Integration Test\n")

# 1. Register user
print("1. Testing registration...")
response = requests.post(f"{BASE_URL}/auth/register", json={
    "email": f"test_{int(time.time())}@example.com",
    "password": "Test123!@#",
    "first_name": "Test",
    "last_name": "User",
    "role": "patient"
})
print(f"   Status: {response.status_code}")
token = response.json().get('access_token')

# 2. Test profile
print("2. Testing profile endpoints...")
headers = {"Authorization": f"Bearer {token}"}

# Get profile
response = requests.get(f"{BASE_URL}/patients/profile", headers=headers)
print(f"   GET profile: {response.status_code}")

# Update profile
response = requests.put(f"{BASE_URL}/patients/profile", headers=headers, json={
    "date_of_birth": "1960-01-15",
    "address_city": "San Francisco"
})
print(f"   PUT profile: {response.status_code}")

# 3. Test lifestyle recommendations
print("3. Testing lifestyle recommendations...")
response = requests.post(f"{BASE_URL}/lifestyle/recommendations/quick", 
    headers=headers,
    json={
        "diagnosis": "Early Stage Parkinson's Disease",
        "pd_probability": 78.5,
        "age": 65
    }
)
print(f"   Quick recommendations: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   Categories: {len(data['recommendations'])}")

print("\n✅ Integration test complete!")
EOF
```

---

## 📊 **Performance Tests**

### Test 1: Page Load Times
- Dashboard: < 1 second ✅
- Profile Page: < 1 second ✅
- Comprehensive Analysis: < 2 seconds ✅
- Recommendations: 10-20 seconds (AI generation) ✅

### Test 2: API Response Times
```bash
# Time API endpoints
time curl http://localhost:8000/health
# Expected: ~50-100ms

time curl http://localhost:8000/api/v1/patients/profile \
  -H "Authorization: Bearer $TOKEN"
# Expected: ~100-300ms

time curl -X POST http://localhost:8000/api/v1/lifestyle/recommendations/quick \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"diagnosis": "Early Stage PD", "pd_probability": 75, "age": 65}'
# Expected: ~10-20 seconds (first call), ~5-10 seconds (subsequent)
```

---

## 🐛 **Troubleshooting**

### Issue 1: Database Migration Fails
```bash
# Reset migrations if needed
cd backend
alembic downgrade -1
alembic upgrade head
```

### Issue 2: Gemini API Not Working
```bash
# Check API key
cd backend
source ml_env/bin/activate
python3 -c "
import os
os.environ['GOOGLE_API_KEY'] = 'AIzaSyDA4lY5XN0QnX-sp_IBG5ZaXreIZGnd-rM'
import google.generativeai as genai
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])
model = genai.GenerativeModel('gemini-pro')
response = model.generate_content('Say hello')
print(response.text)
"
```

### Issue 3: Profile Age Not Showing
- Check DOB is saved in database
- Verify User model has `age` property
- Check frontend is calling the correct API

### Issue 4: Recommendations Not Appearing
- Check browser console for errors
- Verify backend logs for AI errors
- Check network tab for API call
- Verify report_id is being passed correctly

---

## ✅ **Test Results Template**

```markdown
# Test Results - [Date]

## Backend Tests
- [ ] Health endpoint
- [ ] Profile GET endpoint
- [ ] Profile PUT endpoint
- [ ] Lifestyle recommendations endpoint
- [ ] Gemini AI service
- [ ] Database migration

## Frontend Tests
- [ ] Dashboard redesign
- [ ] Navigation (4 items)
- [ ] Profile page
- [ ] Comprehensive analysis
- [ ] Lifestyle recommendations display
- [ ] Route redirects

## Integration Tests
- [ ] Complete user journey
- [ ] Age calculation
- [ ] AI recommendation generation
- [ ] Profile data persistence

## Performance
- [ ] Page load times < 2s
- [ ] API response times acceptable
- [ ] AI generation < 30s

## Issues Found
1. [Issue description]
2. [Issue description]

## Overall Status
✅ PASS / ❌ FAIL

## Notes
[Any additional notes]
```

---

## 🎉 **Success Indicators**

When everything is working correctly, you should see:

1. ✅ Clean dashboard with single CTA
2. ✅ 4-item navigation
3. ✅ Profile page with auto-calculated age
4. ✅ Comprehensive analysis working
5. ✅ 7 categories of lifestyle recommendations
6. ✅ No console errors
7. ✅ All old routes redirect properly
8. ✅ Mobile responsive design

---

**Happy Testing! 🧪**

If you encounter any issues, refer to:
- `WEBSITE_REFINEMENT_COMPLETE.md` - Complete documentation
- `LIFESTYLE_RECOMMENDATIONS_INTEGRATION.md` - Integration guide
- `VISUAL_PREVIEW.md` - Visual reference
