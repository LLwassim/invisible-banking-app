# Security Architecture

## Authentication & Authorization

### JWT Token Management

- **Algorithm**: HS256 with configurable secret
- **Payload**: Contains user email (sub), issued-at (iat), and expiry (exp)
- **Expiry**: Configurable via ACCESS_TOKEN_EXPIRE_MINUTES (default: 30 minutes)
- **Storage**: Client must store token securely and include in Authorization header

### Password Security

- **Hashing**: bcrypt with automatic salt generation
- **Storage**: Only hashed passwords stored, never plaintext
- **Verification**: Constant-time comparison via passlib

## Data Protection

### Financial Data

- **Integer Cents**: All monetary values stored as integers to prevent floating-point precision errors
- **Atomic Transactions**: Database transactions ensure consistency for transfers
- **Ownership Validation**: Every operation validates user owns the resource

### Card Security

- **No PAN Storage**: Never store full Primary Account Numbers
- **Tokenization**: Secure random card tokens generated via secrets module
- **CVV Protection**: CVV hashed with bcrypt, never stored in plaintext
- **Random Last4**: Generated randomly instead of using real card data

### Account Access

- **User Isolation**: Strict user ID filtering prevents cross-user data access
- **Account Ownership**: All account operations verify current user owns the account
- **Resource Scoping**: Transaction listings and card operations scoped to owned accounts

## Data Validation

### Input Sanitization

- **Pydantic Models**: All inputs validated via Pydantic schemas
- **Type Safety**: SQLModel ensures type safety between API and database
- **Amount Validation**: Positive amounts enforced, sufficient funds checked

### Error Handling

- **Consistent Responses**: Standard HTTP status codes with descriptive messages
- **Information Disclosure**: Error messages don't leak sensitive data
- **Rate Limiting**: Future consideration for API rate limiting

## Infrastructure Security

### Database

- **Connection Security**: SQLite with check_same_thread=False for thread safety
- **Environment Variables**: Database URL and secrets loaded from environment
- **Migration Safety**: SQLModel automatic table creation

### Communication

- **HTTPS**: Production deployment should enforce HTTPS-only
- **CORS**: Configure CORS policies for frontend integration
- **Headers**: Add security headers (HSTS, CSP, etc.) in production

## Future Security Enhancements

### Audit & Monitoring

- **Audit Logging**: Log all financial transactions and access attempts
- **Anomaly Detection**: Monitor for unusual transaction patterns
- **Failed Login Tracking**: Track and throttle failed authentication attempts

### Enhanced Authentication

- **MFA**: Multi-factor authentication for sensitive operations
- **Session Management**: Refresh tokens and session invalidation
- **Device Fingerprinting**: Track and validate known devices

### Additional Controls

- **Idempotency Keys**: Prevent duplicate transactions
- **Transaction Limits**: Daily/monthly spending limits
- **Fraud Detection**: Real-time transaction monitoring
- **Encryption at Rest**: Database encryption for sensitive data

## Security Configuration

### Environment Variables

```bash
JWT_SECRET=random-256-bit-secret-in-production
DATABASE_URL=encrypted-database-connection-string
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Production Checklist

- [ ] Use strong JWT secret (256+ bits entropy)
- [ ] Enable HTTPS with valid certificates
- [ ] Configure proper CORS policies
- [ ] Set up database encryption at rest
- [ ] Implement request rate limiting
- [ ] Add security headers middleware
- [ ] Enable audit logging
- [ ] Set up monitoring and alerting
