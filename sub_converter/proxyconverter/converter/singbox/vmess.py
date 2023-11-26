from typing import Tuple

from loguru import logger

from ...helper import remove_none_value_item
from ...model import NodeInfo


def _normalize_params(node: NodeInfo) -> Tuple:
    network = node.network
    if network == 'tcp' and node.fake_type == 'http':
        network = 'http'
    elif network == 'websocket':
        network = 'ws'
    elif network == 'none':
        network = None
    elif network == 'tcp':
        # logger.warning(f'network={network},fake_type={node.fake_type},未识别类型,默认设置network=None')
        network = None

    host = node.fake_host
    if network == 'http':
        host = node.fake_host.split(',')

    crypto_method = node.crypto_method if node.crypto_method else 'auto'

    sni = node.sni
    if not sni and network == 'ws' and node.fake_host:
        sni = node.fake_host
    return network, host, crypto_method, sni


def convert(node: NodeInfo) -> dict:
    network, host, scy, sni = _normalize_params(node)

    if network and network not in ['ws', 'http', 'quic', 'grpc']:
        logger.warning(f'singbox:vmess:network={network},暂不支持')
        return {}

    tls = None
    if node.tls:
        tls = {
            "enabled": True,
            "server_name": sni,
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
            "type": network,
            "path": node.path,
            "headers": remove_none_value_item({
                "Host": host
            }),
            "max_early_data": node.max_early_data,
            "early_data_header_name": node.early_data_header_name
        }
    elif network == 'quic':
        transport = {
            "type": network
        }
    elif network == 'grpc':
        transport = {
            "type": network,
            "service_name": node.path
        }

    proxy = remove_none_value_item({
        "type": "vmess",
        "tag": node.name,

        "server": node.server,
        "server_port": node.port,
        "uuid": node.crypto_str,
        "security": scy,
        "alter_id": node.alter_id,

        "tls": remove_none_value_item(tls),

        "transport": remove_none_value_item(transport),

        # 拨号字段
        "tcp_fast_open": node.tfo
    })
    return proxy
