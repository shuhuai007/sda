
CREATE DATABASE IF NOT EXISTS sda;

USE sda;

CREATE EXTERNAL TABLE IF NOT EXISTS sda.zhihu_question_final LIKE sda.zhihu_question;

INSERT OVERWRITE TABLE sda.zhihu_question_final
    SELECT question_id, question_title,
           cast(answer_count as int),
           max(cast(focus_count as int)),
           cast(is_top_question as int),
           created_time
    FROM sda.zhihu_question
    WHERE question_id!='' and question_id!='NULL' and question_id!='?'
          and answer_count!='NULL'
          and focus_count!='NULL'
          and is_top_question!='NULL'
          and created_time!='NULL'
    GROUP BY question_id, question_title, answer_count,
             is_top_question, created_time
;


CREATE TABLE IF NOT EXISTS sda.zhihu_question_id(question_id bigint, created_time STRING)
COMMENT 'This is zhihu question id table'
ROW FORMAT DELIMITED
        FIELDS TERMINATED BY '1';

DROP TABLE sda.zhihu_question_id_incremental;

CREATE TABLE IF NOT EXISTS sda.zhihu_question_id_incremental
ROW FORMAT DELIMITED
        FIELDS TERMINATED BY '1'
AS
    SELECT cast(Q.question_id as bigint), '0' as access_time FROM sda.zhihu_question_final as Q
    WHERE Q.question_id!='' AND Q.question_id!='NULL'
    AND Q.question_id not in (select id.question_id from sda.zhihu_question_id as id);


INSERT OVERWRITE TABLE sda.zhihu_question_id
  SELECT * FROM sda.zhihu_question_id
  UNION ALL
  SELECT * FROM sda.zhihu_question_id_incremental;


