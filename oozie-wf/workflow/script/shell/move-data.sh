#!/usr/bin/env bash

FLUME_DATA_TEMP_DIR="/user/flume/project/test_table"
# create dir if not exist
hadoop fs -test -e ${FLUME_DATA_TEMP_DIR}
if [ $? != "0" ]; then
    echo "create directory"
    hadoop fs -mkdir ${FLUME_DATA_TEMP_DIR}
fi

hadoop fs -mv /user/flume/project/sda/spider/user/* ${FLUME_DATA_TEMP_DIR}

