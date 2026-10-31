# Suppression Lists & Rate Limiting Controls

## Overview
To prevent harassment, protect candidate sender reputation, and comply with CAN-SPAM and GDPR, strict suppression and throttling rules govern outreach.

## Suppression Rules
1. **Global & Candidate Suppression**:
   Any contact added to `outreach_suppression_list` is immediately blocked from receiving any messages.
   Attempts to send return HTTP 403 Forbidden: `"Recipient is on the suppression list."`
2. **Frequency Cap**:
   Maximum 1 outreach message per recipient in a 14-day rolling window.
3. **Daily Candidate Sending Quota**:
   Maximum 20 dispatched messages per candidate per 24 hours. Exceeding this quota blocks further sends until the rolling window resets.

