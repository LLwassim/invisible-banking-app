from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction
from app.schemas.account import AccountCreate, AccountOut
from app.schemas.transaction import DepositWithdrawRequest, TransactionOut

router = APIRouter()


@router.post("", response_model=AccountOut)
def create_account(
    account_data: AccountCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> AccountOut:
    """Create a new account for the current user."""
    account = Account(
        user_id=current_user.id,
        type=account_data.type,
        balance_cents=0
    )
    session.add(account)
    session.commit()
    session.refresh(account)
    
    return AccountOut(
        id=account.id,
        type=account.type,
        balance_cents=account.balance_cents
    )


@router.get("", response_model=List[AccountOut])
def list_accounts(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> List[AccountOut]:
    """List all accounts for the current user."""
    statement = select(Account).where(Account.user_id == current_user.id)
    accounts = session.exec(statement).all()
    
    return [
        AccountOut(
            id=account.id,
            type=account.type,
            balance_cents=account.balance_cents
        )
        for account in accounts
    ]


@router.post("/{account_id}/deposit", response_model=TransactionOut)
def deposit(
    account_id: int,
    deposit_data: DepositWithdrawRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> TransactionOut:
    """Deposit money into an account."""
    if deposit_data.amount_cents <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount must be positive"
        )
    
    # Get account and verify ownership
    statement = select(Account).where(Account.id == account_id, Account.user_id == current_user.id)
    account = session.exec(statement).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    # Update balance
    account.balance_cents += deposit_data.amount_cents
    
    # Create transaction record
    transaction = Transaction(
        account_id=account.id,
        type="deposit",
        amount_cents=deposit_data.amount_cents,
        description=deposit_data.description
    )
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    
    return TransactionOut(
        id=transaction.id,
        type=transaction.type,
        amount_cents=transaction.amount_cents,
        created_at=transaction.created_at,
        description=transaction.description
    )


@router.post("/{account_id}/withdraw", response_model=TransactionOut)
def withdraw(
    account_id: int,
    withdraw_data: DepositWithdrawRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> TransactionOut:
    """Withdraw money from an account."""
    if withdraw_data.amount_cents <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount must be positive"
        )
    
    # Get account and verify ownership
    statement = select(Account).where(Account.id == account_id, Account.user_id == current_user.id)
    account = session.exec(statement).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    # Check sufficient funds
    if account.balance_cents < withdraw_data.amount_cents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient funds"
        )
    
    # Update balance
    account.balance_cents -= withdraw_data.amount_cents
    
    # Create transaction record
    transaction = Transaction(
        account_id=account.id,
        type="withdraw",
        amount_cents=withdraw_data.amount_cents,
        description=withdraw_data.description
    )
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    
    return TransactionOut(
        id=transaction.id,
        type=transaction.type,
        amount_cents=transaction.amount_cents,
        created_at=transaction.created_at,
        description=transaction.description
    )
