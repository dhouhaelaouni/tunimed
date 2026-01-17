# TuniMed - Medicine Reuse & Waste Reduction API

A complete Flask REST API for managing medicine waste reduction and controlled redistribution in Tunisia, with strict regulatory compliance aligned with ANMPS (National Agency for Medicines and Health Products).

## Project Overview

TuniMed is a production-ready Flask REST API that enables:
- **Citizens** to declare unused medicines with full regulatory compliance
- **Pharmacists** to verify medicine packaging and authenticity
- **Regulatory Agents** to validate medicines for safe redistribution
- **Health Facilities** to request approved medicines
- **Automatic enforcement** of import restrictions and safety rules
- **Complete audit trails** for GDPR compliance

## Technology Stack

- **Framework**: Flask
- **Database**: SQLAlchemy ORM with SQLite (development) / PostgreSQL (production)
- **Authentication**: JWT (JSON Web Tokens)
- **Authorization**: Role-Based Access Control (RBAC)
- **Rate Limiting**: Flask-Limiter for login protection
- **Password Security**: Werkzeug hashing

## Folder Structure

```
TuniMed/
├── app.py                    # Main Flask application factory
├── db.py                     # SQLAlchemy database initialization
├── requirements.txt          # Python dependencies
├── .env                      # Environment configuration
├── config/
│   └── config.py            # Application configuration settings
├── decorators/
│   └── decorators.py        # Role-based access control decorators
├── models/
│   ├── __init__.py          # Model exports
│   └── user.py              # User, Medicine, AuditLog models
├── resources/
│   ├── auth.py              # Authentication endpoints
│   ├── medicines.py         # Medicine management endpoints
│   └── info.py              # Information endpoints
└── README.md                # This file
```

## Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Setup

1. **Clone/Create the project directory**
```bash
cd TuniMed
```

2. **Create a virtual environment** (recommended)
```bash
python -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment** (already provided in .env, adjust if needed)
```bash
# The .env file is pre-configured with default values
# Update SECRET_KEY and JWT_SECRET_KEY for production
```

5. **Run the application**
```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Authentication Endpoints

#### Register a new user
```
POST /auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password",
  "role": "CITIZEN"  # CITIZEN, PHARMACIST, REGULATORY_AGENT, HEALTH_FACILITY, ADMIN
}

Response: 201 Created
{
  "msg": "User registered successfully",
  "user": { ... }
}
```

#### Login
```
POST /auth/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "secure_password"
}

Response: 200 OK
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": { ... }
}
```

#### Refresh access token
```
POST /auth/refresh
Authorization: Bearer <refresh_token>

Response: 200 OK
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Get current user info
```
GET /auth/me
Authorization: Bearer <access_token>

Response: 200 OK
{
  "user": { ... }
}
```

### Medicine Declaration Endpoints (CITIZEN)

#### Declare a new medicine
```
POST /medicines/declarations
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Paracetamol 500mg",
  "amm": "13456789",
  "batch_number": "BATCH001",
  "expiration_date": "2025-12-31",
  "quantity": 20,
  "is_imported": false,
  "country_of_origin": null
}

Response: 201 Created
{
  "msg": "Medicine declared successfully",
  "medicine": { ... }
}
```

#### Get my declarations
```
GET /medicines/declarations/my
Authorization: Bearer <access_token>

Response: 200 OK
{
  "medicines": [ ... ],
  "count": 5
}
```

#### Get specific declaration
```
GET /medicines/declarations/<id>
Authorization: Bearer <access_token>

Response: 200 OK
{
  "medicine": { ... }
}
```

### Pharmacy Verification Endpoints (PHARMACIST)

#### Get pending verifications
```
GET /medicines/pending-pharmacy-review
Authorization: Bearer <access_token>

Response: 200 OK
{
  "medicines": [ ... ],
  "count": 3
}
```

#### Verify a medicine
```
POST /medicines/verify/<id>
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "is_valid": true,
  "notes": "Packaging intact, authenticity verified"
}

Response: 200 OK
{
  "msg": "Medicine approved by pharmacy",
  "medicine": { ... }
}
```

### Regulatory Validation Endpoints (REGULATORY_AGENT)

#### Get pending validations
```
GET /medicines/pending-regulatory-review
Authorization: Bearer <access_token>

