# Bulk Delete Debug Guide

## Issue: "Delete Selected" button not working

### Step 1: Check Browser Console
1. Open your browser's **Developer Tools** (F12)
2. Go to the **Console** tab
3. Click "Delete Selected (12)" button
4. Look for these debug messages:

**Expected Console Output:**
```
[DEBUG] handleBulkDelete called, selected: 12
[DEBUG] Confirming deletion of 12 reports
```

**If you see confirmation dialog:**
```
[DEBUG] User cancelled deletion  (if you click Cancel)
[DEBUG] Sending delete request for report IDs: [array of IDs]  (if you click OK)
[DEBUG] Delete response: {success: true, ...}
```

### Step 2: Check Network Tab
1. Go to **Network** tab in Developer Tools
2. Click "Delete Selected (12)" button
3. Click "OK" in confirmation dialog
4. Look for a POST request to `/medical/reports/bulk-delete`

**Expected Request:**
- **URL:** `http://localhost:5174/api/v1/medical/reports/bulk-delete`
- **Method:** POST
- **Status:** 200 OK
- **Request Body:** Array of 12 report IDs
- **Response:** `{"success": true, "deleted_count": 12, ...}`

### Step 3: Check Backend Logs
```bash
tail -f /home/hari/Downloads/parkinson/parkinson-app/backend/backend.log
```

**Expected Backend Output:**
```
[DEBUG] Bulk deleting 12 reports for user <user-id>
[DEBUG] Successfully deleted 12 reports, 0 failed
```

### Step 4: Common Issues & Solutions

#### Issue A: Confirmation dialog doesn't appear
**Symptom:** Nothing happens when clicking "Delete Selected"
**Cause:** Event handler not wired or JavaScript error
**Check:** Browser console for errors
**Solution:** Refresh page and try again

#### Issue B: Confirmation appears but nothing happens after clicking OK
**Symptom:** Dialog closes but reports don't delete
**Check Console for:**
- `[DEBUG] Sending delete request...` - Should appear
- Network errors (401, 403, 500)
- JavaScript errors

**Common Causes:**
1. **401 Unauthorized:** Token expired
   - **Solution:** Logout and login again
   
2. **Network Error:** Backend not responding
   - **Solution:** Check backend is running: `ps aux | grep uvicorn`
   
3. **CORS Error:** Cross-origin request blocked
   - **Solution:** Backend should have CORS enabled

#### Issue C: Backend receives request but doesn't delete
**Symptom:** Backend logs show request received, but reports remain
**Check Backend Logs for:**
```
[WARNING] Report <id> not found or user doesn't own it
```

**Cause:** User doesn't own the reports (wrong user_id)
**Solution:** Verify you're logged in as the correct user

#### Issue D: Reports deleted but UI doesn't update
**Symptom:** Backend deletes successfully but UI still shows reports
**Check Console for:**
```
[DEBUG] Delete response: {success: true, deleted_count: 12}
```

**Cause:** Frontend state not updating
**Solution:** The code now calls `loadReportsData()` after deletion to reload

### Step 5: Manual Test

Open browser console and run:
```javascript
// Check if selection state exists
console.log('Selected IDs:', window.location); // Just to test console works

// Try calling the delete handler manually (if accessible)
// You'll need to inspect the React component state
```

### Step 6: Alternative - Test Backend Directly

Get your auth token from browser:
```javascript
// In browser console
console.log(localStorage.getItem('auth_token'));
```

Test backend with curl:
```bash
# Replace YOUR_TOKEN with actual token
curl -X POST http://localhost:8000/api/v1/medical/reports/bulk-delete \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '["report-id-1", "report-id-2"]'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Deleted 2 report(s)",
  "deleted_count": 2,
  "failed_count": 0,
  "failed_ids": []
}
```

### Step 7: Force Refresh

If all else fails:
1. **Hard refresh:** Ctrl+Shift+R (or Cmd+Shift+R on Mac)
2. **Clear cache:** Clear browser cache for localhost
3. **Restart frontend:** Kill and restart Vite dev server
4. **Check version:** Verify the updated code is loaded

### Quick Checklist

Before reporting an issue, verify:
- [ ] Browser console shows no JavaScript errors
- [ ] Backend is running (check with `ps aux | grep uvicorn`)
- [ ] You're logged in with valid token
- [ ] Network tab shows POST request being sent
- [ ] Backend logs show request received
- [ ] Frontend has been hard-refreshed (Ctrl+Shift+R)

### What to Report

If still not working, provide:
1. **Browser console output** (all debug messages)
2. **Network tab screenshot** (the bulk-delete request)
3. **Backend log output** (around the time you clicked delete)
4. **Any error messages** from console or alerts

---

## Recent Code Changes

I've added extensive debug logging to help identify the issue:

### Frontend Debug Output:
- `[DEBUG] handleBulkDelete called, selected: N`
- `[DEBUG] Confirming deletion of N reports`
- `[DEBUG] User cancelled deletion` OR
- `[DEBUG] Sending delete request for report IDs: [...]`
- `[DEBUG] Delete response: {...}`
- `[ERROR] Delete failed: ...` (if error)

### Backend Debug Output:
- `[DEBUG] Bulk deleting N reports for user <id>`
- `[WARNING] Report <id> not found or user doesn't own it` (per failed report)
- `[DEBUG] Successfully deleted N reports, M failed`

---

## Try This Now

1. **Open Reports page**
2. **Open browser console** (F12)
3. **Click "Delete Selected (12)"**
4. **Watch console** - paste all output here
5. **Check backend terminal** - look for debug messages

This will help us identify exactly where the issue is!
