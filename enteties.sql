-- MySQL Script generated by MySQL Workbench
-- Fri Nov 24 10:53:29 2017
-- Model: New Model    Version: 1.0
-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- -----------------------------------------------------
-- Schema enteties
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema enteties
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `enteties` DEFAULT CHARACTER SET utf8 ;
USE `enteties` ;

-- -----------------------------------------------------
-- Table `enteties`.`persons`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `enteties`.`persons` ;

CREATE TABLE IF NOT EXISTS `enteties`.`persons` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NOT NULL,
  `email` VARCHAR(45) NOT NULL,
  `phone` VARCHAR(45) NOT NULL,
  `lastUpdate` TIMESTAMP  NOT NULL,
  `number` VARCHAR(45) NOT NULL,
  `password` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `enteties`.`teachers`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `enteties`.`teachers` ;

CREATE TABLE IF NOT EXISTS `enteties`.`teachers` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `Person_id` INT NOT NULL,
  `lastUpdate` TIMESTAMP  NOT NULL,
  PRIMARY KEY (`id`, `Person_id`),
  INDEX `fk_Teacher_Person_idx` (`Person_id` ASC),
  CONSTRAINT `fk_Teacher_Person`
    FOREIGN KEY (`Person_id`)
    REFERENCES `enteties`.`persons` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `enteties`.`students`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `enteties`.`students` ;

CREATE TABLE IF NOT EXISTS `enteties`.`students` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `Person_id` INT NOT NULL,
  `lastUpdate` TIMESTAMP  NOT NULL,
  PRIMARY KEY (`id`, `Person_id`),
  INDEX `fk_Student_Person1_idx` (`Person_id` ASC),
  CONSTRAINT `fk_Student_Person1`
    FOREIGN KEY (`Person_id`)
    REFERENCES `enteties`.`persons` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `enteties`.`rooms`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `enteties`.`rooms` ;

CREATE TABLE IF NOT EXISTS `enteties`.`rooms` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `number` VARCHAR(45) NOT NULL,
  `number_places` VARCHAR(45) NOT NULL,
  `description` VARCHAR(45) NOT NULL,
  `lastUpdate` TIMESTAMP  NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `enteties`.`persons_has_rooms`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `enteties`.`persons_has_rooms` ;

CREATE TABLE IF NOT EXISTS `enteties`.`persons_has_rooms` (
  `persons_id` INT NULL,
  `rooms_id` INT NULL,
  INDEX `fk_persons_has_rooms_rooms1_idx` (`rooms_id` ASC),
  INDEX `fk_persons_has_rooms_persons1_idx` (`persons_id` ASC),
  CONSTRAINT `fk_persons_has_rooms_persons1`
    FOREIGN KEY (`persons_id`)
    REFERENCES `enteties`.`persons` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_persons_has_rooms_rooms1`
    FOREIGN KEY (`rooms_id`)
    REFERENCES `enteties`.`rooms` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `enteties`.`employees`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `enteties`.`employees` ;

CREATE TABLE IF NOT EXISTS `enteties`.`employees` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `role` VARCHAR(45) NOT NULL,
  `persons_id` INT NOT NULL,
  `lastUpdate` TIMESTAMP  NOT NULL,
  PRIMARY KEY (`id`, `persons_id`),
  INDEX `fk_employees_persons1_idx` (`persons_id` ASC),
  CONSTRAINT `fk_employees_persons1`
    FOREIGN KEY (`persons_id`)
    REFERENCES `enteties`.`persons` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
