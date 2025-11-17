# Integration Guide: Lifestyle Recommendations in Comprehensive Analysis

## Overview
This guide shows how to integrate the LifestyleRecommendations component into the ComprehensiveAnalysis page to display AI-powered lifestyle advice after diagnosis.

---

## Step 1: Update ComprehensiveAnalysis.tsx

Add the LifestyleRecommendations component at the end of the analysis results.

### Import the component

```tsx
import LifestyleRecommendations from '../components/patient/LifestyleRecommendations';
```

### Add state for recommendations

```tsx
const [recommendations, setRecommendations] = useState<any>(null);
const [loadingRecommendations, setLoadingRecommendations] = useState(false);
```

### Fetch recommendations after successful analysis

Add this function after the analysis completes:

```tsx
const fetchLifestyleRecommendations = async (reportId: number) => {
  try {
    setLoadingRecommendations(true);
    const token = localStorage.getItem('authToken');
    
    const response = await axios.post(
      `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1/lifestyle/recommendations/${reportId}`,
      {},
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    );
    
    if (response.data.success) {
      setRecommendations(response.data.recommendations);
    }
  } catch (error) {
    console.error('Error fetching lifestyle recommendations:', error);
    // Non-blocking error - recommendations are optional
  } finally {
    setLoadingRecommendations(false);
  }
};
```

### Call the function after analysis

Update your analysis submission handler:

```tsx
const handleSubmit = async () => {
  // ... existing analysis code ...
  
  if (analysisResponse.data.success && analysisResponse.data.report_id) {
    // Fetch lifestyle recommendations
    await fetchLifestyleRecommendations(analysisResponse.data.report_id);
  }
};
```

### Display recommendations in JSX

Add this section after the analysis results:

```tsx
{/* Lifestyle Recommendations Section */}
{recommendations && (
  <div className="mt-8">
    <LifestyleRecommendations
      recommendations={recommendations}
      diagnosis={analysisResults.finalDiagnosis}
      confidence={analysisResults.confidence * 100}
      generatedAt={recommendations.metadata?.generated_at}
    />
  </div>
)}

{/* Loading state for recommendations */}
{loadingRecommendations && (
  <div className="mt-8 bg-white rounded-lg shadow-md p-8 border border-gray-200">
    <div className="flex items-center justify-center gap-3">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
      <p className="text-gray-600">Generating personalized lifestyle recommendations...</p>
    </div>
  </div>
)}
```

---

## Step 2: Update Backend to Return Report ID

Ensure your comprehensive analysis endpoint returns the report_id:

```python
@router.post("/comprehensive")
async def comprehensive_analysis(
    # ... parameters ...
):
    # ... analysis logic ...
    
    return {
        "success": True,
        "report_id": diagnosis_report.id,  # Make sure this is included
        "diagnosis": diagnosis_report.final_diagnosis,
        "confidence": diagnosis_report.confidence,
        # ... other fields ...
    }
```

---

## Step 3: Alternative - Quick Recommendations

If you don't have a saved report ID, you can use the quick recommendations endpoint:

```tsx
const fetchQuickRecommendations = async (diagnosis: string, confidence: number, age: number) => {
  try {
    setLoadingRecommendations(true);
    const token = localStorage.getItem('authToken');
    
    const response = await axios.post(
      `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1/lifestyle/recommendations/quick`,
      {
        diagnosis: diagnosis,
        pd_probability: confidence,
        age: age
      },
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    );
    
    if (response.data.success) {
      setRecommendations(response.data.recommendations);
    }
  } catch (error) {
    console.error('Error fetching lifestyle recommendations:', error);
  } finally {
    setLoadingRecommendations(false);
  }
};
```

---

## Step 4: Add Loading Animation

Create a nice loading state while AI generates recommendations:

```tsx
const RecommendationsLoader = () => (
  <div className="mt-8 bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg shadow-md p-12 border border-purple-100">
    <div className="flex flex-col items-center gap-4">
      <div className="relative">
        <div className="animate-spin rounded-full h-16 w-16 border-4 border-purple-200"></div>
        <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-purple-600 absolute top-0 left-0"></div>
      </div>
      <div className="text-center">
        <h3 className="text-xl font-semibold text-gray-900 mb-2">
          Generating Your Personalized Recommendations
        </h3>
        <p className="text-gray-600">
          Our AI is analyzing your results to provide tailored lifestyle guidance...
        </p>
      </div>
      <div className="flex items-center gap-2 mt-4">
        <div className="h-2 w-2 rounded-full bg-purple-600 animate-bounce" style={{ animationDelay: '0ms' }}></div>
        <div className="h-2 w-2 rounded-full bg-purple-600 animate-bounce" style={{ animationDelay: '150ms' }}></div>
        <div className="h-2 w-2 rounded-full bg-purple-600 animate-bounce" style={{ animationDelay: '300ms' }}></div>
      </div>
    </div>
  </div>
);
```

