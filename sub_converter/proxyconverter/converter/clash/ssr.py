from typing import Dict

from ...helper import remove_none_value_item
from ...model import NodeInfo


def convert(node: NodeInfo) -> Dict:
    proxy = {
        "name": node.name,
        "type": node.protocol,
        "server": node.server,
        "port": node.port,
        'cipher': node.crypto_method,
        'password': node.crypto_str,
        'protocol': node.ssr_protocol,
        'protocol-param': node.ssr_protocol_param,
        'obfs': node.ssr_obfs,
        'obfs-param': node.ssr_obfs_param,
        'udp': node.udp
    }

    return remove_none_value_item(proxy)
