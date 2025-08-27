from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionOut

router = APIRouter()


@router.get("", response_model=List[TransactionOut])
def list_transactions(
    account_id: int = Query(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> List[TransactionOut]:
    """List transactions for an account (newest first)."""
    # Verify account ownership
    account_statement = select(Account).where(Account.id == account_id, Account.user_id == current_user.id)
    account = session.exec(account_statement).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    # Get transactions, newest first
    statement = select(Transaction).where(Transaction.account_id == account_id).order_by(Transaction.created_at.desc())
    transactions = session.exec(statement).all()
    
    return [
        TransactionOut(
            id=transaction.id,
            type=transaction.type,
            amount_cents=transaction.amount_cents,
            created_at=transaction.created_at,
            description=transaction.description
        )
        for transaction in transactions
    ]
