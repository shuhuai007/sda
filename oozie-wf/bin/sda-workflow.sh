#!/usr/bin/env bash

BIN=$(cd "$( dirname "$0" )"; pwd)

WORKFLOW_DIR="${BIN}/../workflow"

echo "workflow dir path: ${WORKFLOW_DIR}"

PROJECT_HDFS_PATH="/user/oozie/apps/sda"

JOB_PROPERTIES_PATH="${PROJECT_HDFS_PATH}/workflow/job.properties"


usage() {
cat << EOF
    usage: $0 options

    NAME
        $0 - script to run/info oozie workflow job

    SYNOPSIS
        $0  -j <job-id> [run|info]

    OPTIONS:
        -h      Show this message

EOF
}

parseArgs() {
    while getopts "j:h" arg
    do
        case ${arg} in
             j)
                job_id=$OPTARG
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

#remove old workflow files, including config files and lib, then run the job
run(){

    hadoop fs -rmr "${PROJECT_HDFS_PATH}/workflow"

    hadoop fs -put ${WORKFLOW_DIR} ${PROJECT_HDFS_PATH}

    oozie job -config ${JOB_PROPERTIES_PATH} -run
}

info(){

    oozie job -info ${job_id}

}


parseArgs $*

shift $((OPTIND-1))

WHAT=$1
echo "...What:${WHAT}"

if [ "$WHAT" == "info" ]; then
    info
elif [ "$WHAT" == "run" ]; then
    echo "...start the workflow job..."
    run
else
    echo "run or info should be appended, please see the usage of command"
    usage
fi
