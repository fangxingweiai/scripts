import json
import urllib.parse
from typing import Union, Dict

from loguru import logger

from ...helper import create_base_node, is_base64, base64_decode, str_to_int, create_base_clash_node
from ...model import NodeInfo


def _resolve_params(node: NodeInfo, param: str):
    param_name, param_value = param.split('=', 1)

    # 小火箭
    if param_name == 'remarks':
        node.name = urllib.parse.unquote(param_value)
    elif param_name == 'tls':
        node.tls = True if param_value == '1' else None
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
    elif param_name == 'xtls':
        if param_value == '1':
            node.xtls = True
            node.xtls_flow = 'xtls-rprx-direct'
    # ====================
    elif param_name == 'encryption':
        node.crypto_method = param_value
    elif param_name == 'type' or param_name == 'obfs':
        node.network = param_value
    elif param_name == 'host' or param_name == 'obfsParam':
        host = param_value
        try:
            param_value = urllib.parse.unquote(param_value)
            dict_data = json.loads(param_value)
            host = dict_data.get('Host')
        except:
            pass
        node.fake_host = host
    elif param_name == 'headerType':
        node.fake_type = param_value
    elif param_name == 'path' or param_name == 'serviceName':
        node.path = urllib.parse.unquote(param_value)
    elif param_name == 'security':
        if param_value.strip() == '':
            return

        if param_value == 'tls':
            node.tls = True
        elif param_value == 'xtls':
            node.xtls = True
        else:
            logger.warning(f'vless:{param_value}未知')
    elif param_name == 'sni' or param_name == 'peer':
        node.sni = param_value
    elif param_name == 'flow':
        node.xtls_flow = param_value
    elif param_name == 'alpn':
        node.alpn = urllib.parse.unquote(param_value)
    elif param_name == 'mode':
        node.grpc_mode = param_value
    else:
        logger.warning(f'vless:params:{param},未能解析')


def parse_str_vless(vless: str) -> NodeInfo:
    vless_data, node = create_base_node(vless)

    main_info, params = vless_data.rsplit('?', 1)

    if is_base64(main_info):  # 小火箭
        main_info = base64_decode(main_info)
    else:
        # vless://72972da9-d188-40c6-83a6-4ec28fde2c0a@cg.rutracker-cn.com:443?path=%2FxxPb49hL0C&security=tls&encryption=none&type=ws&sni=cg.rutracker-cn.com#v2cross.com
        params, name = params.rsplit('#', 1)
        node.name = urllib.parse.unquote(name)

    # 72972da9-d188-40c6-83a6-4ec28fde2c0a@cg.rutracker-cn.com:
    cry_info, server_and_port = main_info.rsplit('@', 1)

    c = cry_info.split(':')
    if len(c) == 1:
        node.crypto_str = cry_info
    elif len(c) == 2:
        node.crypto_method, node.crypto_str = c

    node.server, port = server_and_port.split(':')
    node.port = str_to_int(port)

    param_list = params.split('&')
    for param in param_list:
        _resolve_params(node, param)

    return node


def parse_clash_vless(vless: Dict) -> NodeInfo:
    node = create_base_clash_node(vless)

    node.crypto_str = vless.get('uuid')

    if flow := vless.get('flow'):  # flow: xtls-rprx-direct # xtls-rprx-origin  # enable XTLS
        node.xtls_flow = flow
        node.xtls = True

    node.tls = vless.get('tls')
    node.sni = vless.get('servername')
    node.skip_cert_verify = vless.get('skip-cert-verify')
    node.udp = vless.get('udp')
    node.fingerprint = vless.get('client-fingerprint')

    if network := vless.get('network'):
        node.network = network
        if network == 'ws':
            if opts := vless.get('ws-opts'):
                node.path = opts.get('path')

                if headers := opts.get('headers'):
                    node.fake_host = headers.get('Host')

                    if len(headers.keys()) > 1:
                        logger.warning(f'clash:vless:network:ws-opts:headers={headers},未能完全解析')
        elif network == 'grpc':
            if opts := vless.get('grpc-opts'):
                node.path = opts.get('grpc-service-name')
        else:
            logger.warning(f'clash:vless:network={network},未能解析')

    if reality_opts := vless.get('reality-opts'):
        node.public_key = reality_opts.get('public-key')
        node.short_id = reality_opts.get('short-id')

    return node


def parse(vless_data: Union[str, Dict]) -> NodeInfo:
    node = None
    if isinstance(vless_data, str):
        node = parse_str_vless(vless_data)
    elif isinstance(vless_data, Dict):  # clash meta支持vless
        node = parse_clash_vless(vless_data)

    return node
