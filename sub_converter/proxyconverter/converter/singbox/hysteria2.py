from typing import Tuple

from ...helper import remove_none_value_item
from ...model import NodeInfo


def _normalize_params(node: NodeInfo) -> Tuple:
    up = f'{node.up}'
    down = f'{node.down}'

    if up and 'ps' not in up:
        up = f'{up} Mbps'

    if down and 'ps' not in down:
        down = f'{down} Mbps'

    if node.sni:
        node.tls = True
    return up, down


def convert(node: NodeInfo) -> dict:
    # up, down = _normalize_params(node)

    tls = None
    if node.tls or True:  # hysteria 都要tls？
        tls = {
            "enabled": True,
            "server_name": node.sni,
            "insecure": node.skip_cert_verify
        }

    proxy = remove_none_value_item({
        "type": "hysteria2",
        "tag": node.name,
        "server": node.server,
        "server_port": node.port,
        "up_mbps": node.up,
        "down_mbps": node.down,
        # "obfs": {
        #     "type": "salamander",
        #     "password": "cry_me_a_r1ver"
        # },
        "password": node.crypto_str,
        "network": node.network,
        "tls": remove_none_value_item(tls),
        # "brutal_debug": False,
    })
    return proxy
