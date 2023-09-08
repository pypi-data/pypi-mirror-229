##################################################
# 功能说明：
# 更新日期：
# 更新次数：
# 完成情况：
# 执行次数：205
# 执行时间：2023-09-08 11:59:38
##################################################
import sys
import re
from logging.handlers import TimedRotatingFileHandler
import logging
import os
import configparser
from ziyulibs.function.zycommon import updatedescribe
updatedescribe(__file__)


def setup_log(logpath):

    # 创建logger对象。传入logger名字
    log_path1 = '/'.join(logpath.split('/')[0:-1])
    log_name = logpath.split('/')[-1]
    if not os.path.exists(log_path1):
        os.makedirs(log_path1)
    logger = logging.getLogger(log_name)
    logger.__dict__['handlers'].clear()
    # 设置日志记录等级
    logger.setLevel(logging.INFO)

    # backupCount  表示日志保存个数
    file_handler = TimedRotatingFileHandler(filename=logpath, when="MIDNIGHT", interval=1, backupCount=int(10))
    file_handler.suffix = "%Y-%m-%d.log"
    # extMatch是编译好正则表达式，用于匹配日志文件名后缀
    file_handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}.log$")

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter('%(asctime)s %(thread)d %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s'))

    # 定义日志输出格式
    file_handler.setFormatter(logging.Formatter("[%(asctime)s] [%(process)d] [%(levelname)s] - %(module)s.%(funcName)s (%(filename)s:%(lineno)d) - %(message)s"))
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger


cameras_newlog1 = setup_log('log/log1')
cameras_newlog1.info('日志内容')
cameras_newlog2 = setup_log('log/log2')
cameras_newlog2.info('日志内容2')
