DROP DATABASE IF EXISTS USERS_DATABASE;
CREATE DATABASE USERS_DATABASE;
USE USERS_DATABASE;

DELIMITER //
CREATE PROCEDURE init()
    LANGUAGE SQL
BEGIN
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