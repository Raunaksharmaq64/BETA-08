# Rollback Runbook

## 1. When to Rollback
Initiate an emergency rollback when:
- Post-deployment smoke tests fail critical endpoints.
- Error rates on core endpoints exceed 5% after release.
- Application containers crash-loop or fail liveness checks.

## 2. Automated Rollback Execution
```bash
bash infrastructure/scripts/rollback.sh
```

### Rollback Process:
1. Re-tags and restarts the previous known-stable container release.
2. Polls health check probes to confirm recovery.
3. Database compatibility check:
   - If migration added nullable columns, zero rollback needed (backward-compatible).
   - If destructive forward migration occurred, execute forward-fix or restore from pre-release snapshot.

