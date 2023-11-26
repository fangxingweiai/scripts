from typing import Tuple

from loguru import logger

from ...helper import remove_none_value_item
from ...model import NodeInfo


def _normalize_params(node: NodeInfo) -> Tuple:
    network = node.network

    if network == 'websocket':
        network = 'ws'
    elif network == 'tcp':  # ?
        if node.fake_type == 'http':
            network = 'http'
        else:
            network = None

    host = node.fake_host
    if network == 'http' and host:
        host = node.fake_host.split(',')
    return network, host


def convert(node: NodeInfo) -> dict:
    network, host = _normalize_params(node)

    if network and network not in ['http', 'ws', 'grpc', 'quic']:
        logger.warning(f'singbox:trojan:network={network},暂不支持')
        return {}

    tls = None
    if node.tls or node.sni:
        tls = {
            "enabled": True,
            "server_name": node.sni,
            "insecure": node.skip_cert_verify
        }

    transport = None
    if network == 'http':
        transport = {
            "type": network,
            "host": host,
            "path": node.path,
            # "method": "",
            # "headers": {}
        }
    elif network == 'ws':
        transport = {
            "path": node.path,
            "headers": remove_none_value_item({
                "Host": host
            }),
            "max_early_data": node.max_early_data,
            "early_data_header_name": node.early_data_header_name
        }
    elif network == 'quic':
        pass
    elif network == 'grpc':
        transport = {
            "service_name": node.grpc_mode
        }

    proxy = remove_none_value_item({
        "type": "trojan",
        "tag": node.name,

        "server": node.server,
        "server_port": node.port,
        "password": node.crypto_str,
        # "network": "tcp",

        "tls": remove_none_value_item(tls),

        "transport": remove_none_value_item(transport),

        # 拨号字段
        "tcp_fast_open": node.tfo
    })
    return proxy
