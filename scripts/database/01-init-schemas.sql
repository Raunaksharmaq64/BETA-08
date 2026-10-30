-- ==============================================================================
-- RIGHT FIT — Multi-Schema Local Database Initialization Script
-- Executed automatically on first PostgreSQL container startup
-- ==============================================================================

-- 1. Create Core Career Engine Schema
CREATE SCHEMA IF NOT EXISTS career_core;
COMMENT ON SCHEMA career_core IS 'Core Career Engine schema: users, profiles, resumes, matches, applications';

-- 2. Create LeadHunter AI Schema
CREATE SCHEMA IF NOT EXISTS leadhunter_db;
COMMENT ON SCHEMA leadhunter_db IS 'LeadHunter AI satellite schema: business directory, website audits, outreach history';

-- 3. Create Startup Intelligence Schema
CREATE SCHEMA IF NOT EXISTS startup_intel_db;
COMMENT ON SCHEMA startup_intel_db IS 'Startup Intelligence satellite schema: community signals, bottlenecks, founder tracking';

-- Enable uuid-ossp and pg_trgm extensions if available
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

