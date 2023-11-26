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
    up, down = _normalize_params(node)

    tls = None
    if node.tls or True:  # hysteria 都要tls？
        tls = {
            "enabled": True,
            "server_name": node.sni,
            "insecure": node.skip_cert_verify
        }

    proxy = remove_none_value_item({
        "type": "hysteria",
        "tag": node.name,
        "server": node.server,
        "server_port": node.port,
        # ports 暂时没有
        "auth_str": node.crypto_str,
        "up": up,
        "down": down,
        "obfs": node.hy_obfs,
        "disable_mtu_discovery": node.disable_mtu_discovery,

        "tcp_fast_open": node.tfo,

        "tls": remove_none_value_item(tls),

    })
    return proxy
