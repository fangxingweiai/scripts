from typing import Tuple

from loguru import logger

from ...helper import remove_none_value_item
from ...model import NodeInfo


def _normalize_params(node: NodeInfo) -> Tuple:
    plugin = node.plugin
    if plugin == 'obfs':
        plugin = 'obfs-local'

    host = node.fake_host
    if node.plugin_param_mode == 'tls':
        host = node.sni

    return plugin, host


def convert(node: NodeInfo) -> dict:
    plugin, host = _normalize_params(node)
    if plugin and plugin not in ['obfs-local', 'v2ray-plugin']:
        logger.warning(f'singbox:ss:plugin={plugin},暂不支持')
        return {}

    if node.plugin_param_mode and node.plugin_param_mode not in ['tls', 'http', 'websocket']:
        logger.warning(f'singbox:ss:{plugin}:mode={node.plugin_param_mode},暂不支持')
        return {}

    plugin_opts = None
    if plugin:
        if node.plugin_param_mode == 'http':
            params = ['obfs=http']
            if host:
                params.append(f'obfs-host={host}')
        elif node.plugin_param_mode == 'tls':
            params = ['tls']
            if host:
                params.append(f'host={host}')
        elif node.plugin_param_mode == 'websocket':
            params = ['tls']
            if host:
                params.append(f'host={host}')

    proxy = remove_none_value_item({
        "type": "shadowsocks",
        "tag": node.name,

        "server": node.server,
        "server_port": node.port,
        "method": node.crypto_method,
        "password": node.crypto_str,
        "plugin": plugin,
        "plugin_opts": plugin_opts,
        # "network": "udp",
        "udp_over_tcp": node.udp_over_tcp,
        # 拨号字段
        "tcp_fast_open": node.tfo
    })

    return proxy
