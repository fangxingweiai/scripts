from typing import List, Dict

import yaml

from . import vless, hysteria, hysteria2
from ..clash import http, snell, socks, ss, ssr, trojan, vmess
from ...helper import check_and_rename

converter_map = {
    'http': http.convert,
    'snell': snell.convert,
    'socks': socks.convert,
    'socks5': socks.convert,
    'ss': ss.convert,
    'ssr': ssr.convert,
    'trojan': trojan.convert,
    'vless': vless.convert,
    'vmess': vmess.convert,
    'hysteria': hysteria.convert,
    'hysteria2': hysteria2.convert,
}


def gen_config(proxies: List[Dict]):
    dict_config = {
        # "port": 1087,
        # "socks-port": 1086,
        "mixed-port": 7890,
        "allow-lan": False,
        "mode": "rule",
        "log-level": "info",
        "external-controller": "127.0.0.1:9090",
        "tcp-concurrent": True,
        "find-process-mode": "strict",
        "global-client-fingerprint": "chrome",
        "profile": {
            "store-selected": True,
            "store-fake-ip": True
        },
        "geodata-mode": True,
        "geox-url": {
            "geoip": "https://cdn.jsdelivr.net/gh/Loyalsoldier/geoip@release/geoip.dat",
            "geosite": "https://cdn.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@releases/latest/download/geosite.dat",
            "mmdb": "https://cdn.jsdelivr.net/gh/Loyalsoldier/geoip@release/Country.mmdb"
        },
        "sniffer": {
            "enable": True,
            "sniff": {
                "TLS": {
                    "ports": [443, 8443]
                },
                "HTTP": {
                    "ports": [80, "8080-8880"],
                    "override-destination": True
                }
            }
        },
        "tun": {
            "enable": True,
            "stack": "system",
            "dns-hijack": [
                "any:53"
            ],
            "auto-route": True,
            "auto-detect-interface": True
        },
        "dns": {
            "enable": True,
            "listen": ":1053",
            "use-hosts": True,
            "ipv6": False,
            "enhanced-mode": "fake-ip",
            "fake-ip-range": "198.18.0.1/16",
            "fake-ip-filter": ["*", "+.lan", "+.local"],
            "default-nameserver": [
                "223.5.5.5",
                "119.29.29.29"
            ],
            "nameserver": [
                "tls://1.0.0.1",
                "https://doh.dns.sb/dns-query",
                "https://pdns.itxe.net/dns-query"
            ],
            "proxy-server-nameserver": [
                "https://223.5.5.5/dns-query",
                "https://pdns.itxe.net/dns-query"
            ],
            "nameserver-policy": {
                "geosite:tld-cn,cn,private": [
                    "223.5.5.5",
                    "119.29.29.29"
                ]
            }
        }
    }

    proxy_name_list = []
    clash_proxies = []

    name_check_list = []
    for proxy in proxies:
        name = check_and_rename(name_check_list, proxy["name"])
        proxy['name'] = name

        proxy_name_list.append(name)
        clash_proxies.append(proxy)

    dict_config['proxies'] = clash_proxies

    load_balance_group_name = 'load-balance'
    load_balance_group = {
        "name": load_balance_group_name,
        "type": "load-balance",
        "proxies": proxy_name_list,
        "url": "http://www.gstatic.com/generate_204",
        "interval": 300,
        'lazy': True
    }

    fallback_auto_group_name = 'fallback-auto'
    fallback_auto_group = {
        "name": fallback_auto_group_name,
        "type": "fallback",
        "proxies": proxy_name_list,
        "url": "http://www.gstatic.com/generate_204",
        "interval": 300,
        'lazy': True
    }

    url_test_group_name = 'auto'
    url_test_group = {
        "name": url_test_group_name,
        "type": "url-test",
        "proxies": proxy_name_list,
        "url": "http://www.gstatic.com/generate_204",
        "interval": 300,
        'lazy': True
    }

    select_group_name = 'proxy'
    select_group = {
        "name": select_group_name,
        "type": "select",
        "proxies": [
            url_test_group_name,
            fallback_auto_group_name,
            load_balance_group_name,
            *proxy_name_list
        ]
    }

    dict_config['proxy-groups'] = [
        select_group,
        fallback_auto_group,
        url_test_group,
        load_balance_group
    ]

    dict_config['rules'] = [
        "DOMAIN-SUFFIX,deta.app,DIRECT",
        'geosite,private,DIRECT',
        f'geosite,geolocation-!cn,{select_group_name}',
        'geosite,cn,DIRECT',
        'geosite,tld-cn,DIRECT',

        'geoip,private,DIRECT,no-resolve',
        f'geoip,telegram,{select_group_name}',
        'geoip,cn,DIRECT',
        f'MATCH,{select_group_name}'
    ]

    config = yaml.dump(dict_config, allow_unicode=True, default_flow_style=False, sort_keys=False)
    return config
