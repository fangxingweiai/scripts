from typing import Dict

from ...helper import remove_none_value_item
from ...model import NodeInfo


def convert(node: NodeInfo) -> Dict:
    tls = None
    if node.tls:
        tls = {
            "enabled": True,
            "server_name": node.sni,
            "insecure": node.skip_cert_verify
        }

    proxy = remove_none_value_item({
        "type": "http",
        "tag": node.name,

        "server": node.server,
        "server_port": node.port,
        "username": node.username,
        "password": node.crypto_str,
        "tls": remove_none_value_item(tls),

        # 拨号字段
        "tcp_fast_open": node.tfo
    })

    return proxy
