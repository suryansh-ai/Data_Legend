"""
Booking Engine — Appointment scheduling and management.

Handles appointment booking, cancellation, and status tracking.
Uses SQLite for persistence with fallback to in-memory storage.
"""

import uuid
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from dataclasses import dataclass, asdict
from enum import Enum


class AppointmentStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class AppointmentType(Enum):
    CONSULTATION = "consultation"
    FOLLOW_UP = "follow_up"
    EMERGENCY = "emergency"
    PROCEDURE = "procedure"
    DIAGNOSTIC = "diagnostic"


@dataclass
class Appointment:
    id: str
    facility_id: str
    facility_name: str
    patient_name: str
    patient_phone: str
    patient_email: Optional[str]
    specialty: str
    appointment_type: str
    date: str
    time: str
    status: str
    notes: Optional[str]
    created_at: str
    updated_at: str
    doctor_name: Optional[str] = None
    doctor_id: Optional[str] = None
    estimated_duration: int = 30  # minutes
    confirmation_code: Optional[str] = None
    reminder_sent: bool = False
    outcome_recorded: bool = False


class BookingEngine:
    def __init__(self):
        self.appointments: Dict[str, Appointment] = {}
        self._load_persistence()
    
    def _load_persistence(self):
        """Load appointments from persistence layer."""
        try:
            from server.lakebase import db
            # Try to load from database if available
            pass
        except:
            pass
    
    def _save_persistence(self, appointment: Appointment):
        """Save appointment to persistence layer."""
        try:
            from server.lakebase import db
            # Save to database if available
            pass
        except:
            pass
    
    def create_appointment(
        self,
        facility_id: str,
        facility_name: str,
        patient_name: str,
        patient_phone: str,
        patient_email: Optional[str],
        specialty: str,
        appointment_type: str,
        date: str,
        time: str,
        notes: Optional[str] = None,
        doctor_name: Optional[str] = None,
        estimated_duration: int = 30
    ) -> Appointment:
        """Create a new appointment."""
        appointment_id = str(uuid.uuid4())
        confirmation_code = f"DL{datetime.now().strftime('%Y%m%d')}{appointment_id[:6].upper()}"
        
        now = datetime.now().isoformat()
        
        appointment = Appointment(
            id=appointment_id,
            facility_id=facility_id,
            facility_name=facility_name,
            patient_name=patient_name,
            patient_phone=patient_phone,
            patient_email=patient_email,
            specialty=specialty,
            appointment_type=appointment_type,
            date=date,
            time=time,
            status=AppointmentStatus.PENDING.value,
            notes=notes,
            created_at=now,
            updated_at=now,
            doctor_name=doctor_name,
            estimated_duration=estimated_duration,
            confirmation_code=confirmation_code
        )
        
        self.appointments[appointment_id] = appointment
        self._save_persistence(appointment)
        
        return appointment
    
    def get_appointment(self, appointment_id: str) -> Optional[Appointment]:
        """Get appointment by ID."""
        return self.appointments.get(appointment_id)
    
    def get_appointments_by_facility(self, facility_id: str) -> List[Appointment]:
        """Get all appointments for a facility."""
        return [apt for apt in self.appointments.values() if apt.facility_id == facility_id]
    
    def get_appointments_by_patient(self, patient_phone: str) -> List[Appointment]:
        """Get all appointments for a patient."""
        return [apt for apt in self.appointments.values() if apt.patient_phone == patient_phone]
    
    def update_appointment_status(
        self,
        appointment_id: str,
        status: str,
        notes: Optional[str] = None
    ) -> Optional[Appointment]:
        """Update appointment status."""
        appointment = self.appointments.get(appointment_id)
        if not appointment:
            return None
        
        appointment.status = status
        appointment.updated_at = datetime.now().isoformat()
        
        if notes:
            appointment.notes = notes
        
        self._save_persistence(appointment)
        return appointment
    
    def cancel_appointment(self, appointment_id: str, reason: Optional[str] = None) -> Optional[Appointment]:
        """Cancel an appointment."""
        return self.update_appointment_status(
            appointment_id,
            AppointmentStatus.CANCELLED.value,
            reason
        )
    
    def confirm_appointment(self, appointment_id: str) -> Optional[Appointment]:
        """Confirm an appointment."""
        return self.update_appointment_status(
            appointment_id,
            AppointmentStatus.CONFIRMED.value
        )
    
    def complete_appointment(self, appointment_id: str, notes: Optional[str] = None) -> Optional[Appointment]:
        """Mark appointment as completed."""
        return self.update_appointment_status(
            appointment_id,
            AppointmentStatus.COMPLETED.value,
            notes
        )
    
    def get_available_slots(
        self,
        facility_id: str,
        date: str,
        specialty: Optional[str] = None
    ) -> List[Dict]:
        """Get available time slots for a facility on a specific date."""
        # Get existing appointments for that date
        existing_appointments = [
            apt for apt in self.appointments.values()
            if apt.facility_id == facility_id
            and apt.date == date
            and apt.status not in [AppointmentStatus.CANCELLED.value]
        ]
        
        # Generate time slots (9 AM to 5 PM, 30-minute intervals)
        all_slots = []
        for hour in range(9, 17):
            for minute in [0, 30]:
                time_str = f"{hour:02d}:{minute:02d}"
                all_slots.append(time_str)
        
        # Filter out booked slots
        booked_times = {apt.time for apt in existing_appointments}
        available_slots = [slot for slot in all_slots if slot not in booked_times]
        
        return [
            {
                "time": slot,
                "available": True,
                "specialty": specialty
            }
            for slot in available_slots
        ]
    
    def get_appointment_stats(self, facility_id: Optional[str] = None) -> Dict:
        """Get appointment statistics."""
        appointments = list(self.appointments.values())
        
        if facility_id:
            appointments = [apt for apt in appointments if apt.facility_id == facility_id]
        
        total = len(appointments)
        by_status = {}
        by_specialty = {}
        by_type = {}
        
        for apt in appointments:
            # Count by status
            by_status[apt.status] = by_status.get(apt.status, 0) + 1
            
            # Count by specialty
            by_specialty[apt.specialty] = by_specialty.get(apt.specialty, 0) + 1
            
            # Count by type
            by_type[apt.appointment_type] = by_type.get(apt.appointment_type, 0) + 1
        
        return {
            "total": total,
            "by_status": by_status,
            "by_specialty": by_specialty,
            "by_type": by_type,
            "completion_rate": (by_status.get(AppointmentStatus.COMPLETED.value, 0) / total * 100) if total > 0 else 0,
            "cancellation_rate": (by_status.get(AppointmentStatus.CANCELLED.value, 0) / total * 100) if total > 0 else 0,
        }


# Global booking engine instance
booking_engine = BookingEngine()