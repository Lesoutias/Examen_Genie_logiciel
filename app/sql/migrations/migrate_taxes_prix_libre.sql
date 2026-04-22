-- ============================================================
-- Migration : Add prix_libre column to taxes
-- Supports "Occasionnel" taxes with agent-defined prices
-- ============================================================

ALTER TABLE taxes
    ADD COLUMN prix_libre BOOLEAN NOT NULL DEFAULT 0;
