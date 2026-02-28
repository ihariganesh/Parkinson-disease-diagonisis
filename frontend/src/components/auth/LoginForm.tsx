import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { EyeIcon, EyeSlashIcon, ArrowLeftIcon } from "@heroicons/react/24/outline";
import { useAuth } from "../../contexts/AuthContext";
import { LoadingSpinner } from "../common";
import Aurora from "../common/Aurora";

export default function LoginForm() {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      await login(formData.email, formData.password);
      navigate("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center bg-slate-50 overflow-hidden font-sans">
      {/* Absolute Aurora Background Component */}
      <div className="absolute inset-0 z-0 opacity-80 fixed">
        <Aurora
          colorStops={["#7cff67", "#B19EEF", "#5227FF"]}
          amplitude={1.2}
          blend={0.51}
        />
      </div>

      {/* Glassmorphism Card */}
      <div className="relative z-10 w-full max-w-md mx-4 p-8 sm:p-10 rounded-3xl bg-white/50 backdrop-blur-xl border border-white/40 shadow-2xl shadow-slate-200/50">

        {/* Back Link */}
        <Link
          to="/"
          className="inline-flex items-center text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors mb-8 group"
          aria-label="Back to Home"
        >
          <ArrowLeftIcon className="h-4 w-4 mr-2 group-hover:-translate-x-1 transition-transform" />
          Back to Home
        </Link>

        {/* Header Block */}
        <div className="text-center mb-8">
          <div className="mx-auto h-16 w-16 bg-gradient-to-tr from-indigo-50 to-purple-50 rounded-2xl flex items-center justify-center shadow-lg border border-indigo-100 backdrop-blur-md mb-6 transform rotate-3">
            <svg
              className="h-8 w-8 text-indigo-600 -rotate-3"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
          <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight">
            Welcome Back
          </h2>
          <p className="mt-3 text-sm text-slate-500">
            Sign in to access your dashboard
          </p>
        </div>

        <form className="space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-500/10 border border-red-500/50 text-red-200 rounded-xl p-4 flex items-start text-sm">
              <span className="flex-1">{error}</span>
            </div>
          )}

          <div className="space-y-5">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-slate-700 mb-1.5">
                Email address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                className="w-full px-4 py-3 bg-white/70 border border-slate-200 rounded-xl text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all"
                placeholder="doctor@example.com"
                value={formData.email}
                onChange={handleChange}
                disabled={isLoading}
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-slate-700 mb-1.5">
                Password
              </label>
              <div className="relative">
                <input
                  id="password"
                  name="password"
                  type={showPassword ? "text" : "password"}
                  autoComplete="current-password"
                  required
                  className="w-full px-4 py-3 bg-white/70 border border-slate-200 rounded-xl text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all pr-12"
                  placeholder="••••••••"
                  value={formData.password}
                  onChange={handleChange}
                  disabled={isLoading}
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-4 flex items-center text-slate-400 hover:text-slate-600 transition-colors"
                  onClick={() => setShowPassword(!showPassword)}
                  title={showPassword ? "Hide password" : "Show password"}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? (
                    <EyeSlashIcon className="h-5 w-5" />
                  ) : (
                    <EyeIcon className="h-5 w-5" />
                  )}
                </button>
              </div>
            </div>
          </div>

          <div className="flex items-center justify-end">
            <Link
              to="/forgot-password"
              className="text-sm font-medium text-indigo-600 hover:text-indigo-700 transition-colors"
            >
              Forgot password?
            </Link>
          </div>

          <div>
            <button
              type="submit"
              className="w-full flex justify-center items-center py-3.5 px-4 bg-indigo-600 text-white hover:bg-indigo-700 rounded-xl font-bold text-[15px] shadow-xl hover:shadow-2xl transition duration-200 cursor-pointer active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <LoadingSpinner size="sm" color="currentColor" className="mr-3" />
                  Authenticating...
                </>
              ) : (
                "Sign In"
              )}
            </button>
          </div>

          <p className="text-center text-sm text-slate-600 mt-8">
            New to ParkinsonCare?{" "}
            <Link
              to="/register"
              className="font-bold text-indigo-600 hover:text-indigo-700 transition-colors"
            >
              Create Account
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}
