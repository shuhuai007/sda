
CREATE DATABASE IF NOT EXISTS sda;

USE sda;


-- (question_id, question_title, answer_count, focus_count, is_top_question, created_time)

CREATE TABLE IF NOT EXISTS sda.zhihu_question(
  question_id STRING,
  question_title STRING,
  answer_count STRING,
  focus_count STRING,
  is_top_question STRING,
  created_time STRING)
COMMENT 'This is zhihu question table'
ROW FORMAT DELIMITED
        FIELDS TERMINATED BY '1';

LOAD DATA  INPATH '${INPUT}' INTO TABLE sda.zhihu_question;
