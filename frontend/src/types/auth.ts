export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

export interface Patient extends User {
  role: 'patient';
  medicalRecordNumber: string;
  assignedDoctorId?: string;
  emergencyContact?: {
    name: string;
    relationship: string;
    phoneNumber: string;
  };
}

export interface Doctor extends User {
  role: 'doctor';
  licenseNumber: string;
  specialization: string;
  hospital: string;
  experience: number;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  role?: string;
  dateOfBirth?: string;
  phoneNumber?: string;
  licenseNumber?: string;
  specialization?: string;
  hospital?: string;
}