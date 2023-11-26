import json
import re
import urllib.parse
from typing import Union, Dict

from loguru import logger

from ...helper import create_base_node, is_base64, base64_decode, str_to_int, create_base_clash_node, is_clash_proxy
from ...model import NodeInfo


def _resolve_params(node: NodeInfo, param: str):
    param_name, param_value = param.split('=', 1)

    if param_name == 'plugin':
        if param_value not in ['obfs-local', 'obfs']:
            logger.warning(f'ss:{param}参数未能解析')
            return
        node.plugin = param_value
    elif param_name == 'obfs':
        node.plugin_param_mode = param_value
    elif param_name == 'obfsParam':  # 小火箭ws:host wss:host
        node.fake_host = param_value
    elif param_name == 'path' or param_name == 'obfs-uri':
        node.path = param_value
    elif param_name == 'obfs-host':
        if node.plugin_param_mode == 'tls':
            try:
                dict_host = json.loads(param_value)
                node.sni = dict_host.get('Host')
            except:
                node.sni = param_value
        elif node.plugin_param_mode == 'http':
            node.fake_host = param_value
        else:
            logger.warning(f'ss:{param}参数未能解析')
    elif param_name == 'fast-open' or param_name == 'tfo':
        node.tfo = True if param_value == 'true' or param_value == '1' else None
    elif param_name == 'uot':
        node.udp_over_tcp = True
    elif param_name == 'v2ray-plugin':  # 小火箭
        node.plugin = 'v2ray-plugin'
        try:
            opts = base64_decode(param_value)
            opts = json.loads(opts)
        except:
            logger.error(f'shadowrocket:ss:v2ray-plugin={param},未能解析')
            return

        node.mux = opts.get('mux')
        node.tfo = opts.get('tfo')
        node.plugin_param_mode = opts.get('mode')
        node.skip_cert_verify = opts.get('allowInsecure')
        node.tls = opts.get('tls')
        node.fake_host = opts.get('host')
        node.sni = opts.get('peer')
        node.path = opts.get('path')
    else:
        logger.warning(f'ss:params:{param},未能解析')


def parse_clash_ss(ss: Dict) -> NodeInfo:
    node = create_base_clash_node(ss)

    node.crypto_method = ss.get('cipher')
    node.crypto_str = ss.get('password')
    node.udp = ss.get('udp')

    if plugin := ss.get('plugin'):
        node.plugin = plugin

        if opts := ss.get('plugin-opts'):
            mode = opts.get('mode')
            node.plugin_param_mode = mode

            host = opts.get('host')

            if mode == 'websocket':
                node.tls = opts.get('tls')
                node.skip_cert_verify = opts.get('skip-cert-verify')
                node.fake_host = host  # ?
                node.path = opts.get('path')
            elif mode == 'tls':
                node.sni = host
            elif mode == 'http':
                node.fake_host = host
            else:
                logger.warning(f'clash:ss:plugin-opts:mode={mode},未能解析')

    return node


def parse_dict_ss(ss: Dict) -> NodeInfo:
    node = NodeInfo()
    node.protocol = 'ss'

    node.name = ss.get('remarks')
    node.server = ss.get('server')
    node.port = str_to_int(ss.get('server_port'))
    node.crypto_method = ss.get('method')
    node.crypto_str = ss.get('password')

    if plugin := ss.get('plugin'):
        node.plugin = plugin

        if opts := ss.get('plugin_opts'):  # obfs:mode,host
            mode = opts.get('mode')
            host = opts.get('host')

            node.plugin_param_mode = mode

            if mode == 'tls':
                node.sni = host
            elif mode == 'http':
                node.fake_host = host
            else:
                logger.warning(f'ss:plugin_opts:mode={mode},未能解析')

            if len(opts.keys()) > 2:
                logger.warning(f'ss:plugin_opts={opts},未能全解析')
    return node


def parse_str_ss(ss: str) -> NodeInfo:
    ss_data, node = create_base_node(ss)

    proxy_data, proxy_name = ss_data.split('#')
    node.name = urllib.parse.unquote(proxy_name)

    params = None
    if '@' in proxy_data:
        cry_info, rest = proxy_data.split('@')
        if is_base64(cry_info):
            cry_info = base64_decode(cry_info)
        else:  # 'ss://2022-blake3-aes-128-gcm:aHU5RjJFU3lWUTNSc2VNVmZqNzdwdU1lWFYyMWhBdXE=@217.145.236.128:21506#HKG'
            cry_method, cry_str = cry_info.split(':')
            if is_base64(cry_method):
                cry_method = base64_decode(cry_method)
            if is_base64(cry_str):
                cry_str = base64_decode(cry_str)
            cry_info = f'{cry_method}:{cry_str}'  # 统一格式，接下来一起处理
        if '?' in rest:
            server_and_port, params = rest.split('?', 1)
        else:
            server_and_port = rest
    elif '?' in proxy_data:  # 小火箭
        base64_data, params = proxy_data.split('?', 1)
        decoded_data = base64_decode(base64_data)
        cry_info, server_and_port = decoded_data.rsplit('@', 1)
    elif is_base64(proxy_data):
        decoded_data = base64_decode(proxy_data)
        cry_info, rest = decoded_data.rsplit('@', 1)
        if '?' in rest:
            server_and_port, params = rest.split('?', 1)
        else:
            server_and_port = rest
    else:
        logger.warning(f'未识ss格式: ss://{proxy_data}')
        return node

    node.crypto_method, node.crypto_str = cry_info.split(':')

    node.server, port = server_and_port.split(':')
    node.port = str_to_int(port)

    if params:
        params = urllib.parse.unquote(params)

        param_list = re.split(r';|&', params)
        if param_list:
            for param in param_list:
                _resolve_params(node, param)
        else:
            logger.warning(f'ss:params={params}参数未能解析')
    return node


def parse(ss_data: Union[str, Dict]) -> NodeInfo:
    node = None
    if isinstance(ss_data, str):
        node = parse_str_ss(ss_data)
    elif isinstance(ss_data, Dict):
        if is_clash_proxy(ss_data):
            node = parse_clash_ss(ss_data)
        else:
            node = parse_dict_ss(ss_data)
    return node
