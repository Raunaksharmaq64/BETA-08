# Core-to-LeadHunter Versioned API Contract

## Specification
- **Contract Codebase**: `contracts/leads/models.py`
- **Protocol**: HTTP/1.1 REST JSON
- **Base URL**: Environment variable `LEADHUNTER_BASE_URL` (default: `http://localhost:8001`)

## Contract Schemas
```python
class LeadDiscoveryRequest(BaseModel):
    query: str = Field(..., min_length=2)
    city: str = Field(..., min_length=2)
    max_results: int = Field(default=20, ge=1, le=100)
    include_with_website: bool = Field(default=False)
    deep_scan: bool = Field(default=True)

class LeadSummary(BaseModel):
    lead_id: str
    business_name: str
    category: str
    city: str
    website: Optional[str] = None
    is_broken_website: bool = False
    phone: Optional[str] = None
    email: Optional[str] = None
    rating: float = 0.0
    reviews_count: int = 0
    suggested_pitch: Optional[str] = None

class LeadDiscoveryResult(BaseModel):
    discovery_id: str
    leads: List[LeadSummary]
    total_leads: int
```

## Error Envelopes
LeadHunter errors conform to standard JSON responses (`{"success": false, "detail": "..."}`). The Core Adapter translates non-2xx status codes into typed domain exceptions (`LeadHunterUnavailableError`, `LeadHunterAuthError`).

