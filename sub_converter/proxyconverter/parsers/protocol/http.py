from typing import Dict

from ...helper import create_base_clash_node
from ...model import NodeInfo


def parse_clash_http(http: Dict) -> NodeInfo:
    node = create_base_clash_node(http)

    node.username = http.get('username')
    node.crypto_str = http.get('password')
    node.tls = http.get('tls')
    node.skip_cert_verify = http.get('skip-cert-verify')
    node.sni = http.get('sni')
    return node


def parse(http: Dict) -> NodeInfo:
    node = parse_clash_http(http)
    return node
