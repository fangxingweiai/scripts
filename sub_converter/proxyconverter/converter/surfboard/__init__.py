import os
from typing import Tuple, List

from . import socks, ss, trojan, vmess, http
from ...helper import check_and_rename

converter_map = {
    'http': http.convert,
    'socks': socks.convert,
    'socks5': socks.convert,
    'ss': ss.convert,
    'trojan': trojan.convert,
    'vmess': vmess.convert,
}


def gen_config(proxies: List[Tuple]):
    sub_data = [
        '[General]',
        'dns-server = 8.8.8.8, 114.114.114.114',
        'skip-proxy = 127.0.0.1, 192.168.0.0/16, 10.0.0.0/8, 172.16.0.0/12, 100.64.0.0/10, localhost, *.local',
        'proxy-test-url = http://www.gstatic.com/generate_204',
        'http-listen = 0.0.0.0:1087',
        'socks5-listen = 0.0.0.0:1086',
        '[Proxy]'
    ]

    proxy_nodes = []
    # proxy_name_list = []
    for proxy in proxies:
        name, proxy_data = proxy

        name = check_and_rename(proxy_nodes, name)
        # proxy_name_list.append(name)

        line = f'{name} = {proxy_data}'
        sub_data.append(line)

    # names = ', '.join(proxy_name_list)

    sub_data.append('[Proxy Group]')

    select_group = f'Proxy = select, Auto, Fallback, Load-Balance, include-all-proxies=true'
    sub_data.append(select_group)

    auto_group = f'Auto = url-test, include-all-proxies=true, url=http://www.gstatic.com/generate_204, interval=600, tolerance=100, timeout=5'
    sub_data.append(auto_group)

    fallback_group = f'Fallback = fallback, include-all-proxies=true, url=http://www.gstatic.com/generate_204, interval=600, timeout=5'
    sub_data.append(fallback_group)

    load_balance_group = f'Load-Balance = load-balance, include-all-proxies=true'
    sub_data.append(load_balance_group)

    sub_data.append('[Rule]')
    sub_data.append('DOMAIN-SUFFIX, deta.dev, DIRECT')
    sub_data.append(
        'DOMAIN-SET, https://mirror.ghproxy.com/https://raw.githubusercontent.com/Loyalsoldier/surge-rules/release/private.txt, DIRECT')
    # sub_data.append('DOMAIN-SET, https://cdn.jsdelivr.net/gh/Loyalsoldier/surge-rules@release/reject.txt, REJECT')
    sub_data.append(
        'DOMAIN-SET, https://mirror.ghproxy.com/https://raw.githubusercontent.com/Loyalsoldier/surge-rules/release/proxy.txt, Proxy, force-remote-dns')
    sub_data.append(
        'DOMAIN-SET, https://mirror.ghproxy.com/https://raw.githubusercontent.com/Loyalsoldier/surge-rules/release/direct.txt, DIRECT')
    sub_data.append(
        'RULE-SET, https://mirror.ghproxy.com/https://raw.githubusercontent.com/Loyalsoldier/surge-rules/release/ruleset/telegramcidr.txt, Proxy')
    # sub_data.append('RULE-SET, https://cdn.jsdelivr.net/gh/Loyalsoldier/surge-rules@release/cncidr.txt, DIRECT')
    sub_data.append('GEOIP, CN, DIRECT')
    sub_data.append('FINAL, Proxy')

    sub_content = os.linesep.join(sub_data)
    return sub_content
