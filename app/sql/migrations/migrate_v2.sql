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
