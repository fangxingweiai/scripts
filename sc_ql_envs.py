"""
cron: */5 * * * *
new Env('青龙变量操作');
"""

import os
from datetime import datetime
from json import dumps as jsonDumps

import requests

ql = None


class QL:
    def __init__(self, address: str, id: str, secret: str) -> None:
        """
        初始化
        """
        self.address = address
        self.id = id
        self.secret = secret
        self.valid = True
        self.login()

    def log(self, content: str) -> None:
        """
        日志
        """
        print(content)

    def login(self) -> None:
        """
        登录
        """
        url = f"{self.address}/open/auth/token?client_id={self.id}&client_secret={self.secret}"
        try:
            rjson = requests.get(url).json()
            if (rjson['code'] == 200):
                self.auth = f"{rjson['data']['token_type']} {rjson['data']['token']}"
            else:
                self.log(f"登录失败：{rjson['message']}")
        except Exception as e:
            self.valid = False
            self.log(f"登录失败：{str(e)}")

    def get_envs(self) -> list:
        """
        获取环境变量
        """
        url = f"{self.address}/open/envs?searchValue="
        headers = {"Authorization": self.auth}
        try:
            rjson = requests.get(url, headers=headers).json()
            if (rjson['code'] == 200):
                return rjson['data']
            else:
                self.log(f"获取环境变量失败：{rjson['message']}")
        except Exception as e:
            self.log(f"获取环境变量失败：{str(e)}")

    def delete_envs(self, ids: list) -> bool:
        """
        删除环境变量
        """
        url = f"{self.address}/open/envs"
        headers = {"Authorization": self.auth, "content-type": "application/json"}
        try:
            rjson = requests.delete(url, headers=headers, data=jsonDumps(ids)).json()
            if (rjson['code'] == 200):
                self.log(f"删除环境变量成功：{len(ids)}")
                return True
            else:
                self.log(f"删除环境变量失败：{rjson['message']}")
                return False
        except Exception as e:
            self.log(f"删除环境变量失败：{str(e)}")
            return False

    def add_envs(self, envs: list) -> bool:
        """
        新建环境变量
        """
        url = f"{self.address}/open/envs"
        headers = {"Authorization": self.auth, "content-type": "application/json"}
        try:
            rjson = requests.post(url, headers=headers, data=jsonDumps(envs)).json()
            if (rjson['code'] == 200):
                self.log(f"新建环境变量成功：{len(envs)}")
                return True
            else:
                self.log(f"新建环境变量失败：{rjson['message']}")
                return False
        except Exception as e:
            self.log(f"新建环境变量失败：{str(e)}")
            return False

    def update_env(self, env: dict) -> bool:
        """
        更新环境变量
        """
        url = f"{self.address}/open/envs"
        headers = {"Authorization": self.auth, "content-type": "application/json"}
        try:
            rjson = requests.put(url, headers=headers, json=env).json()
            if (rjson['code'] == 200):
                self.log(f"更新环境变量成功")
                return True
            else:
                self.log(f"更新环境变量失败：{rjson['message']}")
                return False
        except Exception as e:
            self.log(f"更新环境变量失败：{str(e)}")
            return False

    def disable_env_by_id(self, env_id):
        url = f'{self.address}/open/envs/disable'
        headers = {"Authorization": self.auth, "content-type": "application/json"}

        try:
            rjson = requests.put(url, headers=headers, json=[env_id]).json()
            if (rjson['code'] == 200):
                self.log(f"禁用环境变量成功")
                return True
            else:
                self.log(f"禁用环境变量失败：{rjson['message']}")
                return False
        except Exception as e:
            self.log(f"禁用环境变量失败：{str(e)}")
            return False

    def enable_env_by_id(self, env_id):
        url = f'{self.address}/open/envs/enable'
        headers = {"Authorization": self.auth, "content-type": "application/json"}

        try:
            rjson = requests.put(url, headers=headers, json=[env_id]).json()
            if (rjson['code'] == 200):
                self.log(f"启用环境变量成功")
                return True
            else:
                self.log(f"启用环境变量失败：{rjson['message']}")
                return False
        except Exception as e:
            self.log(f"启用环境变量失败：{str(e)}")
            return False


def init_ql():
    global ql
    if ql is None:
        ql_env = os.getenv('ql_env')
        if ql_env is None:
            print('没有设置环境变量：ql_env')
            return

        address, client_id, client_secret = ql_env.split('#')
        ql = QL(address, client_id, client_secret)


# 切换电信ck
def exchange_telecom_ck():
    init_ql()
    envs = ql.get_envs()
    for env in envs:
        env_name = env['name']
        if env_name == 'chinaTelecomAccount':
            env_id = env['id']
            env_value = env['value']

            # 头部ck放置尾部
            b = env_value.split('&')
            b.append(b.pop(0))
            env_value = '&'.join(b)

            new_env = {"name": env_name, "value": env_value, "id": env_id}
            ql.update_env(new_env)


# 禁用/启用京东代理
def disable_jd_proxy():
    init_ql()
    # 112 JD_PROXY_OPEN
    ql.disable_env_by_id(112)


def enable_jd_proxy():
    init_ql()
    # 112 JD_PROXY_OPEN
    ql.enable_env_by_id(112)


# 转换jd试用ck
def transform_jd_try_ck():
    init_ql()
    envs = ql.get_envs()

    jd_ck_list = []
    for env in envs:
        name = env['name']
        if name == 'JD_COOKIE':
            value = env['value'].rstrip(';').replace('pt_key=', '').replace('pt_pin=', '').replace(';', '@')
            jd_ck_list.append(value)

    jd_ck = '#'.join(jd_ck_list)

    new_env = {"name": "jd_ck", "value": jd_ck, "id": 117}
    ql.update_env(new_env)


def main():
    now = datetime.now()
    hour = now.hour
    minute = now.minute

    if hour == 23 and minute == 55:
        exchange_telecom_ck()

    if hour == 3 and minute == 30:
        disable_jd_proxy()
    if hour == 22 and minute == 30:
        enable_jd_proxy()

    if hour in [6, 10, 13, 16, 20, 23] and minute == 25:
        transform_jd_try_ck()


if __name__ == "__main__":
    main()
