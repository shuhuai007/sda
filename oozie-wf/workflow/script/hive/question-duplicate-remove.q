
CREATE DATABASE IF NOT EXISTS sda;

USE sda;

CREATE EXTERNAL TABLE IF NOT EXISTS sda.zhihu_question_final LIKE sda.zhihu_question;

INSERT OVERWRITE TABLE sda.zhihu_question_final
    SELECT question_id, question_title,
           max(cast(answer_count as int)),
           max(cast(focus_count as int)),
           max(cast(is_top_question as int)),
           created_time
    FROM sda.zhihu_question
    WHERE question_id!='' and question_id!='NULL'
    GROUP BY question_id, question_title, answer_count, focus_count,
             is_top_question, created_time
;