import json
import urllib.parse
from typing import Tuple

from loguru import logger

from ...helper import remove_none_value_item
from ...model import NodeInfo


def _normalize_params(node: NodeInfo) -> Tuple:
    name = urllib.parse.quote(node.name)

    network = node.network
    if network == 'ws':
        network = 'websocket'
    elif network == 'tcp':  # sr:torjan基础设置参数无network 默认tcp？
        network = None

    plugin = node.plugin
    if plugin is None:
        if network == 'websocket':
            plugin = 'obfs-local'

    obfs_param = None
    if network == 'grpc':
        dict_obfs_param = {
            'Host': node.fake_host
        }
        if dict_obfs_param := remove_none_value_item(dict_obfs_param):
            json_obfs_param = json.dumps(dict_obfs_param)
            obfs_param = urllib.parse.quote(json_obfs_param)

    return name, network, plugin, obfs_param


def convert(node: NodeInfo) -> str:
    name, network, plugin, obfs_param = _normalize_params(node)

    if network and network not in ['websocket', 'grpc']:
        logger.warning(f'Shadowrocket:vmess:network={network},暂不支持')
        return ''

    base_link = f'{node.crypto_str}@{node.server}:{node.port}'

    allow_insecure = '&allowInsecure=1' if node.skip_cert_verify else ''
    peer = f'&peer={node.sni}' if node.sni else ''
    tfo = '&tfo=1' if node.tfo else ''
    mux = '&mux=1' if node.mux else ''
    xtls = '&xtls=1' if node.xtls else ''
    alpn = f'&alpn={node.alpn}' if node.alpn else ''

    obfs = f'&obfs={network}' if network == 'websocket' or network == 'grpc' else ''

    ws_plugin = ''
    obfs_host = ''
    obfs_uri = ''
    grpc_obfs_param = ''
    path = ''
    if network == 'websocket':
        ws_plugin = f'&plugin={plugin}'  # ws->obfs-local

        obfs = obfs.replace('&', ';', 1)
        # websocket
        obfs_host = f';obfs-host={node.fake_host}' if plugin and node.fake_host else ''
        obfs_uri = f';obfs-uri={node.path}' if plugin and node.path else ''
    elif network == 'grpc':
        grpc_obfs_param = f'&obfsParam={obfs_param}' if obfs_param else ''
        path = f'&path={node.path}' if node.path else ''

    params = f'{allow_insecure}{peer}{tfo}{mux}{xtls}{alpn}{ws_plugin}{obfs}{obfs_host}{obfs_uri}{grpc_obfs_param}{path}'
    params = params.lstrip('&')

    link = f'trojan://{base_link}?{params}#{name}'

    return link
