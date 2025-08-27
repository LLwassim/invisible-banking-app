import calendar
from datetime import datetime
from sqlmodel import Session, select

from app.models.account import Account
from app.models.transaction import Transaction
from app.models.statement import Statement


def generate_statement(
    session: Session,
    account_id: int,
    month_str: str
) -> Statement:
    """Generate monthly statement for an account."""
    # Parse month string (YYYY-MM)
    try:
        year, month = map(int, month_str.split('-'))
    except ValueError:
        raise ValueError("Invalid month format. Use YYYY-MM")
    
    # Calculate period boundaries
    period_start = datetime(year, month, 1, 0, 0, 0)
    
    # Get last day of month and first day of next month
    last_day = calendar.monthrange(year, month)[1]
    if month == 12:
        period_end = datetime(year + 1, 1, 1, 0, 0, 0)
    else:
        period_end = datetime(year, month + 1, 1, 0, 0, 0)
    
    # Calculate opening balance (transactions before period start)
    opening_stmt = select(Transaction).where(
        Transaction.account_id == account_id,
        Transaction.created_at < period_start
    )
    opening_transactions = session.exec(opening_stmt).all()
    
    opening_balance_cents = 0
    for tx in opening_transactions:
        if tx.type in ["deposit", "transfer_in"]:
            opening_balance_cents += tx.amount_cents
        elif tx.type in ["withdraw", "transfer_out", "card_charge"]:
            opening_balance_cents -= tx.amount_cents
        elif tx.type == "card_refund":
            opening_balance_cents += tx.amount_cents
    
    # Calculate closing balance (transactions up to period end)
    closing_stmt = select(Transaction).where(
        Transaction.account_id == account_id,
        Transaction.created_at < period_end
    )
    closing_transactions = session.exec(closing_stmt).all()
    
    closing_balance_cents = 0
    for tx in closing_transactions:
        if tx.type in ["deposit", "transfer_in"]:
            closing_balance_cents += tx.amount_cents
        elif tx.type in ["withdraw", "transfer_out", "card_charge"]:
            closing_balance_cents -= tx.amount_cents
        elif tx.type == "card_refund":
            closing_balance_cents += tx.amount_cents
    
    # Create statement
    statement = Statement(
        account_id=account_id,
        period_start=period_start,
        period_end=period_end,
        opening_balance_cents=opening_balance_cents,
        closing_balance_cents=closing_balance_cents
    )
    
    session.add(statement)
    session.commit()
    session.refresh(statement)
    
    return statement
