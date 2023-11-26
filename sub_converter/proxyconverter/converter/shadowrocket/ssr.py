from typing import Tuple

from ...helper import base64_encode
from ...model import NodeInfo


def _normalize_params(node: NodeInfo) -> Tuple:
    crypto_str = node.crypto_str
    password = base64_encode(crypto_str)

    name = base64_encode(node.name)
    protoparam = base64_encode(node.ssr_protocol_param) if node.ssr_protocol_param else ''
    obfsparam = base64_encode(node.ssr_obfs_param) if node.ssr_obfs_param else ''

    return password, name, protoparam, obfsparam


def convert(node: NodeInfo) -> str:
    password, name, protoparam, obfsparam = _normalize_params(node)

    base_link = f'{node.server}:{node.port}:{node.ssr_protocol}:{node.crypto_method}:{node.ssr_obfs}:{password}'
    remarks = f'&remarks={name}'
    protoparam = f'&protoparam={protoparam}'
    obfsparam = f'&obfsparam={obfsparam}'
    tfo = '&tfo=1' if node.tfo else ''

    params = f'{remarks}{protoparam}{obfsparam}{tfo}'
    params = params.lstrip('&')

    origin_link = f'{base_link}/?{params}'

    base64_link = base64_encode(origin_link)
    link = f'ssr://{base64_link}'

    return link
