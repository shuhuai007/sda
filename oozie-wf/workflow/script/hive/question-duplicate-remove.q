
CREATE DATABASE IF NOT EXISTS sda;

USE sda;


CREATE TABLE IF NOT EXISTS sda.zhihu_question_id(question_id bigint, created_time STRING)
COMMENT 'This is zhihu question id table'
ROW FORMAT DELIMITED
        FIELDS TERMINATED BY '1';


DROP TABLE sda.zhihu_question_id_incremental;

CREATE TABLE IF NOT EXISTS sda.zhihu_question_id_incremental
ROW FORMAT DELIMITED
        FIELDS TERMINATED BY '1'
AS
    SELECT cast(Q.question_id as bigint) as question_id, '0' as access_time FROM sda.zhihu_question as Q
    WHERE Q.question_id!='' AND Q.question_id!='NULL'
    AND Q.question_id not in (select id.question_id from sda.zhihu_question_id as id);


INSERT OVERWRITE TABLE sda.zhihu_question_id_incremental
  select distinct question_id as question_id, '1970-01-01' as access_time from sda.zhihu_question_id_incremental;


INSERT OVERWRITE TABLE sda.zhihu_question_id
  SELECT * FROM sda.zhihu_question_id
  UNION ALL
  SELECT * FROM sda.zhihu_question_id_incremental;


