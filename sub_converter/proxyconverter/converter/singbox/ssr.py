from ...helper import remove_none_value_item
from ...model import NodeInfo


def convert(node: NodeInfo) -> dict:
    proxy = remove_none_value_item({
        "type": "shadowsocksr",
        "tag": node.name,

        "server": node.server,
        "server_port": node.port,
        "method": node.crypto_method,
        "password": node.crypto_str,
        "obfs": node.ssr_obfs,
        "obfs_param": node.ssr_obfs_param,
        "protocol": node.ssr_protocol,
        "protocol_param": node.ssr_protocol_param,
        # "network": "udp",

        # 拨号字段
        "tcp_fast_open": node.tfo
    })
    return proxy
