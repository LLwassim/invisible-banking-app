# Banking Service Solution

## Stack

- **Python 3.11** - Runtime
- **FastAPI** - Web framework with automatic OpenAPI docs
- **SQLModel** - Type-safe ORM built on SQLAlchemy
- **SQLite** - Embedded database for simplicity
- **JWT + bcrypt** - Authentication and password security
- **pytest** - Testing framework

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Copy environment configuration:

```bash
cp env.example .env
```

3. Run the server:

```bash
uvicorn app.main:app --reload
```

4. Visit the API docs at: http://localhost:8000/docs

## Endpoints Map

### Authentication

- `POST /api/v1/auth/signup` - Create user account
- `POST /api/v1/auth/login` - Authenticate user

### Users

- `GET /api/v1/users/me` - Get current user info

### Accounts

- `POST /api/v1/accounts` - Create account
- `GET /api/v1/accounts` - List user's accounts
- `POST /api/v1/accounts/{id}/deposit` - Deposit money
- `POST /api/v1/accounts/{id}/withdraw` - Withdraw money

### Transactions

- `GET /api/v1/transactions?account_id=ID` - List account transactions

### Transfers

- `POST /api/v1/transfers` - Transfer between accounts

### Cards

- `POST /api/v1/cards` - Issue new card
- `GET /api/v1/cards?account_id=ID` - List account cards

### Statements

- `POST /api/v1/statements/{account_id}` - Generate monthly statement

## Testing

Run the test suite:

```bash
pytest -q
```

## Demo Steps

1. **Signup**: Create a user account
2. **Create Accounts**: Create checking and savings accounts
3. **Deposit**: Add money to checking account
4. **Transfer**: Move money between accounts
5. **Issue Card**: Create a payment card
6. **Statement**: Generate monthly statement

## Key Design Tradeoffs

- **SQLite over PostgreSQL**: Simplicity for demo; would use PostgreSQL in production
- **Integer cents**: Avoids floating-point precision issues
- **Card tokenization**: Never store PAN; use secure tokens
- **Atomic transfers**: Single database transaction ensures consistency
- **Ownership validation**: All operations verify user owns the resource
- **CVV hashing**: Secure storage without plaintext CVV
- **Standard library dates**: No external dateutil dependency

## Security & Hygiene

After a mistaken commit of .env, we rotated the JWT secret (treating the old key as compromised) and restarted the service so any previously issued tokens became invalid. We also scrubbed the repository history using git-filter-repo to remove .env from all past commits and ensured .env is ignored to prevent future tracking.
