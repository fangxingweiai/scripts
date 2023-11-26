from loguru import logger

from ...model import NodeInfo


def _normalize_params(node: NodeInfo) -> str:
    network = node.network
    if network == 'websocket':
        network = 'ws'
    elif network == 'tcp':  # v2rayN
        network = None

    return network


def convert(node: NodeInfo) -> str:
    network = _normalize_params(node)
    if network and network not in ['ws']:
        logger.warning(f'Leaf:trojan:network={network},暂不支持')
        return ''

    password = f', password={node.crypto_str}' if node.crypto_str else ''
    sni = f', sni={node.sni}' if node.sni else ''
    ws = ', ws=true' if network else ''
    ws_path = f', ws-path={node.path}' if ws and node.path else ''
    ws_host = f', ws-host={node.fake_host}' if ws and node.fake_host else ''

    link = f'{node.protocol}, {node.server}, {node.port}{password}{sni}{ws}{ws_path}{ws_host}'
    return link
