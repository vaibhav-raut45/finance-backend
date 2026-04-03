from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.database import get_db
from app.models.financial import FinancialRecord
from app.models.user import User
from app.services.access_control import get_current_user, require_admin

router = APIRouter()


class RecordRequest(BaseModel):
    amount: float
    type: str
    category: str
    date: datetime
    notes: Optional[str] = None


@router.post("/")
def create_record(request: RecordRequest, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    if request.type not in ["income", "expense"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Type must be income or expense"
        )

    if request.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount must be greater than 0"
        )

    record = FinancialRecord(
        amount=request.amount,
        type=request.type,
        category=request.category,
        date=request.date,
        notes=request.notes,
        created_by=current_user.id
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return {"message": "Record created successfully", "id": record.id}


@router.get("/")
def get_records(
    type: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(FinancialRecord).filter(FinancialRecord.is_deleted == False)

    if type:
        query = query.filter(FinancialRecord.type == type)
    if category:
        query = query.filter(FinancialRecord.category == category)
    if start_date:
        query = query.filter(FinancialRecord.date >= start_date)
    if end_date:
        query = query.filter(FinancialRecord.date <= end_date)

    records = query.all()

    result = []
    for record in records:
        result.append({
            "id": record.id,
            "amount": record.amount,
            "type": record.type,
            "category": record.category,
            "date": record.date,
            "notes": record.notes,
            "created_by": record.created_by,
            "created_at": record.created_at
        })

    return result


@router.get("/{record_id}")
def get_record(record_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    record = db.query(FinancialRecord).filter(
        FinancialRecord.id == record_id,
        FinancialRecord.is_deleted == False
    ).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record not found"
        )

    return {
        "id": record.id,
        "amount": record.amount,
        "type": record.type,
        "category": record.category,
        "date": record.date,
        "notes": record.notes,
        "created_by": record.created_by,
        "created_at": record.created_at
    }


@router.put("/{record_id}")
def update_record(record_id: int, request: RecordRequest, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    record = db.query(FinancialRecord).filter(
        FinancialRecord.id == record_id,
        FinancialRecord.is_deleted == False
    ).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record not found"
        )

    if request.type not in ["income", "expense"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Type must be income or expense"
        )

    if request.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount must be greater than 0"
        )

    record.amount = request.amount
    record.type = request.type
    record.category = request.category
    record.date = request.date
    record.notes = request.notes

    db.commit()
    db.refresh(record)

    return {"message": "Record updated successfully", "id": record.id}


@router.delete("/{record_id}")
def delete_record(record_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    record = db.query(FinancialRecord).filter(
        FinancialRecord.id == record_id,
        FinancialRecord.is_deleted == False
    ).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record not found"
        )

    record.is_deleted = True
    db.commit()

    return {"message": "Record deleted successfully"}