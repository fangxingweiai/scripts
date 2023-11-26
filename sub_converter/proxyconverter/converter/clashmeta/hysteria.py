from typing import Dict

from ...helper import remove_none_value_item
from ...model import NodeInfo


def convert(node: NodeInfo) -> Dict:
    proxy = {
        "name": node.name,
        "type": node.protocol,
        "server": node.server,
        "port": node.port,
        "ports": node.hy_ports,
        "auth_str": node.crypto_str,
        "auth-str": node.crypto_str,
        "obfs": node.hy_obfs,

        "protocol": node.hy_protocol,
        "up": node.up,
        "down": node.down,
        "sni": node.sni,
        'skip-cert-verify': node.skip_cert_verify,

        "disable_mtu_discovery": node.disable_mtu_discovery,
        "fingerprint": node.fingerprint,
        "fast-open": node.tfo,
    }

    return remove_none_value_item(proxy)
