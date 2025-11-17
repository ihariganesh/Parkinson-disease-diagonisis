# Bulk Delete Reports Feature

## Overview
The bulk delete feature allows users to select multiple diagnosis reports and delete them all at once. This provides a more efficient way to manage and clean up multiple reports compared to deleting them individually.

## Implementation Details

### Backend Changes

#### 1. New Endpoint: Bulk Delete Reports
**File:** `backend/app/api/v1/endpoints/medical_data.py`

```python
@router.post("/reports/bulk-delete")
async def bulk_delete_diagnosis_reports(
    report_ids: List[str],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
)
```

**Features:**
- Accepts an array of report IDs to delete
- Validates ownership for each report (users can only delete their own reports)
- Returns detailed statistics about the operation:
  - `deleted_count`: Number of successfully deleted reports
  - `failed_count`: Number of reports that couldn't be deleted
  - `failed_ids`: Array of report IDs that failed to delete
- Implements transactional deletion (all-or-nothing for database commit)
- Comprehensive error handling and logging

**API Response Format:**
```json
{
  "success": true,
  "message": "Deleted 5 report(s)",
  "deleted_count": 5,
  "failed_count": 0,
  "failed_ids": []
}
```

### Frontend Changes

#### 1. Service Method
**File:** `frontend/src/services/medical.ts`

```typescript
async bulkDeleteDiagnosisReports(reportIds: string[]) {
  return await apiClient.post('/medical/reports/bulk-delete', reportIds);
}
```

#### 2. Reports Page - State Management
**File:** `frontend/src/pages/ReportsPage.tsx`

Added new state variables:
```typescript
const [selectedReportIds, setSelectedReportIds] = useState<Set<string>>(new Set());
const [isSelectionMode, setIsSelectionMode] = useState(false);
```

#### 3. Selection Handlers

**Toggle Individual Selection:**
```typescript
const handleToggleSelection = (reportId: string) => {
  const newSelected = new Set(selectedReportIds);
  if (newSelected.has(reportId)) {
    newSelected.delete(reportId);
  } else {
    newSelected.add(reportId);
  }
  setSelectedReportIds(newSelected);
};
```

**Select/Deselect All:**
```typescript
const handleSelectAll = () => {
  if (selectedReportIds.size === filteredReports.length) {
    setSelectedReportIds(new Set());
  } else {
    setSelectedReportIds(new Set(filteredReports.map(r => r.id)));
  }
};
```

**Bulk Delete with Confirmation:**
```typescript
const handleBulkDelete = async () => {
  if (selectedReportIds.size === 0) {
    alert('Please select at least one report to delete');
    return;
  }

  const count = selectedReportIds.size;
  if (!window.confirm(`Are you sure you want to delete ${count} report(s)?`)) {
    return;
  }

  const response = await medicalService.bulkDeleteDiagnosisReports(
    Array.from(selectedReportIds)
  );
  
  if (response.success) {
    setReports(reports.filter(r => !selectedReportIds.has(r.id)));
    setSelectedReportIds(new Set());
    setIsSelectionMode(false);
    alert(`Successfully deleted ${deletedCount} report(s)!`);
  }
};
```

#### 4. UI Components

**Bulk Actions Toolbar:**
Located above the reports list, provides:
- "Select Multiple" button to enter selection mode
- Selection counter showing number of selected reports
- "Select All" / "Deselect All" toggle button
- "Delete Selected (N)" button with count
- "Cancel" button to exit selection mode

**Checkbox Overlays:**
- Positioned absolutely in top-left corner of each report card
- Only visible when in selection mode
- Accessible with proper aria-labels
- Styled with Tailwind CSS for consistency

## User Flow

### Entering Selection Mode
1. User clicks "Select Multiple" button above reports list
2. Checkboxes appear on all report cards
3. Action toolbar transforms to show selection controls

### Selecting Reports
1. Click individual checkboxes to select/deselect reports
2. Or click "Select All" to select all visible reports
3. Selection counter updates in real-time
4. "Delete Selected" button shows count of selected items

### Bulk Deletion
1. Click "Delete Selected (N)" button
2. Confirmation dialog appears: "Are you sure you want to delete N report(s)?"
3. On confirmation:
   - API request sent with array of report IDs
   - Selected reports removed from UI optimistically
   - Success message displayed
   - Selection mode automatically exits
4. On cancellation: Dialog closes, selection remains

### Exiting Selection Mode
1. Click "Cancel" button to exit without deleting
2. Or deletion completes automatically
3. All checkboxes hidden
4. Toolbar returns to normal state

## Security Features

### Backend Security
1. **Authentication Required:** All requests must include valid JWT token
2. **Ownership Verification:** Each report is checked to ensure current user owns it
3. **Individual Validation:** Reports not owned by user are skipped (not deleted)
4. **Failed Operations Tracking:** Returns list of failed IDs for debugging
5. **Transaction Safety:** Uses database transactions for atomicity

### Frontend Security
1. **Confirmation Required:** User must confirm before deletion
2. **Count Display:** Shows exact number of reports being deleted
3. **No Silent Failures:** All errors are displayed to user
4. **Optimistic Updates:** UI updates immediately for better UX

