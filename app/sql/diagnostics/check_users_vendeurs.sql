-- ============================================================
-- Diagnostic : Inspect users and vendeurs
-- ============================================================

-- ── Users ─────────────────────────────────────────────────────
SELECT id, email, role, vendeur_id FROM users;

-- ── Vendeurs ──────────────────────────────────────────────────
SELECT id, nom, prenom, telephone FROM vendeurs;
