import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { api } from '../lib/api';
import { Calendar, Clock, User, Phone, Mail, Building, Plus, Star, ShieldCheck, Heart, ArrowLeft, ChevronRight, Check } from 'lucide-react';

interface Facility {
  unique_id: string;
  name: string;
  city: string;
  state: string;
  trust_score?: number;
  _trust_score?: number;
}

interface TimeSlot {
  time: string;
  available: boolean;
  specialty: string;
}

interface Appointment {
  id: string;
  facility_name: string;
  specialty: string;
  date: string;
  time: string;
  status: string;
  confirmation_code: string;
}

export function BookingPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const [facilities, setFacilities] = useState<Facility[]>([]);
  const [selectedFacility, setSelectedFacility] = useState<Facility | null>(null);
  const [availableSlots, setAvailableSlots] = useState<TimeSlot[]>([]);
  const [selectedDate, setSelectedDate] = useState('');
  const [selectedTime, setSelectedTime] = useState('');
  const [patientName, setPatientName] = useState('');
  const [patientPhone, setPatientPhone] = useState('');
  const [patientEmail, setPatientEmail] = useState('');
  const [specialty, setSpecialty] = useState('');
  const [notes, setNotes] = useState('');
  const [myAppointments, setMyAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [view, setView] = useState<'book' | 'appointments'>('book');

  // Load facilities on mount
  useEffect(() => {
    loadFacilities();
    const facilityId = searchParams.get('facility');
    if (facilityId) {
      loadFacility(facilityId);
    }
  }, [searchParams]);

  // Load available slots when date/facility changes
  useEffect(() => {
    if (selectedFacility && selectedDate) {
      loadAvailableSlots();
    }
  }, [selectedFacility, selectedDate]);

  const loadFacilities = async () => {
    try {
      const response = await api.get<{ items: Facility[] }>('/facilities?limit=100&sort_by=trust_score&sort_order=desc');
      setFacilities(response.items || []);
    } catch (err: any) {
      console.error('Failed to load facilities:', err);
    }
  };

  const loadFacility = async (facilityId: string) => {
    try {
      const response = await api.get<Facility>(`/facilities/${facilityId}`);
      setSelectedFacility(response);
    } catch (err: any) {
      console.error('Failed to load facility:', err);
    }
  };

  const loadAvailableSlots = async () => {
    if (!selectedFacility || !selectedDate) return;

    try {
      const response = await api.get<{ slots: TimeSlot[] }>(
        `/booking/slots?facility_id=${selectedFacility.unique_id}&date=${selectedDate}`
      );
      setAvailableSlots(response.slots || []);
    } catch (err: any) {
      console.error('Failed to load slots:', err);
    }
  };

  const handleBookAppointment = async () => {
    if (!selectedFacility || !selectedDate || !selectedTime || !patientName || !patientPhone || !specialty) {
      setError('Please fill in all required fields');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await api.post<{ data: { confirmation_code: string } }>('/booking/appointments', {
        facility_id: selectedFacility.unique_id,
        facility_name: selectedFacility.name,
        patient_name: patientName,
        patient_phone: patientPhone,
        patient_email: patientEmail || undefined,
        specialty,
        appointment_type: 'consultation',
        date: selectedDate,
        time: selectedTime,
        notes: notes || undefined,
      });

      setSuccess(`Appointment booked! Confirmation code: ${response.data.confirmation_code}`);
      
      // Reset form
      setSelectedDate('');
      setSelectedTime('');
      setPatientName('');
      setSpecialty('');
      setNotes('');
      
      // Switch to appointments view
      setView('appointments');
      loadMyAppointments();
    } catch (err: any) {
      setError(err.message || 'Failed to book appointment');
    } finally {
      setLoading(false);
    }
  };

  const loadMyAppointments = async () => {
    if (!patientPhone) return;

    try {
      const response = await api.get<{ data: Appointment[] }>(`/booking/appointments/patient/${patientPhone}`);
      setMyAppointments(response.data || []);
    } catch (err: any) {
      console.error('Failed to load appointments:', err);
    }
  };

  const handleCancelAppointment = async (appointmentId: string) => {
    if (!confirm('Are you sure you want to cancel this appointment?')) {
      return;
    }

    try {
      await api.post(`/booking/appointments/${appointmentId}/cancel`);
      setSuccess('Appointment cancelled successfully');
      loadMyAppointments();
    } catch (err: any) {
      setError(err.message || 'Failed to cancel appointment');
    }
  };

  const getStatusMeta = (status: string) => {
    switch (status) {
      case 'confirmed':
        return {
          label: 'Confirmed',
          color: 'bg-emerald-50 text-emerald-800 dark:bg-emerald-950/20 dark:text-emerald-400 border-emerald-200/40',
        };
      case 'cancelled':
        return {
          label: 'Cancelled',
          color: 'bg-red-50 text-red-800 dark:bg-red-950/20 dark:text-red-400 border-red-200/40',
        };
      case 'completed':
        return {
          label: 'Completed',
          color: 'bg-teal-50 text-teal-800 dark:bg-teal-950/20 dark:text-teal-400 border-teal-200/40',
        };
      default:
        return {
          label: 'Pending Approval',
          color: 'bg-amber-50 text-amber-800 dark:bg-amber-950/20 dark:text-amber-400 border-amber-200/40',
        };
    }
  };

  return (
    <div className="space-y-8 py-2 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight" style={{ color: 'var(--text-primary)' }}>
            Hospital Slot Booking
          </h1>
          <p className="mt-1 text-sm" style={{ color: 'var(--text-secondary)' }}>
            Reserve clinical consultation slots and bed availability.
          </p>
        </div>

        {/* Tab Selector */}
        <div className="flex rounded-xl border overflow-hidden p-1 bg-slate-100 dark:bg-slate-800" style={{ borderColor: 'var(--border-color)' }}>
          <button
            onClick={() => setView('book')}
            className={`flex items-center gap-1.5 px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${
              view === 'book'
                ? 'bg-white shadow-sm dark:bg-slate-700 text-teal-700 dark:text-teal-400'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
            }`}
          >
            <Calendar className="h-3.5 w-3.5" />
            <span>Book Slot</span>
          </button>
          <button
            onClick={() => setView('appointments')}
            className={`flex items-center gap-1.5 px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${
              view === 'appointments'
                ? 'bg-white shadow-sm dark:bg-slate-700 text-teal-700 dark:text-teal-400'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
            }`}
          >
            <Clock className="h-3.5 w-3.5" />
            <span>My Bookings</span>
          </button>
        </div>
      </div>

      {success && (
        <div className="p-4 rounded-xl bg-emerald-50 dark:bg-emerald-950/20 border border-emerald-200 dark:border-emerald-900/30 text-xs font-bold text-emerald-800 dark:text-emerald-400 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Check className="h-4 w-4" />
            <span>{success}</span>
          </div>
          <button onClick={() => setSuccess(null)} className="text-xs hover:underline">Dismiss</button>
        </div>
      )}

      {error && (
        <div className="p-4 rounded-xl bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-900/30 text-xs font-bold text-red-800 dark:text-red-400">
          {error}
        </div>
      )}

      {/* Book Panel */}
      {view === 'book' && (
        <div className="grid gap-6 md:grid-cols-3">
          {/* Form */}
          <div className="md:col-span-2 card p-6 space-y-5">
            <h2 className="text-base font-bold text-slate-800 dark:text-slate-200">Patient Details</h2>
            
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-1">
                <label className="text-xs font-bold text-slate-600 dark:text-slate-400">Full Name *</label>
                <input
                  type="text"
                  placeholder="e.g. John Doe"
                  value={patientName}
                  onChange={(e) => setPatientName(e.target.value)}
                  className="input"
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-bold text-slate-600 dark:text-slate-400">Phone Number *</label>
                <input
                  type="text"
                  placeholder="e.g. 9876543210"
                  value={patientPhone}
                  onChange={(e) => setPatientPhone(e.target.value)}
                  className="input"
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-bold text-slate-600 dark:text-slate-400">Email Address (Optional)</label>
                <input
                  type="email"
                  placeholder="e.g. john@example.com"
                  value={patientEmail}
                  onChange={(e) => setPatientEmail(e.target.value)}
                  className="input"
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-bold text-slate-600 dark:text-slate-400">Select Specialty *</label>
                <select
                  value={specialty}
                  onChange={(e) => setSpecialty(e.target.value)}
                  className="input"
                >
                  <option value="">Choose Department</option>
                  {['General Medicine', 'Maternity / OB-GYN', 'Pediatrics', 'Cardiology', 'Oncology', 'Emergency Surgery'].map(s => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="space-y-1">
              <label className="text-xs font-bold text-slate-600 dark:text-slate-400">Select Hospital *</label>
              <select
                value={selectedFacility?.unique_id || ''}
                onChange={(e) => {
                  const facility = facilities.find(f => f.unique_id === e.target.value);
                  setSelectedFacility(facility || null);
                }}
                className="input text-xs"
              >
                <option value="">Choose Hospital</option>
                {facilities.map(f => (
                  <option key={f.unique_id} value={f.unique_id}>
                    {f.name} ({f.city}, {f.state}) — {(f._trust_score ?? f.trust_score ?? 0).toFixed(0)}% trust
                  </option>
                ))}
              </select>
            </div>

            <div className="grid gap-4 sm:grid-cols-2 pt-2">
              <div className="space-y-1">
                <label className="text-xs font-bold text-slate-600 dark:text-slate-400">Date *</label>
                <input
                  type="date"
                  value={selectedDate}
                  onChange={(e) => setSelectedDate(e.target.value)}
                  className="input"
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-bold text-slate-600 dark:text-slate-400">Select Available Time Slot *</label>
                <select
                  value={selectedTime}
                  disabled={!selectedDate || !selectedFacility}
                  onChange={(e) => setSelectedTime(e.target.value)}
                  className="input disabled:opacity-50"
                >
                  <option value="">Select Time</option>
                  {availableSlots.length > 0 ? (
                    availableSlots.map(slot => (
                      <option key={slot.time} value={slot.time} disabled={!slot.available}>
                        {slot.time} {slot.available ? '(Available)' : '(Booked)'}
                      </option>
                    ))
                  ) : (
                    selectedDate && <option disabled>No slots available today</option>
                  )}
                </select>
              </div>
            </div>

            <div className="space-y-1">
              <label className="text-xs font-bold text-slate-600 dark:text-slate-400">Planner / Patient Notes</label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Include medical history, urgency notes, or travel estimates..."
                rows={3}
                className="input py-2"
              />
            </div>

            <button
              onClick={handleBookAppointment}
              disabled={loading || !selectedFacility || !selectedTime || !patientName || !patientPhone}
              className="btn-primary w-full py-3 text-xs font-bold"
            >
              {loading ? 'Confirming Appointment...' : 'Submit Appointment Request'}
            </button>
          </div>

          {/* Right Information Summary Panel */}
          <div className="card p-6 flex flex-col justify-between">
            <div className="space-y-4">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">Summary</h3>
              {selectedFacility ? (
                <div className="space-y-3">
                  <div>
                    <h4 className="font-extrabold text-sm text-slate-800 dark:text-slate-200">{selectedFacility.name}</h4>
                    <p className="text-[10px] font-semibold text-slate-400">{selectedFacility.city}, {selectedFacility.state}</p>
                  </div>
                  <div className="p-3.5 rounded-xl border bg-slate-50 dark:bg-slate-900/60 text-xs flex justify-between items-center" style={{ borderColor: 'var(--border-color)' }}>
                    <span className="font-bold text-slate-600 dark:text-slate-400">Verification Level</span>
                    <span className="font-extrabold text-teal-700 dark:text-teal-400">{(selectedFacility._trust_score ?? selectedFacility.trust_score ?? 0).toFixed(0)}% Trust</span>
                  </div>
                </div>
              ) : (
                <p className="text-xs italic text-slate-400">Select a hospital on the left to see verified trust ratings.</p>
              )}
            </div>

            <div className="pt-6 border-t text-[10px] text-slate-400 leading-relaxed space-y-1.5" style={{ borderColor: 'var(--border-color)' }}>
              <p className="font-bold text-slate-500 uppercase tracking-wider">⚠️ Please Note:</p>
              <p>Appointments booked here are sent directly to the local facility coordinator desk. Ensure your phone number is correct to receive verification SMS/Calls.</p>
            </div>
          </div>
        </div>
      )}

      {/* Appointments List View */}
      {view === 'appointments' && (
        <div className="card p-6 space-y-5">
          <div className="max-w-md space-y-2">
            <h2 className="text-base font-bold text-slate-800 dark:text-slate-200">Track Patient Bookings</h2>
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="Enter patient phone number..."
                value={patientPhone}
                onChange={(e) => setPhoneAndFetch(e.target.value)}
                className="input py-2 text-xs"
              />
              <button onClick={loadMyAppointments} className="btn-primary py-2 text-xs">Search</button>
            </div>
          </div>

          <div className="space-y-4">
            {myAppointments.length === 0 ? (
              <p className="text-xs italic text-slate-400 py-4 text-center">No current bookings found for this number.</p>
            ) : (
              myAppointments.map(apt => {
                const meta = getStatusMeta(apt.status);
                return (
                  <div key={apt.id} className="p-5 rounded-2xl border bg-slate-50 dark:bg-slate-900 flex flex-col sm:flex-row justify-between sm:items-center gap-4" style={{ borderColor: 'var(--border-color)' }}>
                    <div className="space-y-1.5">
                      <div className="flex items-center gap-2 flex-wrap">
                        <h4 className="font-extrabold text-sm text-slate-800 dark:text-slate-100">{apt.facility_name}</h4>
                        <span className={`px-2 py-0.5 rounded text-[9px] font-bold border ${meta.color}`}>{meta.label}</span>
                      </div>
                      <div className="flex items-center gap-4 text-[10px] font-bold text-slate-400">
                        <span>Dept: {apt.specialty}</span>
                        <span>Date: {apt.date} at {apt.time}</span>
                        <span>Code: {apt.confirmation_code}</span>
                      </div>
                    </div>

                    {apt.status !== 'cancelled' && (
                      <button
                        onClick={() => handleCancelAppointment(apt.id)}
                        className="text-xs font-bold text-red-600 hover:text-red-700 self-start sm:self-center border border-red-200 dark:border-red-900/30 px-3 py-1.5 rounded-lg bg-white dark:bg-slate-800"
                      >
                        Cancel Slot
                      </button>
                    )}
                  </div>
                );
              })
            )}
          </div>
        </div>
      )}
    </div>
  );

  function setPhoneAndFetch(val: string) {
    setPatientPhone(val);
  }
}