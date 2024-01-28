from typing import Dict

from ...helper import remove_none_value_item
from ...model import NodeInfo


def convert(node: NodeInfo) -> Dict:
    proxy = {
        "name": node.name,
        "type": node.protocol,
        "server": node.server,
        "port": node.port,
        "up": node.up,
        "down": node.down,
        "password": node.crypto_str,

        "obfs": node.hy2_obfs,
        "obfs-password": node.obfs_password,

        "sni": node.sni,
        'skip-cert-verify': node.skip_cert_verify,

        "fingerprint": node.fingerprint,
        "alpn": node.alpn
    }

    return remove_none_value_item(proxy)
