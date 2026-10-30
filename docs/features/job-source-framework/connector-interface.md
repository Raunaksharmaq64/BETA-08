# Connector Interface & Adapters

**Phase:** 5 — Job Source Framework: Registry, Connectors, Normalization & Provenance  
**Status:** IMPLEMENTED & TESTED  
**Version:** 1.0.0  

---

## 1. Abstract Connector Specification

All external sources implement the `BaseJobConnector` interface defined in `backend/app/services/connectors/base.py`:

```python
class BaseJobConnector(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Unique provider slug (e.g. 'greenhouse', 'ashby', 'synthetic')."""
        pass

    @abstractmethod
    def validate_config(self, base_url: str, credential_reference: Optional[str] = None) -> None:
        """Validates endpoint syntax and settings before registration."""
        pass

    @abstractmethod
    async def check_health(self, source: JobSourceRecord) -> HealthCheckResult:
        """Probes the external source for reachability and latency."""
        pass

    @abstractmethod
    async def fetch_jobs(self, source: JobSourceRecord, limit: int = 50) -> ConnectorFetchResult:
        """Pulls raw listings and packages them into standardized RawJobPayload envelopes."""
        pass
```

### Data Containers
- `HealthCheckResult`: `healthy: bool`, `status_code: Optional[int]`, `latency_ms: float`, `message: str`, `checked_at: datetime`.
- `RawJobPayload`: `external_job_id: str`, `listing_url: str`, `raw_payload: Dict[str, Any]`, `source_published_at: Optional[datetime]`, `source_updated_at: Optional[datetime]`.
- `ConnectorFetchResult`: `records: List[RawJobPayload]`, `total_found: int`, `metadata: Dict[str, Any]`, `fetched_at: datetime`.

---

## 2. Initial Supported Adapters

### 1. Greenhouse Connector (`GreenhouseConnector`)
- **Adapter Slug:** `greenhouse`
- **Methodology:** Queries the official public Greenhouse JSON API:
  `GET https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true`
- **Automatic URL Normalization:** Accepts board website URLs (e.g. `https://boards.greenhouse.io/stripe`) or raw board slugs, transforming them automatically into canonical JSON API endpoints.
- **Payload Extraction:**
  - `external_job_id`: Greenhouse integer job ID converted to string.
  - `listing_url`: `absolute_url` field.
  - `source_published_at`: Parsed from `updated_at`.
  - Content: Full HTML description.

### 2. Ashby Connector (`AshbyConnector`)
- **Adapter Slug:** `ashby`
- **Methodology:** Queries the official public Ashby posting JSON API:
  `GET https://api.ashbyhq.com/posting-api/job-board/{board_token}`
- **Automatic URL Normalization:** Accepts job board links (`https://jobs.ashbyhq.com/notion`) or slugs, translating them to the canonical posting API.
- **Payload Extraction:**
  - `external_job_id`: Ashby UUID identifier.
  - `listing_url`: `jobUrl` permalink.
  - `isRemote`: Provider boolean remote indicator.
  - `compensation`: Explicit compensation tier summary if present.

### 3. Synthetic Test Connector (`SyntheticJobConnector`)
- **Adapter Slug:** `synthetic`
- **Methodology:** In-memory deterministic fixture generator for test suites and CI/CD without external network dependencies.
- **Capabilities:**
  - Generates realistic engineering, product, and design roles with HTML content and skill tags.
  - Includes explicit compensation testing and omitted compensation testing.
  - Fault injection testing: simulates transient network errors (`SIMULATE_TRANSIENT_ERROR`), authentication errors (`SIMULATE_AUTH_ERROR`), and degraded health probes (`SIMULATE_UNHEALTHY`).

---

## 3. Extensibility & Adding New Adapters

To integrate a new official ATS feed (e.g. Workday Public Feed or Lever API):
1. Subclass `BaseJobConnector` in `backend/app/services/connectors/<provider>.py`.
2. Implement `validate_config`, `check_health`, and `fetch_jobs`.
3. Register the connector instance in `backend/app/services/connectors/registry.py`.
4. Update `NormalizationService` provider-specific parsing rules in `backend/app/services/normalization_service.py`.
