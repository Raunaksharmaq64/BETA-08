#!/usr/bin/env bash
# Generates local fallback self-signed TLS certificates for development/staging verification
mkdir -p infrastructure/nginx/certs
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout infrastructure/nginx/certs/privkey.pem \
    -out infrastructure/nginx/certs/fullchain.pem \
    -subj "/C=US/ST=California/L=SanFrancisco/O=RightFit/CN=localhost"
echo "Generated self-signed certs in infrastructure/nginx/certs/"

