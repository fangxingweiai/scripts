from typing import Dict

from ...helper import remove_none_value_item
from ...model import NodeInfo


def convert(node: NodeInfo) -> Dict:
    proxy = {
        "name": node.name,
        "type": node.protocol,
        "server": node.server,
        "port": node.port,
        'cipher': node.crypto_method,
        'password': node.crypto_str,
        'udp': node.udp
    }

    if plugin := node.plugin:
        proxy['plugin'] = plugin

        mode = node.plugin_param_mode
        opts = {
            'plugin-opts': mode
        }

        if plugin == 'obfs':
            if mode == 'tls':
                opts['host'] = node.sni
            elif mode == 'http':
                opts['host'] = node.fake_host
        elif plugin == 'v2ray-plugin':
            if mode == 'websocket':
                opts['tls'] = node.tls
                opts['skip-cert-verify'] = node.skip_cert_verify
                opts['host'] = node.fake_host  # ?
                opts['path'] = node.path
                opts['mux'] = node.mux
                # headers

        if opts := remove_none_value_item(opts):
            proxy['plugin-opts'] = opts

    return remove_none_value_item(proxy)
