#!/usr/bin/env bash

FLUME_SOURCE_DIR="/user/flume/project/sda/spider/user"
FLUME_DATA_TEMP_DIR="/user/flume/project/test_table"

# create dir if not exist
hadoop fs -test -e ${FLUME_DATA_TEMP_DIR}
if [ $? != "0" ]; then
    echo "create directory"
    hadoop fs -mkdir ${FLUME_DATA_TEMP_DIR}
fi

data_file_count=$(hadoop fs -ls ${FLUME_SOURCE_DIR} | wc -l)
if [ ${data_file_count} != "0" ]; then
    hadoop fs -mv ${FLUME_SOURCE_DIR}/* ${FLUME_DATA_TEMP_DIR}
fi


