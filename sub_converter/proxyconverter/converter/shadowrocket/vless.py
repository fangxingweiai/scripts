import json
import urllib.parse
from typing import Tuple

from loguru import logger

from ...helper import base64_encode, remove_none_value_item
from ...model import NodeInfo


def _normalize_params(node: NodeInfo) -> Tuple:
    crypto_method = node.crypto_method
    if crypto_method is None or crypto_method == 'none':
        crypto_method = 'auto'

    name = urllib.parse.quote(node.name) if node.name else ''

    network = node.network
    if network is None:
        network = 'none'
    elif network == 'ws':
        network = 'websocket'
    elif network == 'tcp':  # v2rayN:tcp headerType=none or http
        if node.fake_type == 'http':
            network = 'http'
        elif node.fake_type == 'none':
            network = 'none'

    obfs_param = node.fake_host
    if network == 'websocket':
        dict_obfs_param = {
            'Host': node.fake_host,
        }
        if dict_obfs_param := remove_none_value_item(dict_obfs_param):
            json_obfs_param = json.dumps(dict_obfs_param)
            obfs_param = urllib.parse.quote(json_obfs_param)

    sni = node.sni
    if not sni and network == 'websocket' and node.fake_host:
        sni = node.fake_host
    return crypto_method, name, network, obfs_param, sni


def convert(node: NodeInfo) -> str:
    crypto_method, name, network, obfs_param, sni = _normalize_params(node)

    if network not in ['websocket', 'http', 'grpc', 'none']:  # none=tcp
        logger.warning(f'Shadowrocket:vless:network={network},暂不支持')
        return ''

    base_link = f'{crypto_method}:{node.crypto_str}@{node.server}:{node.port}'
    base64_base_link = base64_encode(base_link)

    remarks = f'&remarks={name}'
    obfs_param = f'&obfsParam={obfs_param}' if obfs_param else ''  # http ws
    path = f'&path={node.path}' if node.path else ''  # http ws grpc
    obfs = f'&obfs={network}'  # tcp=none http ws grpc
    tls = f'&tls=1' if node.tls else ''
    peer = f'&peer={sni}' if sni else ''
    allow_insecure = f'&allowInsecure=1' if node.skip_cert_verify else ''
    tfo = f'&tfo=1' if node.tfo else ''
    mux = f'&mux=1' if node.mux else ''
    xtls = f'&xtls=1' if node.xtls else ''

    params = f'{remarks}{obfs_param}{path}{obfs}{tls}{peer}{allow_insecure}{tfo}{mux}{xtls}'
    params = params.lstrip('&')

    link = f'vless://{base64_base_link}?{params}'

    return link
