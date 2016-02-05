#!/usr/bin/env bash

bin=`cd "$( dirname "$0" )"; pwd`
spider_dir=`cd ${bin}/..;pwd`

echo "......execute update-question-detail.sh remotely......"
nohup ${spider_dir}/zhihu_question_detail.py -m develop > ${bin}/question_detail.log 2>&1 &
