
CREATE DATABASE IF NOT EXISTS sda;

USE sda;

CREATE TABLE IF NOT EXISTS sda.zhihu_user(
  url_suffix STRING,
  data_id STRING,
  user_name STRING,
  user_title STRING,
  gender STRING,
  location STRING,
  business STRING,
  employment STRING,
  position STRING,
  education STRING,
  education_extra STRING,
  user_agree_num STRING,
  user_thanks_num STRING,
  asks_num STRING,
  answers_num STRING,
  posts_num STRING,
  collections_num STRING,
  logs_num STRING,
  followees_num STRING,
  followers_num STRING,
  focus_topics_num STRING,
  browse_num STRING)
COMMENT 'This is zhihu user table'
ROW FORMAT DELIMITED
        FIELDS TERMINATED BY '1';

LOAD DATA  INPATH '${INPUT}' INTO TABLE sda.zhihu_user;
