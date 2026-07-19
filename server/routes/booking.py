"""
Booking Routes — Appointment scheduling and management endpoints.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/booking", tags=["booking"])


class AppointmentCreate(BaseModel):
    facility_id: str
    facility_name: str
    patient_name: str
    patient_phone: str
    patient_email: Optional[str] = None
    specialty: str
    appointment_type: str = "consultation"
    date: str
    time: str
    notes: Optional[str] = None
    doctor_name: Optional[str] = None
    estimated_duration: int = 30


class AppointmentUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None


@router.post("/appointments")
async def create_appointment(request: AppointmentCreate):
    """Create a new appointment."""
    from server.booking_engine import booking_engine
    
    # Validate date format
    try:
        appointment_date = datetime.strptime(request.date, "%Y-%m-%d")
        if appointment_date.date() < datetime.now().date():
            raise HTTPException(status_code=400, detail="Cannot book appointments in the past")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    # Create appointment
    appointment = booking_engine.create_appointment(
        facility_id=request.facility_id,
        facility_name=request.facility_name,
        patient_name=request.patient_name,
        patient_phone=request.patient_phone,
        patient_email=request.patient_email,
        specialty=request.specialty,
        appointment_type=request.appointment_type,
        date=request.date,
        time=request.time,
        notes=request.notes,
        doctor_name=request.doctor_name,
        estimated_duration=request.estimated_duration
    )
    
    return {
        "status": "success",
        "data": {
            "appointment_id": appointment.id,
            "confirmation_code": appointment.confirmation_code,
            "status": appointment.status,
            "message": "Appointment created successfully"
        }
    }


@router.get("/appointments/{appointment_id}")
async def get_appointment(appointment_id: str):
    """Get appointment details by ID."""
    from server.booking_engine import booking_engine
    
    appointment = booking_engine.get_appointment(appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    return {
        "status": "success",
        "data": {
            "id": appointment.id,
            "facility_id": appointment.facility_id,
            "facility_name": appointment.facility_name,
            "patient_name": appointment.patient_name,
            "patient_phone": appointment.patient_phone,
            "patient_email": appointment.patient_email,
            "specialty": appointment.specialty,
            "appointment_type": appointment.appointment_type,
            "date": appointment.date,
            "time": appointment.time,
            "status": appointment.status,
            "notes": appointment.notes,
            "doctor_name": appointment.doctor_name,
            "confirmation_code": appointment.confirmation_code,
            "created_at": appointment.created_at,
            "updated_at": appointment.updated_at,
        }
    }


@router.get("/appointments/facility/{facility_id}")
async def get_facility_appointments(facility_id: str):
    """Get all appointments for a facility."""
    from server.booking_engine import booking_engine
    
    appointments = booking_engine.get_appointments_by_facility(facility_id)
    
    return {
        "status": "success",
        "count": len(appointments),
        "data": [
            {
                "id": apt.id,
                "patient_name": apt.patient_name,
                "specialty": apt.specialty,
                "date": apt.date,
                "time": apt.time,
                "status": apt.status,
                "appointment_type": apt.appointment_type,
            }
            for apt in appointments
        ]
    }


@router.get("/appointments/patient/{patient_phone}")
async def get_patient_appointments(patient_phone: str):
    """Get all appointments for a patient."""
    from server.booking_engine import booking_engine
    
    appointments = booking_engine.get_appointments_by_patient(patient_phone)
    
    return {
        "status": "success",
        "count": len(appointments),
        "data": [
            {
                "id": apt.id,
                "facility_name": apt.facility_name,
                "specialty": apt.specialty,
                "date": apt.date,
                "time": apt.time,
                "status": apt.status,
                "confirmation_code": apt.confirmation_code,
            }
            for apt in appointments
        ]
    }


@router.put("/appointments/{appointment_id}/status")
async def update_appointment_status(appointment_id: str, request: AppointmentUpdate):
    """Update appointment status."""
    from server.booking_engine import booking_engine
    
    if request.status:
        appointment = booking_engine.update_appointment_status(
            appointment_id,
            request.status,
            request.notes
        )
    else:
        appointment = booking_engine.get_appointment(appointment_id)
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    return {
        "status": "success",
        "data": {
            "id": appointment.id,
            "status": appointment.status,
            "updated_at": appointment.updated_at,
            "message": "Appointment updated successfully"
        }
    }


@router.post("/appointments/{appointment_id}/cancel")
async def cancel_appointment(appointment_id: str, reason: Optional[str] = None):
    """Cancel an appointment."""
    from server.booking_engine import booking_engine
    
    appointment = booking_engine.cancel_appointment(appointment_id, reason)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    return {
        "status": "success",
        "data": {
            "id": appointment.id,
            "status": appointment.status,
            "message": "Appointment cancelled successfully"
        }
    }


@router.post("/appointments/{appointment_id}/confirm")
async def confirm_appointment(appointment_id: str):
    """Confirm an appointment."""
    from server.booking_engine import booking_engine
    
    appointment = booking_engine.confirm_appointment(appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    return {
        "status": "success",
        "data": {
            "id": appointment.id,
            "status": appointment.status,
            "message": "Appointment confirmed successfully"
        }
    }


@router.get("/slots")
async def get_available_slots(
    facility_id: str,
    date: str,
    specialty: Optional[str] = None
):
    """Get available time slots for a facility."""
    from server.booking_engine import booking_engine
    
    # Validate date format
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    slots = booking_engine.get_available_slots(facility_id, date, specialty)
    
    return {
        "status": "success",
        "facility_id": facility_id,
        "date": date,
        "slots": slots
    }


@router.get("/stats")
async def get_booking_stats(facility_id: Optional[str] = None):
    """Get booking statistics."""
    from server.booking_engine import booking_engine
    
    stats = booking_engine.get_appointment_stats(facility_id)
    
    return {
        "status": "success",
        "data": stats
    }