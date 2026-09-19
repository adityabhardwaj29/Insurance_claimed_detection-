# Security, Authentication & Access Control

## 1. Authentication Architecture

FraudShield AI implements a secure authentication layer using industry standards:
- **Password Hashing**: Direct `bcrypt.hashpw` with standard salt generation. Truncates passwords to 72 bytes per bcrypt protocol specifications.
- **Session Tokens**: JSON Web Tokens (JWT) signed with HMAC-SHA256 (`HS256`) containing user ID, email, role, and expiration timestamps.
- **Token Transport**: Transmitted in the HTTP `Authorization` header as `Bearer <token>`.

---

## 2. Role-Based Access Control (RBAC) Matrix

| Endpoint / Operation | Claims Officer | SIU Investigator | Operations Supervisor | Fraud Analyst | System Admin |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Search Customers & Policies** | YES | YES | YES | YES | YES |
| **Submit New Claim** | YES | NO | NO | NO | YES |
| **Upload Claim Documents** | YES | YES | NO | NO | YES |
| **View 360° Forensic Dossier** | YES | YES | YES | YES | YES |
| **Add SIU Forensic Case Notes** | NO | YES | YES | NO | YES |
| **Record Human Claim Decision** | NO | YES | YES | NO | YES |
| **Assign Investigation Cases** | NO | NO | YES | NO | YES |
| **Model Drift & Calibration** | NO | NO | NO | YES | YES |
| **View Immutable Audit Logs** | NO | NO | YES | NO | YES |
| **Manage Users & Permissions** | NO | NO | NO | NO | YES |

---

## 3. Database Security & Row-Level Security (RLS)

In Supabase PostgreSQL, Row-Level Security is active on all core operational and case management tables:
- **Claims & Intakes**: Accessible to authenticated insurance personnel with active JWTs.
- **Investigation Cases & Notes**: Restricted to members of the SIU department, Supervisors, and Administrators.
- **Audit Logs**: Strictly append-only. No `UPDATE` or `DELETE` grants exist on the `audit_logs` table for any role, ensuring tamper-evident legal records.

---

## 4. Input Sanitization & Document Safety

1. **File Uploads**:
   - Files are validated against approved MIME types (`application/pdf`, `image/jpeg`, `image/png`, `application/dicom`).
   - Saved with generated UUID filenames in `data/documents/` to prevent path traversal attacks.
2. **SQL Injection Prevention**:
   - All database queries use parameterized SQL or ORM query builders.
3. **CORS Configuration**:
   - Restricted to authorized frontend origins (e.g. `http://localhost:3000`, `http://127.0.0.1:3000`).
