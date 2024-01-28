from typing import Union, Dict

from ...helper import create_base_clash_node
from ...model import NodeInfo


def parse_clash_hysteria2(hysteria2: Dict) -> NodeInfo:
    node = create_base_clash_node(hysteria2)

    node.up = hysteria2.get('up')
    node.down = hysteria2.get('down')
    node.crypto_str = hysteria2.get('password')
    node.hy2_obfs = hysteria2.get('obfs')
    node.obfs_password = hysteria2.get('obfs-password')
    node.sni = hysteria2.get('sni')
    node.skip_cert_verify = hysteria2.get('skip-cert-verify')
    node.fingerprint = hysteria2.get('fingerprint')
    node.alpn = hysteria2.get('alpn')

    return node


def parse(hysteria2: Union[str, Dict]) -> NodeInfo:
    node = None
    if isinstance(hysteria2, Dict):
        node = parse_clash_hysteria2(hysteria2)
    return node
