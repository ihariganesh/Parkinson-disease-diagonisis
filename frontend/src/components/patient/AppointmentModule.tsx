import { useState, useEffect } from "react";
import axios from "axios";
import { useAuth } from "../../contexts/AuthContext";
import { LoadingSpinner, Alert } from "../common";
import { CalendarIcon, ClockIcon, VideoCameraIcon, MapPinIcon, CheckCircleIcon, XMarkIcon, IdentificationIcon } from "@heroicons/react/24/outline";

interface Appointment {
    id: string;
    doctor_id: string;
    doctor_name: string;
    doctor_specialization: string;
    appointment_date: string;
    status: "upcoming" | "completed" | "cancelled";
    type: "online" | "offline";
    reason_for_visit?: string;
    meeting_link?: string;
}

interface Doctor {
    id: string;
    name: string;
    specialization: string;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

export default function AppointmentModule() {
    const { state } = useAuth();
    const [appointments, setAppointments] = useState<Appointment[]>([]);
    const [doctors, setDoctors] = useState<Doctor[]>([]);

    const [loading, setLoading] = useState(true);
    const [docsLoading, setDocsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);

    // Create Form State

    const [formData, setFormData] = useState({
        doctor_id: "",
        date: "",
        time: "",
        type: "online",
        reason: "",
    });
    const [creating, setCreating] = useState(false);
    const [filter, setFilter] = useState<"all" | "upcoming" | "completed" | "cancelled">("all");
    const [searchTerm, setSearchTerm] = useState("");

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

    const fetchDoctors = async () => {
        try {
            setDocsLoading(true);
            const res = await axios.get(`${API_BASE_URL}/appointments/doctors`, {
                headers: { Authorization: `Bearer ${state.token}` }
            });
            setDoctors(res.data);
        } catch {
            setError("Failed to load doctors");
        } finally {
            setDocsLoading(false);
        }
    };

    useEffect(() => {
        fetchAppointments();
        fetchDoctors();
    }, [state.token]);

    const handleCreate = async (e: React.FormEvent) => {
        e.preventDefault();
        setCreating(true);
        setError(null);
        try {
            // Combine date and time
            const datetime = new Date(`${formData.date}T${formData.time}:00`).toISOString();
            await axios.post(`${API_BASE_URL}/appointments/`, {
                doctor_id: formData.doctor_id,
                appointment_date: datetime,
                type: formData.type,
                reason_for_visit: formData.reason
            }, {
                headers: { Authorization: `Bearer ${state.token}` }
            });
            setSuccess("Appointment successfully booked!");
            fetchAppointments();
            setFormData({ doctor_id: "", date: "", time: "", type: "online", reason: "" });
            setTimeout(() => setSuccess(null), 3000);
        } catch (err: any) {
            if (err.response?.status === 403) {
                setError("You must be assigned to this doctor to book an appointment.");
            } else {
                setError("Failed to create appointment.");
            }
        } finally {
            setCreating(false);
        }
    };

    const handleStatusChange = async (id: string, newStatus: string) => {
        try {
            await axios.patch(`${API_BASE_URL}/appointments/${id}`, { status: newStatus }, {
                headers: { Authorization: `Bearer ${state.token}` }
            });
            setSuccess(`Appointment ${newStatus}`);
            fetchAppointments();
            setTimeout(() => setSuccess(null), 3000);
        } catch {
            setError(`Failed to set status to ${newStatus}`);
        }
    };

    const stats = {
        upcoming: appointments.filter(a => a.status === "upcoming").length,
        completed: appointments.filter(a => a.status === "completed").length,
        cancelled: appointments.filter(a => a.status === "cancelled").length,
    };

    const filtered = appointments.filter(a => {
        if (filter !== "all" && a.status !== filter) return false;
        if (searchTerm && !a.doctor_name.toLowerCase().includes(searchTerm.toLowerCase())) return false;
        return true;
    });

    if (loading) return <div className="py-20 flex justify-center"><LoadingSpinner /></div>;

    return (
        <div className="space-y-6">
            {/* Alerts */}
            {error && <Alert type="error" message={error} onClose={() => setError(null)} />}
            {success && (
                <div className="bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded-xl flex items-center gap-2">
                    <CheckCircleIcon className="h-5 w-5 text-green-600" />{success}
                </div>
            )}

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex items-center gap-4 hover:shadow-md transition">
                    <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center text-blue-600">
                        <CalendarIcon className="h-6 w-6" />
                    </div>
                    <div><p className="text-sm text-gray-500 font-medium">Upcoming</p><p className="text-2xl font-bold text-gray-900">{stats.upcoming}</p></div>
                </div>
                <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex items-center gap-4 hover:shadow-md transition">
                    <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center text-green-600">
                        <CheckCircleIcon className="h-6 w-6" />
                    </div>
                    <div><p className="text-sm text-gray-500 font-medium">Completed</p><p className="text-2xl font-bold text-gray-900">{stats.completed}</p></div>
                </div>
                <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex items-center gap-4 hover:shadow-md transition">
                    <div className="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center text-red-600">
                        <XMarkIcon className="h-6 w-6" />
                    </div>
                    <div><p className="text-sm text-gray-500 font-medium">Cancelled</p><p className="text-2xl font-bold text-gray-900">{stats.cancelled}</p></div>
                </div>
            </div>

            <div className="flex flex-col md:flex-row gap-6">
                {/* Left Side: Booking Form */}
                <div className="md:w-1/3">
                    <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 sticky top-4">
                        <h3 className="text-lg font-bold text-gray-900 mb-4">Book Appointment</h3>
                        {docsLoading ? <div className="py-4 text-center"><LoadingSpinner size="sm" /></div> :
                            doctors.length === 0 ? (
                                <div className="text-center py-6 text-sm text-gray-500 bg-gray-50 rounded-xl">
                                    You must accept connection requests from doctors or have them assign you before booking.
                                </div>
                            ) : (
                                <form onSubmit={handleCreate} className="space-y-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">Doctor</label>
                                        <select required value={formData.doctor_id} onChange={e => setFormData({ ...formData, doctor_id: e.target.value })}
                                            className="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none">
                                            <option value="" disabled>Select Doctor</option>
                                            {doctors.map(d => <option key={d.id} value={d.id}>{d.name} ({d.specialization})</option>)}
                                        </select>
                                    </div>
                                    <div className="grid grid-cols-2 gap-3">
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-1">Date</label>
                                            <input required type="date" min={new Date().toISOString().split('T')[0]} value={formData.date} onChange={e => setFormData({ ...formData, date: e.target.value })}
                                                className="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none" />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-1">Time</label>
                                            <input required type="time" value={formData.time} onChange={e => setFormData({ ...formData, time: e.target.value })}
                                                className="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none" />
                                        </div>
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">Consultation Type</label>
                                        <div className="flex gap-4">
                                            <label className="flex items-center gap-2 text-sm cursor-pointer">
                                                <input type="radio" value="online" checked={formData.type === "online"} onChange={() => setFormData({ ...formData, type: "online" })} className="text-blue-600 focus:ring-blue-500" />
                                                <VideoCameraIcon className="h-4 w-4 text-gray-500" /> Online
                                            </label>
                                            <label className="flex items-center gap-2 text-sm cursor-pointer">
                                                <input type="radio" value="offline" checked={formData.type === "offline"} onChange={() => setFormData({ ...formData, type: "offline" })} className="text-blue-600 focus:ring-blue-500" />
                                                <MapPinIcon className="h-4 w-4 text-gray-500" /> Offline
                                            </label>
                                        </div>
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">Reason for Visit</label>
                                        <textarea rows={3} placeholder="Briefly describe your symptoms..." value={formData.reason} onChange={e => setFormData({ ...formData, reason: e.target.value })}
                                            className="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none resize-none" />
                                    </div>
                                    <button type="submit" disabled={creating} className="w-full py-2.5 bg-blue-600 text-white rounded-xl text-sm font-medium hover:bg-blue-700 transition flex justify-center items-center">
                                        {creating ? <LoadingSpinner size="sm" /> : "Confirm Booking"}
                                    </button>
                                </form>
                            )}
                    </div>
                </div>

                {/* Right Side: Appointment List */}
                <div className="md:w-2/3 space-y-4">
                    <div className="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 flex flex-col sm:flex-row justify-between gap-3">
                        <div className="flex gap-2">
                            {["all", "upcoming", "completed", "cancelled"].map(f => (
                                <button key={f} onClick={() => setFilter(f as any)} className={`px-4 py-1.5 rounded-full text-xs font-medium capitalize transition ${filter === f ? "bg-gray-800 text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200"}`}>{f}</button>
                            ))}
                        </div>
                        <input type="text" placeholder="Search doctor name..." value={searchTerm} onChange={e => setSearchTerm(e.target.value)}
                            className="px-4 py-1.5 text-sm bg-gray-50 border border-gray-200 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-400" />
                    </div>

                    <div className="space-y-4">
                        {filtered.length === 0 ? (
                            <div className="bg-white p-10 rounded-2xl text-center border border-gray-100 shadow-sm">
                                <CalendarIcon className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                                <p className="text-gray-500 font-medium">No appointments found</p>
                                <p className="text-sm text-gray-400 mt-1">Book an appointment from the left panel.</p>
                            </div>
                        ) : filtered.map(apt => (
                            <div key={apt.id} className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition">
                                <div className="flex justify-between items-start mb-4">
                                    <div className="flex gap-4 items-center">
                                        <div className="w-12 h-12 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center font-bold text-lg">
                                            {apt.doctor_name.replace("Dr. ", "")[0]}
                                        </div>
                                        <div>
                                            <h4 className="font-bold text-gray-900">{apt.doctor_name}</h4>
                                            <p className="text-sm text-gray-500 flex items-center gap-1"><IdentificationIcon className="h-3 w-3" /> {apt.doctor_specialization}</p>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <span className={`px-3 py-1 text-xs font-bold rounded-full uppercase tracking-wider
                      ${apt.status === 'upcoming' ? 'bg-blue-100 text-blue-700' :
                                                apt.status === 'completed' ? 'bg-green-100 text-green-700' :
                                                    'bg-red-100 text-red-700'}`}>
                                            {apt.status}
                                        </span>
                                    </div>
                                </div>

                                <div className="grid grid-cols-2 gap-4 bg-gray-50 rounded-xl p-4 mb-4">
                                    <div>
                                        <p className="text-xs text-gray-400 uppercase tracking-wide font-medium">Date & Time</p>
                                        <p className="text-sm font-semibold text-gray-800 flex items-center gap-1 mt-1">
                                            <ClockIcon className="h-4 w-4 text-gray-400" />
                                            {new Date(apt.appointment_date).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' })}
                                        </p>
                                    </div>
                                    <div>
                                        <p className="text-xs text-gray-400 uppercase tracking-wide font-medium">Consultation Type</p>
                                        <p className="text-sm font-semibold text-gray-800 flex items-center gap-1 mt-1 capitalize">
                                            {apt.type === 'online' ? <VideoCameraIcon className="h-4 w-4 text-blue-500" /> : <MapPinIcon className="h-4 w-4 text-green-500" />}
                                            {apt.type}
                                        </p>
                                    </div>
                                </div>

                                {apt.reason_for_visit && (
                                    <p className="text-sm text-gray-600 mb-4"><span className="font-medium text-gray-700">Reason:</span> {apt.reason_for_visit}</p>
                                )}

                                <div className="flex justify-end gap-3 pt-3 border-t border-gray-100">
                                    {apt.status === 'upcoming' && (
                                        <>
                                            <button onClick={() => handleStatusChange(apt.id, 'cancelled')} className="px-4 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition font-medium">Cancel</button>
                                            {apt.type === 'online' && apt.meeting_link && (
                                                <a href={apt.meeting_link} target="_blank" rel="noreferrer" className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium shadow-sm">Join Meeting</a>
                                            )}
                                        </>
                                    )}
                                    {apt.status === 'completed' && (
                                        <button className="px-4 py-2 text-sm text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition font-medium">View Prescription</button>
                                    )}
                                    {apt.status === 'cancelled' && (
                                        <button onClick={() => handleStatusChange(apt.id, 'upcoming')} className="px-4 py-2 text-sm text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition font-medium flex items-center gap-1"><CalendarIcon className="h-4 w-4" /> Rebook</button>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
