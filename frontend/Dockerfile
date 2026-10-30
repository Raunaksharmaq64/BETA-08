# ==============================================================================
# RIGHT FIT — Frontend Dockerfile (Next.js 16)
# STATUS: TEMPLATE / ARCHITECTURE SETUP PHASE (NOT FINALIZED FOR PRODUCTION RUN)
# ==============================================================================

# Stage 1: Dependencies installation
FROM node:20-alpine AS deps
WORKDIR /app
# Check https://github.com/nodejs/docker-node/tree/b4117f9333da4138b03a546ec926ef50a31506c3#nodealpine to understand why libc6-compat might be needed.
RUN apk add --no-cache libc6-compat
# In active development: COPY package.json package-lock.json ./
# RUN npm ci

# Stage 2: Source builder
FROM node:20-alpine AS builder
WORKDIR /app
# COPY --from=deps /app/node_modules ./node_modules
# COPY . .
# RUN npm run build

# Stage 3: Production runner
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

USER nextjs

EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Placeholder entrypoint for foundation phase
CMD ["echo", "[TEMPLATE] Next.js 16 container runner placeholder"]

