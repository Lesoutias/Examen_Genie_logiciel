DROP PROCEDURE IF EXISTS sp_UpdateUser;

DELIMITER //

CREATE PROCEDURE sp_UpdateUser(
    IN p_user_id INT,
    IN p_full_name VARCHAR(255),
    IN p_phone_number VARCHAR(50),
    IN p_role VARCHAR(50)
)
BEGIN
    UPDATE users 
    SET full_name = p_full_name,
        phone_number = p_phone_number,
        role = p_role
    WHERE id = p_user_id;
END //

DELIMITER ;
