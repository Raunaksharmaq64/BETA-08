# Secrets Management & Environment Configuration

## 1. Secrets Governance Policy
- **Zero Secrets in Git**: Git repositories, PRs, and commit history must never contain plaintext secrets, passwords, private keys, or API tokens.
- **Zero Secrets in Docker Images**: Docker build arguments (`ARG`) and environment variables (`ENV`) must not embed sensitive keys into image layers.
- **Least-Privilege Secret Retrieval**: Applications running in AWS retrieve secrets at runtime via IAM instance profile permissions rather than persistent static access keys.

## 2. Secrets Storage Hierarchy
Production secrets are stored in **AWS Systems Manager Parameter Store** as `SecureString` types encrypted with an AWS KMS Customer Managed Key (CMK):

```
/rightfit/production/
  ├── DATABASE_URL           (SecureString: Full connection URI with password)
  ├── REDIS_PASSWORD         (SecureString: Redis authentication token)
  ├── JWT_SECRET             (SecureString: 64-char HMAC signing key)
  ├── GEMINI_API_KEY         (SecureString: Production Google AI API key)
  ├── LEADHUNTER_API_KEY     (SecureString: Internal service-to-service key)
  └── STARTUP_INTEL_API_KEY  (SecureString: Internal service-to-service key)
```

## 3. Runtime Secret Injection
On instance initialization or deployment, `infrastructure/scripts/fetch_secrets_from_ssm.py` executes:
1. Queries SSM under `/rightfit/production/` with KMS decryption.
2. Writes decrypted values to a temporary file `.env.production`.
3. Sets strict POSIX file permissions:
   ```bash
   chmod 600 .env.production
   ```
4. Docker Compose sources `.env.production` at runtime.
5. In-flight secret rotation requires running `fetch_secrets_from_ssm.py` followed by `docker compose -f docker-compose.prod.yml restart`.

