from typing import Dict

from ...helper import remove_none_value_item
from ...model import NodeInfo


def _normalize_params(node: NodeInfo) -> str:
    protocol = node.protocol
    # socks socks5 socks5-tls
    if protocol == 'socks' or protocol == 'socks5-tls':
        protocol = 'socks5'

    return protocol


def convert(node: NodeInfo) -> Dict:
    protocol = _normalize_params(node)

    proxy = {
        "name": node.name,
        "type": protocol,
        "server": node.server,
        "port": node.port,
        'username': node.username,
        'password': node.crypto_str,
        'tls': node.tls,
        'skip-cert-verify': node.skip_cert_verify,
        'udp': node.udp
    }
    return remove_none_value_item(proxy)
