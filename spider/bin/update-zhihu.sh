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
        update-zhihu.sh - script to update the question remotely.

    SYNOPSIS
        $0 -m <run-mode>

    OPTIONS:
        -h      Show this message
        -m      running mode - develop/prod
        -c      what should be updated - question_detail/question/answer
EOF
}

parseArgs() {
    while getopts "m:c:h" arg
    do
        case ${arg} in
             m)
                mode=$OPTARG
                ;;
             c)
                content=$OPTARG
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
echo "......content:$content"

echo "......execute update-zhihu.sh remotely......"

PYTHON_ZHIHU_SCRIPT="${spider_dir}/zhihu_${content}.py"
LOG_FILE="${log_dir}/${content}.log"

echo "......script:${PYTHON_ZHIHU_SCRIPT}"
echo "......log file:${LOG_FILE}"

nohup python ${PYTHON_ZHIHU_SCRIPT} -m ${mode} > ${LOG_FILE} 2>&1 &
