-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: job_recruitment_db
-- ------------------------------------------------------
-- Server version	9.3.0

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
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) COLLATE utf8mb4_vi_0900_as_cs NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_vi_0900_as_cs;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
INSERT INTO `alembic_version` VALUES ('35c0ae97ccfa');
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `application`
--

DROP TABLE IF EXISTS `application`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `application` (
  `id` int NOT NULL AUTO_INCREMENT,
  `cv_id` int NOT NULL,
  `post_id` int NOT NULL,
  `applied_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `status` enum('RECEIVED','INTERVIEW','APPROVED','REJECT') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'RECEIVED',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_app_cv_post` (`cv_id`,`post_id`),
  KEY `fk_app_post` (`post_id`),
  CONSTRAINT `fk_app_cv` FOREIGN KEY (`cv_id`) REFERENCES `cv` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_app_post` FOREIGN KEY (`post_id`) REFERENCES `post` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `application`
--

LOCK TABLES `application` WRITE;
/*!40000 ALTER TABLE `application` DISABLE KEYS */;
INSERT INTO `application` VALUES (1,1,1,'2026-04-19 08:30:04','RECEIVED'),(2,2,1,'2026-04-19 08:30:04','INTERVIEW'),(3,3,2,'2026-04-19 08:30:04','RECEIVED'),(4,4,3,'2026-04-19 08:30:04','REJECT'),(5,5,4,'2026-04-19 08:30:04','RECEIVED'),(6,6,5,'2026-04-19 08:30:04','INTERVIEW'),(7,7,6,'2026-04-19 08:30:04','RECEIVED'),(8,8,7,'2026-04-19 08:30:04','REJECT'),(9,9,8,'2026-04-19 08:30:04','RECEIVED'),(10,10,9,'2026-04-19 08:30:04','INTERVIEW'),(11,1,3,'2026-04-19 08:30:04','RECEIVED'),(12,2,4,'2026-04-19 08:30:04','REJECT'),(13,3,5,'2026-04-19 08:30:04','INTERVIEW'),(14,4,6,'2026-04-19 08:30:04','RECEIVED'),(15,5,7,'2026-04-19 08:30:04','REJECT'),(16,6,8,'2026-04-19 08:30:04','RECEIVED'),(17,7,9,'2026-04-19 08:30:04','INTERVIEW'),(18,8,10,'2026-04-19 08:30:04','RECEIVED'),(19,9,2,'2026-04-19 08:30:04','REJECT'),(20,10,1,'2026-04-19 08:30:04','RECEIVED');
/*!40000 ALTER TABLE `application` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `company`
--

DROP TABLE IF EXISTS `company`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `company` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `location` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `website` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `establish_date` date DEFAULT NULL,
  `scale` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `tax_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `is_approved` tinyint(1) DEFAULT '0',
  `avatar_url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `business_license` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `tax_code` (`tax_code`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `company`
--

LOCK TABLES `company` WRITE;
/*!40000 ALTER TABLE `company` DISABLE KEYS */;
INSERT INTO `company` VALUES (1,'Interspace Vietnam','HCM','https://interspace.vn','2015-06-01','150','TAX001','Ads platform',1,NULL,''),(2,'FPT Software','Hanoi','https://fpt.com','2000-01-01','1000','TAX002','Outsourcing',1,NULL,''),(3,'VNG Corp','HCM','https://vng.com','2004-09-09','2000','TAX003','Tech company',1,NULL,''),(4,'Tiki','HCM','https://tiki.vn','2010-01-01','800','TAX004','Ecommerce',1,NULL,''),(5,'Shopee','HCM','https://shopee.vn','2015-01-01','3000','TAX005','Ecommerce',1,NULL,''),(6,'khong biet','Ho Chi Minh','',NULL,'1','123',NULL,0,NULL,'pending'),(7,'abc','TP. Hồ Chí Minh','',NULL,'1-50 nhân viên','1921282399',NULL,0,NULL,'Job5ing_ERD_Update_1.png');
/*!40000 ALTER TABLE `company` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cv`
--

DROP TABLE IF EXISTS `cv`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cv` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `summary` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `education` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `skills` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `experience` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `cv_url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `last_modified` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `cv_content` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`),
  KEY `fk_cv_user` (`user_id`),
  CONSTRAINT `fk_cv_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cv`
--

LOCK TABLES `cv` WRITE;
/*!40000 ALTER TABLE `cv` DISABLE KEYS */;
INSERT INTO `cv` VALUES (1,4,'Java Dev',NULL,NULL,'Java, Spring','Fresher',NULL,'2026-04-19 08:29:51','2026-04-19 08:29:51',NULL),(2,5,'Backend Dev',NULL,NULL,'NodeJS, SQL','1 year',NULL,'2026-04-19 08:29:51','2026-04-19 08:29:51',NULL),(3,6,'Fullstack',NULL,NULL,'React, Node','Intern',NULL,'2026-04-19 08:29:51','2026-04-19 08:29:51',NULL),(4,7,'Data Analyst',NULL,NULL,'SQL, Python','Fresher',NULL,'2026-04-19 08:29:51','2026-04-19 08:29:51',NULL),(5,8,'Java Dev',NULL,NULL,'Spring Boot, MySQL','1 year',NULL,'2026-04-19 08:29:51','2026-04-19 08:29:51',NULL),(6,9,'Frontend',NULL,NULL,'HTML, CSS, JS','Intern',NULL,'2026-04-19 08:29:51','2026-04-19 08:29:51',NULL),(7,10,'DevOps',NULL,NULL,'Docker, AWS','Fresher',NULL,'2026-04-19 08:29:51','2026-04-19 08:29:51',NULL),(8,11,'Mobile Dev',NULL,NULL,'Flutter','Intern',NULL,'2026-04-19 08:29:51','2026-04-19 08:29:51',NULL),(9,12,'QA Tester',NULL,NULL,'Manual Test','Fresher',NULL,'2026-04-19 08:29:51','2026-04-19 08:29:51',NULL),(10,13,'Backend',NULL,NULL,'Java, Microservice','2 years',NULL,'2026-04-19 08:29:51','2026-04-19 08:29:51',NULL);
/*!40000 ALTER TABLE `cv` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notification`
--

DROP TABLE IF EXISTS `notification`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notification` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `type` enum('APPLICATION_STATUS_CHANGED','INTERVIEW_INVITATION','NEW_APPLICATION','ACCOUNT_APPROVED','POST_BLOCKED') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `is_read` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `fk_noti_user` (`user_id`),
  CONSTRAINT `fk_noti_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notification`
--

LOCK TABLES `notification` WRITE;
/*!40000 ALTER TABLE `notification` DISABLE KEYS */;
INSERT INTO `notification` VALUES (1,4,'Application received','NEW_APPLICATION','2026-04-19 08:30:13',0),(2,5,'Interview invitation','INTERVIEW_INVITATION','2026-04-19 08:30:13',0),(3,6,'Application rejected','APPLICATION_STATUS_CHANGED','2026-04-19 08:30:13',0),(4,7,'New job posted','NEW_APPLICATION','2026-04-19 08:30:13',0),(5,8,'Interview invitation','INTERVIEW_INVITATION','2026-04-19 08:30:13',0),(6,9,'Application approved','APPLICATION_STATUS_CHANGED','2026-04-19 08:30:13',0),(7,10,'Account approved','ACCOUNT_APPROVED','2026-04-19 08:30:13',0),(8,11,'Application received','NEW_APPLICATION','2026-04-19 08:30:13',0),(9,12,'Post blocked','POST_BLOCKED','2026-04-19 08:30:13',0),(10,13,'Interview invitation','INTERVIEW_INVITATION','2026-04-19 08:30:13',0),(11,14,'Application rejected','APPLICATION_STATUS_CHANGED','2026-04-19 08:30:13',0),(12,15,'Application received','NEW_APPLICATION','2026-04-19 08:30:13',0);
/*!40000 ALTER TABLE `notification` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `post`
--

DROP TABLE IF EXISTS `post`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `post` (
  `id` int NOT NULL AUTO_INCREMENT,
  `recruiter_id` int NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `skills` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `experience` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `salary_range` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `deadline` date DEFAULT NULL,
  `status` enum('ACTIVE','OVERDUE','CLOSED','PINNED','BLOCKED') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'ACTIVE',
  `is_reported` tinyint(1) DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `last_modified` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_post_recruiter` (`recruiter_id`),
  CONSTRAINT `fk_post_recruiter` FOREIGN KEY (`recruiter_id`) REFERENCES `recruiter` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `post`
--

LOCK TABLES `post` WRITE;
/*!40000 ALTER TABLE `post` DISABLE KEYS */;
INSERT INTO `post` VALUES (1,1,'Java Intern','Backend dev','Java, Spring','Không yêu cầu kinh nghiệm','Không lương','2026-05-19','BLOCKED',0,'2026-04-19 08:29:58','2026-04-27 16:29:48'),(2,1,'Backend Dev','API system','NodeJS','<1 năm kinh nghiệm','3-5 triệu','2026-05-19','ACTIVE',0,'2026-04-19 08:29:58','2026-04-23 13:17:10'),(3,2,'Frontend Dev','UI dev','React','Không yêu cầu kinh nghiệm','3-5 triệu','2026-05-19','ACTIVE',0,'2026-04-19 08:29:58','2026-04-23 13:17:10'),(4,2,'QA Tester','Test app','Manual','<1 năm kinh nghiệm','5-10 triệu','2026-05-25','ACTIVE',0,'2026-04-19 08:29:58','2026-04-23 13:17:10'),(5,3,'Data Analyst','Analyze data','SQL, Python','<1 năm kinh nghiệm','5-10 triệu','2026-05-26','ACTIVE',0,'2026-04-19 08:29:58','2026-04-23 13:17:10'),(6,3,'DevOps','Deploy system','AWS','>5 năm kinh nghiệm','Thỏa thuận','2026-05-27','ACTIVE',0,'2026-04-19 08:29:58','2026-04-23 13:17:10'),(7,1,'Mobile Dev','App dev','Flutter','Không yêu cầu kinh nghiệm','Thỏa thuận','2026-05-10','ACTIVE',0,'2026-04-19 08:29:58','2026-04-23 13:17:10'),(8,2,'Fullstack','Web dev','React, Node','3-5 năm kinh nghiệm','Trên 30 triệu','2026-05-13','ACTIVE',0,'2026-04-19 08:29:58','2026-04-23 13:17:10'),(9,3,'Java Senior','Microservice','Java','3-5 năm kinh nghiệm','Thỏa thuận','2026-05-14','ACTIVE',0,'2026-04-19 08:29:58','2026-04-23 13:17:10'),(10,1,'Intern Backend','Learn system','Java','Không yêu cầu kinh nghiệm','5-10 triệu','2026-05-12','ACTIVE',0,'2026-04-19 08:29:58','2026-04-23 13:17:10');
/*!40000 ALTER TABLE `post` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recruiter`
--

DROP TABLE IF EXISTS `recruiter`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `recruiter` (
  `user_id` int NOT NULL,
  `company_id` int DEFAULT NULL,
  `position` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_approved` tinyint(1) DEFAULT '0',
  `is_company_admin` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`user_id`),
  KEY `fk_recruiter_company` (`company_id`),
  CONSTRAINT `fk_recruiter_company` FOREIGN KEY (`company_id`) REFERENCES `company` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_recruiter_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recruiter`
--

LOCK TABLES `recruiter` WRITE;
/*!40000 ALTER TABLE `recruiter` DISABLE KEYS */;
INSERT INTO `recruiter` VALUES (1,1,'HR Manager',1,1),(2,2,'HR Executive',1,1),(3,3,'Tech Recruiter',1,1),(24,1,'chức vụ',0,0),(26,6,'chức vụ',1,1),(29,7,'chức vụ',1,1),(30,2,'chức vụ',0,0);
/*!40000 ALTER TABLE `recruiter` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `first_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `last_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `address` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `date_of_birth` date DEFAULT NULL,
  `sex` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  `is_admin` tinyint(1) DEFAULT '0',
  `is_employer` tinyint(1) DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `last_login` timestamp NULL DEFAULT NULL,
  `avatar_url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'scrypt:32768:8:1$bnJcp1cAY2fJJcb2$a626297599424a9557832f05770fbff3b255e987e46a8f32b3259c3708a914366cc2108381f430316cfcc36c959adeb8992d07029785bcda38e68bd228cc8989','Anh','Pham','anh@company.com',NULL,NULL,NULL,NULL,1,0,1,'2026-04-19 08:29:08','2026-04-27 09:28:01',NULL),(2,'scrypt:32768:8:1$nyRVoI78hm4mY3mf$5c152153d52b05cc4e48efceb16d9d7a81f5263757db213abc425a53cbf556b97e2b565e3720f0e5c9b1f7c97633c0b499875bb0095978d015b24e6fcfa3eb3a','Huy','Tran','huy@gmail.com',NULL,NULL,NULL,NULL,1,0,0,'2026-04-19 08:29:08','2026-04-29 00:10:41',NULL),(3,'123','Linh','Nguyen','linh@gmail.com',NULL,NULL,NULL,NULL,1,0,0,'2026-04-19 08:29:08',NULL,NULL),(4,'123','Nam','Le','nam@gmail.com',NULL,NULL,NULL,NULL,1,0,0,'2026-04-19 08:29:08',NULL,NULL),(5,'123','Trang','Vo','trang@gmail.com',NULL,NULL,NULL,NULL,1,0,0,'2026-04-19 08:29:08',NULL,NULL),(6,'123','Khoa','Pham','khoa@gmail.com',NULL,NULL,NULL,NULL,1,0,0,'2026-04-19 08:29:08',NULL,NULL),(7,'123','Minh','Do','minh@gmail.com',NULL,NULL,NULL,NULL,1,0,0,'2026-04-19 08:29:08',NULL,NULL),(8,'123','Tuan','Hoang','tuan@gmail.com',NULL,NULL,NULL,NULL,1,0,0,'2026-04-19 08:29:08',NULL,NULL),(9,'123','Quang','Bui','quang@gmail.com',NULL,NULL,NULL,NULL,1,0,0,'2026-04-19 08:29:08',NULL,NULL),(10,'123','Vy','Tran','vy@gmail.com',NULL,NULL,NULL,NULL,1,0,0,'2026-04-19 08:29:08',NULL,NULL),(11,'123','Phuc','Nguyen','phuc@gmail.com',NULL,NULL,NULL,NULL,1,0,0,'2026-04-19 08:29:08',NULL,NULL),(12,'123','Lan','Pham','lan@gmail.com',NULL,NULL,NULL,NULL,1,0,0,'2026-04-19 08:29:08',NULL,NULL),(13,'123','Hung','Le','hung@gmail.com',NULL,NULL,NULL,NULL,1,0,0,'2026-04-19 08:29:08',NULL,NULL),(14,'123','Thao','Nguyen','thao@gmail.com',NULL,NULL,NULL,NULL,1,0,0,'2026-04-19 08:29:08',NULL,NULL),(15,'123','Long','Tran','long@gmail.com',NULL,NULL,NULL,NULL,1,0,0,'2026-04-19 08:29:08',NULL,NULL),(22,'scrypt:32768:8:1$7fVD6cPevEcOaZac$9f7847ca08eac7f8b840a54296e80ad96b04a316ca70fe112b5b06f68991c805a2dd60161c65b06d64ec03854b663eeb0a4d86daf0b08afaec343bc9d981e493','Tú','Võ Minh Cẩm','2251052132tu@ou.edu.vn',NULL,NULL,NULL,NULL,1,0,0,'2026-04-22 07:02:13','2026-04-23 08:07:50','https://lh3.googleusercontent.com/a/ACg8ocJyTwKEFczDqm20AthNzHXpCxDaK9Ho55fuqG_Ry5L9ky0YjEs=s96-c'),(23,'scrypt:32768:8:1$cvn6cpNmKNYeslWO$1b0ef340c572a487ea561ce26d89b3377b3c62f393f2302b20e65ff8715e682a5ed8fec277816dbf89ce993064558a50b8842465d9692820199a34b3a3d2ab9b',NULL,NULL,'admin@example.com',NULL,NULL,NULL,NULL,1,1,0,'2026-04-22 10:31:12','2026-04-22 10:33:45',NULL),(24,'scrypt:32768:8:1$xCZVdApToCTMBAcA$5f8c65c3b4e53e13d2043a0529f9289ec18c95c8808e01b65fe802d439a98e7ac58ff56bd5c09ca3bba7d3e3f2bdbcc51580c3455b84932cbeaaabad58304890',NULL,NULL,'annguyen123@gmail.com',NULL,NULL,NULL,NULL,1,0,1,'2026-04-22 11:40:04','2026-04-22 11:40:04',NULL),(25,'scrypt:32768:8:1$1VjITJ7NxDHtYWQo$295ec2134cb128d246cfa75c527093212b09d9ef7054466e189682499b32ca85a50fc553800eded6fc115b2145576afca52b5ccb2fe8994c111c49b644c6d849',NULL,NULL,'abc@example.com',NULL,NULL,NULL,NULL,1,0,1,'2026-04-22 11:43:37','2026-04-22 11:43:37',NULL),(26,'scrypt:32768:8:1$nyRVoI78hm4mY3mf$5c152153d52b05cc4e48efceb16d9d7a81f5263757db213abc425a53cbf556b97e2b565e3720f0e5c9b1f7c97633c0b499875bb0095978d015b24e6fcfa3eb3a',NULL,NULL,'abcd@example.com',NULL,NULL,NULL,NULL,1,1,1,'2026-04-22 11:46:33','2026-04-25 08:32:12',NULL),(27,'scrypt:32768:8:1$rx5Cg3BEjqmvyAx4$89bda1b94a51b6fd35adc2a2eb98e4d4b2746fb6bb14df06c2e1c27404534c0cbb96ec4dd4e1a9d5be5de41a4475578170e1642e67fc72881f524f38f1bd005c',NULL,NULL,'recruiter_1@test.com',NULL,NULL,NULL,NULL,1,0,1,'2026-04-23 06:41:27','2026-04-23 06:41:27',NULL),(28,'scrypt:32768:8:1$lSeJ2ghjV0SVKpav$a242e19c1abf3ae827383a5d0d213e1f2a074368af11fac6ecfbebf9ac97c24adcc9998c329acd2cb9a6dfea6c0f226f318bdaab0205ac26307be42b5ad541ab',NULL,NULL,'recruiter_2@test.com',NULL,NULL,NULL,NULL,1,0,1,'2026-04-23 06:54:59','2026-04-23 06:54:59',NULL),(29,'scrypt:32768:8:1$bnJcp1cAY2fJJcb2$a626297599424a9557832f05770fbff3b255e987e46a8f32b3259c3708a914366cc2108381f430316cfcc36c959adeb8992d07029785bcda38e68bd228cc8989',NULL,NULL,'recruiter_3@test.com',NULL,NULL,NULL,NULL,1,0,1,'2026-04-23 07:21:48','2026-04-27 09:24:24',NULL),(30,'scrypt:32768:8:1$lpjn3x01wpnjyDwK$8458e0658c328ae396098742556b1e13345951afa905e5c818aedde29e777d8e78cf92752d0be3a2b1de6c564b1be3e6c69826189dffa1de687a903838a71083',NULL,NULL,'recruiter_4@test.com',NULL,NULL,NULL,NULL,1,0,1,'2026-04-23 07:32:02','2026-04-23 07:32:02',NULL);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-04-29 14:18:56
