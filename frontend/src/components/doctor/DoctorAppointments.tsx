import { useState, useEffect } from "react";
import axios from "axios";
import { useAuth } from "../../contexts/AuthContext";
import { LoadingSpinner, Alert } from "../common";
import Calendar from "react-calendar";
import 'react-calendar/dist/Calendar.css';
import { CalendarIcon, ClockIcon, CheckCircleIcon } from "@heroicons/react/24/outline";

interface Patient {
    id: string;
    first_name: string;
    last_name: string;
}

interface Appointment {
    id: string;
    patient_name: string;
    appointment_date: string;
    status: "upcoming" | "completed" | "cancelled";
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

const TIME_SLOTS = [
    "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
    "12:00", "13:00", "13:30", "14:00", "14:30", "15:00",
    "15:30", "16:00", "16:30"
];

export default function DoctorAppointments({ patients }: { patients: Patient[] }) {
    const { state } = useAuth();
    const [appointments, setAppointments] = useState<Appointment[]>([]);
    const [loading, setLoading] = useState(true);
    const [bookingLoading, setBookingLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);

    const [selectedDate, setSelectedDate] = useState<Date>(new Date());
    const [selectedTime, setSelectedTime] = useState<string>("");
    const [selectedPatient, setSelectedPatient] = useState<string>("");

    useEffect(() => {
        fetchAppointments();
    }, [state.token]);

    const fetchAppointments = async () => {
        try {
            setLoading(true);
            const res = await axios.get(`${API_BASE_URL}/appointments/`, {
                headers: { Authorization: `Bearer ${state.token}` }
            });
            setAppointments(res.data);
        } catch {
            setError("Failed to load appointments");
        } finally {
            setLoading(false);
        }
    };

    const handleBook = async () => {
        if (!selectedPatient) return setError("Please select a patient.");
        if (!selectedDate) return setError("Please select a date.");
        if (!selectedTime) return setError("Please select a time.");

        setBookingLoading(true);
        setError(null);
        try {
            const dateStr = selectedDate.toLocaleDateString('en-CA'); // YYYY-MM-DD
            await axios.post(`${API_BASE_URL}/appointments/book`, {
                patient_id: selectedPatient,
                selected_date: dateStr,
                selected_time: selectedTime
            }, {
                headers: { Authorization: `Bearer ${state.token}` }
            });
            setSuccess("Appointment successfully booked!");
            setSelectedTime("");
            setSelectedPatient("");
            fetchAppointments();
            setTimeout(() => setSuccess(null), 3000);
        } catch (err: any) {
            setError(err.response?.data?.detail || "Failed to book appointment. Time slot may be taken.");
        } finally {
            setBookingLoading(false);
        }
    };

    const isTimeSlotTaken = (time: string, date: Date) => {
        const dateStr = date.toLocaleDateString('en-CA'); // YYYY-MM-DD
        return appointments.some(apt => {
            if (apt.status === "cancelled") return false;
            const aptDate = new Date(apt.appointment_date);
            const aptDateStr = aptDate.toLocaleDateString('en-CA');
            const aptTimeStr = aptDate.toTimeString().substring(0, 5); // HH:MM
            return aptDateStr === dateStr && aptTimeStr === time;
        });
    };

    const formatAMPM = (timeStr: string) => {
        const [hStr, mStr] = timeStr.split(':');
        let h = parseInt(hStr, 10);
        const ampm = h >= 12 ? 'PM' : 'AM';
        h = h % 12 || 12;
        return `${h}:${mStr} ${ampm}`;
    };

    // Custom styling for calendar via react-calendar injected classes is common
    return (
        <div className="animate-fade-in space-y-6">
            {error && <Alert type="error" message={error} onClose={() => setError(null)} />}
            {success && (
                <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 px-4 py-3 rounded-xl flex items-center gap-2">
                    <CheckCircleIcon className="h-5 w-5 text-emerald-600" />{success}
                </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Left: Calendar & Booking */}
                <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 flex flex-col items-center">
                    <h2 className="text-lg font-semibold text-gray-900 mb-5 flex items-center gap-2 w-full justify-start">
                        <CalendarIcon className="h-5 w-5 text-indigo-600" /> Date & Time
                    </h2>

                    <div className="mb-6 w-full max-w-sm">
                        <Calendar
                            onChange={(val) => { setSelectedDate(val as Date); setSelectedTime(""); }}
                            value={selectedDate}
                            minDate={new Date()}
                            className="rounded-xl border-none shadow-sm p-2 text-sm w-full mx-auto"
                        />
                    </div>

                    <div className="w-full">
                        <h3 className="text-sm font-semibold text-gray-700 mb-3 flex flex-row items-center gap-2"><ClockIcon className="h-5 w-5" /> Available Slots</h3>
                        <div className="grid grid-cols-3 sm:grid-cols-4 gap-2">
                            {TIME_SLOTS.map(t => {
                                const taken = isTimeSlotTaken(t, selectedDate);
                                return (
                                    <button
                                        key={t}
                                        disabled={taken}
                                        onClick={() => setSelectedTime(t)}
                                        className={`py-2 px-1 text-xs font-medium border rounded-lg transition
                                          ${taken ? 'bg-gray-100 text-gray-400 border-gray-200 cursor-not-allowed opacity-60' :
                                                selectedTime === t ? 'bg-indigo-600 text-white border-indigo-600 shadow-sm' :
                                                    'bg-white text-gray-700 border-gray-200 hover:border-indigo-300 hover:bg-indigo-50'}
                                        `}
                                    >
                                        {formatAMPM(t)}
                                    </button>
                                )
                            })}
                        </div>

                        <div className="mt-6 space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Select Patient</label>
                                <select
                                    value={selectedPatient}
                                    onChange={e => setSelectedPatient(e.target.value)}
                                    className="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                                >
                                    <option value="" disabled>Select a patient...</option>
                                    {patients.map(p => (
                                        <option key={p.id} value={p.id}>{p.first_name} {p.last_name}</option>
                                    ))}
                                </select>
                            </div>
                            <button
                                onClick={handleBook}
                                disabled={bookingLoading}
                                className="w-full py-2.5 bg-indigo-600 text-white rounded-xl text-sm font-medium hover:bg-indigo-700 transition flex justify-center items-center shadow-sm"
                            >
                                {bookingLoading ? <LoadingSpinner size="sm" /> : "Book Appointment"}
                            </button>
                        </div>
                    </div>
                </div>

                {/* Right: Appointments List */}
                <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 flex flex-col h-[700px] overflow-hidden">
                    <h2 className="text-lg font-semibold text-gray-900 mb-5 flex items-center gap-2">
                        <CalendarIcon className="h-5 w-5 text-indigo-600" /> Upcoming Appointments
                    </h2>
                    <div className="flex-1 overflow-y-auto pr-2 space-y-4">
                        {loading ? <div className="py-20 flex justify-center"><LoadingSpinner /></div> : appointments.length === 0 ? (
                            <div className="text-center py-10 bg-gray-50 rounded-2xl border border-gray-100">
                                <CalendarIcon className="h-10 w-10 text-gray-300 mx-auto mb-3" />
                                <p className="text-gray-500 font-medium">No appointments scheduled</p>
                                <p className="text-sm text-gray-400 mt-1">Book an appointment from the left panel.</p>
                            </div>
                        ) : appointments.map(apt => (
                            <div key={apt.id} className="bg-white rounded-xl p-4 shadow-sm border border-gray-100 hover:shadow-md transition">
                                <div className="flex justify-between items-start mb-2">
                                    <div className="flex items-center gap-3">
                                        <div className="w-10 h-10 bg-indigo-50 text-indigo-600 rounded-full flex items-center justify-center font-bold">
                                            {apt.patient_name[0]}
                                        </div>
                                        <div>
                                            <h4 className="font-bold text-gray-900 text-sm">{apt.patient_name}</h4>
                                            <p className="text-xs text-gray-500 flex items-center gap-1 mt-0.5">
                                                <ClockIcon className="h-3 w-3" />
                                                {new Date(apt.appointment_date).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' })}
                                            </p>
                                        </div>
                                    </div>
                                    <span className={`px-2.5 py-1 text-[10px] font-bold rounded-full uppercase tracking-wider
                                        ${apt.status === 'upcoming' ? 'bg-blue-100 text-blue-700' :
                                            apt.status === 'completed' ? 'bg-emerald-100 text-emerald-700' :
                                                'bg-red-100 text-red-700'}`}>
                                        {apt.status}
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
            {/* To fix default react-calendar styling which can look messy, inject a small custom style */}
            <style dangerouslySetInnerHTML={{
                __html: `
.react-calendar {
  border: none !important;
  font-family: inherit !important;
  width: 100% !important;
}
.react-calendar__navigation button {
  min-width: 44px;
  background: none;
  font-weight: 600;
  color: #374151;
  border-radius: 8px;
}
.react-calendar__navigation button:hover {
  background-color: #f3f4f6;
}
.react-calendar__month-view__weekdays {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  color: #6b7280;
}
.react-calendar__tile {
  padding: 0.75em 0.5em;
  border-radius: 8px;
  font-weight: 500;
  color: #374151;
}
.react-calendar__tile:enabled:hover,
.react-calendar__tile:enabled:focus {
  background-color: #eef2ff;
  color: #4f46e5;
}
.react-calendar__tile--now {
  background-color: #f3f4f6;
  color: #111827;
}
.react-calendar__tile--active {
  background-color: #4f46e5 !important;
  color: white !important;
  font-weight: 600;
}
.react-calendar__tile:disabled {
  background-color: transparent;
  color: #d1d5db;
}
`}} />
        </div>
    );
}

