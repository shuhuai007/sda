
CREATE DATABASE IF NOT EXISTS sda;

USE sda;

CREATE EXTERNAL TABLE IF NOT EXISTS sda.zhihu_user_final LIKE sda.zhihu_user;

INSERT OVERWRITE TABLE sda.zhihu_user_final
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


-- select a.* from
--    (select employment, count(*) as count from zhihu_user_final  group by employment) as a
--    order by a.count desc limit 10;

-- select * from
--    (select gender, count(*) as count from zhihu_user_final group by gender) as a
--    order by a.count desc limit 3;

-- select * from
--    (select location, count(*) as count from zhihu_user_final group by location) as a
--    order by a.count desc limit 30;

-- top 10 user who have the most followers.
-- select url_suffix, user_name, followers_num from zhihu_user_final order by cast(followers_num as int) desc limit 10;


