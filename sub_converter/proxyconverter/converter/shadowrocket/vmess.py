import json
import urllib.parse
from typing import Tuple

from loguru import logger

from ...helper import base64_encode, remove_none_value_item
from ...model import NodeInfo


def _normalize_params(node: NodeInfo) -> Tuple:
    crypto_method = node.crypto_method
    if crypto_method is None:
        crypto_method = 'auto'

    name = urllib.parse.quote(node.name)

    network = node.network
    if network is None:
        network = 'none'
    elif network == 'ws':
        network = 'websocket'
    elif network == 'tcp' and node.fake_type == 'http':
        network = 'http'
    elif network == 'tcp':
        logger.warning(f'network={network},fake_type={node.fake_type},未识别类型,默认设置network=none')
        network = 'none'

    obfs_param = node.fake_host
    if network == 'quic' or network == 'h2' or network == 'mkcp' or network == 'grpc':
        dict_obfs_param = {
            'Host': node.fake_host,
            'congestion': node.congestion,
            'header': node.fake_type,
            'seed': node.seed
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

    if network not in ['websocket', 'http', 'h2', 'grpc', 'quic', 'mkcp', 'none']:
        logger.warning(f'Shadowrocket:vmess:network={network},暂不支持')
        return ''

    base_link = f'{crypto_method}:{node.crypto_str}@{node.server}:{node.port}'
    base64_base_link = base64_encode(base_link)

    remarks = f'&remarks={name}'
    obfs_param = f'&obfsParam={obfs_param}' if obfs_param else ''
    path = f'&path={node.path}' if node.path else ''
    obfs = f'&obfs={network}'
    tls = f'&tls=1' if node.tls else ''
    peer = f'&peer={sni}' if sni else ''
    allow_insecure = '&allowInsecure=1' if node.skip_cert_verify else ''
    tfo = '&tfo=1' if node.tfo else ''
    mux = '&mux=1' if node.mux else ''
    alter_id = f'&alterId={node.alter_id}' if node.alter_id is not None else ''

    params = f'{remarks}{obfs_param}{path}{obfs}{tls}{peer}{allow_insecure}{tfo}{mux}{alter_id}'
    params = params.lstrip('&')

    link = f'vmess://{base64_base_link}?{params}'

    return link
