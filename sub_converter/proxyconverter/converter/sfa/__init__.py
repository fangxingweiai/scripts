import json
from typing import List, Dict

from ..singbox import http, socks, ss, ssr, trojan, vless, vmess, hysteria, hysteria2

converter_map = {
    'http': http.convert,
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
    proxy_name_list = [proxy['tag'] for proxy in proxies]
    config = {
        "log": {
            "disabled": True,
            "level": "debug",
            "output": "",
            "timestamp": True
        },
        "dns": {
            "servers": [
                {
                    "tag": "google",
                    "address": "https://1.1.1.1/dns-query"
                },
                {
                    "tag": "local",
                    "address": "https://223.5.5.5/dns-query",
                    "detour": "direct"
                },
                # {
                #     "tag": "remote",
                #     "address": "fakeip"
                # }
            ],
            "rules": [
                {
                    "outbound": "any",
                    "server": "local"
                },
                {
                    "type": "logical",
                    "mode": "and",
                    "rules": [
                        {
                            "rule_set": "geosite-geolocation-!cn",
                            "invert": True
                        },
                        {
                            "rule_set": [
                                "geosite-cn",
                                "geosite-category-companies@cn"
                            ]
                        }
                    ],
                    "server": "local"
                },
                # {
                #     "query_type": [
                #         "A",
                #         "AAAA"
                #     ],
                #     "server": "remote"
                # }
            ],
            # "fakeip": {
            #     "enabled": True,
            #     "inet4_range": "198.18.0.0/15",
            #     "inet6_range": "fc00::/18"
            # },
            "strategy": "ipv4_only"
        },
        "inbounds": [
            {
                "type": "mixed",
                "tag": "mixed-in",
                "listen": "::",
                "listen_port": 7890
            },
            {
                "type": "tun",
                "mtu": 9000,
                "inet4_address": "172.19.0.1/30",
                # "inet6_address": "fd08::1/126",
                "auto_route": True,
                "strict_route": True,
                "stack": "mixed",
                "sniff": True,
                "sniff_override_destination": True,
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
            "rule_set": [
                {
                    "type": "remote",
                    "tag": "geoip-cn",
                    "format": "binary",
                    "url": "https://mirror.ghproxy.com/https://raw.githubusercontent.com/SagerNet/sing-geoip/rule-set/geoip-cn.srs",
                    "download_detour": "direct"
                },
                {
                    "type": "remote",
                    "tag": "geosite-cn",
                    "format": "binary",
                    "url": "https://mirror.ghproxy.com/https://raw.githubusercontent.com/SagerNet/sing-geosite/rule-set/geosite-cn.srs",
                    "download_detour": "direct"
                },
                {
                    "type": "remote",
                    "tag": "geosite-geolocation-!cn",
                    "format": "binary",
                    "url": "https://mirror.ghproxy.com/https://raw.githubusercontent.com/SagerNet/sing-geosite/rule-set/geosite-geolocation-!cn.srs",
                    "download_detour": "direct"
                },
                {
                    "type": "remote",
                    "tag": "geosite-category-companies@cn",
                    "format": "binary",
                    "url": "https://mirror.ghproxy.com/https://raw.githubusercontent.com/SagerNet/sing-geosite/rule-set/geosite-category-companies@cn.srs",
                    "download_detour": "direct"
                }
            ],
            "rules": [
                {
                    "protocol": "dns",
                    "outbound": "dns-out"
                },
                {
                    "ip_is_private": True,
                    "outbound": "direct"
                },
                {
                    "protocol": "stun",
                    "outbound": "block"
                },
                {
                    "protocol": "quic",
                    "outbound": "block"
                },
                {
                    "type": "logical",
                    "mode": "and",
                    "rules": [
                        {
                            "rule_set": "geosite-geolocation-!cn",
                            "invert": True
                        },
                        {
                            "rule_set": [
                                "geoip-cn",
                                "geosite-cn",
                                "geosite-category-companies@cn"
                            ]
                        }
                    ],
                    "outbound": "direct"
                }
            ],
            "final": "Select",
            "auto_detect_interface": True,
            # "override_android_vpn": True
        },
        "experimental": {
            "clash_api": {
                "external_controller": "127.0.0.1:9090",
                # "external_ui": "web",
                # "external_ui_download_url": "https://mirror.ghproxy.com/https://github.com/MetaCubeX/Yacd-meta/archive/gh-pages.zip",
                # "external_ui_download_detour": "direct",
                "secret": "",
                "default_mode": "rule"
            },
            "cache_file": {
                "enabled": True,
                "path": "cache.db",
                "cache_id": "sfa",
                # "store_fakeip": True
            }
        }
    }
    return json.dumps(config, indent=2)
