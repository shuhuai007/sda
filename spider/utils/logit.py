#! /usr/bin/env python
# -*- coding: utf-8 -*-

from functools import wraps

def logit(logfile='out.log'):
    def logging_decocator(func):
        @wraps(func)
        def wrapped_function(*args, **kwargs):
            log_string = func.__name__ + " was called"
            print(log_string)
            with open(logfile, 'a') as opened_file:
                opened_file.write(log_string + '\n')
        return wrapped_function
    return logging_decocator
