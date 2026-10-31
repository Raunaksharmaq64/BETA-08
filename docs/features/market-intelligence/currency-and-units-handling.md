# Currency and Units Handling

## 1. Native Currency Preservation
A frequent defect in commercial compensation tools is automatic cross-currency translation using volatile spot exchange rates or purchasing power parity (PPP) approximations without user knowledge.
- **Rule of Preservation**: RIGHT FIT strictly stores and displays compensation in its original currency of record (e.g. `USD`, `EUR`, `GBP`, `INR`).
- **No Silent Blending**: An observation of €120,000 in Berlin is never converted to \$131,000 and blended into a US dataset without explicit, documented user selection.
- **Currency Isolation in Benchmarks**: All calculations (medians, percentiles, min/max) are filtered by currency (`WHERE currency = :currency`).

## 2. Pay Frequency and Time Units
Compensation disclosures arrive in varying units depending on opportunity type:
- **Annual**: Standard for salaried full-time roles (e.g. \$160,000 / year).
- **Monthly**: Common in European and Asian markets (e.g. €6,500 / month, ₹2,50,000 / month).
- **Hourly / Daily**: Standard for freelance, contract, and advisory roles (e.g. \$95 / hour).

### Normalization Constraints:
- Annualized benchmarks only evaluate salaried observations normalized to an annualized base ($12 \times \text{monthly}$).
- Hourly and contract observations are classified strictly under `compensation_type = 'CONTRACT_HOURLY'` and are never multiplied by 2,080 hours to simulate a salaried base, preserving candidate transparency regarding lack of paid leave or benefits.

