/**
 * Booking Page — Appointment scheduling and management.
 * Patients can book, view, and manage appointments.
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { api } from '../lib/api';

interface Facility {
  unique_id: string;
  name: string;
  city: string;
  state: string;
  trust_score: number;
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
    // Check URL for facility parameter
    const params = new URLSearchParams(window.location.search);
    const facilityId = params.get('facility');
    if (facilityId) {
      loadFacility(facilityId);
    }
  }, []);

  // Load available slots when date/facility changes
  useEffect(() => {
    if (selectedFacility && selectedDate) {
      loadAvailableSlots();
    }
  }, [selectedFacility, selectedDate]);

  const loadFacilities = async () => {
    try {
      const response = await api.get('/facilities?limit=100&sort_by=trust_score&sort_order=desc');
      setFacilities(response.data.items || []);
    } catch (err: any) {
      console.error('Failed to load facilities:', err);
    }
  };

  const loadFacility = async (facilityId: string) => {
    try {
      const response = await api.get(`/facilities/${facilityId}`);
      setSelectedFacility(response.data);
    } catch (err: any) {
      console.error('Failed to load facility:', err);
    }
  };

  const loadAvailableSlots = async () => {
    if (!selectedFacility || !selectedDate) return;

    try {
      const response = await api.get(
        `/booking/slots?facility_id=${selectedFacility.unique_id}&date=${selectedDate}`
      );
      setAvailableSlots(response.data.slots || []);
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
      const response = await api.post('/booking/appointments', {
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
      setPatientPhone('');
      setPatientEmail('');
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
      const response = await api.get(`/booking/appointments/patient/${patientPhone}`);
      setMyAppointments(response.data.data || []);
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

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed': return 'bg-green-100 text-green-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      case 'completed': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Book Appointment
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Schedule appointments with healthcare facilities
        </p>
      </motion.div>

      {/* View Toggle */}
      <div className="flex gap-4 mb-6">
        <button
          onClick={() => setView('book')}
          className={`px-6 py-2 rounded-lg transition-colors ${
            view === 'book'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300'
          }`}
        >
          Book New Appointment
        </button>
        <button
          onClick={() => {
            setView('appointments');
            loadMyAppointments();
          }}
          className={`px-6 py-2 rounded-lg transition-colors ${
            view === 'appointments'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300'
          }`}
        >
          My Appointments ({myAppointments.length})
        </button>
      </div>

      {/* Messages */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded-lg">
          <p className="text-red-600 dark:text-red-400">{error}</p>
        </div>
      )}

      {success && (
        <div className="mb-6 p-4 bg-green-50 dark:bg-green-900 border border-green-200 dark:border-green-700 rounded-lg">
          <p className="text-green-600 dark:text-green-400">{success}</p>
        </div>
      )}

      {/* Book Appointment View */}
      {view === 'book' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6"
        >
          <h2 className="text-xl font-semibold mb-6 text-gray-900 dark:text-white">
            Schedule an Appointment
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Facility Selection */}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Select Facility *
              </label>
              <select
                value={selectedFacility?.unique_id || ''}
                onChange={(e) => {
                  const facility = facilities.find(f => f.unique_id === e.target.value);
                  setSelectedFacility(facility || null);
                }}
                className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              >
                <option value="">Choose a facility</option>
                {facilities.map(facility => (
                  <option key={facility.unique_id} value={facility.unique_id}>
                    {facility.name} - {facility.city}, {facility.state} (Trust: {facility.trust_score.toFixed(1)})
                  </option>
                ))}
              </select>
            </div>

            {/* Date Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Appointment Date *
              </label>
              <input
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                min={new Date().toISOString().split('T')[0]}
                className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
            </div>

            {/* Time Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Appointment Time *
              </label>
              <select
                value={selectedTime}
                onChange={(e) => setSelectedTime(e.target.value)}
                disabled={!selectedDate || availableSlots.length === 0}
                className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white disabled:opacity-50"
              >
                <option value="">Select time</option>
                {availableSlots.map(slot => (
                  <option key={slot.time} value={slot.time} disabled={!slot.available}>
                    {slot.time} {!slot.available ? '(Booked)' : ''}
                  </option>
                ))}
              </select>
            </div>

            {/* Specialty */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Specialty *
              </label>
              <select
                value={specialty}
                onChange={(e) => setSpecialty(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              >
                <option value="">Select specialty</option>
                <option value="general">General</option>
                <option value="cardiology">Cardiology</option>
                <option value="orthopedics">Orthopedics</option>
                <option value="pediatrics">Pediatrics</option>
                <option value="gynecology">Gynecology</option>
                <option value="dermatology">Dermatology</option>
                <option value="ophthalmology">Ophthalmology</option>
                <option value="ent">ENT</option>
                <option value="neurology">Neurology</option>
                <option value="oncology">Oncology</option>
              </select>
            </div>

            {/* Patient Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Patient Name *
              </label>
              <input
                type="text"
                value={patientName}
                onChange={(e) => setPatientName(e.target.value)}
                placeholder="Full name"
                className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
            </div>

            {/* Phone */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Phone Number *
              </label>
              <input
                type="tel"
                value={patientPhone}
                onChange={(e) => setPatientPhone(e.target.value)}
                placeholder="+91 XXXXX XXXXX"
                className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Email (optional)
              </label>
              <input
                type="email"
                value={patientEmail}
                onChange={(e) => setPatientEmail(e.target.value)}
                placeholder="email@example.com"
                className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
            </div>

            {/* Notes */}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Additional Notes (optional)
              </label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={3}
                placeholder="Any specific concerns or requirements..."
                className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
            </div>
          </div>

          <div className="mt-6 flex justify-end gap-4">
            <button
              type="button"
              onClick={() => {
                setSelectedDate('');
                setSelectedTime('');
                setPatientName('');
                setPatientPhone('');
                setPatientEmail('');
                setSpecialty('');
                setNotes('');
              }}
              className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 dark:border-gray-600 dark:hover:bg-gray-700 transition-colors"
            >
              Clear Form
            </button>
            <button
              onClick={handleBookAppointment}
              disabled={loading}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Booking...' : 'Book Appointment'}
            </button>
          </div>
        </motion.div>
      )}

      {/* My Appointments View */}
      {view === 'appointments' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          {myAppointments.length === 0 ? (
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8 text-center">
              <p className="text-gray-500 dark:text-gray-400 mb-4">
                No appointments found. Book your first appointment!
              </p>
              <button
                onClick={() => setView('book')}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Book Appointment
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {myAppointments.map((appointment, idx) => (
                <motion.div
                  key={appointment.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.1 }}
                  className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                        {appointment.facility_name}
                      </h3>
                      <p className="text-gray-600 dark:text-gray-400">
                        {appointment.specialty}
                      </p>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(appointment.status)}`}>
                      {appointment.status.charAt(0).toUpperCase() + appointment.status.slice(1)}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    <div>
                      <p className="text-sm text-gray-500 dark:text-gray-400">Date</p>
                      <p className="font-medium text-gray-900 dark:text-white">{appointment.date}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500 dark:text-gray-400">Time</p>
                      <p className="font-medium text-gray-900 dark:text-white">{appointment.time}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500 dark:text-gray-400">Confirmation Code</p>
                      <p className="font-medium text-gray-900 dark:text-white font-mono">
                        {appointment.confirmation_code}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500 dark:text-gray-400">Appointment ID</p>
                      <p className="font-medium text-gray-900 dark:text-white text-sm">
                        {appointment.id.substring(0, 8)}...
                      </p>
                    </div>
                  </div>

                  {appointment.status !== 'cancelled' && appointment.status !== 'completed' && (
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleCancelAppointment(appointment.id)}
                        className="px-4 py-2 border border-red-300 text-red-600 rounded-lg hover:bg-red-50 dark:border-red-700 dark:text-red-400 dark:hover:bg-red-900 transition-colors"
                      >
                        Cancel Appointment
                      </button>
                    </div>
                  )}
                </motion.div>
              ))}
            </div>
          )}
        </motion.div>
      )}
    </div>
  );
}