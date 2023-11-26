import os
from typing import List, Tuple

from . import ss, trojan, vmess
from ...helper import check_and_rename

converter_map = {
    'ss': ss.convert,
    'trojan': trojan.convert,
    'vmess': vmess.convert,
}


def gen_config(proxies: List[Tuple]):
    sub_data = [
        '[General]',
        'loglevel = info',
        'dns-server = 8.8.8.8, 114.114.114.114',
        'interface = 127.0.0.1',
        'port = 1087',
        'socks-interface = 127.0.0.1',
        'socks-port = 1086',
        '[Proxy]',
        'Direct = direct',
        'Reject = reject',
    ]

    proxy_nodes = []
    proxy_name_list = []
    for proxy in proxies:
        name, proxy_data = proxy

        name = check_and_rename(proxy_nodes, name)
        proxy_name_list.append(name)

        line = f'{name} = {proxy_data}'
        sub_data.append(line)

    names = ', '.join(proxy_name_list)

    sub_data.append('[Proxy Group]')
    auto_group = f'Proxy = fallback, {names}, interval=600, timeout=5'
    sub_data.append(auto_group)

    sub_data.append('[Rule]')
    sub_data.append('DOMAIN-SUFFIX, deta.dev, Direct')
    sub_data.append('EXTERNAL, site:category-ads-all, Reject')
    sub_data.append('EXTERNAL, site:geolocation-!cn, Proxy')
    sub_data.append('EXTERNAL, site:cn, Direct')
    sub_data.append('GEOIP, CN, Direct')
    sub_data.append('FINAL, Proxy')

    sub_content = os.linesep.join(sub_data)
    return sub_content
