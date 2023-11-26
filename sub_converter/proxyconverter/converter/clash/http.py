from typing import Dict

from ...helper import remove_none_value_item
from ...model import NodeInfo


def convert(node: NodeInfo) -> Dict:
    proxy = {
        "name": node.name,
        "type": node.protocol,
        "server": node.server,
        "port": node.port,
        'username': node.username,
        'password': node.crypto_str,
        'tls': node.tls,
        'skip-cert-verify': node.skip_cert_verify,
        'sni': node.sni
    }

    return remove_none_value_item(proxy)
