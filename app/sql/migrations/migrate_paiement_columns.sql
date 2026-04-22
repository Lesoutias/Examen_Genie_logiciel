-- ============================================================
-- Migration : Add columns to `paiements`
-- Adds `created_at` and `date_paiement` if they don't exist.
-- ============================================================

-- ── created_at ───────────────────────────────────────────────
ALTER TABLE paiements
    ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP;

-- ── date_paiement ────────────────────────────────────────────
ALTER TABLE paiements
    ADD COLUMN date_paiement DATETIME DEFAULT CURRENT_TIMESTAMP;
