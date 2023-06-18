-- MySQL dump 10.13  Distrib 8.0.32, for Win64 (x86_64)
--
-- Host: localhost    Database: poker
-- ------------------------------------------------------
-- Server version	8.0.32

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `chip_case`
--

DROP TABLE IF EXISTS `chip_case`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `chip_case` (
  `Case_id` int unsigned NOT NULL,
  `Game_id` int unsigned NOT NULL,
  `Total_value` decimal(11,2) NOT NULL DEFAULT ((((((`Green_chips_amount` * `Green_chips_value`) + (`White_chips_amount` * `White_chips_value`)) + (`Red_chips_amount` * `Red_chips_value`)) + (`Blue_chips_amount` * `Blue_chips_value`)) + (`Black_chips_amount` * `Black_chips_value`))),
  `Current_value` decimal(11,2) NOT NULL DEFAULT '0.00',
  `Green_chips_amount` int unsigned NOT NULL DEFAULT '0',
  `Green_chips_value` decimal(11,2) NOT NULL DEFAULT '0.00',
  `White_chips_amount` int unsigned NOT NULL DEFAULT '0',
  `White_chips_value` decimal(11,2) NOT NULL DEFAULT '0.00',
  `Red_chips_amount` int unsigned NOT NULL DEFAULT '0',
  `Red_chips_value` decimal(11,2) NOT NULL DEFAULT '0.00',
  `Blue_chips_amount` int unsigned NOT NULL DEFAULT '0',
  `Blue_chips_value` decimal(11,2) NOT NULL DEFAULT '0.00',
  `Black_chips_amount` int unsigned NOT NULL DEFAULT '0',
  `Black_chips_value` decimal(11,2) NOT NULL DEFAULT '0.00',
  PRIMARY KEY (`Case_id`),
  UNIQUE KEY `Case_id_UNIQUE` (`Case_id`),
  UNIQUE KEY `Game_id_UNIQUE` (`Game_id`),
  CONSTRAINT `fk_chip_case_to_game` FOREIGN KEY (`Game_id`) REFERENCES `game` (`Game_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `chip_case`
--

LOCK TABLES `chip_case` WRITE;
/*!40000 ALTER TABLE `chip_case` DISABLE KEYS */;
/*!40000 ALTER TABLE `chip_case` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `debt`
--

DROP TABLE IF EXISTS `debt`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `debt` (
  `Debt_id` int unsigned NOT NULL,
  `Debtor_id` int unsigned NOT NULL,
  `Creditor_id` int unsigned NOT NULL,
  `Debt_amount` decimal(11,2) NOT NULL,
  `Date_created` date DEFAULT NULL,
  `Time_created` time DEFAULT NULL,
  PRIMARY KEY (`Debt_id`),
  UNIQUE KEY `Debt_id_UNIQUE` (`Debt_id`),
  KEY `fk_debt_debtor_id_to_player` (`Debtor_id`),
  KEY `fk_debt_creditor_id_to_player` (`Creditor_id`),
  CONSTRAINT `fk_debt_creditor_id_to_player` FOREIGN KEY (`Creditor_id`) REFERENCES `player` (`Player_id`),
  CONSTRAINT `fk_debt_debtor_id_to_player` FOREIGN KEY (`Debtor_id`) REFERENCES `player` (`Player_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `debt`
--

LOCK TABLES `debt` WRITE;
/*!40000 ALTER TABLE `debt` DISABLE KEYS */;
/*!40000 ALTER TABLE `debt` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `game`
--

DROP TABLE IF EXISTS `game`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `game` (
  `Game_id` int unsigned NOT NULL,
  `Game_name` varchar(45) NOT NULL,
  `Join_code` int unsigned NOT NULL,
  `Date` date NOT NULL,
  `Start_time` time NOT NULL,
  `Stop_time` time DEFAULT NULL,
  `Min_buyin` decimal(11,2) unsigned NOT NULL,
  `Max_buyin` decimal(11,2) unsigned NOT NULL,
  `Small_blind` decimal(11,2) unsigned NOT NULL,
  `Big_blind` decimal(11,2) unsigned NOT NULL,
  PRIMARY KEY (`Game_id`),
  UNIQUE KEY `Game_id_UNIQUE` (`Game_id`),
  UNIQUE KEY `Join_code_UNIQUE` (`Join_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `game`
--

LOCK TABLES `game` WRITE;
/*!40000 ALTER TABLE `game` DISABLE KEYS */;
/*!40000 ALTER TABLE `game` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `host`
--

DROP TABLE IF EXISTS `host`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `host` (
  `Host_id` int unsigned NOT NULL,
  `Game_id` int unsigned NOT NULL,
  `First_name` varchar(45) NOT NULL,
  `Last_name` varchar(45) NOT NULL,
  PRIMARY KEY (`Host_id`),
  UNIQUE KEY `Host_id_UNIQUE` (`Host_id`),
  UNIQUE KEY `Game_id_UNIQUE` (`Game_id`),
  CONSTRAINT `fk_host_to_game` FOREIGN KEY (`Game_id`) REFERENCES `game` (`Game_id`),
  CONSTRAINT `fk_host_to_player` FOREIGN KEY (`Host_id`) REFERENCES `player` (`Player_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `host`
--

LOCK TABLES `host` WRITE;
/*!40000 ALTER TABLE `host` DISABLE KEYS */;
/*!40000 ALTER TABLE `host` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `participates_in`
--

DROP TABLE IF EXISTS `participates_in`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `participates_in` (
  `Player_id` int unsigned NOT NULL,
  `Game_id` int unsigned NOT NULL,
  `Buyin_amount` decimal(11,2) unsigned DEFAULT '0.00',
  `Cashout_amount` decimal(11,2) unsigned DEFAULT '0.00',
  `Num_buyins` int unsigned DEFAULT '0',
  `Num_cashouts` int unsigned DEFAULT '0',
  `Currently_playing` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`Player_id`,`Game_id`),
  UNIQUE KEY `Player_id_UNIQUE` (`Player_id`),
  KEY `fk_participates_in_to_game_idx` (`Game_id`),
  CONSTRAINT `fk_participates_in_player_id_to_player` FOREIGN KEY (`Player_id`) REFERENCES `player` (`Player_id`),
  CONSTRAINT `fk_participates_in_to_game` FOREIGN KEY (`Game_id`) REFERENCES `game` (`Game_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `participates_in`
--

LOCK TABLES `participates_in` WRITE;
/*!40000 ALTER TABLE `participates_in` DISABLE KEYS */;
/*!40000 ALTER TABLE `participates_in` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `player`
--

DROP TABLE IF EXISTS `player`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `player` (
  `Player_id` int unsigned NOT NULL,
  `Username` varchar(45) NOT NULL,
  `Password` varchar(45) NOT NULL,
  `First_name` varchar(45) NOT NULL,
  `Last_name` varchar(45) NOT NULL,
  `Games_played` int unsigned DEFAULT '0',
  `Games_won` int unsigned DEFAULT '0',
  `Games_lost` int unsigned DEFAULT '0',
  `Total_debt` decimal(11,2) DEFAULT '0.00',
  `Total_buyin_amount` decimal(11,2) DEFAULT '0.00',
  `Total_cashout_amount` decimal(11,2) DEFAULT '0.00',
  `Win_percentage` decimal(5,2) GENERATED ALWAYS AS (if(((`Games_won` = 0.0) or (`Games_lost` = 0.0)),0,((`Games_won` / (`Games_won` + `Games_lost`)) * 100))) VIRTUAL,
  `Earnings_per_buyin` decimal(11,2) GENERATED ALWAYS AS (if((`Total_buyin_amount` = 0),0,((`Total_cashout_amount` - `Total_buyin_amount`) / `Total_buyin_amount`))) VIRTUAL,
  PRIMARY KEY (`Player_id`,`Username`),
  UNIQUE KEY `Player_id_UNIQUE` (`Player_id`),
  UNIQUE KEY `username_UNIQUE` (`Username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `player`
--

LOCK TABLES `player` WRITE;
/*!40000 ALTER TABLE `player` DISABLE KEYS */;
INSERT INTO `player` (`Player_id`, `Username`, `Password`, `First_name`, `Last_name`, `Games_played`, `Games_won`, `Games_lost`, `Total_debt`, `Total_buyin_amount`, `Total_cashout_amount`) VALUES (1,'admin','password','first','last',0,0,0,0.00,0.00,0.00),(650495581,'willt','password','will','t',0,0,0,0.00,0.00,0.00);
/*!40000 ALTER TABLE `player` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `prize_pool`
--

DROP TABLE IF EXISTS `prize_pool`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `prize_pool` (
  `Pool_id` int unsigned NOT NULL,
  `Game_id` int unsigned NOT NULL,
  `Total_value` decimal(11,2) NOT NULL DEFAULT '0.00',
  PRIMARY KEY (`Pool_id`),
  UNIQUE KEY `Pool_id_UNIQUE` (`Pool_id`),
  UNIQUE KEY `Game_id_UNIQUE` (`Game_id`),
  CONSTRAINT `fk_prize_pool_to_game` FOREIGN KEY (`Game_id`) REFERENCES `game` (`Game_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `prize_pool`
--

LOCK TABLES `prize_pool` WRITE;
/*!40000 ALTER TABLE `prize_pool` DISABLE KEYS */;
/*!40000 ALTER TABLE `prize_pool` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-05-05  9:42:55
