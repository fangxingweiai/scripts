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
                    "tag": "dns-proxy",
                    "address": "https://doh.dns.sb/dns-query",
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
                    "outbound": "direct",
                    "server": "dns-local"
                },
                {
                    "outbound": "any",
                    "server": "dns-proxy-server"
                }
            ],
            "final": "dns-proxy",
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
                    "port": 53,
                    "outbound": "dns-out"
                },
                {
                    "network": "udp",
                    "port": 443,
                    "outbound": "block"
                },
                {
                    "geosite": [
                        "cn",
                        "private"
                    ],
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
                "external_ui": "web",
                "external_ui_download_url": "https://yanyu.ltd/https://github.com/MetaCubeX/Yacd-meta/archive/gh-pages.zip",
                "external_ui_download_detour": "direct",
                "default_mode": "rule",
                "store_selected": True,
                # "store_fakeip": True,
                "cache_file": "cache.db"
            }
        }
    }
    return json.dumps(config, indent=2)
