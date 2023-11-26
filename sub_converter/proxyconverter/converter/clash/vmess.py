from typing import Dict

from loguru import logger

from ...helper import remove_none_value_item
from ...model import NodeInfo


def _normalize_params(node: NodeInfo) -> str:
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
    return network


def convert(node: NodeInfo) -> Dict:
    network = _normalize_params(node)
    if network and network not in ['ws', 'http', 'h2', 'grpc']:
        logger.warning(f'clash:vmess:network={network},暂不支持')
        return {}

    proxy = {
        "name": node.name,
        "type": node.protocol,
        "server": node.server,
        "port": node.port,
        "uuid": node.crypto_str,
        "alterId": node.alter_id,
        "cipher": node.crypto_method or 'auto',

        "tls": node.tls,
        "skip-cert-verify": node.skip_cert_verify,
        "servername": node.sni,  # priority over wss host

        # common
        "udp": node.udp,
        "network": network
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
    elif network == 'http':
        proxy.pop('tls')
        proxy.pop('servername')

        opts = {}

        if node.fake_host:
            hosts = node.fake_host.split(',')
            opts['headers'] = {
                "Host": hosts
            }
        if node.path:
            if ',' in node.path:  # ?
                path = node.path.split(',')
            else:
                path = node.path
            opts['path'] = path

        if opts:
            proxy['http-opts'] = opts
    elif network == 'h2':
        opts = {}
        if node.fake_host:
            hosts = node.fake_host.split(',')
            opts['host'] = hosts
        if node.path:
            opts['path'] = node.path
        if opts:
            proxy['h2-opts'] = opts
    elif network == 'grpc' and node.path:
        opts = {
            'grpc-service-name': node.path
        }
        proxy['grpc-opts'] = opts

    return remove_none_value_item(proxy)
