#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
cron: */30 * * * *
new Env('机场续购');

脚本同目录下添加sc_jcxg.json文件配置机场信息
如果需要代理则设置环境变量scripts_http_proxy，例如 scripts_http_proxy = 127.0.0.1:1098
"""

import json
import os
import re
from datetime import datetime

import requests
import yaml
from requests.utils import dict_from_cookiejar, cookiejar_from_dict

from py_dep.log import logger

requests.packages.urllib3.disable_warnings()

######################################################
configs_file = 'sc_jcxg.yaml'
cache_file = 'sc_jcxg.cache'
cache = {}
new_cache = {}

# 环境变量设置http代理 例如 scripts_http_proxy = 127.0.0.1:1098
http_proxy_env_key = 'scripts_http_proxy'
######################################################

sess = None
proxies = None


# SHA_TZ = timezone(
#     timedelta(hours=8),
#     name='Asia/Shanghai',
# )
#
#
# def get_current_datetime() -> str:
#     return datetime.now(tz=SHA_TZ).strftime('%Y-%m-%d %H:%M:%S')
#

def resolve_proxy():
    if http_proxy := os.getenv(http_proxy_env_key):
        # logger.info(f'启用代理：{http_proxy}')
        global proxies
        proxies = {
            'http': f'http://{http_proxy}',
            'https': f'http://{http_proxy}'
        }


class Task(object):
    def __init__(self, email, password, domain, order_form_period, order_form_plan_id):
        self.email = email
        self.password = password
        self.domain = domain
        self.order_form_period = order_form_period
        self.order_form_plan_id = order_form_plan_id

        self.need_order = None

    def run(self):
        logger.info(f'-------{self.domain}-------')
        logger.info(f'用户：{self.email}')

        if self.login():
            if self.need_order is False:
                return
            self.run_task()

    def login(self):
        global sess

        ok = False

        # 使用上次登录过后的数据
        if data := cache.get(f'{self.domain}|{self.email}'):
            cookie = data.get('cookie')
            authorization = data.get('authorization')

            headers = {
                'authorization': authorization,
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.33'
            }

            sess = requests.Session()
            sess.cookies = cookiejar_from_dict(cookie)
            sess.headers = headers
            sess.verify = False

            try:
                self.check_subscribe()
                new_cache[f'{self.domain}|{self.email}'] = data
                ok = True
            except Exception as e:
                logger.error(f'使用缓存数据失败：{e}')

        # 账户密码登录
        if ok is False:
            url = f'https://{self.domain}/api/v1/passport/auth/login'

            form_data = {
                'email': self.email.strip(),
                'password': self.password.strip()
            }

            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.33'
            }

            sess = requests.Session()
            sess.headers = headers
            sess.verify = False

            try:
                resp = sess.post(url, data=form_data, proxies=proxies)
                data = resp.json().get('data')

                if data.get('token') and (authorization := data.get('auth_data')):
                    logger.info('使用邮箱和密码登录成功')

                    login_data = {
                        'cookie': dict_from_cookiejar(resp.cookies),
                        'authorization': authorization
                    }
                    new_cache[f'{self.domain}|{self.email}'] = login_data

                    sess.headers.update({
                        'authorization': authorization
                    })

                    ok = True
            except Exception as e:
                logger.error(f'使用邮箱和密码登录失败：{e}')

        return ok

    def order(self):
        url = f'https://{self.domain}/api/v1/user/order/save'
        form_data = {
            'period': self.order_form_period,
            'plan_id': self.order_form_plan_id
        }

        resp = sess.post(url, data=form_data, proxies=proxies)
        dict_content = resp.json()
        trade_no = dict_content.get('data')
        msg = dict_content.get('message')

        return trade_no, msg

    def checkout(self, trade_no):
        url = f'https://{self.domain}/api/v1/user/order/checkout'
        form_data = {
            'trade_no': trade_no,
            'method': '1'
        }

        resp = sess.post(url, data=form_data, proxies=proxies)
        if data := resp.json().get('data'):
            logger.debug(f'{data}')
            logger.info('下单成功')

    def get_unpaid_trade_no(self):
        url = f'https://{self.domain}/api/v1/user/order/fetch'

        resp = sess.get(url, proxies=proxies)
        dict_content = resp.json()

        unpaid_trade_no = None
        if orders := dict_content.get('data'):
            for item in orders:
                status = item.get('status')
                trade_no = item.get('trade_no')

                if status == 0:  # 0待付款 1开通中 2已取消 3完成
                    unpaid_trade_no = trade_no
                    break

        return unpaid_trade_no

    # def get_order_status(self, target_trade_no):
    #     url = f'https://{self.domain}/api/v1/user/order/fetch'
    #     try:
    #         resp = sess.get(url, proxies=proxies)
    #         dict_content = resp.json()
    #
    #         if orders := dict_content.get('data'):
    #             for item in orders:
    #                 status = item.get('status')
    #                 trade_no = item.get('trade_no')
    #
    #                 if target_trade_no == trade_no:  # 0待付款 1开通中 3完成
    #                     return status
    #     except Exception as e:
    #         logger.error(f'订单状态检查过程出错, 原因: {e}')

    def check_subscribe(self):
        info_url = f'https://{self.domain}/api/v1/user/getSubscribe'
        resp = sess.get(info_url, proxies=proxies)
        info_data = resp.json()

        total = info_data['data']['transfer_enable']
        used = info_data['data']['d']
        used_percent = used / total

        expired_at = info_data['data']['expired_at']
        delta_days = None
        if expired_at:
            expired_time = datetime.fromtimestamp(expired_at)
            delta_time = expired_time - datetime.now()
            delta_days = delta_time.days
        logger.info(f'剩余天数：{delta_days}，已使用流量：{round(used_percent * 100, 1)}%')

        self.need_order = False
        if used_percent > 0.7 or (delta_days and delta_days < 2):
            self.need_order = True

    def run_task(self):
        unpaid_trade_no = self.get_unpaid_trade_no()
        if unpaid_trade_no:
            self.checkout(unpaid_trade_no)
        else:
            if self.need_order is None:
                self.check_subscribe()

            if self.need_order is True:
                trade_no, msg = self.order()
                if trade_no:
                    self.checkout(trade_no)
                else:
                    logger.warning(msg)


class ShengFeng(Task):

    def __init__(self, email, password, domain, order_form_period, order_form_plan_id, min_days, min_flow):
        super().__init__(email, password, domain, order_form_period, order_form_plan_id)
        self.min_days = min_days
        self.min_flow = min_flow

    def login(self):
        global sess

        ok = False

        # 使用上次登录过后的数据
        if data := cache.get(f'{self.domain}|{self.email}'):
            cookie = data.get('cookie')

            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.33'
            }

            sess = requests.Session()
            sess.cookies = cookiejar_from_dict(cookie)
            sess.headers = headers
            sess.verify = False

            try:
                self.check_subscribe()
                new_cache[f'{self.domain}|{self.email}'] = data
                ok = True
            except Exception as e:
                logger.error(f'使用缓存数据失败：{e}')

        # 账户密码登录
        if ok is False:
            url = f'https://{self.domain}/auth/login'

            form_data = {
                'email': self.email.strip(),
                'passwd': self.password.strip(),
                'remember_me': 'on',
                'code': ''
            }

            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.33'
            }

            sess = requests.Session()
            sess.headers = headers
            sess.verify = False

            try:
                resp = sess.post(url, data=form_data, proxies=proxies)
                data = resp.json()

                if data.get('msg') == '登录成功':
                    logger.info('使用邮箱和密码登录成功')

                    login_data = {
                        'cookie': dict_from_cookiejar(resp.cookies)
                    }
                    new_cache[f'{self.domain}|{self.email}'] = login_data

                    ok = True
            except Exception as e:
                logger.error(f'使用邮箱和密码登录失败：{e}')

        return ok

    def order(self):
        url = f'https://{self.domain}/user/buy'
        form_data = {
            'coupon': '',
            'shop': '1',
            'autorenew': '0',
            'disableothers': '1'
        }

        resp = sess.post(url, data=form_data, proxies=proxies)
        data = resp.json()
        msg = data.get('msg')
        logger.info(msg)

    def check_subscribe(self):
        info_url = f'https://{self.domain}/user'
        resp = sess.get(info_url, proxies=proxies)
        content = resp.text

        if '<title>登录' in content:
            raise RuntimeError('缓存失效！')

        expire = False
        delta_days = None
        match = re.search(r'普通会员.+?(\d+-\d+-\d+)\s*到期', content, re.S)
        if match:
            str_date = match.group(1)
            expired_time = datetime.strptime(str_date, '%Y-%m-%d')
            delta_time = expired_time - datetime.now()
            delta_days = delta_time.days + 1
            if delta_days < self.min_days:
                expire = True

        traffic = False
        a = None
        b = None
        match = re.search(r'((\d+|\d+\.\d+)(M|G)B).+?剩余流量', content, re.S)
        if match:
            a, b = match.group(2), match.group(3)

            # if (b == 'G' and float(a) < 10) or b == 'M':
            #     traffic = True

            match2 = re.search(r'(\d+|\d+\.\d+)([MG])', self.min_flow)
            flow_num = match2.group(1)
            flow_unit = match2.group(2)

            if b == flow_unit and float(a) < float(flow_num):
                traffic = True
            if b == 'M' and flow_unit == 'G':
                traffic = True
        logger.info(f'剩余天数：{delta_days}，流量剩余：{a + b if a and b else None}')

        self.need_order = False
        if expire or traffic:
            self.need_order = True

    def run_task(self):
        if self.need_order is None:
            self.check_subscribe()

        if self.need_order is True:
            self.order()


def main():
    resolve_proxy()

    global cache
    configs = []
    if os.path.exists(configs_file) and os.path.isfile(configs_file):
        with open(configs_file) as f:
            # data = json.load(f)
            configs = yaml.load(f, Loader=yaml.FullLoader)
    else:
        logger.warning(f'请在脚本同目录下添加文件名为{configs_file}的机场配置文件')

    if os.path.exists(cache_file) and os.path.isfile(cache_file):
        with open(cache_file) as f:
            cache = json.load(f)

    for config in configs:
        email = config.get('email')
        password = config.get('password')
        domain = config.get('domain')
        jc_type = config.get('type')
        order_form_period = config.get('order_form_period')
        order_form_plan_id = config.get('order_form_plan_id')
        min_days = config.get('min_days')
        min_flow = config.get('min_flow')

        try:
            if jc_type == 2:
                ShengFeng(email, password, domain, order_form_period, order_form_plan_id, min_days, min_flow).run()
            else:
                Task(email, password, domain, order_form_period, order_form_plan_id).run()
        except Exception as e:
            logger.error(f'出错：{e}')

    with open(cache_file, 'w') as f:
        f.write(json.dumps(new_cache, indent=2))


if __name__ == '__main__':
    main()
