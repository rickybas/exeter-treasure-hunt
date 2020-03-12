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
        `course` VARCHAR(100),
        `year` VARCHAR(50),
        PRIMARY KEY (`username`)
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
    CREATE TABLE IF NOT EXISTS `recentLocationData`(
        `username` VARCHAR(50) NOT NULL,
        `lattitude` DECIMAL(10, 8) NOT NULL,
        `longitude` DECIMAL(11, 8) NOT NULL,
        `timeStamp` VARCHAR(50) NOT NULL,
        PRIMARY KEY(`username`)
    );
    CREATE TABLE IF NOT EXISTS `userCards`(
        `username` VARCHAR(50) NOT NULL,
        `cardLocation` VARCHAR(255) NOT NULL,
        `completedTimeStamp` TIMESTAMP,
        `state` VARCHAR(50) NOT NULL,
        PRIMARY KEY (`username`, `cardLocation`)
    );
END;
//
DELIMITER ;
CALL init();