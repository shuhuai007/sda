#!/usr/bin/env bash


bin=`cd "$( dirname "$0" )"; pwd`
spider_dir=`cd ${bin}/..;pwd`

usage() {
cat << EOF
    usage: $0 options

    NAME
        slave-control.sh - script to control the slaves remotely.

    SYNOPSIS
        $0 -p <password> [start|status]

    OPTIONS:
        -h      Show this message
        -p      Password, default all the slaves have the same password
EOF
}


parseArgs() {
    while getopts "p:h" arg
    do
        case ${arg} in
             p)
                password=$OPTARG
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
    ${bin}/remote-execute.sh  10.29.10.111 ${password}  "cd /root/work/sda/spider/; git reset
    --hard;git pull; sleep 3; bin/update-question-detail.sh"
    sleep 3
}

status() {
    echo "########################Slave######################"
    ${bin}/remote-execute.sh  10.29.10.111 ${password} "ps -ef | grep zhihu;"
    sleep 3
}


parseArgs $*

shift $((OPTIND-1))

WHAT=$1
echo "...What:${WHAT}"



if [ "$WHAT" == "status" ]; then
    status
elif [ "$WHAT" == "start" ]; then
    echo "...start the slaves..."
    start
else
    echo "start or status should be appended, please see the usage of command"
    usage
fi
