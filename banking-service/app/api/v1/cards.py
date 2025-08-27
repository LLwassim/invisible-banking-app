import secrets
import random
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select

from app.api.deps import get_current_user
from app.core.security import get_password_hash
from app.db.session import get_session
from app.models.user import User
from app.models.account import Account
from app.models.card import Card
from app.schemas.card import CardIssueRequest, CardOut

router = APIRouter()


@router.post("", response_model=CardOut)
def issue_card(
    card_data: CardIssueRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> CardOut:
    """Issue a new card for an account."""
    # Verify account ownership
    account_stmt = select(Account).where(
        Account.id == card_data.account_id,
        Account.user_id == current_user.id
    )
    account = session.exec(account_stmt).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    # Generate secure card token and random last4
    card_token = secrets.token_urlsafe(32)
    last4 = str(random.randint(1000, 9999))
    
    # Hash CVV (never store plain CVV)
    cvv_hash = get_password_hash(card_data.cvv)
    
    # Create card
    card = Card(
        account_id=card_data.account_id,
        brand="VISA",
        holder_name=card_data.holder_name,
        last4=last4,
        card_token=card_token,
        exp_month=card_data.exp_month,
        exp_year=card_data.exp_year,
        cvv_hash=cvv_hash
    )
    
    session.add(card)
    session.commit()
    session.refresh(card)
    
    return CardOut(
        id=card.id,
        brand=card.brand,
        holder_name=card.holder_name,
        last4=card.last4,
        card_token=card.card_token,
        exp_month=card.exp_month,
        exp_year=card.exp_year
    )


@router.get("", response_model=List[CardOut])
def list_cards(
    account_id: int = Query(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> List[CardOut]:
    """List cards for an account."""
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
    
    # Get cards for account
    statement = select(Card).where(Card.account_id == account_id)
    cards = session.exec(statement).all()
    
    return [
        CardOut(
            id=card.id,
            brand=card.brand,
            holder_name=card.holder_name,
            last4=card.last4,
            card_token=card.card_token,
            exp_month=card.exp_month,
            exp_year=card.exp_year
        )
        for card in cards
    ]
