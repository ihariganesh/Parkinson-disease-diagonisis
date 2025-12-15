import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { medicalService } from '../services/medical';
import axios from 'axios';
import type { DiagnosisReport } from '../types';
import {
  SparklesIcon,
  UserIcon,
  MapPinIcon,
  CalendarIcon,
  HeartIcon,
  FireIcon,
  MoonIcon,
  BeakerIcon,
  ExclamationCircleIcon,
  CheckCircleIcon,
  ArrowPathIcon,
} from '@heroicons/react/24/outline';

interface Recommendation {
  category: string;
  recommendations: string[];
}

const RecommendationsPage = () => {
  const { state } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [latestReport, setLatestReport] = useState<DiagnosisReport | null>(null);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [userProfile, setUserProfile] = useState<any>(null);
  const [diseaseCategory, setDiseaseCategory] = useState<string>('');
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch user profile
      const token = localStorage.getItem('auth_token');
      const profileResponse = await axios.get(
        `${import.meta.env.VITE_API_BASE_URL}/auth/me`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setUserProfile(profileResponse.data);

      // Fetch latest diagnosis report
      const reportsResponse = await medicalService.getDiagnosisReports(state.user?.id, 1, 1);
      
      if (reportsResponse.success && reportsResponse.data?.items?.length > 0) {
        const report = reportsResponse.data.items[0];
        setLatestReport(report);
        
        // Determine disease category
        const category = determineDiseaseCategory(report);
        setDiseaseCategory(category);
        
        // Load recommendations
        await loadRecommendations(report.id);
      } else {
        setError('No diagnosis reports found. Please complete an analysis first.');
      }
    } catch (err: any) {
      console.error('Error loading data:', err);
      setError(err.message || 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const determineDiseaseCategory = (report: DiagnosisReport): string => {
    const stage = report.stage || 0;
    const confidence = report.confidence || 0;

    if (stage === 0 && confidence < 0.3) {
      return 'Healthy - Low Risk';
    } else if (stage === 0) {
      return 'Healthy - Monitor Regularly';
    } else if (stage === 1) {
      return 'Early Stage - Mild Symptoms';
    } else if (stage === 2) {
      return 'Moderate Stage - Active Management';
    } else {
      return 'Advanced Stage - Comprehensive Care';
    }
  };

  const loadRecommendations = async (reportId: string) => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await axios.get(
        `${import.meta.env.VITE_API_BASE_URL}/lifestyle/recommendations/${reportId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (response.data.success && response.data.recommendations) {
        // Convert object format to array format
        const recsData = response.data.recommendations;
        const recsArray = Object.entries(recsData)
          .filter(([key]) => key !== 'metadata')
          .map(([category, items]) => ({
            category,
            recommendations: Array.isArray(items) ? items : []
          }));
        
        setRecommendations(recsArray);
      }
    } catch (err: any) {
      console.error('Error loading recommendations:', err);
      // Don't show error, just leave recommendations empty
    }
  };

  const regenerateRecommendations = async () => {
    if (!latestReport) return;
    
    try {
      setIsGenerating(true);
      const token = localStorage.getItem('auth_token');
      const response = await axios.get(
        `${import.meta.env.VITE_API_BASE_URL}/lifestyle/recommendations/${latestReport.id}?force_regenerate=true`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (response.data.success && response.data.recommendations) {
        const recsData = response.data.recommendations;
        const recsArray = Object.entries(recsData)
          .filter(([key]) => key !== 'metadata')
          .map(([category, items]) => ({
            category,
            recommendations: Array.isArray(items) ? items : []
          }));
        
        setRecommendations(recsArray);
      }
    } catch (err: any) {
      console.error('Error regenerating recommendations:', err);
      alert('Failed to regenerate recommendations. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const getCategoryIcon = (category: string) => {
    const normalizedCategory = category.toLowerCase();
    if (normalizedCategory.includes('exercise') || normalizedCategory.includes('physical')) {
      return FireIcon;
    } else if (normalizedCategory.includes('nutrition') || normalizedCategory.includes('diet')) {
      return HeartIcon;
    } else if (normalizedCategory.includes('sleep') || normalizedCategory.includes('rest')) {
      return MoonIcon;
    } else if (normalizedCategory.includes('medication') || normalizedCategory.includes('therapy')) {
      return BeakerIcon;
    }
    return SparklesIcon;
  };

  const getCategoryColor = (category: string) => {
    const normalizedCategory = category.toLowerCase();
    if (normalizedCategory.includes('exercise') || normalizedCategory.includes('physical')) {
      return 'bg-orange-50 border-orange-200 text-orange-700';
    } else if (normalizedCategory.includes('nutrition') || normalizedCategory.includes('diet')) {
      return 'bg-green-50 border-green-200 text-green-700';
    } else if (normalizedCategory.includes('sleep') || normalizedCategory.includes('rest')) {
      return 'bg-purple-50 border-purple-200 text-purple-700';
    } else if (normalizedCategory.includes('medication') || normalizedCategory.includes('therapy')) {
      return 'bg-blue-50 border-blue-200 text-blue-700';
    }
    return 'bg-pink-50 border-pink-200 text-pink-700';
  };

  const calculateAge = (dateOfBirth: string): number => {
    if (!dateOfBirth) return 0;
    const today = new Date();
    const birthDate = new Date(dateOfBirth);
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    return age;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading your personalized recommendations...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md">
          <ExclamationCircleIcon className="h-16 w-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Unable to Load Recommendations</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={loadData}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                <SparklesIcon className="h-8 w-8 text-purple-600" />
                AI-Powered Lifestyle Recommendations
              </h1>
              <p className="mt-2 text-gray-600">
                Personalized health guidance based on your diagnosis and profile
              </p>
            </div>
            <button
              onClick={regenerateRecommendations}
              disabled={isGenerating}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ArrowPathIcon className={`h-5 w-5 ${isGenerating ? 'animate-spin' : ''}`} />
              {isGenerating ? 'Generating...' : 'Regenerate'}
            </button>
          </div>
        </div>

        {/* User Profile & Disease Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* Profile Summary */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center gap-3 mb-4">
              <UserIcon className="h-6 w-6 text-blue-600" />
              <h2 className="text-lg font-semibold text-gray-900">Your Profile</h2>
            </div>
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-sm">
                <CalendarIcon className="h-4 w-4 text-gray-400" />
                <span className="text-gray-600">Age:</span>
                <span className="font-medium text-gray-900">
                  {userProfile?.date_of_birth ? calculateAge(userProfile.date_of_birth) : 'N/A'} years
                </span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <UserIcon className="h-4 w-4 text-gray-400" />
                <span className="text-gray-600">Gender:</span>
                <span className="font-medium text-gray-900 capitalize">
                  {userProfile?.gender || 'Not specified'}
                </span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <MapPinIcon className="h-4 w-4 text-gray-400" />
                <span className="text-gray-600">Location:</span>
                <span className="font-medium text-gray-900">
                  {userProfile?.address_city && userProfile?.address_country
                    ? `${userProfile.address_city}, ${userProfile.address_country}`
                    : 'Not specified'}
                </span>
              </div>
            </div>
          </div>

          {/* Disease Status */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center gap-3 mb-4">
              <BeakerIcon className="h-6 w-6 text-green-600" />
              <h2 className="text-lg font-semibold text-gray-900">Health Status</h2>
            </div>
            <div className="space-y-2">
              <div className="text-sm text-gray-600">Category:</div>
              <div className="text-lg font-bold text-gray-900">{diseaseCategory}</div>
              <div className="mt-3 text-sm text-gray-600">
                Confidence: {latestReport ? `${(latestReport.confidence * 100).toFixed(1)}%` : 'N/A'}
              </div>
            </div>
          </div>

          {/* Latest Report */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center gap-3 mb-4">
              <CheckCircleIcon className="h-6 w-6 text-purple-600" />
              <h2 className="text-lg font-semibold text-gray-900">Latest Report</h2>
            </div>
            <div className="space-y-2">
              <div className="text-sm text-gray-600">
                Analysis Date:
              </div>
              <div className="font-medium text-gray-900">
                {latestReport ? new Date(latestReport.createdAt).toLocaleDateString() : 'N/A'}
              </div>
              <div className="mt-3 text-sm text-gray-600">
                Stage: {latestReport?.stage ?? 'N/A'} / 4
              </div>
            </div>
          </div>
        </div>

        {/* Recommendations Grid */}
        {recommendations.length === 0 ? (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <SparklesIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Generating Your Personalized Recommendations
            </h3>
            <p className="text-gray-600 mb-4">
              Our AI is analyzing your health data, age, gender, and location to create tailored lifestyle guidance.
            </p>
            <button
              onClick={regenerateRecommendations}
              className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
            >
              Generate Recommendations
            </button>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-900">Your Personalized Recommendations</h2>
              <span className="text-sm text-gray-500">
                Based on: {diseaseCategory}
              </span>
            </div>

            <div className="grid grid-cols-1 gap-6">
              {recommendations.map((rec, index) => {
                const Icon = getCategoryIcon(rec.category);
                const colorClass = getCategoryColor(rec.category);

                return (
                  <div
                    key={index}
                    className={`rounded-lg border-2 p-6 ${colorClass}`}
                  >
                    <div className="flex items-center gap-3 mb-4">
                      <Icon className="h-7 w-7" />
                      <h3 className="text-xl font-bold capitalize">
                        {rec.category.replace(/_/g, ' ')}
                      </h3>
                    </div>
                    
                    <ul className="space-y-3">
                      {rec.recommendations.map((item, idx) => (
                        <li key={idx} className="flex items-start gap-3">
                          <CheckCircleIcon className="h-5 w-5 flex-shrink-0 mt-0.5" />
                          <span className="text-sm leading-relaxed">{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Disclaimer */}
        <div className="mt-8 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <ExclamationCircleIcon className="h-6 w-6 text-yellow-600 flex-shrink-0" />
            <div className="text-sm text-yellow-800">
              <p className="font-semibold mb-1">Important Disclaimer</p>
              <p>
                These recommendations are AI-generated suggestions based on your health data and profile. 
                Always consult with your healthcare provider before making significant changes to your lifestyle, 
                diet, or treatment plan. This is not a substitute for professional medical advice.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RecommendationsPage;
