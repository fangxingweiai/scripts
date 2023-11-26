from typing import List, Dict

import yaml

from . import http, snell, socks, ss, ssr, trojan, vmess
from ...helper import check_and_rename

converter_map = {
    'http': http.convert,
    'snell': snell.convert,
    'socks': socks.convert,
    'socks5': socks.convert,
    'ss': ss.convert,
    'ssr': ssr.convert,
    'trojan': trojan.convert,
    'vmess': vmess.convert,
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
        "profile": {
            "store-selected": True,
            "store-fake-ip": True
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
                "https://223.5.5.5/dns-query",
                "https://pdns.itxe.net/dns-query"
            ],
            "fallback": [
                "tls://1.0.0.1",
                "https://doh.dns.sb/dns-query",
                "https://pdns.itxe.net/dns-query"
            ],
            "fallback-filter": {
                "geoip": True,
                "geoip-code": "CN",
                "ipcidr": [
                    "240.0.0.0/4",
                    "0.0.0.0/32"
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

    rule_providers = {
        "proxy": {
            "type": "http",
            "behavior": "domain",
            "url": "https://yanyu.ltd/https://raw.githubusercontent.com/Loyalsoldier/clash-rules/release/proxy.txt",
            "path": "./ruleset/proxy.yaml",
            "interval": 86400
        },
        "direct": {
            "type": "http",
            "behavior": "domain",
            "url": "https://yanyu.ltd/https://raw.githubusercontent.com/Loyalsoldier/clash-rules/release/direct.txt",
            "path": "./ruleset/direct.yaml",
            "interval": 86400
        },
        # "applications": {
        #     "type": "http",
        #     "behavior": "classical",
        #     "url": "https://yanyu.ltd/https://raw.githubusercontent.com/Loyalsoldier/clash-rules/release/applications.txt",
        #     "path": "./ruleset/applications.yaml",
        #     "interval": 86400
        # },
        # "lancidr": {
        #     "type": "http",
        #     "behavior": "ipcidr",
        #     "url": "https://yanyu.ltd/https://raw.githubusercontent.com/Loyalsoldier/clash-rules/release/lancidr.txt",
        #     "path": "./ruleset/lancidr.yaml",
        #     "interval": 86400
        # },
        # "cncidr": {
        #     "type": "http",
        #     "behavior": "ipcidr",
        #     "url": "https://yanyu.ltd/https://raw.githubusercontent.com/Loyalsoldier/clash-rules/release/cncidr.txt",
        #     "path": "./ruleset/cncidr.yaml",
        #     "interval": 86400
        # },
        "telegramcidr": {
            "type": "http",
            "behavior": "ipcidr",
            "url": "https://yanyu.ltd/https://raw.githubusercontent.com/Loyalsoldier/clash-rules/release/telegramcidr.txt",
            "path": "./ruleset/telegramcidr.yaml",
            "interval": 86400
        },
        "private": {
            "type": "http",
            "behavior": "domain",
            "url": "https://yanyu.ltd/https://raw.githubusercontent.com/Loyalsoldier/clash-rules/release/private.txt",
            "path": "./ruleset/private.yaml",
            "interval": 86400
        }
    }
    dict_config['rule-providers'] = rule_providers

    dict_config['rules'] = [
        "DOMAIN-SUFFIX,deta.app,DIRECT",
        "RULE-SET,private,DIRECT",
        f"RULE-SET,proxy,{select_group_name}",
        "RULE-SET,direct,DIRECT",

        'GEOIP,private,DIRECT,no-resolve',
        f"RULE-SET,telegramcidr,{select_group_name}",
        "GEOIP,CN,DIRECT",
        f"MATCH,{select_group_name}"
    ]

    config = yaml.dump(dict_config, allow_unicode=True, default_flow_style=False, sort_keys=False)
    return config
