# Bulk Delete Feature - Quick Guide

## What's New? 🎉

You can now **select multiple diagnosis reports** and delete them all at once!

## How to Use

### Step 1: Enter Selection Mode
Click the **"Select Multiple"** button at the top right of the Reports page.

```
┌─────────────────────────────────────────────────────┐
│ Recent Diagnosis Reports    [Select Multiple] ←──┐ │
└───────────────────────────────────────────────────│─┘
                                                     │
                                          Click this button
```

### Step 2: Select Reports
Checkboxes will appear on each report card. Click to select the reports you want to delete.

```
┌─────────────────────────────────────────┐
│ ☑ Report Card                          │
│   Diagnosis: Healthy                   │
│   Date: Nov 13, 2025                   │
│   Confidence: 42%                      │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ ☐ Report Card                          │
│   Diagnosis: Early Stage               │
│   Date: Nov 12, 2025                   │
│   Confidence: 68%                      │
└─────────────────────────────────────────┘
```

### Step 3: Use Bulk Actions
The toolbar transforms to show:
- **Selection counter:** "5 selected"
- **Select All / Deselect All** button
- **Delete Selected (5)** button in red
- **Cancel** button

```
┌──────────────────────────────────────────────────────────────────┐
│ 5 selected  [Select All]  [Delete Selected (5)]  [Cancel] │
└──────────────────────────────────────────────────────────────────┘
```

### Step 4: Delete
1. Click **"Delete Selected (5)"**
2. Confirm in the popup: "Are you sure you want to delete 5 report(s)?"
3. Reports are instantly removed!
4. Success message: "Successfully deleted 5 report(s)!"

### Step 5: Exit Selection Mode
- Click **"Cancel"** to exit without deleting
- Or deletion automatically exits selection mode

## Features ✨

### ✅ Select All / Deselect All
Toggle all reports at once with one click.

### ✅ Real-Time Counter
See exactly how many reports you've selected.

### ✅ Confirmation Dialog
Prevents accidental bulk deletions.

### ✅ Instant UI Updates
Selected reports disappear immediately after deletion.

### ✅ Security Built-In
- You can only delete your own reports
- Each report's ownership is verified
- Failed deletions are tracked and reported

### ✅ Individual Delete Still Works
The trash icon on each report card still works for single deletions.

## Keyboard Tips 💡

While in selection mode:
- Click checkboxes to toggle selection
- Use "Select All" for quick selection
- Press "Cancel" to exit without changes

## Visual Changes

### Before Selection Mode:
```
┌────────────────────────────────────────────┐
│ Recent Diagnosis Reports  [Select Multiple]│
├────────────────────────────────────────────┤
│  Report Card 1                             │
│  Report Card 2                             │
│  Report Card 3                             │
└────────────────────────────────────────────┘
```

### During Selection Mode:
```
┌────────────────────────────────────────────────────────┐
│ 2 selected [Select All] [Delete Selected (2)] [Cancel] │
├────────────────────────────────────────────────────────┤
│ ☑ Report Card 1                                        │
│ ☑ Report Card 2                                        │
│ ☐ Report Card 3                                        │
└────────────────────────────────────────────────────────┘
```

## Button States

| Button | State | Description |
|--------|-------|-------------|
| **Select Multiple** | Default | Click to enter selection mode |
| **Select All** | Active | Selects all visible reports |
| **Deselect All** | Active | Clears all selections |
| **Delete Selected (N)** | Active when N > 0 | Deletes N selected reports |
| **Delete Selected (0)** | Disabled | No reports selected |
| **Cancel** | Always active | Exit selection mode |

## Error Handling 🛡️

### If you try to delete without selecting:
```
⚠️ Alert: "Please select at least one report to delete"
```

### If deletion fails:
```
⚠️ Alert: "Failed to delete reports: [error message]"
```

### If some reports fail to delete:
```
✅ Success: "Successfully deleted 4 report(s)!"
(Backend tracks which ones failed)
```

## API Endpoint

**Backend Endpoint:** `POST /api/v1/medical/reports/bulk-delete`

**Request:**
```json
["report-id-1", "report-id-2", "report-id-3"]
```

**Response:**
```json
{
  "success": true,
  "message": "Deleted 3 report(s)",
  "deleted_count": 3,
  "failed_count": 0,
  "failed_ids": []
}
```

## Files Modified

### Backend:
- ✅ `backend/app/api/v1/endpoints/medical_data.py` - Added bulk delete endpoint

### Frontend:
- ✅ `frontend/src/services/medical.ts` - Added service method
- ✅ `frontend/src/pages/ReportsPage.tsx` - Added selection UI and handlers

### Documentation:
- ✅ `BULK_DELETE_FEATURE.md` - Comprehensive documentation
- ✅ `BULK_DELETE_QUICK_GUIDE.md` - This quick guide

## Testing Checklist ✓

- [ ] Click "Select Multiple" button
- [ ] Select 2-3 reports using checkboxes
- [ ] Verify counter shows correct number
- [ ] Click "Select All" - all checkboxes checked
- [ ] Click "Select All" again - all unchecked
- [ ] Select some reports again
- [ ] Click "Delete Selected (N)"
- [ ] Confirm deletion in dialog
- [ ] Verify reports disappear
- [ ] Verify success message appears
- [ ] Check that Total Reports count decreased

## Next Steps

1. **Refresh your Reports page** to see the new "Select Multiple" button
2. **Try selecting 2-3 reports** and deleting them
3. **Test "Select All"** functionality
4. **Verify the reports are permanently deleted**

## Need Help?

If you encounter any issues:
1. Check the browser console for errors
2. Check backend logs: `tail -f backend/backend.log`
3. Verify you're logged in with a valid token
4. Try refreshing the page

---

**Enjoy your new bulk delete feature!** 🚀
