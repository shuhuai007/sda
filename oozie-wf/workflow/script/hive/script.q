

CREATE TABLE IF NOT EXISTS test_hive2 (a STRING) ;
LOAD DATA  INPATH '${INPUT}' INTO TABLE test_hive2;
