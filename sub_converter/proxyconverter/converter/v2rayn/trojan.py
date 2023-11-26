import urllib.parse
from typing import Tuple

from loguru import logger

from ...model import NodeInfo


def _normalize_params(node: NodeInfo) -> Tuple:
    network = node.network
    header_type = None
    if network == 'websocket':
        network = 'ws'
    elif network is None:  # ?
        network = 'tcp'
        header_type = 'none'

    xtls_flow = None
    sec = None
    if node.tls:
        sec = 'tls'
    elif node.xtls:
        sec = 'xtls'
        xtls_flow = node.xtls_flow

    return network, header_type, sec, xtls_flow


def convert(node: NodeInfo) -> str:
    network, header_type, sec, xtls_flow = _normalize_params(node)

    if network not in ['tcp', 'ws', 'grpc']:
        logger.warning(f'v2rayN:trojan:network={network},暂不支持')
        return ''

    # trojan://7ee507cd-95fa-4012-aa83-ead33d77aa45@baidu.com:12041?flow=xtls-rprx-origin&security=tls&sni=baidu.fake.com&alpn=h2%2Chttp%2F1.1&type=tcp&headerType=http&host=baidu.fake.com#test
    flow = f'&flow={xtls_flow}' if xtls_flow else ''
    security = f'&security={sec}' if sec else ''
    sni = f'&sni={node.sni}' if node.sni else ''
    alpn = f'&alpn={urllib.parse.quote_plus(node.alpn)}' if node.alpn else ''
    type_ = f'&type={network}' if network else ''

    service_name = ''
    if network == 'grpc':
        service_name = f'&serviceName={urllib.parse.quote_plus(node.path)}' if node.path else ''

    mode = f'&mode={node.grpc_mode}' if node.grpc_mode else ''

    header_type = f'&headerType={header_type}' if header_type else ''

    host = ''
    if network != 'grpc':
        host = f'&host={node.fake_host}' if node.fake_host else ''

    path = ''
    if network != 'grpc':
        path = f'&path={urllib.parse.quote_plus(node.path)}' if node.path else ''

    params = f'{flow}{security}{sni}{alpn}{type_}{service_name}{mode}{header_type}{host}{path}'
    params = params.lstrip('&')

    name = urllib.parse.quote(node.name)

    link = f'trojan://{node.crypto_str}@{node.server}:{node.port}?{params}#{name}'

    return link
