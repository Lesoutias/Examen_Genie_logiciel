-- ============================================================
-- Migration : Onboarding columns for `users`
-- Adds `role` and `phone_number` columns if they don't exist.
-- ============================================================

-- ── role ─────────────────────────────────────────────────────
ALTER TABLE users ADD COLUMN role VARCHAR(50);

-- ── phone_number ─────────────────────────────────────────────
ALTER TABLE users ADD COLUMN phone_number VARCHAR(50);
