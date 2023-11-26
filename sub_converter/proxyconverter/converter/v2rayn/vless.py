import urllib.parse
from typing import Tuple

from loguru import logger

from ...model import NodeInfo


def _normalize_params(node: NodeInfo) -> Tuple:
    network = node.network
    header_type = node.fake_type

    if network == 'http':  # sr:vless:http
        network = 'tcp'
        header_type = 'http'
    elif network == 'none' or network is None:  # sr:vless:tcp=none
        network = 'tcp'
        header_type = 'none'
    elif network == 'websocket':
        network = 'ws'

    crypto_method = node.crypto_method
    if crypto_method == 'auto' or crypto_method is None:  # ?
        crypto_method = 'none'

    xtls_flow = None
    sec = None
    if node.xtls:
        sec = 'xtls'
        xtls_flow = node.xtls_flow
    elif node.tls:
        sec = 'tls'

    sni = node.sni
    if not sni and network == 'ws' and node.fake_host:
        sni = node.fake_host

    return network, header_type, crypto_method, xtls_flow, sec, sni


def convert(node: NodeInfo) -> str:
    network, header_type, crypto_method, xtls_flow, sec, sni = _normalize_params(node)

    if network not in ['tcp', 'ws', 'grpc']:
        logger.warning(f'v2rayN:vless:network={network},暂不支持')
        return ''

    # vless://72972da9-d188-40c6-83a6-4ec28fde2c0a@cg.rutracker-cn.com:443?encryption=none&flow=xtls-rprx-origin&security=tls&sni=cg.rutracker-cn.com&alpn=h2%2Chttp%2F1.1&type=tcp&headerType=http&host=test.com#testde%E6%B5%8B%E8%AF%95
    # vless://cba4a4a4-5651-4424-b3b7-14ebd3a4bbfc@baidu.com:443?encryption=none&flow=xtls-rprx-origin&security=tls&sni=sni.com&alpn=h2%2Chttp%2F1.1&type=ws&host=fake.http.com&path=%2Fpathdddddddddfdfsdf#v2rayN%E7%9A%84vless
    # 'vless://cba4a4a4-5651-4424-b3b7-14ebd3a4bbfc@baidu.com:443?encryption=none&flow=xtls-rprx-origin&security=xtls&sni=sni.com&alpn=h2%2Chttp%2F1.1&type=grpc&serviceName=%2Fpathdddddddddfdfsdf&mode=gun#v2rayN%E7%9A%84vless'
    encryption = f'&encryption={crypto_method}'
    flow = f'&flow={xtls_flow}' if xtls_flow else ''
    security = f'&security={sec}' if sec else ''
    sni = f'&sni={sni}' if sni else ''
    alpn = f'&alpn={urllib.parse.quote_plus(node.alpn)}' if node.alpn else ''
    type_ = f'&type={network}' if network else ''
    header_type = f'&headerType={header_type}' if header_type else ''
    host = f'&host={node.fake_host}' if node.fake_host else ''
    path = f'&path={urllib.parse.quote_plus(node.path)}' if node.path else ''
    servicename = f'&serviceName={urllib.parse.quote_plus(node.path)}' if network == 'grpc' and node.path else ''
    mode = f'&mode={node.grpc_mode}' if node.grpc_mode else ''

    params = f'{encryption}{flow}{security}{sni}{alpn}{type_}{header_type}{host}{path}{servicename}{mode}'
    params = params.lstrip('&')

    name = urllib.parse.quote(node.name)

    link = f'vless://{node.crypto_str}@{node.server}:{node.port}?{params}#{name}'

    return link
