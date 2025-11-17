# 🎨 Website Refinement Plan

**Date**: November 13, 2025  
**Goal**: Transform the Parkinson's diagnosis web app to focus on multimodal analysis with AI-powered lifestyle recommendations

---

## 📋 Overview

### Core Purpose
The web app diagnoses Parkinson's disease through **multimodal AI analysis** combining:
1. **DaT Scan Analysis** (brain imaging)
2. **Handwriting Analysis** (motor symptoms)
3. **Voice Analysis** (speech biomarkers)

### Key Outputs
- Comprehensive diagnosis report
- AI-powered lifestyle recommendations (using Google Gemini)
- Profile management with age calculation and address

---

## ✅ Changes Completed

### 1. Dashboard Redesign ✅
**File**: `frontend/src/components/patient/PatientDashboard.tsx`

**Changes Made**:
- ✅ Removed individual analysis tool buttons (Handwriting, Speech, DaT)
- ✅ Enhanced comprehensive analysis section with better visual design
- ✅ Added gradient background with modern UI
- ✅ Included visual grid showing all modalities
- ✅ Updated CTA buttons to point to `/comprehensive`

**New Dashboard Features**:
- Single prominent "Start Comprehensive Analysis" button
- Visual representation of all 3 modalities
- Modality weights displayed (25% handwriting, 25% voice, 50% reports)
- Modern gradient design (indigo → purple → blue)

---

## 🔄 Changes Needed

### 2. Remove Individual Analysis Routes
**Files to Modify**:
- `frontend/src/App.tsx`
- `frontend/src/components/common/Navbar.tsx`

**Actions**:
- ❌ Remove routes: `/handwriting`, `/speech`, `/dat` (keep demo versions)
- ❌ Remove from navbar navigation
- ✅ Keep: `/comprehensive` as main analysis page
- ✅ Keep: `/demo/*` routes for public access

### 3. Add Google Gemini AI Integration

#### Backend Changes

**New File**: `backend/app/services/gemini_service.py`
```python
import google.generativeai as genai
from typing import Dict, Any

class GeminiLifestyleService:
    def __init__(self):
        genai.configure(api_key="AIzaSyDA4lY5XN0QnX-sp_IBG5ZaXreIZGnd-rM")
        self.model = genai.GenerativeModel('gemini-pro')
    
    async def generate_recommendations(
        self,
        diagnosis: str,
        pd_probability: float,
        age: int,
        patient_history: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate personalized lifestyle recommendations"""
        
        prompt = f\"\"\"
        Generate personalized lifestyle recommendations for a patient with:
        - Diagnosis: {diagnosis}
        - Parkinson's Probability: {pd_probability}%
        - Age: {age} years
        
        Provide recommendations in these categories:
        1. Exercise & Physical Activity
        2. Diet & Nutrition
        3. Mental Health & Stress Management
        4. Daily Routine & Sleep
        5. Medical Follow-ups
        
        Format as JSON with categories and specific actionable advice.
        \"\"\"
        
        response = self.model.generate_content(prompt)
        return self._parse_recommendations(response.text)
```

**New Endpoint**: `backend/app/api/v1/lifestyle.py`
```python
@router.post("/recommendations")
async def get_lifestyle_recommendations(
    diagnosis_id: int,
    current_user: User = Depends(get_current_user)
):
    # Get diagnosis details
    # Call Gemini service
    # Return recommendations
```

#### Frontend Changes

**New Component**: `frontend/src/components/patient/LifestyleRecommendations.tsx`
- Display AI-generated recommendations
- Categorized view (Exercise, Diet, Mental Health, etc.)
- Actionable tips with icons
- Save/bookmark favorite recommendations

### 4. Profile Management Page

**New File**: `frontend/src/pages/ProfilePage.tsx`

**Features**:
```typescript
interface UserProfile {
  firstName: string;
  lastName: string;
  email: string;
  dateOfBirth: Date;
  age: number;  // Calculated from DOB
  address: {
    street: string;
    city: string;
    state: string;
    zipCode: string;
    country: string;
  };
  phone?: string;
  emergencyContact?: {
    name: string;
    phone: string;
    relationship: string;
  };
}
```

**UI Sections**:
1. Personal Information
   - Name, Email (read-only after registration)
   - Date of Birth → Auto-calculate age
   - Phone number

2. Address Information
   - Complete address form
   - Editable fields

3. Emergency Contact
   - Name, phone, relationship

4. Account Settings
   - Change password
   - Notification preferences
   - Data privacy settings

### 5. Backend API Enhancements

**Update User Model**: `backend/app/models/user.py`
```python
class User(Base):
    # Existing fields...
    date_of_birth: Date
    address_street: str
    address_city: str
    address_state: str
    address_zip: str
    address_country: str
    phone: str
    emergency_contact_name: str
    emergency_contact_phone: str
    emergency_contact_relationship: str
    
    @property
    def age(self) -> int:
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < 
            (self.date_of_birth.month, self.date_of_birth.day)
        )
```

**New Endpoints**:
```python
# Profile Management
GET /api/v1/users/profile
PUT /api/v1/users/profile
GET /api/v1/users/profile/age  # Returns calculated age

# Lifestyle Recommendations
POST /api/v1/lifestyle/recommendations
GET /api/v1/lifestyle/recommendations/{diagnosis_id}
```

