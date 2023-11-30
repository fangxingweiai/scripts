import json
from typing import List, Dict

from . import http, socks, ss, ssr, trojan, vless, vmess, hysteria

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
                {
                    "tag": "google",
                    "address": "tls://8.8.8.8"
                },
                {
                    "tag": "local",
                    "address": "223.5.5.5",
                    "detour": "direct"
                }
            ],
            "rules": [
                {
                    "outbound": "any",
                    "server": "local"
                }
            ],
            "strategy": "ipv4_only"
        },
        "inbounds": [
            {
                "type": "mixed",
                "tag": "mixed-in",
                "listen": "::",
                "listen_port": 7890
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
                    "url": "https://yanyu.ltd/https://raw.githubusercontent.com/SagerNet/sing-geoip/rule-set/geoip-cn.srs",
                    "download_detour": "direct"
                },
                {
                    "type": "remote",
                    "tag": "geosite-cn",
                    "format": "binary",
                    "url": "https://yanyu.ltd/https://raw.githubusercontent.com/SagerNet/sing-geosite/rule-set/geosite-cn.srs",
                    "download_detour": "direct"
                },
                {
                    "type": "remote",
                    "tag": "geosite-geolocation-!cn",
                    "format": "binary",
                    "url": "https://yanyu.ltd/https://raw.githubusercontent.com/SagerNet/sing-geosite/rule-set/geosite-geolocation-!cn.srs",
                    "download_detour": "direct"
                },
                {
                    "type": "remote",
                    "tag": "geosite-category-companies@cn",
                    "format": "binary",
                    "url": "https://yanyu.ltd/https://raw.githubusercontent.com/SagerNet/sing-geosite/rule-set/geosite-category-companies@cn.srs",
                    "download_detour": "direct"
                }
            ],
            "rules": [
                {
                    "port": 53,
                    "outbound": "dns-out"
                },
                {
                    "network": "udp",
                    "port": 443,
                    "outbound": "block"
                },
                {
                    "ip_is_private": True,
                    "outbound": "direct"
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
            "auto_detect_interface": True
        },
        "experimental": {
            "clash_api": {
                "external_controller": "127.0.0.1:9090",
                "external_ui": "UI",
                "external_ui_download_url": "https://yanyu.ltd/https://github.com/MetaCubeX/Yacd-meta/archive/gh-pages.zip",
                "external_ui_download_detour": "direct",
                "secret": "",
                "default_mode": "rule",
            },
            "cache_file": {
                "enabled": True,
                "path": "cache.db",
                "cache_id": "windows",
                # "store_fakeip": True
            }
        }
    }
    return json.dumps(config, indent=2)
