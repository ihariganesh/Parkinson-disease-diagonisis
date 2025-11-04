import { Link } from "react-router-dom";
import {
  HeartIcon,
  CpuChipIcon,
  ShieldCheckIcon,
  UserGroupIcon,
  ChartBarIcon,
  BeakerIcon,
} from "@heroicons/react/24/outline";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-blue-600">
                ParkinsonCare
              </h1>
            </div>
            <div className="space-x-4">
              <Link
                to="/login"
                className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
              >
                Sign In
              </Link>
              <Link to="/register" className="btn-primary">
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
        <div className="text-center">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
            AI-Powered
            <span className="text-blue-600"> Parkinson's </span>
            Detection
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Comprehensive AI-powered health analysis combining handwriting patterns, 
            voice analysis, and medical reports for 
            accurate early detection and personalized treatment planning.
          </p>
          <div className="space-x-4">
            <Link to="/analysis" className="btn-primary text-lg px-8 py-3">
              Start AI Analysis
            </Link>
            <Link to="/about" className="text-gray-600 hover:text-gray-900 text-lg px-4 py-3 underline">
              Learn More
            </Link>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="bg-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Comprehensive Health Analysis
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Our platform combines multiple data sources to provide accurate,
              early detection of Parkinson's disease with AI-powered insights.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="text-center p-6 rounded-lg bg-gray-50">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <CpuChipIcon className="h-6 w-6 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                AI-Powered Analysis
              </h3>
              <p className="text-gray-600">
                Advanced machine learning models analyze multiple data
                modalities for accurate diagnosis and staging.
              </p>
            </div>

            <div className="text-center p-6 rounded-lg bg-gray-50">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <HeartIcon className="h-6 w-6 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                Multimodal Data
              </h3>
              <p className="text-gray-600">
                Analyze handwriting patterns, voice recordings, 
                and medical reports for comprehensive health assessment and monitoring.
              </p>
            </div>

            <div className="text-center p-6 rounded-lg bg-gray-50">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <UserGroupIcon className="h-6 w-6 text-purple-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                Doctor Collaboration
              </h3>
              <p className="text-gray-600">
                Secure platform for doctors to review AI analysis, verify
                results, and provide clinical oversight.
              </p>
            </div>

            <div className="text-center p-6 rounded-lg bg-gray-50">
              <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <ChartBarIcon className="h-6 w-6 text-yellow-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                Progress Tracking
              </h3>
              <p className="text-gray-600">
                Monitor health changes over time with detailed reports and trend
                analysis for better care management.
              </p>
            </div>

            <div className="text-center p-6 rounded-lg bg-gray-50">
              <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <BeakerIcon className="h-6 w-6 text-red-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                Lifestyle Recommendations
              </h3>
              <p className="text-gray-600">
                Personalized lifestyle suggestions based on your stage and
                condition using AI-powered recommendation system.
              </p>
            </div>

            <div className="text-center p-6 rounded-lg bg-gray-50">
              <div className="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <ShieldCheckIcon className="h-6 w-6 text-indigo-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                HIPAA Compliant
              </h3>
              <p className="text-gray-600">
                Secure, encrypted platform that protects your medical data with
                enterprise-grade security measures.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* How It Works Section */}
      <div className="bg-gray-50 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              How It Works
            </h2>
            <p className="text-lg text-gray-600">
              Simple, secure process to get your health assessment
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4 text-white text-xl font-bold">
                1
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Create Account
              </h3>
              <p className="text-gray-600">
                Sign up as a patient or healthcare provider to access the
                platform
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4 text-white text-xl font-bold">
                2
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Upload Data
              </h3>
              <p className="text-gray-600">
                Securely upload your medical data including handwriting samples, voice recordings, 
                and doctor reports
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4 text-white text-xl font-bold">
                3
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                AI Analysis
              </h3>
              <p className="text-gray-600">
                Our AI models analyze your data and generate comprehensive
                reports
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4 text-white text-xl font-bold">
                4
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Get Results
              </h3>
              <p className="text-gray-600">
                Receive detailed results and personalized care recommendations
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-blue-600 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to Get Started?
          </h2>
          <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
            Join thousands of patients and healthcare providers using our
            comprehensive AI platform for multimodal Parkinson's analysis and personalized care.
          </p>
          <Link
            to="/analysis"
            className="bg-white text-blue-600 hover:bg-gray-100 font-medium py-3 px-8 rounded-lg text-lg transition duration-200 ease-in-out"
          >
            Try Free Analysis
          </Link>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-lg font-semibold mb-4">ParkinsonCare</h3>
              <p className="text-gray-400">
                AI-powered platform for early Parkinson's detection and
                personalized care.
              </p>
            </div>
            <div>
              <h4 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-4">
                Platform
              </h4>
              <ul className="space-y-2 text-gray-400">
                <li>
                  <Link to="/features" className="hover:text-white">
                    Features
                  </Link>
                </li>
                <li>
                  <Link to="/pricing" className="hover:text-white">
                    Pricing
                  </Link>
                </li>
                <li>
                  <Link to="/security" className="hover:text-white">
                    Security
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-4">
                Support
              </h4>
              <ul className="space-y-2 text-gray-400">
                <li>
                  <Link to="/help" className="hover:text-white">
                    Help Center
                  </Link>
                </li>
                <li>
                  <Link to="/contact" className="hover:text-white">
                    Contact Us
                  </Link>
                </li>
                <li>
                  <Link to="/docs" className="hover:text-white">
                    Documentation
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-4">
                Legal
              </h4>
              <ul className="space-y-2 text-gray-400">
                <li>
                  <Link to="/privacy" className="hover:text-white">
                    Privacy Policy
                  </Link>
                </li>
                <li>
                  <Link to="/terms" className="hover:text-white">
                    Terms of Service
                  </Link>
                </li>
                <li>
                  <Link to="/hipaa" className="hover:text-white">
                    HIPAA Compliance
                  </Link>
                </li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 ParkinsonCare. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
