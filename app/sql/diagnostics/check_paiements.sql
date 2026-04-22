-- ============================================================
-- Diagnostic : Quick inspection of paiements, taxes, vendeurs
-- ============================================================

-- ── Paiements ─────────────────────────────────────────────────
SELECT * FROM paiements LIMIT 10;

-- ── Taxes ─────────────────────────────────────────────────────
SELECT * FROM taxes LIMIT 10;

-- ── Vendeurs ──────────────────────────────────────────────────
SELECT id, nom, prenom FROM vendeurs LIMIT 10;