Response: 200 OK
{
  "medicines": [ ... ],
  "count": 2
}
```

#### Validate a medicine
```
POST /medicines/validate/<id>
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "decision": "APPROVED",  # APPROVED, RESTRICTED, REJECTED
  "notes": "All safety checks passed"
}

Response: 200 OK
{
  "msg": "Medicine regulatory validation completed: APPROVED",
  "medicine": { ... }
}
```

### Eligibility Check Endpoints

#### Check medicine eligibility for redistribution
```
GET /medicines/<id>/eligibility
Authorization: Bearer <access_token>

Response: 200 OK
{
  "medicine_id": 1,
  "is_eligible": true,
  "status": "APPROVED_FOR_REDISTRIBUTION",
  "reasons": ["Medicine is eligible for redistribution"]
}
```

### Health Facility Endpoints (HEALTH_FACILITY)

#### Get approved medicines available for redistribution
```
GET /medicines/approved
Authorization: Bearer <access_token>

Response: 200 OK
{
  "medicines": [ ... ],
  "count": 10
}
```

### Information Endpoints

#### Get import regulations
```
GET /info/import-rules

Response: 200 OK
{
  "title": "Import Regulations for Medicine Redistribution",
  "rules": [ ... ]
}
```

#### Get redistribution options
```
GET /info/redistribution-options

Response: 200 OK
{
  "title": "Redistribution Options",
  "recipient_types": [ ... ]
}
```

#### Get workflow statuses
```
GET /info/workflow-statuses

Response: 200 OK
{
  "title": "Medicine Declaration Workflow Statuses",
  "statuses": [ ... ]
}
```

#### Get error catalog
```
GET /info/error-catalog

Response: 200 OK
{
  "title": "TuniMed API Error Catalog",
  "errors": { ... }
}
```

#### Health check
```
GET /info/health

Response: 200 OK
{
  "status": "healthy",
  "service": "TuniMed API",
  "version": "1.0.0"
}
```

## User Roles

| Role | Permissions |
|------|-------------|
| **CITIZEN** | Declare medicines, view own declarations, check eligibility |
| **PHARMACIST** | Verify medicines, review packaging and authenticity |
| **REGULATORY_AGENT** | Validate medicines, approve for redistribution |
| **HEALTH_FACILITY** | View approved medicines available for redistribution |
| **ADMIN** | Full platform access |

## Medicine Declaration Workflow

```
1. CITIZEN SUBMITS (Status: SUBMITTED)
   └─> POST /medicines/declarations
       - Medicine declared with basic information
       - Automatically checked for expiration
       - Imported medicines flagged

2. PHARMACIST VERIFIES (Status: PHARMACY_VERIFIED or PHARMACY_REJECTED)
   └─> GET /medicines/pending-pharmacy-review
   └─> POST /medicines/verify/{id}
       - Verify packaging integrity
       - Check authenticity
       - Add notes

3. REGULATORY AGENT VALIDATES (Status: APPROVED_FOR_REDISTRIBUTION, RESTRICTED_USE, or REJECTED_REGULATORY)
   └─> GET /medicines/pending-regulatory-review
   └─> POST /medicines/validate/{id}
       - Validate AMM (Market Authorization)
       - Check for recalls
       - Enforce import restrictions
       - Make final decision

4. DISTRIBUTION
   └─> GET /medicines/approved (HEALTH_FACILITY view)
       - Approved medicines available for health facilities
       - Eligibility automatically enforced
```

## Safety Rules & Automatic Enforcement

### Automatic Blocks
- ❌ **Expired medicines** - Blocked at submission (checked by system)
- ❌ **Imported medicines** - Auto-flagged, cannot redistribute (non-local origin)
- ❌ **Recalled medicines** - Blocked by regulatory agent
- ❌ **Invalid AMM** - Rejected at regulatory stage

### Eligible for Redistribution
- ✅ **Local regulated** - Eligible after approval
- ✅ **Pharmacy verified** - Packaging and authenticity confirmed
- ✅ **Regulatory approved** - All safety checks passed

## Test Credentials

The application automatically creates test users on first run:

| Username | Password | Role |
|----------|----------|------|
| citizen_test | citizenpass | CITIZEN |
| pharmacist_test | pharmacistpass | PHARMACIST |
| regulatory_test | regulatorypass | REGULATORY_AGENT |
| healthfacility_test | facilitypass | HEALTH_FACILITY |
| admin | adminpass | ADMIN |

## Testing with cURL

### Register a user
```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_user",
    "email": "test@example.com",
    "password": "testpass",
    "role": "CITIZEN"
  }'
