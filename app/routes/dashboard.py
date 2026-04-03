from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.database import get_db
from app.models.financial import FinancialRecord
from app.models.user import User
from app.services.access_control import get_current_user, require_analyst_or_admin

router = APIRouter()


@router.get("/summary")
def get_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total_income = db.query(func.sum(FinancialRecord.amount)).filter(
        FinancialRecord.type == "income",
        FinancialRecord.is_deleted == False
    ).scalar() or 0

    total_expense = db.query(func.sum(FinancialRecord.amount)).filter(
        FinancialRecord.type == "expense",
        FinancialRecord.is_deleted == False
    ).scalar() or 0

    net_balance = total_income - total_expense

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "net_balance": net_balance
    }


@router.get("/categories")
def get_category_totals(db: Session = Depends(get_db), current_user: User = Depends(require_analyst_or_admin)):
    results = db.query(
        FinancialRecord.category,
        FinancialRecord.type,
        func.sum(FinancialRecord.amount).label("total")
    ).filter(
        FinancialRecord.is_deleted == False
    ).group_by(
        FinancialRecord.category,
        FinancialRecord.type
    ).all()

    category_data = []
    for row in results:
        category_data.append({
            "category": row.category,
            "type": row.type,
            "total": row.total
        })

    return category_data


@router.get("/recent")
def get_recent_activity(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    records = db.query(FinancialRecord).filter(
        FinancialRecord.is_deleted == False
    ).order_by(
        FinancialRecord.created_at.desc()
    ).limit(10).all()

    result = []
    for record in records:
        result.append({
            "id": record.id,
            "amount": record.amount,
            "type": record.type,
            "category": record.category,
            "date": record.date,
            "notes": record.notes
        })

    return result


@router.get("/trends")
def get_monthly_trends(db: Session = Depends(get_db), current_user: User = Depends(require_analyst_or_admin)):
    six_months_ago = datetime.utcnow() - timedelta(days=180)

    records = db.query(FinancialRecord).filter(
        FinancialRecord.is_deleted == False,
        FinancialRecord.date >= six_months_ago
    ).all()

    monthly_data = {}
    for record in records:
        month_key = record.date.strftime("%Y-%m")
        if month_key not in monthly_data:
            monthly_data[month_key] = {"income": 0, "expense": 0}
        if record.type == "income":
            monthly_data[month_key]["income"] += record.amount
        else:
            monthly_data[month_key]["expense"] += record.amount

    result = []
    for month, data in sorted(monthly_data.items()):
        result.append({
            "month": month,
            "income": data["income"],
            "expense": data["expense"],
            "net": data["income"] - data["expense"]
        })

    return result