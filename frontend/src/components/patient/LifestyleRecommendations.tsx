import React from 'react';
import {
  HeartIcon,
  SparklesIcon,
  BeakerIcon,
  MoonIcon,
  HomeIcon,
  ShieldCheckIcon,
  DevicePhoneMobileIcon
} from '@heroicons/react/24/outline';

interface RecommendationCategory {
  category: string;
  items: string[];
  priority: string;
}

interface LifestyleRecommendationsProps {
  recommendations: {
    exercise: RecommendationCategory;
    nutrition: RecommendationCategory;
    mental_health: RecommendationCategory;
    sleep: RecommendationCategory;
    daily_living: RecommendationCategory;
    medical_management: RecommendationCategory;
    technology_support: RecommendationCategory;
  };
  diagnosis: string;
  confidence: number;
  generatedAt?: string;
}

const categoryIcons: { [key: string]: React.ElementType } = {
  exercise: HeartIcon,
  nutrition: SparklesIcon,
  mental_health: BeakerIcon,
  sleep: MoonIcon,
  daily_living: HomeIcon,
  medical_management: ShieldCheckIcon,
  technology_support: DevicePhoneMobileIcon,
};

const categoryTitles: { [key: string]: string } = {
  exercise: 'Exercise & Physical Activity',
  nutrition: 'Nutrition & Diet',
  mental_health: 'Mental Health & Wellbeing',
  sleep: 'Sleep & Rest',
  daily_living: 'Daily Living Activities',
  medical_management: 'Medical Management',
  technology_support: 'Technology Support',
};

const priorityColors: { [key: string]: string } = {
  high: 'text-red-600 bg-red-50 border-red-200',
  medium: 'text-amber-600 bg-amber-50 border-amber-200',
  low: 'text-green-600 bg-green-50 border-green-200',
};

const LifestyleRecommendations: React.FC<LifestyleRecommendationsProps> = ({
  recommendations,
  diagnosis,
  confidence,
  generatedAt
}) => {
  const categoryOrder = [
    'exercise',
    'nutrition',
    'mental_health',
    'sleep',
    'daily_living',
    'medical_management',
    'technology_support'
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-4">
          <SparklesIcon className="h-8 w-8 text-purple-600" />
          <h2 className="text-3xl font-bold text-gray-900">
            Personalized Lifestyle Recommendations
          </h2>
        </div>
        <div className="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg p-6 border border-purple-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Based on your diagnosis:</p>
              <p className="text-lg font-semibold text-gray-900">{diagnosis}</p>
              <p className="text-sm text-gray-600 mt-1">
                Confidence: <span className="font-medium">{confidence.toFixed(1)}%</span>
              </p>
            </div>
            {generatedAt && (
              <div className="text-right">
                <p className="text-xs text-gray-500">Generated on</p>
                <p className="text-sm font-medium text-gray-700">
                  {new Date(generatedAt).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </p>
              </div>
            )}
          </div>
          <div className="mt-4 flex items-start gap-2 text-sm text-gray-600">
            <ShieldCheckIcon className="h-5 w-5 text-purple-600 flex-shrink-0 mt-0.5" />
            <p>
              These recommendations are AI-generated based on your diagnosis and are meant to complement,
              not replace, professional medical advice. Always consult with your healthcare provider before
              making significant lifestyle changes.
            </p>
          </div>
        </div>
      </div>

      {/* Recommendations Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {categoryOrder.map((categoryKey) => {
          const category = recommendations[categoryKey as keyof typeof recommendations];
          if (!category || !category.items || category.items.length === 0) return null;

          const Icon = categoryIcons[categoryKey];
          const priorityClass = priorityColors[category.priority] || priorityColors.medium;

          return (
            <div
              key={categoryKey}
              className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300 border border-gray-200 overflow-hidden"
            >
              {/* Category Header */}
              <div className="bg-gradient-to-r from-indigo-500 to-purple-600 px-6 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="bg-white/20 backdrop-blur-sm rounded-lg p-2">
                      <Icon className="h-6 w-6 text-white" />
                    </div>
                    <h3 className="text-lg font-semibold text-white">
                      {categoryTitles[categoryKey]}
                    </h3>
                  </div>
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-medium border ${priorityClass}`}
                  >
                    {category.priority.toUpperCase()}
                  </span>
                </div>
              </div>

              {/* Recommendations List */}
              <div className="p-6">
                <ul className="space-y-3">
                  {category.items.map((item, index) => (
                    <li key={index} className="flex items-start gap-3 group">
                      <div className="flex-shrink-0 mt-1">
                        <div className="w-2 h-2 rounded-full bg-gradient-to-r from-indigo-500 to-purple-600 group-hover:scale-125 transition-transform duration-200" />
                      </div>
                      <p className="text-gray-700 leading-relaxed">{item}</p>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          );
        })}
      </div>

      {/* Footer Note */}
      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
        <div className="flex items-start gap-3">
          <ShieldCheckIcon className="h-6 w-6 text-blue-600 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="text-lg font-semibold text-blue-900 mb-2">
              Important Medical Disclaimer
            </h4>
            <p className="text-sm text-blue-800 leading-relaxed">
              These recommendations are generated by AI based on general medical knowledge and your diagnosis.
              They are provided for informational purposes only and should not be considered as a substitute
              for professional medical advice, diagnosis, or treatment. Individual needs may vary significantly
              based on your specific health condition, medications, and other factors. Always seek the advice
              of your physician or other qualified health provider with any questions you may have regarding
              your condition or treatment plan.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LifestyleRecommendations;
