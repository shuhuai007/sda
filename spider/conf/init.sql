CREATE DATABASE IF NOT EXISTS `sda` /*!40100 DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci */;
USE `sda`;

CREATE TABLE IF NOT EXISTS `ZHIHU_TOPIC` (
  `ID` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `NAME` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `LAST_VISIT` TIMESTAMP NOT NULL DEFAULT 0,
  `TOPIC_ID` int(10) unsigned NOT NULL,
  `PARENT_ID` int(10) unsigned NOT NULL,
  `ADD_TIME` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `TOPIC_ID` (`TOPIC_ID`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE IF NOT EXISTS `ZHIHU_QUESTION_ID` (
  `QUESTION_ID` int(10) unsigned NOT NULL,
  `LAST_VISIT` VARCHAR(30) NOT NULL,
  PRIMARY KEY (`QUESTION_ID`)
);

CREATE TABLE IF NOT EXISTS `ZHIHU_PROXY` (
  `ID` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `PROXY_IP` VARCHAR(30) NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `PROXY_IP` (`PROXY_IP`)
);


# CREATE TABLE IF NOT EXISTS `ZHIHU_QUESTION` (
#   `QUESTION_ID` int(10) unsigned NOT NULL,
#   `QUESTION_TITLE` varchar(500) COLLATE utf8_unicode_ci NOT NULL,
#   `QUESTION_CONTENT`TEXT,
#   `LAST_VISIT` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
#   `FOCUS` int(10) unsigned NOT NULL DEFAULT 0,
#   `ANSWER` int(10) unsigned NOT NULL,
#   `ADD_TIME` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
#   `TOP_ANSWER_NUMBER` int(10) unsigned NOT NULL DEFAULT 0,
#   `IS_TOP_QUESTION` tinyint,
#   `CREATED_TIME` TIMESTAMP NOT NULL,
#   PRIMARY KEY (`QUESTION_ID`)
# ) ENGINE=MyISAM AUTO_INCREMENT=1000000000000030 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
