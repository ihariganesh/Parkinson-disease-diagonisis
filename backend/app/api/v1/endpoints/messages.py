from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
from datetime import datetime
import uuid

from app.db.database import get_db
from app.db.models import User, UserRole, DoctorPatientMessage
from app.core.security import get_current_user

router = APIRouter()

@router.get("/contacts")
async def get_contacts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available contacts for messaging.
    Doctors see all patients. Patients see all doctors."""
    if current_user.role == UserRole.DOCTOR:
        # Doctor sees all patients
        users = db.query(User).filter(
            User.role == UserRole.PATIENT,
            User.is_active == True,
            User.id != current_user.id
        ).all()
    else:
        # Patient sees all doctors
        users = db.query(User).filter(
            User.role == UserRole.DOCTOR,
            User.is_active == True,
            User.id != current_user.id
        ).all()
    
    return [
        {
            "id": u.id,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "role": u.role.value,
            "email": u.email,
            "patient_id": getattr(u, 'patient_id', None)
        }
        for u in users
    ]

@router.post("/send")
async def send_message(
    recipient_id: str = Body(...),
    message_text: str = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message to a doctor or patient"""
    # Verify recipient exists
    recipient = db.query(User).filter(User.id == recipient_id).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
        
    msg_id = str(uuid.uuid4())
    new_msg = DoctorPatientMessage(
        id=msg_id,
        sender_id=current_user.id,
        recipient_id=recipient_id,
        message_text=message_text,
        sent_at=datetime.utcnow()
    )
    
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    
    return {"id": new_msg.id, "success": True, "message": "Message sent"}

@router.get("/history/{other_user_id}")
async def get_message_history(
    other_user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get message history with a specific user"""
    messages = db.query(DoctorPatientMessage).filter(
        or_(
            and_(DoctorPatientMessage.sender_id == current_user.id, DoctorPatientMessage.recipient_id == other_user_id),
            and_(DoctorPatientMessage.sender_id == other_user_id, DoctorPatientMessage.recipient_id == current_user.id)
        )
    ).order_by(DoctorPatientMessage.sent_at.asc()).all()
    
    # Mark as read
    unread_messages = [m for m in messages if m.recipient_id == current_user.id and not m.is_read]
    if unread_messages:
        for m in unread_messages:
            m.is_read = True
            m.read_at = datetime.utcnow()
        db.commit()
    
    result = []
    for msg in messages:
        result.append({
            "id": msg.id,
            "sender_id": msg.sender_id,
            "recipient_id": msg.recipient_id,
            "message_text": msg.message_text,
            "sent_at": msg.sent_at.isoformat() if msg.sent_at else None,
            "is_read": msg.is_read,
            "is_mine": msg.sender_id == current_user.id
        })
        
    return result

@router.get("/conversations")
async def get_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all conversations for the current user"""
    # Find all unique users this user has messaged or received messages from
    messages = db.query(DoctorPatientMessage).filter(
        or_(
            DoctorPatientMessage.sender_id == current_user.id,
            DoctorPatientMessage.recipient_id == current_user.id
        )
    ).order_by(DoctorPatientMessage.sent_at.desc()).all()
    
    # Group by conversation partner
    conversations = {}
    for msg in messages:
        other_id = msg.recipient_id if msg.sender_id == current_user.id else msg.sender_id
        if other_id not in conversations:
            other_user = db.query(User).filter(User.id == other_id).first()
            if other_user:
                conversations[other_id] = {
                    "id": other_id,
                    "first_name": other_user.first_name,
                    "last_name": other_user.last_name,
                    "role": other_user.role.value,
                    "last_message": msg.message_text,
                    "last_message_at": msg.sent_at.isoformat() if msg.sent_at else None,
                    "unread_count": 0
                }
        
        # Count unread messages from this partner
        if msg.sender_id == other_id and msg.recipient_id == current_user.id and not msg.is_read:
            conversations[other_id]["unread_count"] += 1
            
    return list(conversations.values())
