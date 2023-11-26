import urllib.parse
from typing import Union, Dict

from ...helper import create_base_node, base64_decode, str_to_int, create_base_clash_node
from ...model import NodeInfo


def parse_str_socks(socks: str) -> NodeInfo:
    socks_data, node = create_base_node(socks)

    # socks://dXNlcm5hbWVkZnNkOnBhc3N3b3JkZGZzZGY=@baidu.com:443#testsocks
    rest, name = socks_data.rsplit('#')

    node.name = urllib.parse.unquote(name)

    user_and_pwd, addr_and_port = rest.rsplit('@')
    node.server, port = addr_and_port.split(':')
    node.port = str_to_int(port)

    decoded_data = base64_decode(user_and_pwd)
    node.username, node.crypto_str = decoded_data.split(':')

    return node


def parse_clash_socks(socks: Dict) -> NodeInfo:
    node = create_base_clash_node(socks)

    node.username = socks.get('username')
    node.crypto_str = socks.get('password')
    node.tls = socks.get('tls')
    node.skip_cert_verify = socks.get('skip-cert-verify')
    node.udp = socks.get('udp')
    return node


def parse(socks: Union[str, Dict]) -> NodeInfo:
    node = None
    if isinstance(socks, str):
        node = parse_str_socks(socks)
    elif isinstance(socks, Dict):
        node = parse_clash_socks(socks)
    return node
