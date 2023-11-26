import urllib.parse

from ...helper import base64_encode
from ...model import NodeInfo


def convert(node: NodeInfo) -> str:
    # ss://YWVzLTI1Ni1nY206WTZSOXBBdHZ4eHptR0M=@134.195.196.231:5600#%E6%B5%8B%E8%AF%95

    crypto_info = f'{node.crypto_method}:{node.crypto_str}'
    base64_crypto_info = base64_encode(crypto_info)

    name = urllib.parse.quote(node.name)

    link = f'ss://{base64_crypto_info}@{node.server}:{node.port}#{name}'

    return link
