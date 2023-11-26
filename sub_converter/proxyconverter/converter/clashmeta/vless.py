from typing import Tuple, Dict

from loguru import logger

from ...helper import remove_none_value_item
from ...model import NodeInfo


def _normalize_params(node: NodeInfo) -> Tuple:
    network = node.network

    if network == 'websocket':
        network = 'ws'
    elif network == 'none' or network == 'tcp':
        network = None

    xtls_flow = node.xtls_flow
    if xtls_flow == '1':
        xtls_flow = 'xtls-rprx-direct'
    elif node.xtls_flow == '0':
        xtls_flow = None

    return network, xtls_flow


def convert(node: NodeInfo) -> Dict:
    network, xtls_flow = _normalize_params(node)
    if network and network not in ['ws', 'grpc']:
        logger.warning(f'clashmeta:vless:network={network},暂不支持')
        return {}

    proxy = {
        "name": node.name,
        "type": node.protocol,
        "server": node.server,
        "port": node.port,
        "uuid": node.crypto_str,
        "servername": node.sni,
        'flow': xtls_flow,
        'skip-cert-verify': node.skip_cert_verify,
        "tls": node.tls,
        'udp': node.udp,
        "network": network,
        "reality-opts": remove_none_value_item({
            'public-key': node.public_key,
            'short-id': node.short_id
        }),
        "client-fingerprint": node.fingerprint
    }

    if network == 'ws':
        opts = {}
        if node.path:
            opts['path'] = node.path
        if node.fake_host:
            opts['headers'] = {
                "Host": node.fake_host
            }
            if not proxy['servername']:
                proxy['servername'] = node.fake_host
        if opts:
            proxy['ws-opts'] = opts
    elif network == 'grpc' and node.path:
        opts = {
            'grpc-service-name': node.path
        }
        proxy['grpc-opts'] = opts

    return remove_none_value_item(proxy)
