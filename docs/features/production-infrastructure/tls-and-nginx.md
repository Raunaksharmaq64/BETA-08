# TLS, Domain & Nginx Ingress Architecture

## 1. Edge Proxy Configuration
Nginx operates as the edge reverse proxy and SSL termination point.
- **Port 80**: Listens for HTTP traffic, serves ACME challenges (`/.well-known/acme-challenge/`), and issues 301 permanent redirects to `https://$host$request_uri`.
- **Port 443**: Terminates TLSv1.2 and TLSv1.3 with modern Mozilla Intermediate ciphers.
- **Reverse Proxy Routing**:
  - `/` &rarr; `http://frontend:3000` (Next.js 16 Web Application)
  - `/api/` &rarr; `http://backend:8000` (FastAPI Core Engine)
  - `/healthz` &rarr; Returns HTTP 200 JSON probe for AWS ALB health check.
- **Internal Satellites**: `service-leadhunter:8001` and `service-startup-intelligence:8002` are **NOT exposed via Nginx location blocks**.

## 2. Hardened Security Headers
All HTTPS responses include:
```nginx
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;
```

## 3. Rate Limiting Zones
- General API endpoints: `30 requests/second` per client IP (`limit_req_zone $binary_remote_addr zone=api_limit:10m rate=30r/s; burst=25 nodelay;`).
- Authentication endpoints (`/api/v1/auth/`): `5 requests/second` per client IP (`burst=5 nodelay;`) to protect against brute force attacks.

