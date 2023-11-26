from typing import Dict

from ...helper import remove_none_value_item
from ...model import NodeInfo


def convert(node: NodeInfo) -> Dict:
    proxy = remove_none_value_item({
        "type": "socks",
        "tag": node.name,

        "server": node.server,
        "server_port": node.port,
        "version": "5",
        "username": node.username,
        "password": node.crypto_str,
        # "network": node.udp,
        "udp_over_tcp": node.udp_over_tcp,

        # 拨号字段
        "tcp_fast_open": node.tfo
    })
    return proxy
