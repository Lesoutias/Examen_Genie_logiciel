-- ============================================================
-- Migration : Add `vendeur_id` FK column to `users`
-- ============================================================

ALTER TABLE users
    ADD COLUMN vendeur_id INTEGER REFERENCES vendeurs(id);
