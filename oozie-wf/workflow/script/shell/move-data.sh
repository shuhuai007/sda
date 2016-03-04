#!/usr/bin/env bash

# create dir if not exist
hadoop fs -test -e /user/flume/project/test_table
if [ $? != "0" ]; then
    echo "create directory"
    hadoop fs -mkdir /user/flume/project/test_table
fi

hadoop fs -mv /user/flume/aaa.txt /user/flume/project/test_table