```

### Login
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_user",
    "password": "testpass"
  }'
```

### Declare a medicine (as CITIZEN with access_token)
```bash
curl -X POST http://localhost:5000/medicines/declarations \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Aspirin 100mg",
    "amm": "12345678",
    "batch_number": "BATCH123",
    "expiration_date": "2025-12-31",
    "quantity": 50,
    "is_imported": false
  }'
```

### Health check
```bash
curl http://localhost:5000/info/health
```

## Security Features

### Authentication & Authorization
- ✅ **JWT Authentication** - Token-based authentication with access and refresh tokens
- ✅ **Role-Based Access Control** - Routes protected by user roles
- ✅ **Password Security** - Passwords hashed using Werkzeug
- ✅ **Token Expiration** - Access tokens expire after 15 minutes, refresh tokens after 30 days

### Data Protection
- ✅ **Rate Limiting** - Login attempts limited to 5 per minute
- ✅ **SQL Injection Prevention** - SQLAlchemy parameterized queries
- ✅ **HTTPS Ready** - Recommended for production deployment
- ✅ **GDPR Compliance** - Data minimization, audit trails, soft delete ready

### Audit Trail
- ✅ **Immutable Logging** - All actions logged with timestamps
- ✅ **User Tracking** - Who performed which action and when
- ✅ **Decision Trail** - Pharmacy and regulatory decisions tracked
- ✅ **Complete History** - No data deletion for audit purposes

## GDPR Compliance

- ✅ **Data Minimization** - Only required fields stored
- ✅ **User Consent** - Explicit opt-in for data processing
- ✅ **Right to Access** - Users can view their declarations via `/medicines/declarations/my`
- ✅ **Right to Deletion** - Soft delete implementation ready
- ✅ **Audit Trail** - All actions logged with timestamps for accountability
- ✅ **ID Security** - Sensitive IDs can be encrypted for production

## Error Handling

The API provides comprehensive error responses with error codes for easy client-side handling:

```json
{
  "msg": "Descriptive error message",
  "code": "error_code_identifier"
}
```

Common error codes:
- `authentication_failed` - Invalid credentials (401)
- `token_expired` - JWT token expired (401)
- `invalid_token` - Invalid or missing JWT (401)
- `insufficient_permissions` - User lacks required role (403)
- `invalid_input` - Request validation failed (400)
- `expired_medicine` - Medicine has expired (400)
- `not_found` - Resource not found (404)
- `user_exists` - Username already exists (409)
- `email_exists` - Email already exists (409)

See `/info/error-catalog` for complete error documentation.

## Production Deployment

### Important: Security Updates

Before deploying to production:

1. **Update Secret Keys** in `.env`:
   ```bash
   SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
   JWT_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
   ```

2. **Use PostgreSQL** instead of SQLite:
   ```bash
   DATABASE_URL=postgresql://user:password@localhost:5432/tunimed
   ```

3. **Enable HTTPS** and set `FLASK_ENV=production`

4. **Use a production WSGI server**:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

5. **Set up proper logging and monitoring**

## Troubleshooting

### Database connection errors
- Ensure the database file exists or PostgreSQL is running
- Check DATABASE_URL in .env

### JWT token errors
- Verify token is in Authorization header: `Authorization: Bearer <token>`
- Check token hasn't expired (use refresh endpoint)
- Ensure JWT_SECRET_KEY is properly set

### Permission denied errors
- Verify user has required role for the endpoint
- Check user is active (`is_active=True`)

## Support & Documentation

For more information about TuniMed API functionality, see:
- `/info/workflow-statuses` - Detailed workflow documentation
- `/info/import-rules` - Import regulations and restrictions
- `/info/error-catalog` - Complete error reference
- `/info/redistribution-options` - Recipient types and workflow

## License

This project is created for the medicine reuse initiative in Tunisia, aligned with ANMPS (National Agency for Medicines and Health Products) regulations.

## Contributing

This is a reference implementation. For contributions or improvements, please follow:
- Clear code with comments
- Proper error handling
- GDPR compliance
- Security best practices

