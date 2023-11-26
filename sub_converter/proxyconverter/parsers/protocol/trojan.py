import json
import re
import urllib.parse
from typing import Union, Dict

from loguru import logger

from ...helper import create_base_node, str_to_int, create_base_clash_node
from ...model import NodeInfo


def _resolve_params(node: NodeInfo, param: str):
    param_name, param_value = param.split('=', 1)

    if param_name == 'type' or param_name == 'obfs':  # ??
        node.network = param_value
    elif param_name == 'obfsParam':
        try:
            json_data = urllib.parse.unquote(param_value)
            dict_data = json.loads(json_data)
            node.fake_host = dict_data.get('Host')
        except:
            logger.warning(f'trojan:{param}参数未能解析')
    elif param_name == 'headerType':
        node.fake_type = param_value
    elif param_name == 'mode':
        node.grpc_mode = param_value
    elif param_name == 'host' or param_name == 'obfs-host':
        node.fake_host = param_value
    elif param_name == 'path' or param_name == 'serviceName' or param_name == 'obfs-uri':
        node.path = urllib.parse.unquote(param_value)
    elif param_name == 'xtls':
        if param_value == '1':
            node.xtls = True
            node.xtls_flow = 'xtls-rprx-direct'
    elif param_name == 'security':
        if param_value == 'tls':
            node.tls = True
        elif param_value == 'xtls':
            node.xtls = True
        else:
            logger.warning(f'trojan:{param}未知')
    elif param_name == 'sni' or param_name == 'peer':
        node.sni = param_value
    elif param_name == 'flow':
        node.xtls_flow = param_value

    elif param_name == 'alpn':
        node.alpn = urllib.parse.unquote(param_value)
    elif param_name == 'tfo':
        node.tfo = True if param_value == '1' else None
    elif param_name == 'mux':
        node.mux = True if param_value == '1' else None
    elif param_name == 'plugin':  # 小火箭 ws
        param_list = param_value.split(';')

        node.plugin = param_list.pop(0)

        for i in param_list:
            _resolve_params(node, i)
    elif param_name == 'allowInsecure':
        node.skip_cert_verify = True if param_value == '1' else None  # allowInsecure=1，允许不安全（跳过证书验证）, v2rayN无效
    elif param_name == 'encryption':
        node.crypto_method = param_value
    else:
        logger.warning(f'trojan:params:{param},未能解析')


def parse_str_trojan(trojan: str) -> NodeInfo:
    trojan_data, node = create_base_node(trojan)

    rest, name = trojan_data.rsplit('#', 1)
    node.name = urllib.parse.unquote(name)

    if '?' in rest:
        main_info, params = rest.rsplit('?', 1)
    else:
        main_info = rest
        params = None

    node.crypto_str, server_and_port = main_info.rsplit('@', 1)
    node.server, port = server_and_port.split(':')
    if port.isnumeric():
        node.port = str_to_int(port)
    else:
        # 3424/
        node.port = re.match(r'\d+', port).group()
        logger.warning(f'trojan连接中port后面出现特殊字符：{port}')

    if params:
        param_list = params.split('&')
        for param in param_list:
            _resolve_params(node, param)

    return node


def parse_clash_trojan(trojan: Dict) -> NodeInfo:
    node = create_base_clash_node(trojan)

    node.crypto_str = trojan.get('password')
    node.udp = trojan.get('udp')
    node.sni = trojan.get('sni') or node.server

    alpn = trojan.get('alpn')
    if alpn:
        node.alpn = ','.join(alpn)

    node.skip_cert_verify = trojan.get('skip-cert-verify')

    if network := trojan.get('network'):
        node.network = network

        if network == 'ws':
            if opts := trojan.get('ws-opts'):
                node.path = opts.get('path')

                if headers := opts.get('headers'):
                    node.fake_host = headers.get('Host')
        elif network == 'grpc':
            if opts := trojan.get('grpc-opts'):
                node.path = opts.get('grpc-service-name')
        else:
            logger.warning(f'clash:trojan:network={network},未能解析')
    return node


def parse(trojan: Union[str, Dict]) -> NodeInfo:
    node = None
    if isinstance(trojan, str):
        node = parse_str_trojan(trojan)
    elif isinstance(trojan, Dict):
        node = parse_clash_trojan(trojan)
    return node
