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
    # https://getsurfboard.com/docs/profile-format/proxy/
    network = _normalize_params(node)

    if network and network not in ['ws']:
        logger.warning(f'Surfboard:trojan:network={network},暂不支持')
        return ''

    password = f', password={node.crypto_str}' if node.crypto_str else ''

    udp_relay = ''
    if node.udp is True:
        udp_relay = f', udp-relay=true'
    elif node.udp is False:
        udp_relay = f', udp-relay=false'

    skip_cert_verify = ''
    if node.skip_cert_verify is True:
        skip_cert_verify = f', skip-cert-verify=true'
    elif node.skip_cert_verify is False:
        skip_cert_verify = f', skip-cert-verify=false'

    sni = f', sni={node.sni}' if node.sni else ''
    ws = ', ws=true' if network else ''
    ws_path = f', ws-path={node.path}' if ws and node.path else ''
    ws_headers = f', ws-headers={"Host:" + node.fake_host}' if ws and node.fake_host else ''

    link = f'{node.protocol}, {node.server}, {node.port}{password}{udp_relay}{skip_cert_verify}{sni}{ws}{ws_path}{ws_headers}'
    return link
