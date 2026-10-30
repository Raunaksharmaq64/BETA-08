# Authorization, Tenant Isolation & IDOR Defense

## 1. Overview & Architectural Principles

In **RIGHT FIT**, authorization and candidate data isolation are enforced at the architectural and code levels. The platform enforces the principle of least privilege, strict defense against Insecure Direct Object References (IDOR), and cryptographic tenant/user boundary isolation.

---

## 2. Role-Based & Lifecycle-Based Authorization

### 2.1 Role Hierarchy (`UserRole`)
The system defines three core roles in `contracts/auth/schemas.py`:
- `CANDIDATE`: Default role. Owns individual career profiles, preferences, resume data, and privacy settings.
- `RECRUITER`: Sourcing and outbound search role. Restricted to searching candidates who have opted into visibility (`allow_opportunity_matching == True`).
- `ADMIN`: Platform operations and governance. Possesses privileges to view anonymized telemetry and manage platform-wide rate limits.

### 2.2 Account Status Restrictions (`AccountStatus`)
Endpoints are guarded by dependency chains in `app/core/dependencies.py`:
1. `get_current_user`: Decodes JWT access token, checks revocation in the token store, verifies token signature and expiration, and extracts the database user record.
2. `get_current_active_user`: Enforces lifecycle status checks:
   - Rejects accounts with `status == AccountStatus.SUSPENDED` with `403 Forbidden ("Account is suspended")`.
   - Rejects accounts with `status == AccountStatus.DELETION_PENDING` with `403 Forbidden ("Account is scheduled for deletion")`.
   - Rejects accounts with `status == AccountStatus.DELETED` with `403 Forbidden ("Account has been deleted")`.

---

## 3. IDOR Defense (Insecure Direct Object Reference)

A critical vulnerability in multi-tenant SaaS applications is IDOR, where an authenticated user modifies URL path parameters (e.g. `/api/v1/profile/education/12345`) to access or delete another user's records.

**RIGHT FIT eliminates IDOR vulnerabilities through three structural rules:**

### Rule 1: Identity Always Derived from Token Context
- Endpoints **never** accept `user_id` as a route parameter or request body input.
- User identity is extracted strictly from the cryptographic JWT `sub` claim via `get_current_active_user(user: User = Depends(...))`.

```python
# SECURE IMPLEMENTATION IN RIGHT FIT
@router.get("/profile", response_model=CandidateProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    profile = await profile_service.get_profile(db, current_user.id)
    return profile
```

### Rule 2: Compound Query Scoping on Sub-Resources
- When mutating sub-resources (education, experience, skills), the database query **always** matches both the resource primary key AND the authenticated candidate's ID:

```python
# Secure deletion in profile_service.py
stmt = select(EducationRecord).where(
    EducationRecord.id == education_id,
    EducationRecord.candidate_id == profile.id
)
```
- If a malicious candidate attempts to delete an `education_id` belonging to another user, the query returns `None`, resulting in a safe `404 Not Found` without data leakage.

### Rule 3: UUIDv4 Identifiers
- All database entities use random 128-bit UUIDv4 identifiers, preventing sequential ID enumeration attacks.

---

## 4. Cross-Service Boundary Isolation

RIGHT FIT's Option A Hybrid Architecture guarantees candidate isolation across microservices:
1. **Core Career Engine Exclusive Custody**:
   - Only Core has direct read/write credentials to the candidate PostgreSQL database.
2. **Satellite Zero-Direct-Access**:
   - `LeadHunter AI` and `Startup Problems Hunter` run with dedicated, isolated database schemas.
   - Satellite services must communicate with Core via authenticated REST contracts using service tokens.
   - Core acts as a privacy gatekeeper, automatically filtering out candidate PII according to privacy toggles before transmitting data to satellites.

