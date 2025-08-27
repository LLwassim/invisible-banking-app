# Banking Service API

## Authentication

### POST /api/v1/auth/signup

Create a new user account.

**Request:**

```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "full_name": "John Doe"
}
```

**Response:**

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### POST /api/v1/auth/login

Authenticate existing user.

**Request:**

```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:**

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

## Users

### GET /api/v1/users/me

Get current user information. Requires Bearer token.

**Response:**

```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe"
}
```

## Accounts

### POST /api/v1/accounts

Create a new account. Requires Bearer token.

**Request:**

```json
{
  "type": "checking"
}
```

**Response:**

```json
{
  "id": 1,
  "type": "checking",
  "balance_cents": 0
}
```

### GET /api/v1/accounts

List all accounts for current user. Requires Bearer token.

**Response:**

```json
[
  {
    "id": 1,
    "type": "checking",
    "balance_cents": 50000
  }
]
```

### POST /api/v1/accounts/{id}/deposit

Deposit money into account. Requires Bearer token.

**Request:**

```json
{
  "amount_cents": 10000,
  "description": "Salary deposit"
}
```

### POST /api/v1/accounts/{id}/withdraw

Withdraw money from account. Requires Bearer token.

**Request:**

```json
{
  "amount_cents": 5000,
  "description": "ATM withdrawal"
}
```

## Transfers

### POST /api/v1/transfers

Transfer money between accounts. Requires Bearer token.

**Request:**

```json
{
  "from_account_id": 1,
  "to_account_id": 2,
  "amount_cents": 10000,
  "description": "Transfer to savings"
}
```

**Response:**

```json
[
  {
    "id": 10,
    "type": "transfer_out",
    "amount_cents": 10000,
    "created_at": "2024-01-15T10:30:00Z",
    "description": "Transfer to savings"
  },
  {
    "id": 11,
    "type": "transfer_in",
    "amount_cents": 10000,
    "created_at": "2024-01-15T10:30:00Z",
    "description": "Transfer to savings"
  }
]
```

## Cards

### POST /api/v1/cards

Issue a new payment card. Requires Bearer token.

**Request:**

```json
{
  "account_id": 1,
  "holder_name": "John Doe",
  "exp_month": 12,
  "exp_year": 2027,
  "cvv": "123"
}
```

**Response:**

```json
{
  "id": 1,
  "brand": "VISA",
  "holder_name": "John Doe",
  "last4": "1234",
  "card_token": "card_secure_token_abc123",
  "exp_month": 12,
  "exp_year": 2027
}
```

## Statements

### POST /api/v1/statements/{account_id}

Generate monthly statement. Requires Bearer token.

**Request:**

```json
{
  "month": "2024-01"
}
```

**Response:**

```json
{
  "id": 1,
  "account_id": 1,
  "period_start": "2024-01-01T00:00:00Z",
  "period_end": "2024-02-01T00:00:00Z",
  "opening_balance_cents": 0,
  "closing_balance_cents": 50000
}
```

## Error Responses

- `400` - Bad request (invalid amount, insufficient funds)
- `401` - Unauthorized (invalid/missing token)
- `403` - Forbidden (not allowed)
- `404` - Not found (account/resource doesn't exist)

All amounts are in cents to avoid floating-point issues.
Bearer token required in `Authorization` header for protected endpoints.
