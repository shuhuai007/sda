#!/usr/bin/env bash

bin=`cd "$( dirname "$0" )"; pwd`
spider_dir=`cd ${bin}/..;pwd`
log_dir=${spider_dir}/log

[ ! -d ${log_dir} ] && mkdir ${log_dir}

echo "......execute update-question-detail.sh remotely......"

nohup python ${spider_dir}/zhihu_question_detail.py -m develop > ${log_dir}/question_detail.log 2>&1 &
