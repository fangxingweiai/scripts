from typing import Dict

from loguru import logger

from ...helper import create_base_clash_node, str_to_int
from ...model import NodeInfo


def parse_clash_snell(snell: Dict) -> NodeInfo:
    node = create_base_clash_node(snell)

    node.psk = snell.get('psk')
    node.version = str_to_int(snell.get('version'))

    if opts := snell.get('obfs-opts'):
        mode = opts.get('mode')
        node.plugin_param_mode = mode

        host = opts.get('host')

        if mode == 'tls':
            node.sni = host
        elif mode == 'http':
            node.fake_host = host  # mode=tls host=sni?
        else:
            logger.warning(f'clash:snell:obfs-opts:mode={host},未能解析')
    return node


def parse(snell: Dict) -> NodeInfo:
    node = parse_clash_snell(snell)
    return node
