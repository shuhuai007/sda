
CREATE DATABASE IF NOT EXISTS sda;

USE sda;

CREATE EXTERNAL TABLE IF NOT EXISTS sda.zhihu_question_final LIKE sda.zhihu_question;

INSERT OVERWRITE TABLE sda.zhihu_question_final
    SELECT url_suffix, data_id, user_name, user_title,
           gender, location, business, employment,
           position, education, education_extra,
           max(cast(user_agree_num as int)), max(cast(user_thanks_num as int)),
           max(cast(asks_num as int)), max(cast(answers_num as int)),
           max(cast(posts_num as int)), max(cast(collections_num as int)),
           max(cast(logs_num as int)), max(cast(followees_num as int)),
           max(cast(followers_num as int)), max(cast(focus_topics_num as int)),
           max(cast(browse_num as int))
    FROM sda.zhihu_user
    WHERE data_id!='' and data_id!='NULL' and url_suffix!='' and url_suffix!='NULL'
    GROUP BY url_suffix, data_id, user_name, user_title,
             gender, location, business, employment,
             position, education, education_extra
;