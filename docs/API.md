# REST API Reference & Endpoint Specifications

All endpoints are served by the FastAPI application on `http://localhost:8000`. Interactive OpenAPI documentation is accessible at `http://localhost:8000/docs`.

---

## 1. Authentication (`/api/auth`)

### `POST /api/auth/login`
Authenticates a user and issues a signed JWT.
- **Request Body**:
  ```json
  {
    "email": "claims.officer@insurance.com",
    "password": "password123",
    "role": "CLAIMS_OFFICER"
  }
  ```
- **Response**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6...",
    "token_type": "bearer",
    "user": {
      "id": "usr_01",
      "email": "claims.officer@insurance.com",
      "role": "CLAIMS_OFFICER"
    }
  }
  ```

### `GET /api/auth/me`
Returns details for the currently authenticated user based on the Bearer token.

---

## 2. Customers & Claimants (`/api/customers`)

### `GET /api/customers`
Query claimant records. Supports optional search parameter `?q=`.

### `POST /api/customers`
Register a new claimant profile.

### `GET /api/customers/{id}`
Returns the Customer 360 profile including associated policies, vehicles, claims, and cumulative risk tier.

---

## 3. Policies & Underwriting (`/api/policies`)

### `GET /api/policies`
Query underwriting policies. Supports optional filter `?customer_id=`.

### `POST /api/policies/verify`
Automated underwriting eligibility check against policy effective dates, claim history, and limits.

---

## 4. Claims & Multi-Signal Fraud Pipeline (`/api/claims`)

### `GET /api/claims`
List claims with optional filtering by status (`?status=`), risk tier (`?risk=`), and limit (`?limit=`).

### `POST /api/claims`
Create a new claim record from intake.

### `POST /api/claims/{id}/analyze`
Executes the automated 4-pillar fraud pipeline on the specified claim:
- Extracts 38 feature attributes
- Evaluates Supervised XGBoost ensemble
- Computes Isolation Forest anomaly score
- Searches duplicate claim registry
- Traverses bipartite graph syndicate network
- Computes blended hybrid risk score and SHAP explanations
- Automatically generates an SIU case if risk >= 0.50

### `GET /api/claims/{id}/analysis`
Retrieves the complete 360° forensic analysis dossier for the claim.

### `POST /api/claims/{id}/decision`
Records an official human determination (`APPROVE`, `REJECT`, `ESCALATE_SIU`, `REQUEST_INFO`) with investigator notes.

---

## 5. Supporting Documents (`/api/documents`)

### `POST /api/documents/upload/{claim_id}`
Multipart form upload of corroborating PDF/image files.

---

## 6. SIU Case Management (`/api/cases`)

### `GET /api/cases`
Retrieve all open, in-progress, or escalated SIU investigation cases.

### `POST /api/cases/{id}/notes`
Add a forensic annotation to an investigation case.

### `POST /api/cases/{id}/assign`
Assign an investigation case to a designated investigator.

---

## 7. Regulatory Audit Logs (`/api/audit-logs`)

### `GET /api/audit-logs`
Retrieve chronological, immutable audit log stream.

---

## 8. Platform Health (`/api/health`)

### `GET /api/health`
Returns health status of the API, database connectivity, and ML model loaded states.
