#!/usr/bin/env bash
# ==============================================================================
# RIGHT FIT — Certbot Automated TLS Certificate Generation & Renewal Script
# ==============================================================================
set -euo pipefail

DOMAIN="${1:-rightfit.careers}"
EMAIL="${2:-admin@rightfit.careers}"
WEBROOT="/var/www/certbot"

echo "=== [TLS Management] Starting Certbot Certificate Check for ${DOMAIN} ==="

if [ ! -d "/etc/letsencrypt/live/${DOMAIN}" ]; then
    echo "No existing certificate found. Requesting initial certificate from Let's Encrypt..."
    certbot certonly --webroot -w "${WEBROOT}" \
        -d "${DOMAIN}" -d "www.${DOMAIN}" -d "api.${DOMAIN}" \
        --email "${EMAIL}" \
        --rsa-key-size 4096 \
        --agree-tos \
        --non-interactive
    
    echo "Linking certificates into Nginx path..."
    ln -sf "/etc/letsencrypt/live/${DOMAIN}/fullchain.pem" /etc/nginx/certs/fullchain.pem
    ln -sf "/etc/letsencrypt/live/${DOMAIN}/privkey.pem" /etc/nginx/certs/privkey.pem
else
    echo "Certificate exists. Running renewal check..."
    certbot renew --webroot -w "${WEBROOT}" --quiet
fi

echo "Reloading Nginx configuration..."
nginx -s reload
echo "=== [TLS Management] Completed successfully ==="