Then use it:

```tsx
{loadingRecommendations && <RecommendationsLoader />}
```

---

## Step 5: Error Handling

Add graceful error handling if recommendations fail:

```tsx
const [recommendationError, setRecommendationError] = useState<string | null>(null);

// In fetch function:
catch (error) {
  console.error('Error fetching lifestyle recommendations:', error);
  setRecommendationError('Unable to generate recommendations at this time. Please try again later.');
}

// In JSX:
{recommendationError && (
  <div className="mt-8 bg-yellow-50 border border-yellow-200 rounded-lg p-6">
    <p className="text-yellow-800">
      <strong>Note:</strong> {recommendationError}
    </p>
  </div>
)}
```

---

## Complete Example

Here's a complete integration example:

```tsx
import React, { useState } from 'react';
import axios from 'axios';
import LifestyleRecommendations from '../components/patient/LifestyleRecommendations';

const ComprehensiveAnalysis: React.FC = () => {
  const [analysisResults, setAnalysisResults] = useState<any>(null);
  const [recommendations, setRecommendations] = useState<any>(null);
  const [loadingRecommendations, setLoadingRecommendations] = useState(false);
  const [recommendationError, setRecommendationError] = useState<string | null>(null);

  const fetchLifestyleRecommendations = async (reportId: number) => {
    try {
      setLoadingRecommendations(true);
      setRecommendationError(null);
      const token = localStorage.getItem('authToken');
      
      const response = await axios.post(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1/lifestyle/recommendations/${reportId}`,
        {},
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      
      if (response.data.success) {
        setRecommendations(response.data.recommendations);
      }
    } catch (error) {
      console.error('Error fetching lifestyle recommendations:', error);
      setRecommendationError('Unable to generate recommendations. Please try again later.');
    } finally {
      setLoadingRecommendations(false);
    }
  };

  const handleAnalysisComplete = async (results: any) => {
    setAnalysisResults(results);
    
    // Fetch recommendations after successful analysis
    if (results.report_id) {
      await fetchLifestyleRecommendations(results.report_id);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Analysis Form and Results */}
        {/* ... your existing analysis UI ... */}

        {/* Lifestyle Recommendations */}
        {loadingRecommendations && (
          <div className="mt-8 bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg shadow-md p-12 border border-purple-100">
            <div className="flex flex-col items-center gap-4">
              <div className="animate-spin rounded-full h-16 w-16 border-4 border-purple-600 border-t-transparent"></div>
              <h3 className="text-xl font-semibold text-gray-900">
                Generating Personalized Recommendations
              </h3>
              <p className="text-gray-600">This may take a few moments...</p>
            </div>
          </div>
        )}

        {recommendationError && (
          <div className="mt-8 bg-yellow-50 border border-yellow-200 rounded-lg p-6">
            <p className="text-yellow-800">{recommendationError}</p>
          </div>
        )}

        {recommendations && (
          <LifestyleRecommendations
            recommendations={recommendations}
            diagnosis={analysisResults.finalDiagnosis}
            confidence={analysisResults.confidence * 100}
            generatedAt={recommendations.metadata?.generated_at}
          />
        )}
      </div>
    </div>
  );
};

export default ComprehensiveAnalysis;
```

---

## Testing

### 1. Manual Testing
1. Log in as a patient
2. Navigate to Comprehensive Analysis
3. Upload files and submit
4. Wait for analysis to complete
5. Verify recommendations appear below results
6. Check all 7 categories are displayed
7. Verify medical disclaimers are present

### 2. API Testing
```bash
# Test recommendations endpoint
curl -X POST http://localhost:8000/api/v1/lifestyle/recommendations/quick \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "diagnosis": "Early Stage Parkinson'\''s Disease",
    "pd_probability": 75.5,
    "age": 65
  }'
```

---

## Troubleshooting

### Recommendations not appearing
- Check browser console for errors
- Verify API key is set in backend `.env`
- Check backend logs for Gemini API errors
- Ensure report_id is being returned from analysis

### Slow generation
- Normal for first request (model initialization)
- Subsequent requests should be faster
- Consider showing loading animation

### API rate limits
- Gemini API has rate limits
- Fallback recommendations will be used automatically
- Check Google Cloud Console for quotas

---

## Performance Tips

1. **Lazy Loading**: Only fetch recommendations when user scrolls to that section
2. **Caching**: Store recommendations in localStorage for quick re-display
3. **Debouncing**: Prevent multiple simultaneous API calls
4. **Optimistic UI**: Show loading state immediately

---

## Next Steps

1. Integrate into ComprehensiveAnalysis.tsx
2. Test with real diagnosis data
3. Monitor Gemini API usage
4. Gather user feedback
5. Refine recommendation prompts based on feedback

---

**Note:** The lifestyle recommendations feature is fully implemented and ready to integrate. The component is standalone and can be used anywhere in the application!
