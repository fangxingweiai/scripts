import json
from typing import Tuple

from ...helper import base64_encode
from ...model import NodeInfo


def _normalize_params(node: NodeInfo) -> Tuple:
    net = node.network
    fake_type = 'none'

    if net == 'http':
        net = 'tcp'
        fake_type = 'http'
    elif net == 'grpc':
        fake_type = node.fake_type
    elif net == 'websocket':
        net = 'ws'
    elif net == 'none' or net is None:
        net = ''

    tls = 'tls' if node.tls else ''

    sni = node.sni
    if not sni and net == 'ws' and node.fake_host:
        sni = node.fake_host

    crypto_method = node.crypto_method if node.crypto_method else 'auto'
    path = node.path if node.path else ''
    return net, fake_type, tls, sni, crypto_method, path


def convert(node: NodeInfo) -> str:
    net, type_, tls, sni, scy, path = _normalize_params(node)

    v2_data = {
        "v": node.v,
        "ps": node.name,
        "add": node.server,
        "port": node.port,
        "id": node.crypto_str,
        "aid": node.alter_id,
        "scy": scy,
        "net": net,
        "type": type_,
        "host": node.fake_host,
        "path": path,
        "tls": tls,
        "sni": sni
    }

    base64_node_info = base64_encode(json.dumps(v2_data, ensure_ascii=False))
    link = f'vmess://{base64_node_info}'

    return link
