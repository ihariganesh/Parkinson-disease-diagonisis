import { useState, useEffect, useRef } from "react";
import { Link, useNavigate } from "react-router-dom";
import { EyeIcon, EyeSlashIcon, MagnifyingGlassIcon, ArrowLeftIcon } from "@heroicons/react/24/outline";
import { useAuth } from "../../contexts/AuthContext";
import { LoadingSpinner } from "../common";
import axios from "axios";
import Aurora from "../common/Aurora";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

export default function RegisterForm() {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    confirmPassword: "",
    firstName: "",
    lastName: "",
    role: "patient" as "patient" | "doctor",
    dateOfBirth: "",
    phoneNumber: "",
    gender: "",
    // Address fields
    addressStreet: "",
    addressCity: "",
    addressState: "",
    addressZip: "",
    addressCountry: "",
    // Emergency contact fields
    emergencyContactName: "",
    emergencyContactPhone: "",
    emergencyContactRelationship: "",
    // Doctor specific fields
    licenseNumber: "",
    specialization: "",
    hospital: "",
    // Linking to Doctor (Patient only)
    assignedDoctorId: "",
  });

  const [doctors, setDoctors] = useState<{ id: string; name: string }[]>([]);
  const [doctorSearch, setDoctorSearch] = useState("");
  const [showDoctorDropdown, setShowDoctorDropdown] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Fetch available doctors for patient signup
    const fetchDoctors = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/auth/doctors`);
        setDoctors(response.data);
      } catch (err) {
        console.error("Failed to fetch doctors list", err);
      }
    };
    fetchDoctors();
  }, []);

  // Handle clicking outside of doctor dropdown
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDoctorDropdown(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const filteredDoctors = doctors.filter((doc) =>
    doc.name.toLowerCase().includes(doctorSearch.toLowerCase())
  );

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    // Validation
    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (formData.password.length < 8) {
      setError("Password must be at least 8 characters long");
      return;
    }

    setIsLoading(true);

    try {
      const userData = {
        email: formData.email,
        password: formData.password,
        firstName: formData.firstName,
        lastName: formData.lastName,
        role: formData.role,
        dateOfBirth: formData.dateOfBirth || undefined,
        phoneNumber: formData.phoneNumber || undefined,
        gender: formData.gender || undefined,
        // Address fields
        addressStreet: formData.addressStreet || undefined,
        addressCity: formData.addressCity || undefined,
        addressState: formData.addressState || undefined,
        addressZip: formData.addressZip || undefined,
        addressCountry: formData.addressCountry || undefined,
        // Emergency contact fields
        emergencyContactName: formData.emergencyContactName || undefined,
        emergencyContactPhone: formData.emergencyContactPhone || undefined,
        emergencyContactRelationship: formData.emergencyContactRelationship || undefined,
        assigned_doctor_id: formData.role === "patient" ? formData.assignedDoctorId || undefined : undefined,
        ...(formData.role === "doctor" && {
          licenseNumber: formData.licenseNumber,
          specialization: formData.specialization,
          hospital: formData.hospital,
        }),
      };

      await register(userData);
      navigate("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  // Base styling for all inputs to share
  const inputBaseStyle = "w-full px-4 py-3 bg-white/70 border border-slate-200 rounded-xl text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all";
  const labelStyle = "block text-sm font-medium text-slate-700 mb-1.5";

  return (
    <div className="relative min-h-screen flex items-center justify-center bg-slate-50 overflow-hidden font-sans py-12 px-4 sm:px-6 lg:px-8">
      {/* Absolute Aurora Background Component */}
      <div className="absolute inset-0 z-0 opacity-80 fixed">
        <Aurora
          colorStops={["#7cff67", "#B19EEF", "#5227FF"]}
          amplitude={1.2}
          blend={0.51}
        />
      </div>

      {/* Glassmorphism Card */}
      <div className="relative z-10 w-full max-w-2xl p-8 sm:p-10 rounded-3xl bg-white/50 backdrop-blur-xl border border-white/40 shadow-2xl shadow-slate-200/50 overflow-y-auto max-h-[90vh] custom-scrollbar">

        {/* Back Link */}
        <div className="mb-6">
          <Link
            to="/"
            className="inline-flex items-center text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors group"
            aria-label="Back to Home"
          >
            <ArrowLeftIcon className="h-4 w-4 mr-2 group-hover:-translate-x-1 transition-transform" />
            Back to Home
          </Link>
        </div>

        {/* Header Block */}
        <div className="text-center mb-8">
          <div className="mx-auto h-16 w-16 bg-gradient-to-tr from-indigo-50 to-purple-50 rounded-2xl flex items-center justify-center shadow-lg border border-indigo-100 backdrop-blur-md mb-6 transform rotate-3">
            <svg
              className="h-8 w-8 text-indigo-600 -rotate-3"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
            </svg>
          </div>
          <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight">
            Create an Account
          </h2>
          <p className="mt-3 text-sm text-slate-500">
            Join ParkinsonCare diagnostic platform
          </p>
        </div>

        <form className="space-y-8" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-500/10 border border-red-500/50 text-red-200 rounded-xl p-4 flex items-start text-sm">
              <span className="flex-1">{error}</span>
            </div>
          )}

          <div className="space-y-6">

            {/* Account Type Selection */}
            <div className="p-4 bg-white/40 rounded-2xl border border-slate-200">
              <label htmlFor="role" className={labelStyle}>
                I am signing up as a
              </label>
              <select
                id="role"
                name="role"
                className={`${inputBaseStyle} [&>option]:bg-white [&>option]:text-slate-900 appearance-none cursor-pointer`}
                value={formData.role}
                onChange={handleChange}
                disabled={isLoading}
              >
                <option value="patient">Patient</option>
                <option value="doctor">Medical Professional (Doctor)</option>
              </select>
            </div>

            {/* Basic Info Section */}
            <div className="space-y-5">
              <h3 className="text-lg font-semibold text-slate-900 border-b border-slate-200 pb-2">Basic Details</h3>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                <div>
                  <label htmlFor="firstName" className={labelStyle}>First Name</label>
                  <input
                    id="firstName"
                    name="firstName"
                    type="text"
                    required
                    className={inputBaseStyle}
                    placeholder="Jane"
                    value={formData.firstName}
                    onChange={handleChange}
                    disabled={isLoading}
                  />
                </div>
                <div>
                  <label htmlFor="lastName" className={labelStyle}>Last Name</label>
                  <input
                    id="lastName"
                    name="lastName"
                    type="text"
                    required
                    className={inputBaseStyle}
                    placeholder="Doe"
                    value={formData.lastName}
                    onChange={handleChange}
                    disabled={isLoading}
                  />
                </div>
              </div>

              <div>
                <label htmlFor="email" className={labelStyle}>Email Address</label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  className={inputBaseStyle}
                  placeholder="name@example.com"
                  value={formData.email}
                  onChange={handleChange}
                  disabled={isLoading}
                />
              </div>

              {/* Password Fields */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                <div>
                  <label htmlFor="password" className={labelStyle}>Password</label>
                  <div className="relative">
                    <input
                      id="password"
                      name="password"
                      type={showPassword ? "text" : "password"}
                      required
                      className={`${inputBaseStyle} pr-12`}
                      placeholder="••••••••"
                      value={formData.password}
                      onChange={handleChange}
                      disabled={isLoading}
                    />
                    <button
                      type="button"
                      className="absolute inset-y-0 right-0 pr-4 flex items-center text-slate-400 hover:text-slate-600 transition-colors"
                      onClick={() => setShowPassword(!showPassword)}
                      aria-label={showPassword ? "Hide password" : "Show password"}
                    >
                      {showPassword ? <EyeSlashIcon className="h-5 w-5" /> : <EyeIcon className="h-5 w-5" />}
                    </button>
                  </div>
                </div>

                <div>
                  <label htmlFor="confirmPassword" className={labelStyle}>Confirm Password</label>
                  <div className="relative">
                    <input
                      id="confirmPassword"
                      name="confirmPassword"
                      type={showConfirmPassword ? "text" : "password"}
                      required
                      className={`${inputBaseStyle} pr-12`}
                      placeholder="••••••••"
                      value={formData.confirmPassword}
                      onChange={handleChange}
                      disabled={isLoading}
                    />
                    <button
                      type="button"
                      className="absolute inset-y-0 right-0 pr-4 flex items-center text-slate-400 hover:text-slate-600 transition-colors"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      aria-label={showConfirmPassword ? "Hide password" : "Show password"}
                    >
                      {showConfirmPassword ? <EyeSlashIcon className="h-5 w-5" /> : <EyeIcon className="h-5 w-5" />}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Personal Details Section */}
            <div className="space-y-5">
              <h3 className="text-lg font-semibold text-slate-900 border-b border-slate-200 pb-2">Personal Information</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                <div>
                  <label htmlFor="dateOfBirth" className={labelStyle}>Date of birth <span className="text-red-400">*</span></label>
                  <input
                    id="dateOfBirth"
                    name="dateOfBirth"
                    type="date"
                    required
                    className={`${inputBaseStyle} [&::-webkit-calendar-picker-indicator]:invert-[1]`}
                    value={formData.dateOfBirth}
                    onChange={handleChange}
                    disabled={isLoading}
                  />
                </div>
                <div>
                  <label htmlFor="phoneNumber" className={labelStyle}>Phone number <span className="text-red-400">*</span></label>
                  <input
                    id="phoneNumber"
                    name="phoneNumber"
                    type="tel"
                    required
                    className={inputBaseStyle}
                    placeholder="+1 (555) 123-4567"
                    value={formData.phoneNumber}
                    onChange={handleChange}
                    disabled={isLoading}
                  />
                </div>
              </div>

              <div>
                <label htmlFor="gender" className={labelStyle}>Gender</label>
                <select
                  id="gender"
                  name="gender"
                  className={`${inputBaseStyle} [&>option]:bg-white [&>option]:text-slate-900 appearance-none cursor-pointer`}
                  value={formData.gender}
                  onChange={handleChange}
                  disabled={isLoading}
                >
                  <option value="">Select gender</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                  <option value="prefer_not_to_say">Prefer not to say</option>
                </select>
              </div>
            </div>

            {/* Address Section */}
            <div className="space-y-5">
              <h3 className="text-lg font-semibold text-slate-900 border-b border-slate-200 pb-2">Address Information</h3>
              <div>
                <label htmlFor="addressStreet" className={labelStyle}>Street address <span className="text-red-400">*</span></label>
                <input
                  id="addressStreet"
                  name="addressStreet"
                  type="text"
                  required
                  className={inputBaseStyle}
                  placeholder="123 Main Street, Apt 4B"
                  value={formData.addressStreet}
                  onChange={handleChange}
                  disabled={isLoading}
                />
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                <div>
                  <label htmlFor="addressCity" className={labelStyle}>City <span className="text-red-400">*</span></label>
                  <input
                    id="addressCity"
                    name="addressCity"
                    type="text"
                    required
                    className={inputBaseStyle}
                    placeholder="City"
                    value={formData.addressCity}
                    onChange={handleChange}
                    disabled={isLoading}
                  />
                </div>
                <div>
                  <label htmlFor="addressState" className={labelStyle}>State/Province <span className="text-red-400">*</span></label>
                  <input
                    id="addressState"
                    name="addressState"
                    type="text"
                    required
                    className={inputBaseStyle}
                    placeholder="State"
                    value={formData.addressState}
                    onChange={handleChange}
                    disabled={isLoading}
                  />
                </div>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                <div>
                  <label htmlFor="addressZip" className={labelStyle}>ZIP/Postal code <span className="text-red-400">*</span></label>
                  <input
                    id="addressZip"
                    name="addressZip"
                    type="text"
                    required
                    className={inputBaseStyle}
                    placeholder="12345"
                    value={formData.addressZip}
                    onChange={handleChange}
                    disabled={isLoading}
                  />
                </div>
                <div>
                  <label htmlFor="addressCountry" className={labelStyle}>Country <span className="text-red-400">*</span></label>
                  <input
                    id="addressCountry"
                    name="addressCountry"
                    type="text"
                    required
                    className={inputBaseStyle}
                    placeholder="United States"
                    value={formData.addressCountry}
                    onChange={handleChange}
                    disabled={isLoading}
                  />
                </div>
              </div>
            </div>

            <div className="space-y-5">
              <h3 className="text-lg font-semibold text-slate-900 border-b border-slate-200 pb-2">Emergency Contact</h3>
              <div>
                <label htmlFor="emergencyContactName" className={labelStyle}>Contact name <span className="text-red-400">*</span></label>
                <input
                  id="emergencyContactName"
                  name="emergencyContactName"
                  type="text"
                  required
                  className={inputBaseStyle}
                  placeholder="Full name"
                  value={formData.emergencyContactName}
                  onChange={handleChange}
                  disabled={isLoading}
                />
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                <div>
                  <label htmlFor="emergencyContactPhone" className={labelStyle}>Contact phone <span className="text-red-400">*</span></label>
                  <input
                    id="emergencyContactPhone"
                    name="emergencyContactPhone"
                    type="tel"
                    required
                    className={inputBaseStyle}
                    placeholder="+1 (555) 987-6543"
                    value={formData.emergencyContactPhone}
                    onChange={handleChange}
                    disabled={isLoading}
                  />
                </div>
                <div>
                  <label htmlFor="emergencyContactRelationship" className={labelStyle}>Relationship <span className="text-red-400">*</span></label>
                  <input
                    id="emergencyContactRelationship"
                    name="emergencyContactRelationship"
                    type="text"
                    required
                    className={inputBaseStyle}
                    placeholder="Spouse, Parent, etc."
                    value={formData.emergencyContactRelationship}
                    onChange={handleChange}
                    disabled={isLoading}
                  />
                </div>
              </div>
            </div>

            {/* Doctor-specific fields */}
            {formData.role === "doctor" && (
              <div className="space-y-5 p-5 bg-indigo-500/10 rounded-2xl border border-indigo-200">
                <h3 className="text-lg font-semibold text-indigo-800 mb-2">Professional Details</h3>
                <div>
                  <label htmlFor="licenseNumber" className={labelStyle}>Medical License Number</label>
                  <input
                    id="licenseNumber"
                    name="licenseNumber"
                    type="text"
                    required
                    className={inputBaseStyle}
                    placeholder="License #"
                    value={formData.licenseNumber}
                    onChange={handleChange}
                    disabled={isLoading}
                  />
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                  <div>
                    <label htmlFor="specialization" className={labelStyle}>Specialization</label>
                    <input
                      id="specialization"
                      name="specialization"
                      type="text"
                      required
                      className={inputBaseStyle}
                      placeholder="e.g., Neurology"
                      value={formData.specialization}
                      onChange={handleChange}
                      disabled={isLoading}
                    />
                  </div>
                  <div>
                    <label htmlFor="hospital" className={labelStyle}>Hospital/Clinic</label>
                    <input
                      id="hospital"
                      name="hospital"
                      type="text"
                      required
                      className={inputBaseStyle}
                      placeholder="Hospital Name"
                      value={formData.hospital}
                      onChange={handleChange}
                      disabled={isLoading}
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Link to Doctor (For Patients Only) */}
            {formData.role === "patient" && (
              <div className="space-y-5 p-5 bg-purple-500/10 rounded-2xl border border-purple-200" ref={dropdownRef}>
                <h3 className="text-lg font-semibold text-purple-800 mb-2">Link Your Doctor (Optional)</h3>
                <div className="relative">
                  <label htmlFor="doctorSearch" className={labelStyle}>
                    Select your doctor to automatically share reports
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                      <MagnifyingGlassIcon className="h-5 w-5 text-slate-500" />
                    </div>
                    <input
                      id="doctorSearch"
                      type="text"
                      className={`${inputBaseStyle} pl-12 bg-white/70`}
                      placeholder="Type doctor's name..."
                      value={doctorSearch}
                      onChange={(e) => {
                        setDoctorSearch(e.target.value);
                        setFormData({ ...formData, assignedDoctorId: "" }); // Reset ID if typing
                        setShowDoctorDropdown(true);
                      }}
                      onFocus={() => setShowDoctorDropdown(true)}
                    />
                  </div>

                  {/* Dropdown Menu */}
                  {showDoctorDropdown && (
                    <div className="absolute z-20 mt-2 w-full bg-white/90 backdrop-blur border border-slate-200 shadow-2xl rounded-xl py-2 overflow-auto max-h-60 custom-scrollbar">
                      {filteredDoctors.length === 0 ? (
                        <div className="px-4 py-3 text-sm text-slate-500">
                          {doctors.length === 0 ? "Loading doctors..." : "No doctors found."}
                        </div>
                      ) : (
                        filteredDoctors.map((doc) => (
                          <div
                            key={doc.id}
                            className={`cursor-pointer px-4 py-3 text-sm transition-colors ${formData.assignedDoctorId === doc.id
                              ? "bg-indigo-50 text-indigo-700 font-medium"
                              : "text-slate-700 hover:bg-slate-50 hover:text-slate-900"
                              }`}
                            onClick={() => {
                              setFormData({ ...formData, assignedDoctorId: doc.id });
                              setDoctorSearch(doc.name);
                              setShowDoctorDropdown(false);
                            }}
                          >
                            {doc.name}
                          </div>
                        ))
                      )}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          <div className="pt-6">
            <button
              type="submit"
              className="w-full flex justify-center items-center py-4 px-4 bg-indigo-600 text-white hover:bg-indigo-700 rounded-xl font-bold text-[16px] shadow-xl hover:shadow-2xl transition duration-200 cursor-pointer active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <LoadingSpinner size="sm" color="currentColor" className="mr-3" />
                  Creating account...
                </>
              ) : (
                "Create Account"
              )}
            </button>
          </div>

          <p className="text-center text-sm text-slate-600 mt-8">
            Already have an account?{" "}
            <Link
              to="/login"
              className="font-bold text-indigo-600 hover:text-indigo-700 transition-colors"
            >
              Sign In Here
            </Link>
          </p>
        </form>
      </div>

      <style>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(0, 0, 0, 0.1);
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(0, 0, 0, 0.2);
        }
      `}</style>
    </div>
  );
}
