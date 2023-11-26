from typing import Tuple

from loguru import logger

from ...model import NodeInfo


def _normalize_params(node: NodeInfo) -> Tuple:
    network = node.network
    if network == 'websocket':
        network = 'ws'
    elif network == 'tcp' and node.fake_type == 'http':  # surfboard tcp默认可
        network = 'http'

    sni = node.sni
    if not sni and network == 'ws' and node.fake_host:
        sni = node.fake_host
    return network, sni


def convert(node: NodeInfo) -> str:
    network, sni = _normalize_params(node)

    if network and network not in ['ws', 'tcp']:
        logger.warning(f'Surfboard:vmess:network={network},暂不支持')
        return ''

    # https://getsurfboard.com/docs/profile-format/proxy/
    username = f', username={node.crypto_str}'

    udp_relay = ''
    if node.udp is True:
        udp_relay = f', udp-relay=true'
    elif node.udp is False:
        udp_relay = f', udp-relay=false'

    ws = ', ws=true' if network else ''

    tls = ''
    if node.tls is True:
        tls = ', tls=true'
    elif node.tls is False:
        tls = ', tls=false'

    ws_path = f', ws-path={node.path}' if ws and node.path else ''
    ws_headers = f', ws-headers={"Host:" + node.fake_host}' if ws and node.fake_host else ''

    skip_cert_verify = ''
    if node.skip_cert_verify is True:
        skip_cert_verify = f', skip-cert-verify=true'
    elif node.skip_cert_verify is False:
        skip_cert_verify = f', skip-cert-verify=false'

    sni = f', sni={sni}' if sni else ''

    vmess_aead = ''
    if node.alter_id is not None and node.alter_id > 0:
        vmess_aead = ', vmess-aead=false'

    link = f'{node.protocol}, {node.server}, {node.port}{username}{udp_relay}{ws}{tls}{ws_path}{ws_headers}{skip_cert_verify}{sni}{vmess_aead}'
    return link
