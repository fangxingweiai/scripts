import base64
import ipaddress
import json
import os
import re
import time
from typing import Dict, List

import requests
from urllib3.exceptions import InsecureRequestWarning

from .model import NodeInfo

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def is_sub_url(url: str):
    return url.strip().startswith(('http://', 'https://')) and url.count('/') > 2


def is_ss_sub(content: str):
    try:
        data = json.loads(content)
        if data and isinstance(data, List):
            node = data[0]
            if 'remarks' in node and 'method' in node and 'password' in node and 'server_port' in node:
                return True
    except:
        pass
    return False


def is_clash_sub(content: str):
    if content.startswith('proxies'):  # 只有节点的订阅
        return True

    if "rules:" in content and 'proxy-groups:' in content:  # 普通clash订阅
        return True

    return False


def is_clash_proxy(proxy: dict) -> bool:
    return 'type' in proxy and 'name' in proxy and 'server' in proxy and 'port' in proxy


def create_base_clash_node(proxy: Dict) -> NodeInfo:
    node = NodeInfo()

    node.protocol = proxy.get('type')
    node.name = proxy.get('name')
    node.server = proxy.get('server')
    node.port = str_to_int(proxy.get('port'))
    return node


def create_base_node(proxy: str) -> (str, NodeInfo):
    node = NodeInfo()

    protocol, proxy_data = proxy.split('://', 1)

    node.protocol = protocol

    return proxy_data, node


def remove_none_value_item(d):
    if isinstance(d, dict):
        return dict([i for i in d.items() if i[1] is not None]) or None
    else:
        return d


def is_base64(i: str):
    # return re.match(r'^([A-Za-z0-9+/]{4})*([A-Za-z0-9+/]{4}|[A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{2}==)$', i)
    try:
        base64_decode(i)
        return True
    except:
        return False


def str_to_int(s):
    if isinstance(s, int):
        return s
    if not isinstance(s, str):
        return None
    s = s.strip()
    if s.isnumeric():
        return int(s)
    return None


def base64_decode(content):
    content = content.strip().replace('\r\n', '').replace('\r', '').replace('\n', '') \
        .replace(' ', '').replace('-', '+').replace('_', '/')

    content_length = len(content)
    if content_length % 4 != 0:
        content = content.ljust(content_length + 4 - content_length % 4, "=")

    return str(base64.b64decode(content), "utf-8").strip()


def base64_encode(content):
    bytes_content = content.encode(encoding='utf-8')
    return base64.b64encode(bytes_content).decode('utf-8')


def is_valid_node(node: NodeInfo):
    server = node.server
    port = node.port

    if server is None or not isinstance(server, str):
        return False

    # 1 ~ 65535
    if port is None or port < 1 or port > 65535:
        return False

    server = server.strip()

    if server == "1.1.1.1" or server == "1.0.0.1" or server == "0.0.0.0":
        return False

    try:
        ip_addr = ipaddress.ip_address(server)
        if ip_addr.is_multicast or ip_addr.is_private or ip_addr.is_loopback or ip_addr.is_link_local or ip_addr.is_reserved or ip_addr.is_unspecified:
            return False
    except ValueError as e:
        if '.' not in server:
            return False

    return True


def request(url, method='GET', data=None, json=None, headers=None, allow_redirects=True, retry=2, text_return=True):
    if headers is None:
        # headers = {'User-Agent': 'ClashforWindows/0.20.30'}
        headers = {'User-Agent': 'clash-verge/v1.3.6'}

    proxies = None
    http_proxy = os.getenv('http_proxy')
    if http_proxy:
        proxies = {
            "http": http_proxy,
            'https': http_proxy
        }
    while retry:
        try:
            resp = requests.request(method, url, headers=headers, json=json, data=data, proxies=proxies,
                                    allow_redirects=allow_redirects, verify=False, timeout=2)
            if text_return:
                return resp.text.strip()
            else:
                return resp
        except:
            retry -= 1
            time.sleep(3)


def remove_special_characters(content):
    return bytes(content, "ascii", "ignore").decode()


def check_and_rename(nodes: list, name):
    while True:
        if name not in nodes:
            nodes.append(name)
            return name
        else:
            name = name + '-重复'
            r = check_and_rename(nodes, name)
            if r:
                return r


def load_resources():
    # 从secrets加载
    links_str = os.environ.get('LINKS')
    if links_str:
        return list(filter(lambda x: x.strip() != "", re.split('\r\n|\r|\n', links_str.strip())))

    # 从文件加载
    with open('./resources.txt', 'r') as f:
        return list(filter(lambda x: x.strip() != "", [i.strip() for i in f.readlines()]))


def save_conf(conf, dir_, filename):
    if not os.path.exists(dir_):
        os.mkdir(dir_)

    with open(f'./{dir_}/{filename}', 'w') as f:
        f.write(conf)


if __name__ == '__main__':
    print(time.time())
    time.sleep(2)
    print(time.time())
