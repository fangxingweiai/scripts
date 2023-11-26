from typing import Tuple, Dict

from loguru import logger

from ...helper import remove_none_value_item
from ...model import NodeInfo


def _normalize_params(node: NodeInfo) -> Tuple:
    alpn = node.alpn
    alpn = alpn.split(',') if alpn else None

    network = node.network
    if network == 'websocket':
        network = 'ws'
    elif network == 'tcp':  # v2rayN
        network = None

    return alpn, network


def convert(node: NodeInfo) -> Dict:
    alpn, network = _normalize_params(node)

    if network and network not in ['ws', 'grpc']:
        logger.warning(f'clash:trojan:network={network},暂不支持')
        return {}

    proxy = {
        "name": node.name,
        "type": node.protocol,
        "server": node.server,
        "port": node.port,
        'password': node.crypto_str,
        'udp': node.udp,
        'sni': node.sni,
        'alpn': alpn,
        'skip-cert-verify': node.skip_cert_verify,
        'network': network
    }

    if network == 'ws':
        proxy.pop('alpn')

        opts = {}
        if node.path:
            opts['path'] = node.path
        if node.fake_host:
            opts['headers'] = {
                'Host': node.fake_host
            }

        if opts := remove_none_value_item(opts):
            proxy['ws-opts'] = opts
    elif network == 'grpc':
        proxy.pop('alpn')

        opts = {}
        if node.path:
            opts = {
                'grpc-service-name': node.path
            }
        if opts:
            proxy['grpc-opts'] = opts

    return remove_none_value_item(proxy)
