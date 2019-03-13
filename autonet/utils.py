# -*- coding: utf-8 -*-
# @Time    : 2018/11/8 下午6:30
# @Author  : lingting.fu
# @Email   : lingting.fu@okcoin.com
# @File    : utils.py
# @Software: TAutoNet

import logging
import os
import traceback
import time

'''
    %(levelno)s: 打印日志级别的数值
     %(levelname)s: 打印日志级别名称
     %(pathname)s: 打印当前执行程序的路径，其实就是sys.argv[0]
     %(filename)s: 打印当前执行程序名
     %(funcName)s: 打印日志的当前函数
     %(lineno)d: 打印日志的当前行号
     %(asctime)s: 打印日志的时间
     %(thread)d: 打印线程ID
     %(threadName)s: 打印线程名称
     %(process)d: 打印进程ID
     %(message)s: 打印日志信息
'''


log_level   = logging.DEBUG
log_dir = "/opt/tautonet/v1/logs"
global_path = log_dir + os.path.sep + "global.log"

logging.basicConfig(level=log_level,
                    filename=global_path,
                    format="%(asctime)s [%(levelname)s] %(threadName)s %(filename)10s$%(lineno)3dL: %(message)s",
                    datefmt='%Y-%m-%d %H:%M:%S')
LOG = logging.getLogger("SUPER")

def log_exception(f):
    def wrapper(*args, **kwargs):
        try:
            ret = f(*args, **kwargs)
            return ret
        except Exception as e:
            e_str = traceback.format_exc()
            msg = "function: %s, *args : %s, **kwargs : %s" % (f.__name__, args, kwargs)
            LOG.error(msg[:1000])
            LOG.error(e_str)
    return wrapper

def log_traceback_str():
    e_str = traceback.format_exc()
    LOG.error(e_str)
    return e_str

def log_network_error(f):
    def wrapper(*args, **kwargs):
        try:
            ret = f(*args, **kwargs)
            return ret
        except Exception as e:
            e_str = traceback.format_exc()
            msg = "function: %s, *args : %s, **kwargs : %s" % (f.__name__, args, kwargs)
            LOG.warn(msg[:1000])
            LOG.warn(e_str)
            time.sleep(1)

    return wrapper


def record_time(f):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        ret = f(*args, **kwargs)
        end_time = time.time()
        LOG.info("running %s(*args: %s, **kwagrs: %s) takes %f second" % (f.__name__, args, kwargs, (end_time - start_time)))
        return ret

    return wrapper

def log_input_output(f):
    def wrapper(*args, **kwargs):
        LOG.info("func_name: %s, *args: %s, **kwargs: %s" % (f.__name__, args, kwargs))
        ret = f(*args, **kwargs)
        LOG.info("func_ret: %s" % (str(ret)))
        return ret
    return wrapper

def generate_default_password(length=10):
    pass