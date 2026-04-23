-- ============================================================
-- Migration V2
-- 1. Add `status` column to `users`
-- 2. Create stored procedure sp_UpdateUser
-- ============================================================

-- ── Step 1 : Add status column ──────────────────────────────
-- Check if column already exists before running (MySQL 5.7+)
-- In MySQL 8+ you can use: ALTER TABLE users ADD COLUMN IF NOT EXISTS ...

ALTER TABLE users ADD COLUMN status VARCHAR(50) DEFAULT 'en attente';

-- Backfill existing rows to 'valide'
UPDATE users SET status = 'valide';


-- ── Step 2 : Stored Procedure sp_UpdateUser ─────────────────
DROP PROCEDURE IF EXISTS sp_UpdateUser;

DELIMITER //

CREATE PROCEDURE sp_UpdateUser(
    IN p_user_id    INT,
    IN p_full_name  VARCHAR(255),
    IN p_phone_number VARCHAR(50),
    IN p_role       VARCHAR(50)
)
BEGIN
    UPDATE users
    SET full_name    = p_full_name,
        phone_number = p_phone_number,
        role         = p_role
    WHERE id = p_user_id;
END //

DELIMITER ;

-- ── Step 3 : Stored Procedure sp_update_taxe ─────────────────
DROP PROCEDURE IF EXISTS sp_update_taxe;

DELIMITER //

CREATE PROCEDURE sp_update_taxe(
    IN p_id INT,
    IN p_nom VARCHAR(255),
    IN p_montant_base FLOAT,
    IN p_frequence VARCHAR(255),
    IN p_description TEXT,
    IN p_prix_libre BOOLEAN
)
BEGIN
    UPDATE taxes
    SET
        nom = p_nom,
        montant_base = p_montant_base,
        frequence = p_frequence,
        description = p_description,
        prix_libre = p_prix_libre
    WHERE id = p_id;
END //

DELIMITER ;

-- Vérifier que les procédures ont bien été créées
SHOW PROCEDURE STATUS WHERE Db = DATABASE();
