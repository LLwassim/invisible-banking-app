from fastapi import FastAPI

from app.db.session import init_db
from app.api.v1 import auth, users, accounts, transactions, transfers, cards, statements


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Banking Service API",
        description="A secure banking service with accounts, transfers, and cards",
        version="1.0.0",
    )
    
    # Initialize database
    init_db()
    
    # Include routers
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
    app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
    app.include_router(accounts.router, prefix="/api/v1/accounts", tags=["accounts"])
    app.include_router(transactions.router, prefix="/api/v1/transactions", tags=["transactions"])
    app.include_router(transfers.router, prefix="/api/v1/transfers", tags=["transfers"])
    app.include_router(cards.router, prefix="/api/v1/cards", tags=["cards"])
    app.include_router(statements.router, prefix="/api/v1/statements", tags=["statements"])
    
    return app


app = create_app()
