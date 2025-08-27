from typing import List
from sqlmodel import Session, select

from app.models.account import Account
from app.models.transaction import Transaction


def execute_transfer(
    session: Session,
    from_account_id: int,
    to_account_id: int,
    amount_cents: int,
    description: str = None
) -> List[Transaction]:
    """Execute atomic transfer between accounts."""
    # Get both accounts
    from_account_stmt = select(Account).where(Account.id == from_account_id)
    from_account = session.exec(from_account_stmt).first()
    
    to_account_stmt = select(Account).where(Account.id == to_account_id)
    to_account = session.exec(to_account_stmt).first()
    
    if not from_account or not to_account:
        raise ValueError("Account not found")
    
    if from_account.balance_cents < amount_cents:
        raise ValueError("Insufficient funds")
    
    # Update balances
    from_account.balance_cents -= amount_cents
    to_account.balance_cents += amount_cents
    
    # Create transaction records
    transfer_out = Transaction(
        account_id=from_account_id,
        type="transfer_out",
        amount_cents=amount_cents,
        description=description,
        counterparty_account_id=to_account_id
    )
    
    transfer_in = Transaction(
        account_id=to_account_id,
        type="transfer_in",
        amount_cents=amount_cents,
        description=description,
        counterparty_account_id=from_account_id
    )
    
    session.add(transfer_out)
    session.add(transfer_in)
    session.commit()
    session.refresh(transfer_out)
    session.refresh(transfer_in)
    
    return [transfer_out, transfer_in]
