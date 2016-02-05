#!/usr/bin/env bash

bin=`cd "$( dirname "$0" )"; pwd`

echo "......execute update-question-detail.sh remotely......"
nohup ${bin}/zhihu_question_detail.py -m develop > ${bin}/question_detail.log 2>&1 &
