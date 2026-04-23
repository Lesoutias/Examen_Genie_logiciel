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
