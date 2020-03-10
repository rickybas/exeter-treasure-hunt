-- USER DATABASE
DROP DATABASE IF EXISTS ETH_DATABASE;
CREATE DATABASE ETH_DATABASE;
USE ETH_DATABASE;

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

    CREATE TABLE IF NOT EXISTS `won`
    (
        `username` VARCHAR(50) NOT NULL,
        `cardLocation` VARCHAR(255) NOT NULL,
        `timeStamp` TIMESTAMP,
        PRIMARY KEY (`username`, `cardLocation`)
    );

    CREATE TABLE IF NOT EXISTS `helpRequests`
    (
        `id` int NOT NULL AUTO_INCREMENT,
        `username` VARCHAR(50) NOT NULL,
        `open` BOOL NOT NULL,
        `description` TEXT NOT NULL,
        `timeStamp` TIMESTAMP NOT NULL,
        PRIMARY KEY (`id`)
    );
END;
//
DELIMITER ;
CALL init();