---

## 🎯 Implementation Order

### Phase 1: Navigation & Routing (30 minutes)
1. ✅ Update PatientDashboard.tsx (DONE)
2. Update App.tsx - Remove individual analysis routes
3. Update Navbar.tsx - Remove individual analysis links
4. Test navigation flow

### Phase 2: Gemini AI Integration (2 hours)
1. Install `google-generativeai` package
2. Create `gemini_service.py`
3. Add lifestyle recommendation endpoints
4. Create `LifestyleRecommendations.tsx` component
5. Integrate with ComprehensiveAnalysis page
6. Test recommendation generation

### Phase 3: Profile Management (3 hours)
1. Update User model with new fields
2. Create database migration
3. Update registration form to capture DOB and address
4. Create ProfilePage.tsx
5. Add profile edit functionality
6. Add age calculation utility
7. Update Navbar to include Profile link

### Phase 4: Testing & Polish (1 hour)
1. End-to-end testing
2. UI/UX improvements
3. Error handling
4. Loading states
5. Mobile responsiveness

---

## 📦 Required Packages

### Backend
```bash
pip install google-generativeai
```

### Frontend
No new packages needed (using existing React, Tailwind, Heroicons)

---

## 🎨 UI/UX Improvements

### Dashboard
- ✅ Modern gradient background
- ✅ Larger, more prominent CTA
- ✅ Visual modality representation
- ✅ Cleaner layout without clutter

### Profile Page
- Clean, organized sections
- Inline editing
- Auto-save functionality
- Age badge display
- Address map preview (optional)

### Lifestyle Recommendations
- Card-based layout
- Category filters
- Bookmark/save feature
- Print-friendly format
- Share functionality

---

## 🔐 Security Considerations

1. **API Key Management**
   - Store Gemini API key in environment variables
   - Never expose in client-side code
   - Rate limiting on recommendation endpoint

2. **Profile Data**
   - HIPAA-compliant storage
   - Encrypted sensitive fields
   - Audit logging for changes
   - User consent for AI analysis

3. **Address Validation**
   - Input sanitization
   - Format validation
   - Optional geocoding for accuracy

---

## 📊 Database Schema Changes

```sql
-- Add to users table
ALTER TABLE users ADD COLUMN date_of_birth DATE;
ALTER TABLE users ADD COLUMN address_street VARCHAR(255);
ALTER TABLE users ADD COLUMN address_city VARCHAR(100);
ALTER TABLE users ADD COLUMN address_state VARCHAR(100);
ALTER TABLE users ADD COLUMN address_zip VARCHAR(20);
ALTER TABLE users ADD COLUMN address_country VARCHAR(100);
ALTER TABLE users ADD COLUMN phone VARCHAR(20);
ALTER TABLE users ADD COLUMN emergency_contact_name VARCHAR(255);
ALTER TABLE users ADD COLUMN emergency_contact_phone VARCHAR(20);
ALTER TABLE users ADD COLUMN emergency_contact_relationship VARCHAR(100);

-- Create lifestyle_recommendations table
CREATE TABLE lifestyle_recommendations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    diagnosis_id INTEGER REFERENCES diagnosis_reports(id),
    recommendations JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🚀 Deployment Steps

1. **Database Migration**
   ```bash
   cd backend
   alembic revision --autogenerate -m "Add user profile fields"
   alembic upgrade head
   ```

2. **Install Dependencies**
   ```bash
   pip install google-generativeai
   ```

3. **Environment Variables**
   ```bash
   # Add to .env
   GEMINI_API_KEY=AIzaSyDA4lY5XN0QnX-sp_IBG5ZaXreIZGnd-rM
   ```

4. **Frontend Build**
   ```bash
   cd frontend
   npm run build
   ```

5. **Restart Services**
   ```bash
   # Backend
   uvicorn app.main:app --reload
   
   # Frontend  
   npm run dev
   ```

---

## ✅ Success Criteria

### Dashboard
- [x] Single comprehensive analysis CTA
- [x] No individual analysis buttons
- [x] Modern, clean design
- [ ] Fast load time (< 2s)

### AI Recommendations
- [ ] Generate within 5 seconds
- [ ] Personalized to patient profile
- [ ] Actionable advice
- [ ] Categorized display
- [ ] Save/bookmark feature

### Profile Management
- [ ] Age auto-calculated from DOB
- [ ] Address fields validated
- [ ] Edit & save functionality
- [ ] Mobile-responsive
- [ ] Emergency contact stored

### Overall
- [ ] All routes working
- [ ] No console errors
- [ ] Responsive design
- [ ] Accessibility (WCAG AA)
- [ ] HIPAA compliance

---

## 📝 Next Steps

1. ✅ Update PatientDashboard.tsx (COMPLETED)
2. Update App.tsx and Navbar.tsx
3. Install google-generativeai
4. Create Gemini service and endpoints
5. Build LifestyleRecommendations component
6. Create ProfilePage with age calculation
7. Update User model and database
8. Test end-to-end flow
9. Deploy changes

---

**Status**: Phase 1 (Dashboard) Complete ✅  
**Next**: Phase 2 - Navigation & Routing Updates  
**ETA**: 4-6 hours for complete implementation

