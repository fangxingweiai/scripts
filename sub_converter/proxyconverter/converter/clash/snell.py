from typing import Dict

from ...helper import remove_none_value_item
from ...model import NodeInfo


def convert(node: NodeInfo) -> Dict:
    proxy = {
        "name": node.name,
        "type": node.protocol,
        "server": node.server,
        "port": node.port,
        'psk': node.psk,
        'version': node.version
    }

    if mode := node.plugin_param_mode:
        opts = {
            'mode': mode
        }

        if mode == 'tls':
            opts['host'] = node.sni
        elif mode == 'http':
            opts['host'] = node.fake_host

        if opts := remove_none_value_item(opts):
            proxy['obfs-opts'] = opts

    return remove_none_value_item(proxy)
