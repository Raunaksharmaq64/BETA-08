# Provider Delivery Evidence & Tracking

## Overview
Outreach delivery status is only marked `SENT` or `DELIVERED` when confirmed by provider response evidence.

## Delivery States
- **`ACCEPTED`**: Provider accepted dispatch request into sending queue.
- **`SENT`**: Provider confirmed SMTP handshake or API transmission.
- **`DELIVERED`**: Webhook received from provider verifying inbox acceptance.
- **`BOUNCED`**: Provider reported hard or soft bounce.
- **`UNKNOWN`**: Delivery state unconfirmed.

## Schema (`OutreachDeliveryLogRecord`)
```python
class OutreachDeliveryLogRecord(Base):
    __tablename__ = "outreach_delivery_logs"
    id = Column(String(36), primary_key=True)
    draft_id = Column(String(36), ForeignKey("outreach_drafts.id"))
    provider = Column(String(50))  # SMTP, SENDGRID, RESEND, SIMULATED
    provider_message_id = Column(String(255))
    provider_response_code = Column(Integer)
    provider_raw_response = Column(Text)
    delivery_status = Column(String(30))
    webhook_verified = Column(Boolean, default=False)
    error_message = Column(Text)
    event_timestamp = Column(DateTime(timezone=True))
```

