import json
import urllib.parse
from typing import Union, Dict

from loguru import logger

from ...helper import str_to_int, create_base_node, base64_decode, create_base_clash_node
from ...model import NodeInfo


def _resolve_params(node: NodeInfo, param: str):
    param_name, param_value = param.split('=', 1)

    if param_name == 'remarks':
        node.name = urllib.parse.unquote(param_value)
    elif param_name == 'obfsParam':  # host grpc:{Host} quic:{header} h2:{Host} mkcp:{congestion,seed}
        host = param_value
        header = None
        congestion = None
        seed = None

        try:
            json_host = urllib.parse.unquote(param_value)
            dict_data = json.loads(json_host)
            host = dict_data.get('Host')
            header = dict_data.get('header')
            congestion = dict_data.get('congestion')
            seed = dict_data.get('seed')
        except:
            pass
        node.fake_host = host
        node.fake_type = header
        node.congestion = congestion
        node.seed = seed
    elif param_name == 'path':
        node.path = param_value
    elif param_name == 'obfs':
        node.network = param_value
    elif param_name == 'tls':
        if param_value == '1':
            node.tls = True
        elif param_value == '0':
            node.tls = False
    elif param_name == 'peer':
        node.sni = param_value
    elif param_name == 'allowInsecure':
        if param_value == '1':
            node.skip_cert_verify = True
        elif param_value == '0':
            node.skip_cert_verify = False
    elif param_name == 'tfo':
        if param_value == '1':
            node.tfo = True
        elif param_value == '0':
            node.tfo = False
    elif param_name == 'mux':
        if param_value == '1':
            node.mux = True
        elif param_value == '0':
            node.mux = False
    elif param_name == 'alterId':
        node.alter_id = str_to_int(param_value)
    else:
        logger.warning(f'vmess:params:{param},未能解析')


def parse_shadowrocket_vmess(vmess: str) -> NodeInfo:
    vmess_data, node = create_base_node(vmess)

    base64_data, params = vmess_data.split('?', 1)
    decoded_data = base64_decode((base64_data))
    cry_info, server_and_port = decoded_data.rsplit('@', 1)

    node.crypto_method, node.crypto_str = cry_info.split(':', 1)

    node.server, port = server_and_port.split(':')
    node.port = str_to_int(port)

    param_list = params.split('&')
    for param in param_list:
        _resolve_params(node, param)

    return node


def parse_v2rayn_vmess(vmess: str) -> NodeInfo:
    vmess_data, node = create_base_node(vmess)

    dict_data = json.loads(base64_decode(vmess_data))

    node.v = dict_data.get('v')
    node.name = dict_data.get('ps')
    node.server = dict_data.get('add')
    node.port = str_to_int(dict_data.get('port'))
    node.crypto_str = dict_data.get('id')
    node.alter_id = str_to_int(dict_data.get('aid'))
    node.crypto_method = dict_data.get('scy', 'auto')
    node.network = dict_data.get('net')
    node.fake_type = dict_data.get('type')
    node.fake_host = dict_data.get('host') or None
    node.path = dict_data.get('path') or None
    if tls := dict_data.get('tls'):
        if tls == 'tls':
            node.tls = True
            node.sni = dict_data.get('sni')
    node.alpn = dict_data.get('alpn')
    return node


def parse_str_vmess(vmess: str) -> NodeInfo:
    try:
        node = parse_v2rayn_vmess(vmess)
        return node
    except:
        pass

    node = parse_shadowrocket_vmess(vmess)
    return node


def parse_clash_vmess(vmess: Dict) -> NodeInfo:
    node = create_base_clash_node(vmess)

    node.crypto_str = vmess.get('uuid')
    node.alter_id = vmess.get('alterId')
    node.crypto_method = vmess.get('cipher')
    node.udp = vmess.get('udp')
    node.tls = vmess.get('tls')
    node.skip_cert_verify = vmess.get('skip-cert-verify')
    node.sni = vmess.get('servername')

    if network := vmess.get('network'):  # clash配置network为空，可能为ws,也可能为http
        node.network = network

        if network == 'ws':
            if opts := vmess.get('ws-opts'):
                node.path = opts.get('path')
                node.max_early_data = opts.get('max-early-data')
                node.early_data_header_name = opts.get('early-data-header-name')

                if headers := opts.get('headers'):
                    node.fake_host = headers.get('Host')

                    if len(headers.keys()) > 1:
                        logger.warning(f'clash:vmess:network:ws-opts:headers={headers},未能完全解析')
            if ws_path := vmess.get('ws-path'):
                node.path = ws_path
            if ws_headers := vmess.get('ws-headers'):
                if ws_host := ws_headers.get('Host'):
                    node.fake_host = ws_host
        elif network == 'http':
            if opts := vmess.get('http-opts'):
                if paths := opts.get('path'):
                    if isinstance(paths, list):
                        node.path = ','.join(paths)
                    else:
                        logger.warning(f'clash:vmess:http-opts:path={paths},未能解析')

                if headers := opts.get('headers'):
                    if hosts := headers.get('Host'):
                        if isinstance(hosts, list):
                            node.fake_host = ','.join(hosts)
                        elif isinstance(hosts, str):
                            node.fake_host = hosts
                        else:
                            logger.warning(f'clash:vmess:http-opts:headers:Host={hosts},未能解析')
        elif network == 'h2':
            if opts := vmess.get('h2-opts'):
                if hosts := opts.get('host'):
                    if isinstance(hosts, list):
                        node.fake_host = ','.join(hosts)
                    else:
                        logger.warning(f'clash:vmess:h2-opts:host={hosts},未能解析')

                node.path = opts.get('path')
        elif network == 'grpc':
            if opts := vmess.get('grpc-opts'):
                node.path = opts.get('grpc-service-name')
        else:
            logger.warning(f'clash:vmess:network={network},未能解析')
    return node


def parse(vmess: Union[str, Dict]) -> NodeInfo:
    node = None
    if isinstance(vmess, str):
        node = parse_str_vmess(vmess)
    elif isinstance(vmess, Dict):
        node = parse_clash_vmess(vmess)
    return node
