# Market Intelligence API Contracts

## 1. Base URL
All endpoints are versioned under:
```
/api/v1/market
```

## 2. Endpoints Catalog

### `GET /api/v1/market/skills`
- **Description**: Returns list of canonical skills with optional filtering.
- **Query Parameters**:
  - `query` (string, optional): Search keyword.
  - `category` (string, optional): Taxonomy category.
  - `technology_family` (string, optional): Technology grouping.
  - `limit` (integer, default: 50): Max items.
  - `offset` (integer, default: 0): Pagination offset.
- **Response**: Array of canonical skill objects.

### `GET /api/v1/market/skills/resolve`
- **Description**: Deterministically resolves an input alias or synonym to its canonical skill.
- **Query Parameters**:
  - `alias` (string, required): Term to resolve (e.g. `k8s`, `js`).
- **Response**:
  ```json
  {
    "canonical_skill_id": "uuid",
    "canonical_name": "Kubernetes",
    "slug": "kubernetes",
    "category": "INFRASTRUCTURE",
    "confidence": 1.0,
    "is_alias": true
  }
  ```

### `GET /api/v1/market/skills/{skill_id_or_slug}`
- **Description**: Returns full detail for a skill node, including aliases, snapshots, and methodology.

### `GET /api/v1/market/demand/skills`
- **Description**: Returns time-windowed aggregated demand for canonical skills.
- **Query Parameters**:
  - `time_window` (string, default: `30d`): Options: `7d`, `30d`, `90d`.
  - `role_category` (string, default: `ALL`).
  - `geography` (string, default: `ALL`).
  - `limit` (integer, default: 50).
- **Response**:
  ```json
  {
    "time_window": "30d",
    "sample_size": 24,
    "distinct_employers": 16,
    "skills": [
      {
        "canonical_name": "Python",
        "slug": "python",
        "category": "PROGRAMMING_LANGUAGE",
        "distinct_job_count": 18,
        "frequency_pct": 75.0,
        "trend_direction": "RISING",
        "confidence": "HIGH"
      }
    ],
    "confidence_level": "HIGH",
    "methodology": "Distinct job opportunity counting over audited vacancies."
  }
  ```

### `GET /api/v1/market/compensation`
- **Description**: Returns audited compensation benchmarks and observation records.
- **Query Parameters**:
  - `role_title` (string, optional).
  - `role_category` (string, default: `ALL`).
  - `geography` (string, default: `ALL`).
  - `experience_level` (string, default: `ALL`).
  - `compensation_type` (string, default: `BASE_SALARY`).
  - `currency` (string, default: `USD`).
- **Response**:
  ```json
  {
    "role_category": "ALL",
    "compensation_type": "BASE_SALARY",
    "currency": "USD",
    "sample_size": 8,
    "has_statistically_justified_median": true,
    "median": 165000.0,
    "min": 140000.0,
    "max": 195000.0,
    "p25": 150000.0,
    "p75": 180000.0,
    "missing_compensation_rate": 0.2,
    "observations": [...]
  }
  ```

### `GET /api/v1/market/skill-gaps`
- **Description**: Authenticated endpoint returning personalized skill-gap diagnostics.
- **Query Parameters**:
  - `target_role` (string, default: `Software Engineer`).
  - `time_window` (string, default: `30d`).
- **Headers**: Authorization Cookie / Bearer Token.

### `POST /api/v1/market/skill-gaps/{recommendation_id}/status`
- **Description**: Updates candidate's learning status for a gap recommendation.
- **Body**:
  ```json
  {
    "status": "ALREADY_LEARNING"
  }
  ```

### `GET /api/v1/market/sources`
- **Description**: Returns all registered data sources.

### `GET /api/v1/market/methodology`
- **Description**: Returns audit disclosure and integrity guarantees.

