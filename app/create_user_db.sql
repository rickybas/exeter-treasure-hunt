DROP DATABASE IF EXISTS USERS_DATABASE;
CREATE DATABASE USERS_DATABASE;
USE USERS_DATABASE;

DELIMITER //
CREATE PROCEDURE init()
    LANGUAGE SQL
BEGIN
    DECLARE user_exist INT;
    SET user_exist = (SELECT EXISTS(SELECT DISTINCT user FROM mysql.user WHERE user = "eth_user"));
    IF user_exist = 0 THEN
        CREATE USER 'eth_user'@'localhost' IDENTIFIED BY 'Eth_pass124.';
        GRANT ALL PRIVILEGES ON USERS_DATABASE.* TO 'eth_user'@'localhost';
        FLUSH PRIVILEGES;
    END IF;

    CREATE TABLE IF NOT EXISTS `users`
    (
        `username` VARCHAR(50)  NOT NULL,
        `password` VARCHAR(255) NOT NULL,
        PRIMARY KEY (`username`)
    );

    INSERT INTO users
    VALUES ('lsnb201', 'football'),
           ('ricky', 'tennis');
END;
//
DELIMITER ;
CALL init();