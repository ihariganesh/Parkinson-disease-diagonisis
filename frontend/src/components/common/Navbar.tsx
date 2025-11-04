import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  HomeIcon,
  DocumentTextIcon,
  ChartBarIcon,
  Cog6ToothIcon,
  UserCircleIcon,
  ArrowRightOnRectangleIcon,
  Bars3Icon,
  XMarkIcon,
  MicrophoneIcon,
  PencilIcon,
  BeakerIcon,
  SparklesIcon,
} from "@heroicons/react/24/outline";
import { useAuth } from "../../contexts/AuthContext";

const navigation = {
  patient: [
    { name: "Dashboard", href: "/dashboard", icon: HomeIcon },
    { name: "Upload Data", href: "/patient/upload", icon: DocumentTextIcon },
    { name: "Comprehensive", href: "/comprehensive", icon: SparklesIcon },
    { name: "Handwriting", href: "/handwriting", icon: PencilIcon },
    { name: "Speech", href: "/speech", icon: MicrophoneIcon },
    { name: "DaT Scan", href: "/dat", icon: BeakerIcon },
    { name: "Reports", href: "/patient/reports", icon: ChartBarIcon },
    { name: "Lifestyle", href: "/patient/lifestyle", icon: Cog6ToothIcon },
  ],
  doctor: [
    { name: "Dashboard", href: "/dashboard", icon: HomeIcon },
    { name: "Patients", href: "/doctor/patients", icon: UserCircleIcon },
    { name: "Reports", href: "/doctor/reports", icon: ChartBarIcon },
    { name: "Analytics", href: "/doctor/analytics", icon: ChartBarIcon },
  ],
};

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const { state, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  // Don't show navbar on landing page
  const currentPath = window.location.pathname;
  if (currentPath === '/') {
    return null;
  }

  // Check if this is a demo page
  const isDemoPage = currentPath.startsWith('/demo/');
  
  // If not authenticated and not on demo page, don't show navbar
  if (!state.user && !isDemoPage) return null;

  const userNavigation = state.user ? navigation[state.user.role as keyof typeof navigation] || [] : [];

  // Demo page navbar (simplified)
  if (isDemoPage && !state.user) {
    return (
      <nav className="bg-white shadow-lg border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Link
                to="/"
                className="text-xl font-bold text-blue-600"
              >
                ParkinsonCare
              </Link>
              <span className="ml-4 px-3 py-1 bg-blue-100 text-blue-800 text-sm font-medium rounded-full">
                Demo Mode
              </span>
            </div>
            <div className="flex items-center space-x-4">
              <Link
                to="/login"
                className="text-gray-500 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium"
              >
                Sign In
              </Link>
              <Link
                to="/register"
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium"
              >
                Sign Up
              </Link>
            </div>
          </div>
        </div>
      </nav>
    );
  }

  // Authenticated user navbar (original functionality)
  if (!state.user) return null;

  return (
    <nav className="bg-white shadow-lg border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <Link
                to={`/${state.user.role}`}
                className="text-xl font-bold text-blue-600"
              >
                ParkinsonCare
              </Link>
            </div>
            <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
              {userNavigation.map((item) => (
                <Link
                  key={item.name}
                  to={item.href}
                  className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-gray-700 hover:border-gray-300 transition duration-150 ease-in-out"
                >
                  <item.icon className="h-4 w-4 mr-2" />
                  {item.name}
                </Link>
              ))}
            </div>
          </div>

          <div className="hidden sm:ml-6 sm:flex sm:items-center">
            <div className="relative">
              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-700">
                  {state.user.first_name} {state.user.last_name}
                </span>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 capitalize">
                  {state.user.role}
                </span>
                <button
                  onClick={handleLogout}
                  className="text-gray-400 hover:text-gray-600 transition duration-150 ease-in-out"
                  title="Logout"
                >
                  <ArrowRightOnRectangleIcon className="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>

          <div className="flex items-center sm:hidden">
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500"
            >
              {isOpen ? (
                <XMarkIcon className="block h-6 w-6" />
              ) : (
                <Bars3Icon className="block h-6 w-6" />
              )}
            </button>
          </div>
        </div>
      </div>

      {isOpen && (
        <div className="sm:hidden">
          <div className="pt-2 pb-3 space-y-1">
            {userNavigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className="block pl-3 pr-4 py-2 text-base font-medium text-gray-500 hover:text-gray-700 hover:bg-gray-50"
                onClick={() => setIsOpen(false)}
              >
                <div className="flex items-center">
                  <item.icon className="h-4 w-4 mr-2" />
                  {item.name}
                </div>
              </Link>
            ))}
          </div>
          <div className="pt-4 pb-3 border-t border-gray-200">
            <div className="flex items-center px-4">
              <div className="flex-shrink-0">
                <UserCircleIcon className="h-8 w-8 text-gray-400" />
              </div>
              <div className="ml-3">
                <div className="text-base font-medium text-gray-800">
                  {state.user.first_name} {state.user.last_name}
                </div>
                <div className="text-sm font-medium text-gray-500">
                  {state.user.email}
                </div>
              </div>
            </div>
            <div className="mt-3 space-y-1">
              <button
                onClick={handleLogout}
                className="block px-4 py-2 text-base font-medium text-gray-500 hover:text-gray-700 hover:bg-gray-50 w-full text-left"
              >
                Sign out
              </button>
            </div>
          </div>
        </div>
      )}
    </nav>
  );
}
