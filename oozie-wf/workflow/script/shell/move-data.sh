#!/usr/bin/env bash

hadoop fs -mkdir /user/flume/project/test_table
hadoop fs -mv /user/flume/aaa.txt /user/flume/project/test_table
