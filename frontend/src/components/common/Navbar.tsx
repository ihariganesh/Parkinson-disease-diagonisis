import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  HomeIcon,
  ChartBarIcon,
  UserCircleIcon,
  ArrowRightOnRectangleIcon,
  Bars3Icon,
  XMarkIcon,
  SparklesIcon,
  ArrowTrendingUpIcon,
  CpuChipIcon,
  ClipboardDocumentListIcon,
} from "@heroicons/react/24/outline";
import { useAuth } from "../../contexts/AuthContext";
import GradientText from "./GradientText";

import { ChatBubbleLeftRightIcon, UserGroupIcon } from "@heroicons/react/24/outline";

const navigation = {
  patient: [
    { name: "Dashboard", href: "/patient/dashboard", icon: HomeIcon },
    { name: "Analysis", href: "/comprehensive", icon: SparklesIcon },
    { name: "AI Health Assistant", href: "/patient/dashboard#chatbot", icon: CpuChipIcon },
    { name: "My Doctors", href: "/patient/dashboard#messages", icon: ChatBubbleLeftRightIcon },
    { name: "Medical Records", href: "/patient/dashboard#history", icon: ClipboardDocumentListIcon },
    { name: "Progression", href: "/longitudinal", icon: ArrowTrendingUpIcon },
    { name: "Reports", href: "/reports", icon: ChartBarIcon },
    { name: "Recommendations", href: "/recommendations", icon: SparklesIcon },
    { name: "Profile", href: "/profile", icon: UserCircleIcon },
  ],
  doctor: [
    { name: "Dashboard", href: "/doctor/dashboard", icon: HomeIcon },
    { name: "Patient Requests", href: "/doctor/dashboard#requests", icon: UserGroupIcon },
    { name: "Pending Reports", href: "/doctor/dashboard#pending", icon: ChartBarIcon },
    { name: "My Patients", href: "/doctor/dashboard#patients", icon: UserCircleIcon },
    { name: "Analytics", href: "/doctor/dashboard#analytics", icon: ChartBarIcon },
    { name: "Messages", href: "/doctor/dashboard#messages", icon: ChatBubbleLeftRightIcon },
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
                className="flex items-center"
              >
                <GradientText
                  colors={["#5227FF", "#33d17a", "#1a5fb4"]}
                  animationSpeed={2.5}
                  showBorder={false}
                  className="text-xl font-bold"
                >
                  ParkinsonCare
                </GradientText>
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
    <nav className="bg-white shadow-lg border-b border-slate-200 sticky top-0 z-50">
      <div className="max-w-[1920px] mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <div className="flex flex-1 items-center overflow-hidden">
            <div className="flex-shrink-0 flex items-center pr-2 lg:pr-6">
              <Link
                to={`/${state.user.role}`}
                className="flex items-center"
              >
                <GradientText
                  colors={["#5227FF", "#33d17a", "#1a5fb4"]}
                  animationSpeed={2.5}
                  showBorder={false}
                  className="text-xl font-bold whitespace-nowrap shrink-0"
                >
                  ParkinsonCare
                </GradientText>
              </Link>
            </div>

            {/* Scrollable container for links on medium/large screens */}
            <div className="hidden lg:flex lg:items-center lg:space-x-1 xl:space-x-3 overflow-x-auto no-scrollbar py-1">
              {userNavigation.map((item) => (
                <Link
                  key={item.name}
                  to={item.href}
                  className="inline-flex items-center px-2 py-1.5 rounded-lg text-sm font-semibold text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 transition duration-200 whitespace-nowrap shrink-0"
                >
                  <item.icon className="h-[18px] w-[18px] mr-1.5 shrink-0" />
                  {item.name}
                </Link>
              ))}
            </div>
          </div>

          <div className="hidden lg:ml-6 lg:flex lg:items-center shrink-0 pl-4 lg:border-l lg:border-slate-200 ml-auto">
            <div className="relative">
              <div className="flex items-center space-x-3">
                <span className="text-sm font-bold text-slate-700 whitespace-nowrap truncate max-w-[150px]">
                  {state.user.first_name} {state.user.last_name}
                </span>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold shadow-sm bg-indigo-100 text-indigo-700 capitalize shrink-0">
                  {state.user.role}
                </span>
                <button
                  onClick={handleLogout}
                  className="text-slate-400 hover:text-rose-600 hover:bg-rose-50 p-2 rounded-full transition duration-200 shrink-0"
                  title="Logout"
                >
                  <ArrowRightOnRectangleIcon className="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>

          <div className="flex items-center lg:hidden shrink-0 ml-auto">
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
        <div className="lg:hidden">
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
