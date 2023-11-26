from enum import Enum
from typing import List, Union, Dict, Tuple

from loguru import logger

from . import clash, clashmeta, leaf, surfboard, v2rayn, shadowrocket, singbox, sfa, sfi, mfi
from ..model import NodeInfo


class Client(Enum):
    Clash = 'clash'
    ClashMeta = 'clashmeta'
    Leaf = 'leaf'
    Surfboard = 'surfboard'
    v2rayN = 'v2ray'
    Shadowrocket = 'shadowrocket'
    SingBox = 'singbox'
    MFI = 'mfi'
    SFA = 'sfa'
    SFI = 'sfi'


def _gen_mapping(module):
    return {
        'converter_map': module.converter_map,
        'gen_config': module.gen_config,
    }


TRANSFORM_MAP = {
    Client.Clash: _gen_mapping(clash),
    Client.ClashMeta: _gen_mapping(clashmeta),
    Client.MFI: _gen_mapping(mfi),
    Client.Leaf: _gen_mapping(leaf),
    Client.Surfboard: _gen_mapping(surfboard),
    Client.v2rayN: _gen_mapping(v2rayn),
    Client.Shadowrocket: _gen_mapping(shadowrocket),
    Client.SingBox: _gen_mapping(singbox),
    Client.SFA: _gen_mapping(sfa),
    Client.SFI: _gen_mapping(sfi),
}


def convert(nodes: Union[NodeInfo, List[NodeInfo]], client: Client):
    logger.info(f'开始生成{client.value}节点')
    if isinstance(nodes, NodeInfo):
        nodes = [nodes]

    converter_map = TRANSFORM_MAP[client]['converter_map']

    proxies = []
    for node in nodes:
        logger.info(f'{client.value} 生成节点 from: {node}')

        protocol = node.protocol

        if protocol not in converter_map:
            logger.warning(f'不支持{client.value}:{protocol}节点类型生成')
            continue

        try:
            if proxy := converter_map[protocol](node):
                if client == Client.Leaf or client == Client.Surfboard:
                    proxy = (node.name, proxy)
                    proxies.append(proxy)
                else:
                    proxies.append(proxy)
                logger.info(f'{client.value} 生成节点   to: {proxy}')
        except Exception as e:
            logger.error(f'节点生成失败:{e}')
    return proxies


def gen(proxies: Union[List[str], List[Dict], List[Tuple]], client: Client):
    return TRANSFORM_MAP[client]['gen_config'](proxies)
