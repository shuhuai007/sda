#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
CONFIG_INI_PATH = "{0}/config.ini".format(os.path.dirname(os.path.abspath(__file__)))
QUESTION_ID_SAMPLE_PATH = "{0}/question_id.sample".format(os.path.dirname(os.path.abspath(
                                                          __file__)))


# 1st Level Topics url
LEVEL1_TOPICS_URL = "https://www.zhihu.com/topics"
# 2st Level Topics url
LEVEL2_TOPICS_URL = "https://www.zhihu.com/node/TopicsPlazzaListV2"

ZHIHU_QUESTION_URL = "https://www.zhihu.com/topic/{0}/questions?page={1}"

ZHIHU_QUESTION_DETAIL_URL = "https://www.zhihu.com/question/{0}"

ZHIHU_ANSWER_POST_URL = "https://www.zhihu.com/node/QuestionAnswerListV2"

ZHIHU_QUESTION_DATA_DELIMETER = "\001"

ZHIHU_QUESTION_DETAIL_FIELD_DELIMITER = "\001"


LOG_PREFIX = "------------------enter {0}------------------"
