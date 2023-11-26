from typing import Union, Dict

from loguru import logger

from ...helper import create_base_node, base64_decode, str_to_int, create_base_clash_node
from ...model import NodeInfo


def _resolve_params(node: NodeInfo, param: str):
    param_name, param_value = param.split('=', 1)

    if param_name == 'remarks':
        node.name = base64_decode(param_value)
    elif param_name == 'protoparam':
        node.ssr_protocol_param = base64_decode(param_value)
    elif param_name == 'obfsparam':
        node.ssr_obfs_param = base64_decode(param_value)
    elif param_name == 'tfo':
        node.tfo = True if param_value == '1' else None
    else:
        logger.warning(f'ssr:params:{param},未能解析')


def parse_str_ssr(ssr: str) -> NodeInfo:
    ssr_data, node = create_base_node(ssr)

    decoded_data = base64_decode(ssr_data)

    # 183.232.56.182:1254:auth_aes128_md5:chacha20-ietf:plain:bXRidjhu/?remarks=SmFwYW4&protoparam=MTE0ODgyOkx3ZFlMag&obfsparam=dC5tZS92cG5oYXQ
    node.server, port, node.ssr_protocol, node.crypto_method, node.ssr_obfs, rest = decoded_data.split(':')
    node.port = str_to_int(port)
    # bXRidjhu/?remarks=SmFwYW4&protoparam=MTE0ODgyOkx3ZFlMag&obfsparam=dC5tZS92cG5oYXQ
    password_base64, rest = rest.split('/?', 1)
    node.crypto_str = base64_decode(password_base64)

    # remarks=SmFwYW4&protoparam=MTE0ODgyOkx3ZFlMag&obfsparam=dC5tZS92cG5oYXQ
    param_list = rest.split('&')
    for param in param_list:
        _resolve_params(node, param)

    return node


def parse_clash_ssr(ssr: Dict) -> NodeInfo:
    node = create_base_clash_node(ssr)
    node.crypto_method = ssr.get('cipher')
    node.crypto_str = ssr.get('password')
    node.ssr_protocol = ssr.get('')
    node.ssr_protocol_param = ssr.get('protocol-param')
    node.ssr_obfs = ssr.get('obfs')
    node.ssr_obfs_param = ssr.get('obfs-param')
    node.udp = ssr.get('udp')
    return node


def parse(ssr_data: Union[str, Dict]) -> NodeInfo:
    node = None
    if isinstance(ssr_data, str):
        node = parse_str_ssr(ssr_data)
    elif isinstance(ssr_data, Dict):
        node = parse_clash_ssr(ssr_data)
    return node
