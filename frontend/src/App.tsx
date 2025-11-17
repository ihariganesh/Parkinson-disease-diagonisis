import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
  useLocation,
} from "react-router-dom";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import { Navbar } from "./components/common";
import { LoginForm, RegisterForm, ProtectedRoute } from "./components/auth";
import PatientDashboard from "./components/patient/PatientDashboard";
import DataUpload from "./components/patient/DataUpload";
import { DoctorDashboard } from "./components/doctor";
import LandingPage from "./pages/LandingPage";
import About from "./pages/About";
import Unauthorized from "./pages/Unauthorized";
import NotFound from "./pages/NotFound";
import HandwritingPage from "./pages/HandwritingPage";
import AnalysisHub from "./pages/AnalysisHub";
import SpeechAnalysisPage from "./pages/SpeechAnalysisPage";
import DaTAnalysis from "./pages/DaTAnalysis";
import ComprehensiveAnalysis from "./pages/ComprehensiveAnalysis";
import ProfilePage from "./pages/ProfilePage";
import ReportsPage from "./pages/ReportsPage";
// Individual analysis pages kept only for demo routes

// Component to redirect to appropriate dashboard based on user role
function DashboardRedirect() {
  const { state } = useAuth();
  
  if (state.user?.role === 'doctor') {
    return <Navigate to="/doctor/dashboard" replace />;
  } else if (state.user?.role === 'patient') {
    return <Navigate to="/patient/dashboard" replace />;
  } else {
    // Fallback if role is not determined
    return <Navigate to="/patient/dashboard" replace />;
  }
}

function AppRoutes() {
  const { state } = useAuth();
  const location = useLocation();
  const isDemoPage = location.pathname.startsWith('/demo/');

  return (
    <div className="min-h-screen bg-gray-50">
      {(state.isAuthenticated || isDemoPage) && <Navbar />}
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/about" element={<About />} />
        <Route path="/login" element={<LoginForm />} />
        <Route path="/register" element={<RegisterForm />} />
        <Route path="/unauthorized" element={<Unauthorized />} />
        
        {/* Public Demo routes - accessible without authentication */}
        <Route path="/demo/handwriting" element={<HandwritingPage />} />
        <Route path="/demo/speech" element={<SpeechAnalysisPage />} />
        <Route path="/demo/dat" element={<DaTAnalysis />} />
        <Route path="/demo/comprehensive" element={<ComprehensiveAnalysis />} />
        {/* MRI demo route removed during cleanup */}

        {/* Dashboard redirect - automatically redirect to appropriate dashboard based on role */}
        <Route 
          path="/dashboard" 
          element={
            <ProtectedRoute allowedRoles={["patient", "doctor"]}>
              <DashboardRedirect />
            </ProtectedRoute>
          } 
        />

        {/* Additional helpful redirects */}
        <Route path="/upload" element={<Navigate to="/multimodal-upload" replace />} />
        <Route path="/patient" element={<Navigate to="/patient/dashboard" replace />} />
        <Route path="/doctor" element={<Navigate to="/doctor/dashboard" replace />} />

        {/* Protected Patient routes */}
        <Route
          path="/patient/dashboard"
          element={
            <ProtectedRoute allowedRoles={["patient"]}>
              <PatientDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/patient/upload"
          element={
            <ProtectedRoute allowedRoles={["patient"]}>
              <DataUpload />
            </ProtectedRoute>
          }
        />
        <Route
          path="/analysis"
          element={
            <ProtectedRoute allowedRoles={["patient"]}>
              <AnalysisHub />
            </ProtectedRoute>
          }
        />
        
        {/* Profile Page */}
        <Route
          path="/profile"
          element={
            <ProtectedRoute allowedRoles={["patient", "doctor"]}>
              <ProfilePage />
            </ProtectedRoute>
          }
        />
        
        {/* Reports Page */}
        <Route
          path="/reports"
          element={
            <ProtectedRoute allowedRoles={["patient", "doctor"]}>
              <ReportsPage />
            </ProtectedRoute>
          }
        />
        
        {/* Comprehensive Analysis - Main multimodal analysis page */}
        <Route
          path="/comprehensive"
          element={
            <ProtectedRoute allowedRoles={["patient"]}>
              <ComprehensiveAnalysis />
            </ProtectedRoute>
          }
        />
        {/* Multimodal Upload - kept for backward compatibility, redirects to comprehensive */}
        <Route
          path="/multimodal-upload"
          element={<Navigate to="/comprehensive" replace />}
        />
        
        {/* Individual analysis routes removed - use /comprehensive instead */}
        {/* Redirects for backward compatibility */}
        <Route path="/handwriting" element={<Navigate to="/comprehensive" replace />} />
        <Route path="/speech" element={<Navigate to="/comprehensive" replace />} />
        <Route path="/dat" element={<Navigate to="/comprehensive" replace />} />

        {/* Protected Doctor routes */}
        <Route
          path="/doctor/dashboard"
          element={
            <ProtectedRoute allowedRoles={["doctor"]}>
              <DoctorDashboard />
            </ProtectedRoute>
          }
        />

        {/* Catch all route */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </div>
  );
}

// Component to handle authentication state
function AuthCheck() {
  const { state } = useAuth();

  if (state.isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!state.isAuthenticated && (window.location.pathname.startsWith('/patient') || window.location.pathname.startsWith('/doctor'))) {
    return <Navigate to="/login" replace />;
  }

  return <AppRoutes />;
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <AuthCheck />
      </AuthProvider>
    </Router>
  );
}

export default App;