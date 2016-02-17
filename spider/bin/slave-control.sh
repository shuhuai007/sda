#!/usr/bin/env bash


bin=`cd "$( dirname "$0" )"; pwd`
spider_dir=`cd ${bin}/..;pwd`

usage() {
cat << EOF
    usage: $0 options

    NAME
        slave-control.sh - script to control the slaves remotely.

    SYNOPSIS
        $0 -i <ip> -p <password> -c <content> [start|status]

    OPTIONS:
        -h      Show this message
        -i      IP , slave's ip
        -p      Password, default all the slaves have the same password
        -c      Content, what should be updated - question_detail/question/answer
EOF
}


parseArgs() {
    while getopts "c:p:i:h" arg
    do
        case ${arg} in
             p)
                password=$OPTARG
                ;;
             i)
                ip=$OPTARG
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


start() {
    ${bin}/remote-execute.sh  ${ip} ${password} \
    "cd /root/work/sda/spider/; git reset --hard;\
     git pull; sleep 3; bin/update-zhihu.sh -c ${content}"
    sleep 3
}

REMOTE_SPIDER_DATA_DIR="/root/work/data/zhihu"
REMOTE_SPIDER_LOG_DIR="/root/work/sda/spider/log"
status() {
    echo "########################Slave Status######################"
    ${bin}/remote-execute.sh ${ip} ${password} \
    "ps -ef | grep zhihu;sleep 3; \
    echo data-file:\`ls -l ${REMOTE_SPIDER_DATA_DIR}/${content} | wc -l \`; \
    echo question-id:\`grep -a \"......question id\" ${REMOTE_SPIDER_LOG_DIR}/${content}.log |wc -l\`"
    sleep 3
}


parseArgs $*

shift $((OPTIND-1))

WHAT=$1
echo "...What:${WHAT}"

echo "...content:${content}"

if [ "$content" == "" ]; then
    echo "...content should not be empty."
    exit
fi

if [ "$WHAT" == "status" ]; then
    status
elif [ "$WHAT" == "start" ]; then
    echo "...start the slaves..."
    start
else
    echo "start or status should be appended, please see the usage of command"
    usage
fi
