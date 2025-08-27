from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models.user import User
from app.models.account import Account
from app.schemas.transaction import TransferRequest, TransactionOut
from app.services.transfers import execute_transfer

router = APIRouter()


@router.post("", response_model=List[TransactionOut])
def transfer_money(
    transfer_data: TransferRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> List[TransactionOut]:
    """Transfer money between accounts."""
    if transfer_data.amount_cents <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount must be positive"
        )
    
    if transfer_data.from_account_id == transfer_data.to_account_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot transfer to the same account"
        )
    
    # Verify source account ownership
    from_account_stmt = select(Account).where(
        Account.id == transfer_data.from_account_id,
        Account.user_id == current_user.id
    )
    from_account = session.exec(from_account_stmt).first()
    if not from_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source account not found"
        )
    
    # Verify destination account exists
    to_account_stmt = select(Account).where(Account.id == transfer_data.to_account_id)
    to_account = session.exec(to_account_stmt).first()
    if not to_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Destination account not found"
        )
    
    try:
        transactions = execute_transfer(
            session=session,
            from_account_id=transfer_data.from_account_id,
            to_account_id=transfer_data.to_account_id,
            amount_cents=transfer_data.amount_cents,
            description=transfer_data.description
        )
        
        return [
            TransactionOut(
                id=tx.id,
                type=tx.type,
                amount_cents=tx.amount_cents,
                created_at=tx.created_at,
                description=tx.description
            )
            for tx in transactions
        ]
    
    except ValueError as e:
        if "Insufficient funds" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient funds"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
