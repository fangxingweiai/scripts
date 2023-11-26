from typing import Union, Dict

from ...helper import create_base_clash_node
from ...model import NodeInfo


def parse_clash_hysteria(hysteria: Dict) -> NodeInfo:
    node = create_base_clash_node(hysteria)

    node.up = hysteria.get('up')
    node.down = hysteria.get('down')
    node.crypto_str = hysteria.get('auth_str')
    node.sni = hysteria.get('sni')
    node.skip_cert_verify = hysteria.get('skip-cert-verify')
    node.hy_protocol = hysteria.get('protocol')
    node.hy_ports = hysteria.get('ports')
    node.hy_obfs = hysteria.get('obfs')
    node.tfo = hysteria.get('fast-open')
    node.disable_mtu_discovery = hysteria.get('disable_mtu_discovery')
    node.fingerprint = hysteria.get('fingerprint')
    return node


def parse(hysteria: Union[str, Dict]) -> NodeInfo:
    node = None
    if isinstance(hysteria, Dict):
        node = parse_clash_hysteria(hysteria)
    return node
