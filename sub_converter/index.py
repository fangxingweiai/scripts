import copy
import time

from loguru import logger

from sub_converter.db import user_db, config_db
from sub_converter.proxyconverter import parse, Client, convert, gen
from sub_converter.utils import get_current_datetime
from sub_converter.utils import is_expired


class ConfigFactory(object):
    def __init__(self):
        self.cf_hosts = ['icook.tw', '1.0.0.1', 'cloudflare.com', 'cf.000714.xyz', 'cf.186526.xyz', 'cdn.linil.ml',
                         'cdn.shendubaigei.xyz', 'amp.cloudflare.com', 'www.digitalocean.com', 'www.garmin.com',
                         '1.0.0.0',
                         'domain08.mqcjuc.ml', 'namesilo.com', 'virmach.com', 'ip.sb', 'ping.pe', 'teraco.co.za',
                         'zayo.com',
                         '365datacenters.com', 'tanium.com', 'crowdstrike.com', 'medium.com', 'workers.dev', 'uicdn.cf',
                         'cf.521024.xyz', 'cf.188187.xyz', 'cf.515188.xyz', 'cloudflare.tv']
        # 缓存解析过得link
        self.cache = {}

    @staticmethod
    def get_info_node():
        # 提示节点
        proxy = 'vmess://ew0KICAidiI6ICIyIiwNCiAgInBzIjogIuaPkOekuuiKgueCuSIsDQogICJhZGQiOiAidGVzdC5jb20iLA0KICAicG9ydCI6ICI0NDMiLA0KICAiaWQiOiAiMjAzZDZmNjYtYmQ5Yy00N2YzLTk4MmItNGFkZTkxYjVhZjA0IiwNCiAgImFpZCI6ICIwIiwNCiAgInNjeSI6ICJhdXRvIiwNCiAgIm5ldCI6ICJ3cyIsDQogICJ0eXBlIjogIm5vbmUiLA0KICAiaG9zdCI6ICIiLA0KICAicGF0aCI6ICIiLA0KICAidGxzIjogIiIsDQogICJzbmkiOiAiIiwNCiAgImFscG4iOiAiIg0KfQ=='
        info_node = parse(proxy)[0]
        info_node.server = '127.0.0.1'
        return info_node

    @staticmethod
    def gen_config_from_nodes(nodes, client: Client):
        proxies = convert(nodes, client)
        config = gen(proxies, client)
        return config

    def gen_cf_nodes(self, nodes):
        cf_nodes = []
        for i, node in enumerate(nodes, 1):
            for j, cf_host in enumerate(self.cf_hosts, 1):
                cf_node = copy.deepcopy(node)
                cf_node.name = f'{node.name}-{cf_host}'
                cf_node.server = cf_host
                cf_nodes.append(cf_node)
        return cf_nodes

    def resolve_user_nodes(self, nodes, expire_time, token):
        for i, node in enumerate(nodes, 1):
            node.name = f'N{i}'

        token_node = self.get_info_node()
        token_node.name = f'key:{token}'
        nodes.insert(0, token_node)

        tip_node = self.get_info_node()
        if is_expired(expire_time):
            tip_node.name = f'quá hạn'
        else:
            tip_node.name = f'HSD:{"∞" if expire_time == "-1" else expire_time}'

        nodes.insert(0, tip_node)

    @staticmethod
    def resolve_ml_nodes(nodes, ml_host):
        ml_nodes = [node for node in nodes if node.protocol == 'vmess' or node.protocol == 'vless']
        for node in ml_nodes:
            node.fake_host = ml_host
        return ml_nodes

    def gen_configs(self, info):
        expire_time = info['expired_time']
        token = info["key"]
        is_cf = info['is_cf']
        ml_host = info['ml_host']
        clients = info['clients']

        if is_expired(expire_time):
            # 过期
            nodes = []
        else:
            links = info['links']

            nodes = []
            for link in links:
                if cached_nodes := self.cache.get(link):
                    logger.info(f'{link} 命中解析缓存')
                    nodes.extend(cached_nodes)
                else:
                    if new_nodes := parse(link):
                        nodes.extend(new_nodes)
                        self.cache[link] = new_nodes

            if len(nodes) == 0:
                logger.info(f'全部解析后，没有有效节点')
                return

            nodes.sort(key=lambda x: x.protocol)

        if is_cf:
            nodes = self.gen_cf_nodes(nodes)
        else:
            if ml_host:
                nodes = self.resolve_ml_nodes(nodes, ml_host)

            self.resolve_user_nodes(nodes, expire_time, token)

        data = {}
        for client in clients:
            for i in Client:
                if client == i.value:
                    config = self.gen_config_from_nodes(nodes, i)
                    if client == 'surfboard':
                        config = f'#!MANAGED-CONFIG https://proxycenter-1-f2333586.deta.app/config/{token}/surfboard interval=3600 strict=true\n{config}'

                    data[client] = config
                    break

        return data


#########################################
def _task(factory):
    users = user_db.fetch().items
    for user in users:
        active = user["active"]
        logger.info(user)
        if active:
            expire_time = user['expired_time']
            token = user["key"]

            if is_expired(expire_time):
                # 过期
                logger.info(f'user: [{token}] 过期')
                user_db.update({'active': False}, token)

            if configs := factory.gen_configs(user):
                config_db.put(configs, token)

                user_db.update({'last_update': get_current_datetime()}, token)


def task():
    logger.info(f'=======开始运行订阅转换脚本=======')
    factory = ConfigFactory()
    max_retry_num = 3
    while max_retry_num:
        try:
            _task(factory)
            break
        except Exception as e:
            logger.error(e)
        time.sleep(10)
        max_retry_num -= 1
