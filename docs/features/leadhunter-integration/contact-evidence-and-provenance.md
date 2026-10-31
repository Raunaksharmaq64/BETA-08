# Contact Evidence & Provenance Model

## Overview
Every contact channel (email, phone number, website link, social handle) discovered during lead scraping is audited in the `contact_evidence` table.

## Evidence Status Hierarchy
1. **`VERIFIED`**: Validated by active technical probe (e.g. website returned HTTP 200 and valid SSL certificate, or MX record validated).
2. **`OBSERVED`**: Directly extracted from a public primary listing (e.g. Google Maps phone number, meta tag email).
3. **`INFERRED`**: Pattern-matched from employee names and domain syntax (e.g. `first.last@company.com`).
4. **`INVALID`**: Technical failure (e.g. website returned DNS `NXDOMAIN` or SSL handshake expired).
5. **`UNVERIFIED`**: Unchecked discovery.
6. **`UNKNOWN`**: Verification status undetermined.

## Schema (`ContactEvidenceRecord`)
```python
class ContactEvidenceRecord(Base):
    __tablename__ = "contact_evidence"
    id = Column(String(36), primary_key=True)
    opportunity_id = Column(String(36), ForeignKey("freelance_opportunities.id"))
    contact_type = Column(String(30))  # EMAIL, PHONE, WEBSITE, etc.
    contact_value = Column(String(255))
    source = Column(String(60), default="leadhunter")
    evidence_status = Column(String(30))
    verification_method = Column(String(60))
    verification_notes = Column(Text)
    discovered_at = Column(DateTime(timezone=True))
    verified_at = Column(DateTime(timezone=True))
```

