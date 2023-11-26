import json
from typing import List, Dict

from ..singbox import http, socks, ss, ssr, trojan, vless, vmess, hysteria

converter_map = {
    'http': http.convert,
    'socks': socks.convert,
    'socks5': socks.convert,
    'ss': ss.convert,
    'ssr': ssr.convert,
    'trojan': trojan.convert,
    'vless': vless.convert,
    'vmess': vmess.convert,
    'hysteria': hysteria.convert
}


def gen_config(proxies: List[Dict]):
    proxy_name_list = [proxy['tag'] for proxy in proxies]
    config = {
        "log": {
            "disabled": False,
            "level": "debug",
            "output": "",
            "timestamp": True
        },
        "dns": {
            "servers": [
                # {
                #     "tag": "dns-fakeip",
                #     "address": "fakeip"
                # },
                {
                    "tag": "dns-proxy",
                    "address": "https://1.1.1.1/dns-query",
                    "address_resolver": "dns-local",
                    "address_strategy": "ipv4_only",
                    "detour": "direct"
                },
                {
                    "tag": "dns-proxy-server",
                    "address": "https://pdns.itxe.net/dns-query",
                    "address_resolver": "dns-local",
                    "address_strategy": "ipv4_only",
                    "detour": "direct"
                },
                {
                    "tag": "dns-local",
                    "address": "223.5.5.5",
                    "detour": "direct"
                },
                {
                    "tag": "dns-block",
                    "address": "rcode://success"
                }
            ],
            "rules": [
                {
                    "query_type": [
                        "HTTPS",
                        "SVCB"
                    ],
                    "server": "dns-block",
                    "disable_cache": True
                },
                {
                    "domain_suffix": [
                        ".arpa.",
                        ".arpa"
                    ],
                    "server": "dns-block",
                    "disable_cache": True
                },
                {
                    "geosite": ["cn", "private"],
                    "server": "dns-local"
                },
                {
                    "outbound": "any",
                    "server": "dns-proxy-server"
                },
                # {
                #     "query_type": [
                #         "A",
                #         "AAAA"
                #     ],
                #     "server": "dns-fakeip"
                # }
            ],
            "final": "dns-proxy",
            "strategy": "ipv4_only",
            # "fakeip": {
            #     "enabled": True,
            #     "inet4_range": "198.18.0.0/15",
            #     "inet6_range": "fc00::/18"
            # }
        },
        "inbounds": [
            {
                "type": "mixed",
                "tag": "mixed-in",
                "listen": "::",
                "listen_port": 7890,
                "sniff": True
            },
            {
                "type": "tun",
                "tag": "tun-in",
                "interface_name": "tun0",
                "mtu": 9000,
                "inet4_address": "172.19.0.1/30",
                "inet6_address": "fd08::1/126",
                "auto_route": True,
                "strict_route": True,
                "stack": "system",
                "sniff": True,
                "sniff_override_destination": True
            }
        ],
        "outbounds": [
            {
                "type": "selector",
                "tag": "Select",
                "outbounds": ['Auto', *proxy_name_list],
                "default": 'Auto'
            },
            {
                "type": "urltest",
                "tag": "Auto",
                "outbounds": proxy_name_list,
                "url": "http://www.gstatic.com/generate_204",
                "interval": "5m",
                "tolerance": 100
            },
            *proxies,
            {
                "type": "block",
                "tag": "block"
            },
            {
                "type": "direct",
                "tag": "direct"
            },
            {
                "type": "dns",
                "tag": "dns-out"
            }
        ],
        "route": {
            "geoip": {
                "download_url": "https://yanyu.ltd/https://github.com/soffchen/sing-geoip/releases/latest/download/geoip-cn.db",
                "download_detour": "direct"
            },
            "geosite": {
                "download_url": "https://yanyu.ltd/https://github.com/MetaCubeX/meta-rules-dat/releases/latest/download/geosite.db",
                "download_detour": "direct"
            },
            "rules": [
                {
                    "protocol": "dns",
                    "outbound": "dns-out"
                },
                {
                    "protocol": "quic",
                    "outbound": "block"
                },
                {
                    "geosite": ["cn", "private"],
                    "geoip": [
                        "cn",
                        "private"
                    ],
                    "outbound": "direct"
                }
            ],
            "final": "Select",
            "auto_detect_interface": True
        },
        "experimental": {
            "clash_api": {
                "external_controller": "127.0.0.1:9090",
                # "external_ui": "web",
                # "external_ui_download_url": "https://yanyu.ltd/https://github.com/MetaCubeX/Yacd-meta/archive/gh-pages.zip",
                # "external_ui_download_detour": "direct",
                "default_mode": "rule",
                "store_selected": True,
                # "store_fakeip": True,
                "cache_file": "cache.db"
            }
        }
    }
    return json.dumps(config, indent=2)
