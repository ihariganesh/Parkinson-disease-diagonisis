import { useState, useEffect } from "react";
import {
  UserGroupIcon,
  DocumentTextIcon,
  ChartBarIcon,
  ClipboardDocumentListIcon,
  MagnifyingGlassIcon,
  EyeIcon,
} from "@heroicons/react/24/outline";
import { useAuth } from "../../contexts/AuthContext";
import { LoadingSpinner, Alert } from "../common";

interface Patient {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  date_of_birth?: string;
  phone_number?: string;
  created_at: string;
  diagnosis_status?: "healthy" | "early_stage" | "moderate_stage" | "advanced_stage";
  last_analysis?: string;
}

interface DiagnosisReport {
  id: string;
  patient_id: string;
  patient_name: string;
  diagnosis: string;
  confidence_score: number;
  created_at: string;
  status: "pending" | "completed" | "reviewed";
}

const DoctorDashboard = () => {
  const { state } = useAuth();
  const [patients, setPatients] = useState<Patient[]>([]);
  const [reports, setReports] = useState<DiagnosisReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [error] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"patients" | "reports" | "analytics">("patients");
  const [searchTerm, setSearchTerm] = useState("");

  // Mock data for now - replace with actual API calls
  useEffect(() => {
    const mockPatients: Patient[] = [
      {
        id: "1",
        first_name: "John",
        last_name: "Doe",
        email: "john.doe@example.com",
        date_of_birth: "1970-05-15",
        phone_number: "+1-555-0123",
        created_at: "2024-01-15T10:30:00Z",
        diagnosis_status: "early_stage",
        last_analysis: "2024-09-20T14:20:00Z",
      },
      {
        id: "2",
        first_name: "Jane",
        last_name: "Smith",
        email: "jane.smith@example.com",
        date_of_birth: "1965-08-22",
        phone_number: "+1-555-0124",
        created_at: "2024-02-10T09:15:00Z",
        diagnosis_status: "moderate_stage",
        last_analysis: "2024-09-18T11:45:00Z",
      },
      {
        id: "3",
        first_name: "Robert",
        last_name: "Johnson",
        email: "robert.johnson@example.com",
        date_of_birth: "1958-12-03",
        phone_number: "+1-555-0125",
        created_at: "2024-03-05T16:20:00Z",
        diagnosis_status: "healthy",
        last_analysis: "2024-09-19T09:30:00Z",
      },
    ];

    const mockReports: DiagnosisReport[] = [
      {
        id: "1",
        patient_id: "1",
        patient_name: "John Doe",
        diagnosis: "Early stage Parkinson's indicators detected",
        confidence_score: 0.78,
        created_at: "2024-09-20T14:20:00Z",
        status: "pending",
      },
      {
        id: "2",
        patient_id: "2",
        patient_name: "Jane Smith",
        diagnosis: "Moderate stage progression observed",
        confidence_score: 0.85,
        created_at: "2024-09-18T11:45:00Z",
        status: "completed",
      },
      {
        id: "3",
        patient_id: "3",
        patient_name: "Robert Johnson",
        diagnosis: "No significant Parkinson's indicators",
        confidence_score: 0.92,
        created_at: "2024-09-19T09:30:00Z",
        status: "reviewed",
      },
    ];

    // Simulate API loading
    setTimeout(() => {
      setPatients(mockPatients);
      setReports(mockReports);
      setLoading(false);
    }, 1000);
  }, []);

  const filteredPatients = patients.filter(
    (patient) =>
      patient.first_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      patient.last_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      patient.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getStatusColor = (status: string) => {
    switch (status) {
      case "healthy":
        return "text-green-600 bg-green-50";
      case "early_stage":
        return "text-yellow-600 bg-yellow-50";
      case "moderate_stage":
        return "text-orange-600 bg-orange-50";
      case "advanced_stage":
        return "text-red-600 bg-red-50";
      default:
        return "text-gray-600 bg-gray-50";
    }
  };

  const getReportStatusColor = (status: string) => {
    switch (status) {
      case "pending":
        return "text-yellow-600 bg-yellow-50";
      case "completed":
        return "text-blue-600 bg-blue-50";
      case "reviewed":
        return "text-green-600 bg-green-50";
      default:
        return "text-gray-600 bg-gray-50";
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-96">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Doctor Dashboard</h1>
        <p className="text-gray-600 mt-2">
          Welcome back, Dr. {state.user?.first_name} {state.user?.last_name}
        </p>
      </div>

      {error && <Alert type="error" message={error} className="mb-6" />}

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <UserGroupIcon className="h-8 w-8 text-blue-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Patients</p>
              <p className="text-2xl font-bold text-gray-900">{patients.length}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <DocumentTextIcon className="h-8 w-8 text-green-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Reports</p>
              <p className="text-2xl font-bold text-gray-900">{reports.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <ClipboardDocumentListIcon className="h-8 w-8 text-yellow-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Pending Reviews</p>
              <p className="text-2xl font-bold text-gray-900">
                {reports.filter(r => r.status === "pending").length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <ChartBarIcon className="h-8 w-8 text-purple-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">At Risk Patients</p>
              <p className="text-2xl font-bold text-gray-900">
                {patients.filter(p => p.diagnosis_status && p.diagnosis_status !== "healthy").length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8" aria-label="Tabs">
          {[
            { id: "patients", name: "Patients", icon: UserGroupIcon },
            { id: "reports", name: "Reports", icon: DocumentTextIcon },
            { id: "analytics", name: "Analytics", icon: ChartBarIcon },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as typeof activeTab)}
              className={`
                ${activeTab === tab.id
                  ? "border-blue-500 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                }
                whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2
              `}
            >
              <tab.icon className="h-5 w-5" />
              <span>{tab.name}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Content */}
      {activeTab === "patients" && (
        <div>
          {/* Search Bar */}
          <div className="mb-6">
            <div className="relative">
              <MagnifyingGlassIcon className="h-5 w-5 absolute left-3 top-3 text-gray-400" />
              <input
                type="text"
                placeholder="Search patients..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Patients Table */}
          <div className="bg-white shadow-sm rounded-lg overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Patient
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Contact
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Last Analysis
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredPatients.map((patient) => (
                  <tr key={patient.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {patient.first_name} {patient.last_name}
                        </div>
                        <div className="text-sm text-gray-500">
                          Born: {patient.date_of_birth ? new Date(patient.date_of_birth).toLocaleDateString() : "N/A"}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{patient.email}</div>
                      <div className="text-sm text-gray-500">{patient.phone_number || "N/A"}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(patient.diagnosis_status || "")}`}>
                        {patient.diagnosis_status?.replace("_", " ") || "Unknown"}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {patient.last_analysis ? new Date(patient.last_analysis).toLocaleDateString() : "Never"}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button className="text-blue-600 hover:text-blue-900 mr-3">
                        <EyeIcon className="h-4 w-4 inline mr-1" />
                        View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === "reports" && (
        <div>
          <div className="bg-white shadow-sm rounded-lg overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Patient
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Diagnosis
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Confidence
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {reports.map((report) => (
                  <tr key={report.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {report.patient_name}
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900 max-w-xs truncate">
                        {report.diagnosis}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {(report.confidence_score * 100).toFixed(1)}%
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getReportStatusColor(report.status)}`}>
                        {report.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(report.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button className="text-blue-600 hover:text-blue-900">
                        <EyeIcon className="h-4 w-4 inline mr-1" />
                        Review
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === "analytics" && (
        <div className="bg-white p-8 rounded-lg shadow-sm border text-center">
          <ChartBarIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Analytics Dashboard</h3>
          <p className="text-gray-600">
            Advanced analytics and insights coming soon. This will include patient trend analysis,
            prediction accuracy metrics, and diagnostic patterns.
          </p>
        </div>
      )}
    </div>
  );
};

export default DoctorDashboard;