"""
cron: 0 */3 * * *
new Env('机场订阅更新');
"""

import os
import sys

from loguru import logger

import sub_converter.index

if __name__ == '__main__':
    # 设置日志
    logger.remove()

    logger.add(sys.stdout, level='DEBUG', format='{message}')
    os.environ['http_proxy'] = os.environ.get('proxy_url', '')
    os.environ['deta_key'] = os.environ['deta_key']

    sub_converter.index.task()
