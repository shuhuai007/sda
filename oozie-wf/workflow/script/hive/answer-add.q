CREATE DATABASE IF NOT EXISTS sda;

USE sda;


-- answer_id, answer_content, data_aid, user_name, created_time, vote_count, comment_count

CREATE TABLE IF NOT EXISTS sda.zhihu_answer(
  answer_id STRING,
  answer_content STRING,
  data_aid STRING,
  user_name STRING,
  created_time STRING,
  vote_count STRING,
  comment_count STRING)
COMMENT 'This is zhihu answer table'
ROW FORMAT DELIMITED
        FIELDS TERMINATED BY '1';

LOAD DATA  INPATH '${INPUT}' INTO TABLE sda.zhihu_answer;