from loguru import logger

from ...model import NodeInfo


def _normalize_params(node: NodeInfo) -> str:
    network = node.network
    if network == 'websocket':
        network = 'ws'
    elif network == 'none' or (network == 'tcp' and node.fake_type != 'http'):
        network = None

    return network


def convert(node: NodeInfo) -> str:
    network = _normalize_params(node)
    if network and network not in ['ws']:
        logger.warning(f'Leaf:vmess:network={network},暂不支持')
        return ''

    username = f', username={node.crypto_str}' if node.crypto_str else ''
    ws = ', ws=true' if network else ''
    tls = ', tls=true' if node.tls else ''
    ws_path = f', ws-path={node.path}' if ws and node.path else ''
    ws_host = f', ws-host={node.fake_host}' if ws and node.fake_host else ''

    # tls-cert???
    link = f'{node.protocol}, {node.server}, {node.port}{username}{ws}{tls}{ws_path}{ws_host}'
    return link
