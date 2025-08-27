from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models.user import User
from app.models.account import Account
from app.schemas.statement import StatementRequest, StatementOut
from app.services.statements import generate_statement

router = APIRouter()


@router.post("/{account_id}", response_model=StatementOut)
def create_statement(
    account_id: int,
    statement_data: StatementRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> StatementOut:
    """Generate monthly statement for an account."""
    # Verify account ownership
    account_stmt = select(Account).where(
        Account.id == account_id,
        Account.user_id == current_user.id
    )
    account = session.exec(account_stmt).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    try:
        statement = generate_statement(
            session=session,
            account_id=account_id,
            month_str=statement_data.month
        )
        
        return StatementOut(
            id=statement.id,
            account_id=statement.account_id,
            period_start=statement.period_start,
            period_end=statement.period_end,
            opening_balance_cents=statement.opening_balance_cents,
            closing_balance_cents=statement.closing_balance_cents
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
