#! /usr/bin/env python
# -*- coding: utf-8 -*-

from transaction_manager import TransactionManager


class ZhihuItem:

    def __init__(self, run_mode='prod'):
        self.mode = run_mode
        self.transaction_manager = TransactionManager()

    def is_develop_mode(self):
        return self.mode == 'develop'