## Error Handling

### Backend Error Scenarios
1. **Invalid Report ID:** Skipped, added to failed_ids
2. **Report Not Found:** Skipped, added to failed_ids
3. **User Doesn't Own Report:** Skipped, added to failed_ids
4. **Database Error:** Transaction rolled back, error returned
5. **Unexpected Exception:** Caught, logged, and returned to user

### Frontend Error Handling
1. **Network Errors:** Displayed via alert
2. **API Errors:** Shows error message from backend
3. **Empty Selection:** Warning displayed before allowing deletion
4. **Partial Failures:** Shows count of successfully deleted reports

## Testing

### Manual Testing Steps

1. **Basic Bulk Delete:**
   ```
   - Navigate to Reports page
   - Click "Select Multiple"
   - Select 3-5 reports
   - Click "Delete Selected"
   - Confirm deletion
   - Verify reports are removed
   ```

2. **Select All:**
   ```
   - Enter selection mode
   - Click "Select All"
   - Verify all checkboxes checked
   - Click "Select All" again
   - Verify all checkboxes unchecked
   ```

3. **Cancel Selection:**
   ```
   - Select several reports
   - Click "Cancel"
   - Verify checkboxes disappear
   - Verify reports remain in list
   ```

4. **Empty Selection:**
   ```
   - Enter selection mode
   - Don't select any reports
   - Click "Delete Selected"
   - Verify warning message appears
   ```

5. **Partial Selection:**
   ```
   - Select 2 out of 10 reports
   - Delete them
   - Verify only 2 are removed
   - Verify 8 remain
   ```

### API Testing

**Test Bulk Delete Endpoint:**
```bash
curl -X POST http://localhost:8000/api/v1/medical/reports/bulk-delete \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '["report-id-1", "report-id-2", "report-id-3"]'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Deleted 3 report(s)",
  "deleted_count": 3,
  "failed_count": 0,
  "failed_ids": []
}
```

## Database Impact

### Queries Executed
For each report ID:
```sql
SELECT * FROM diagnosis_reports 
WHERE id = ? AND patient_id = ?;

DELETE FROM diagnosis_reports 
WHERE id = ?;
```

### Performance Considerations
- Each report deletion is a separate query (not batched)
- Uses indexes on `id` and `patient_id` for fast lookups
- Transaction ensures all-or-nothing for database commit
- For large bulk operations (>50 reports), consider pagination

## Future Enhancements

### Potential Improvements
1. **Soft Delete:** Add `deleted_at` timestamp instead of permanent deletion
2. **Undo Functionality:** Allow users to restore recently deleted reports
3. **Archive Instead of Delete:** Move reports to archive before deletion
4. **Background Processing:** For very large deletions (>100 reports)
5. **Bulk Delete History:** Log all bulk deletion operations for audit
6. **Drag-to-Select:** Allow dragging across report cards to select multiple
7. **Keyboard Shortcuts:** Ctrl+A for select all, Delete key for deletion
8. **Custom Confirmation Modal:** Replace browser confirm() with styled modal
9. **Progress Indicator:** Show progress bar for large bulk operations
10. **Batch API Requests:** Optimize backend to handle single query for multiple deletes

### UI Enhancements
1. **Visual Feedback:** Highlight selected reports with border/background
2. **Animation:** Smooth fade-out animation when reports are deleted
3. **Undo Toast:** Show toast with "Undo" button for 5 seconds after deletion
4. **Selection Persistence:** Remember selection when navigating away and back
5. **Filter Integration:** "Select All" respects current filters

## API Reference

### Bulk Delete Reports
**Endpoint:** `POST /api/v1/medical/reports/bulk-delete`

**Authentication:** Required (JWT Bearer token)

**Request Body:**
```typescript
string[]  // Array of report IDs
```

**Response:**
```typescript
{
  success: boolean;
  message: string;
  deleted_count: number;
  failed_count: number;
  failed_ids: string[];
}
```

**Status Codes:**
- `200 OK`: Deletion attempted (check deleted_count for success)
- `401 Unauthorized`: Missing or invalid authentication token
- `422 Unprocessable Entity`: Invalid request body format
- `500 Internal Server Error`: Server error during deletion

**Error Response:**
```typescript
{
  success: false;
  error: string;
}
```

## Changelog

### Version 1.0.0 (November 13, 2025)
- ✅ Initial implementation of bulk delete feature
- ✅ Backend endpoint with ownership validation
- ✅ Frontend selection mode with checkboxes
- ✅ Select All / Deselect All functionality
- ✅ Confirmation dialog before deletion
- ✅ Real-time selection counter
- ✅ Optimistic UI updates
- ✅ Comprehensive error handling
- ✅ Accessibility features (aria-labels)
- ✅ Responsive design for mobile/desktop

## Notes

- The feature uses `Set<string>` for efficient O(1) lookup when checking selections
- Checkboxes are positioned absolutely to overlay report cards without layout shifts
- The bulk delete button is disabled when no reports are selected
- All state changes are managed through React hooks for proper re-rendering
- The feature is fully compatible with existing single-delete functionality
