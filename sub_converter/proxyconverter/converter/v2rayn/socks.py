import urllib.parse

from ...helper import base64_encode
from ...model import NodeInfo


def convert(node: NodeInfo) -> str:
    # socks://dXNlcm5hbWUwMDk6cGFzc3dvcmQwMDY=@baidu.com:443#%E6%B5%8B%E8%AF%95
    name = urllib.parse.quote(node.name)

    username_and_password = f'{node.username}:{node.crypto_str}'
    base64_info = base64_encode(username_and_password)

    link = f'socks://{base64_info}@{node.server}:{node.port}#{name}'

    return link
