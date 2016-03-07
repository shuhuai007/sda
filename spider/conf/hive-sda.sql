use sda;

# question
# question_id, question_title, answer_count, is_top_quesiton, created_time, spider_time
create table sda.zhihu_question (
  question_id               bigint,
  question_title            string,
  answer_count              bigint,
  is_top_question           int,
    created_time            string
);


# question detail
# question_id, question_content, comment_count, focus, focus_user_list, browse_count,
# related_focus, last_edited, spider_time
#drop table sda.zhihu_question_detail;
create table sda.zhihu_question_detail (
  question_id               string,
  question_content          string,
  comment_count             string,
  focus                     string,
  focus_user_list           string,
  browse_count              string,
  related_focus             string,
  last_edited               string,
  created_time              string
)
comment 'question detail info'
ROW FORMAT SERDE 'org.apache.hadoop.hive.contrib.serde2.RegexSerDe'
WITH SERDEPROPERTIES (
"input.regex" = "^([^question\\-detail\\-delimiter]{0,}.*)question\-detail\-delimiter([^question\\-detail\\-delimiter]{0,}.*)question\-detail\-delimiter([^question\\-detail\\-delimiter]{0,}.*)question\-detail\-delimiter([^question\\-detail\\-delimiter]{0,}.*)question\-detail\-delimiter([^question\\-detail\\-delimiter]{0,}.*)question\-detail\-delimiter([^question\\-detail\\-delimiter]{0,}.*)question\-detail\-delimiter([^question\\-detail\\-delimiter]{0,}.*)question\-detail\-delimiter([^question\\-detail\\-delimiter]{0,}.*)question\-detail\-delimiter([^question\\-detail\\-delimiter]{0,}.*)$",
"output.format.string" = "%1$s %2$s %3$s %4$s %5$s %6$s %7$s %8$s %9$s");
# LOAD DATA  INPATH '/tmp/good' INTO TABLE sda.zhihu_question_detail;
# add jar /usr/hdp/2.3.2.0-2950/hive/lib/hive-contrib-1.2.1.2.3.2.0-2950.jar;
#


# answer table
# answer_id(data-atoken), answer_content, data_aid, user created_time(data-created),
# vote_count, comment_count


create database if not exists sda;
CREATE TABLE sda.zhihu_user(
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
  browse_num STRING
)
 COMMENT 'This is zhihu user table'
 ROW FORMAT DELIMITED
   FIELDS TERMINATED BY '\001'
STORED AS SEQUENCEFILE;
