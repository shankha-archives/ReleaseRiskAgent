# Dummy Application for R3 Agent E2E Testing

A full-stack test application designed to help validate the R3 Agent's risk assessment capabilities. This application contains intentional code patterns that trigger different risk levels.

## Purpose

This dummy application is used to:
1. Create realistic PRs with various risk patterns
2. Test the R3 Agent's risk scoring accuracy
3. Validate mitigation recommendations
4. Perform end-to-end testing of the PR review workflow

## Structure

```
dummy-app/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── main.py            # FastAPI entrypoint
│   │   ├── auth/              # HIGH RISK - authentication module
│   │   │   ├── login.py       # Auth logic with intentional issues
│   │   │   └── oauth.py       # OAuth implementation
│   │   ├── payment/           # HIGH RISK - payment processing
│   │   │   ├── processor.py   # Payment logic
│   │   │   └── stripe.py      # Stripe integration
│   │   ├── users/             # MEDIUM RISK - user management
│   │   │   ├── crud.py        # CRUD operations
│   │   │   └── models.py      # User models
│   │   └── utils/             # LOW RISK - utility functions
│   │       ├── helpers.py     # Simple helpers
│   │       └── validators.py  # Input validators
│   ├── tests/                 # Test files
│   └── requirements.txt
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── App.js
│   │   ├── components/
│   │   │   ├── auth/          # HIGH RISK - auth components
│   │   │   ├── payment/       # HIGH RISK - payment forms
│   │   │   └── utils/         # LOW RISK - utilities
│   └── package.json
└── README.md
```

## Risk Levels by Module

| Module | Risk Level | Intentional Issues |
|--------|------------|-------------------|
| `auth/` | HIGH | Hardcoded secrets, bare excepts, weak tokens, timing attacks |
| `payment/` | HIGH | PCI violations, logging card data, no idempotency |
| `users/` | MEDIUM | TODO comments, moderate complexity, coverage gaps |
| `utils/` | LOW | Well-tested, simple functions, no risky patterns |

## Running the Application

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm start
```

## Test Branches for E2E Testing

### Branch 1: `feature/simple-utils` (Expected: LOW Risk)
- Modifies only `utils/helpers.py` and `utils/validators.py`
- Simple functions, good test coverage
- Expected score: 0.1 - 0.25

### Branch 2: `feature/user-management` (Expected: MEDIUM Risk)
- Modifies `users/crud.py` and `users/models.py`
- Moderate complexity, some TODOs
- Expected score: 0.35 - 0.55

### Branch 3: `feature/payment-integration` (Expected: HIGH Risk)
- Modifies `auth/login.py` and `payment/processor.py`
- High complexity, hardcoded secrets, bare excepts
- Expected score: 0.65 - 0.85

## Intentional Vulnerabilities (For Testing Only!)

⚠️ **WARNING**: This application contains intentional security issues for testing purposes. DO NOT deploy to production!

### Backend Issues
- Hardcoded API keys and secrets
- Bare `except` blocks that swallow errors
- Plain text password storage
- Weak token generation (MD5)
- No rate limiting
- Missing input validation

### Frontend Issues
- Token stored in localStorage
- Credentials logged to console
- Price manipulation via URL parameters
- No CSRF protection
- Card data in component state

## License

This is a test application for internal use only.
