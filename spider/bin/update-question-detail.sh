#!/usr/bin/env bash

bin=`cd "$( dirname "$0" )"; pwd`
spider_dir=`cd ${bin}/..;pwd`

cd ${spider_dir}

log_dir=${spider_dir}/log
[ ! -d ${log_dir} ] && mkdir ${log_dir}

usage() {
cat << EOF
    usage: $0 options

    NAME
        update-question-detail.sh - script to update the question remotely.

    SYNOPSIS
        $0 -m <run-mode>

    OPTIONS:
        -h      Show this message
        -m      running mode - develop/prod
EOF
}

parseArgs() {
    while getopts "m:h" arg
    do
        case ${arg} in
             m)
                mode=$OPTARG
                ;;
             h)
                usage
                exit 1
                ;;
             ?)
                echo "Unkonw argument"
                exit 1
                ;;
        esac
    done
}

mode=prod

parseArgs $*
echo "......mode:$mode"

echo "......execute update-question-detail.sh remotely......"

#nohup python ${spider_dir}/zhihu_question_detail.py -m develop > ${log_dir}/question_detail.log
# 2>&1 &
