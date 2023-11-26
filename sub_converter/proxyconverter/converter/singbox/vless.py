from typing import Tuple

from loguru import logger

from ...helper import remove_none_value_item
from ...model import NodeInfo


def _normalize_params(node: NodeInfo) -> Tuple:
    network = node.network
    if network == 'none':
        network = None
    elif network == 'websocket':
        network = 'ws'
    elif network == 'tcp':  # v2rayN:tcp headerType=none or http
        if node.fake_type == 'http':
            network = 'http'
        elif node.fake_type == 'none':
            network = None

    host = node.fake_host
    if network == 'http':
        host = node.fake_host.split(',')

    sni = node.sni
    if not sni and network == 'ws' and node.fake_host:
        sni = node.fake_host
    return network, host, sni


def convert(node: NodeInfo) -> dict:
    network, host, sni = _normalize_params(node)

    if network and network not in ['http', 'ws', 'grpc', 'quic']:
        logger.warning(f'singbox:vless:network={network},暂不支持')
        return {}

    tls = None
    if node.tls:
        tls = {
            "enabled": True,
            "server_name": sni,
            "insecure": node.skip_cert_verify,

            "utls": remove_none_value_item({
                "enabled": True if node.fingerprint else False,
                "fingerprint": node.fingerprint
            }),

            "reality": remove_none_value_item({
                "enabled": True if node.public_key and node.short_id else False,
                "public_key": node.public_key,
                "short_id": node.short_id
            })

        }

    transport = None
    if network:
        transport = {"type": network}
        if network == 'http':
            transport.update({
                "host": host,
                "path": node.path,
                # "method": "",
                # "headers": {}
            })
        elif network == 'ws':
            transport.update({
                "path": node.path,
                "headers": remove_none_value_item({
                    "Host": host
                }),
                "max_early_data": node.max_early_data,
                "early_data_header_name": node.early_data_header_name
            })
        elif network == 'quic':
            pass
        elif network == 'grpc':
            transport.update({
                "service_name": node.path
            })

    proxy = remove_none_value_item({
        "type": "vless",
        "tag": node.name,

        "server": node.server,
        "server_port": node.port,
        "uuid": node.crypto_str,
        "flow": node.xtls_flow,
        # "network": "tcp",
        "tls": remove_none_value_item(tls),

        "transport": remove_none_value_item(transport),

        # 拨号字段
        "tcp_fast_open": node.tfo
    })

    return proxy
