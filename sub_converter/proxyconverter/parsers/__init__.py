import json
import re
import time
from typing import Union, List, Dict

import yaml
from loguru import logger

from .protocol import parser_map
from ..helper import is_clash_proxy, base64_decode, is_clash_sub, is_valid_node, is_base64, is_sub_url, \
    is_ss_sub, request
from ..model import NodeInfo


def _run(protocol, proxy):
    if protocol not in parser_map:
        logger.warning(f'暂不支持此类型节点转换: {protocol}')
        return None

    node = None
    try:
        node = parser_map[protocol](proxy)
    except Exception as e:
        logger.error(f'节点解析失败:{e}')
    return node


def _parse(proxy: Union[str, Dict]):
    logger.info(f'解析节点 from: {proxy}')

    if isinstance(proxy, str):
        proxy = proxy.strip()
        protocol, _ = proxy.split('://')
    else:
        if is_clash_proxy(proxy):
            protocol = proxy.get('type')
        else:  # 特殊ss节点
            protocol = 'ss'

    node = _run(protocol, proxy)
    if node:
        logger.info(f'解析节点   to: {node}')
    return node


###############################################


def _parse_ss_sub(sub_content: str):
    try:
        proxy_list = json.loads(sub_content)
    except Exception as e:
        logger.error(f'ss订阅解析失败: {e}')
        return []

    nodes = []
    for proxy in proxy_list:
        if node := _parse(proxy):
            nodes.append(node)
    return nodes


def _parse_clash_sub(sub_content: str) -> List[NodeInfo]:
    try:
        dict_clash = yaml.load(sub_content, Loader=yaml.FullLoader)  # yaml中有类似@字符导致无法解析
    except Exception as e:
        logger.error(f'yaml解析失败: {e}')
        return []

    nodes = []

    proxies = dict_clash.get("proxies")
    proxy_providers = dict_clash.get("proxy-providers")

    if proxies:
        logger.debug(f'直接获取clash中的proxies：{proxies}')
        for proxy in proxies:
            if node := _parse(proxy):
                nodes.append(node)
    elif proxy_providers:
        logger.info(f'获取clash中的proxy-providers')
        for k, v in proxy_providers.items():
            provider_url = v["url"]
            provider_nodes = parse(provider_url)
            logger.info(f"proxy-providers:{k},节点个数: {len(provider_nodes)}")
            nodes.extend(provider_nodes)
    return nodes


def _parse_base64_sub(content: str) -> List[NodeInfo]:
    nodes = []

    try:
        origin_sub = base64_decode(content)
    except:
        logger.error(f'v2订阅转码失败，查明！{content}')
        return nodes

    links = re.split('\r\n|\n|\r', origin_sub)

    for link in links:
        link = link.strip()
        if node := _parse(link):
            nodes.append(node)

    return nodes


def _parse_sub(sub_content: str):
    # sub_content = remove_special_characters(sub_content)

    if is_clash_sub(sub_content):
        logger.info("该订阅为clash订阅")
        nodes = _parse_clash_sub(sub_content)
    elif is_base64(sub_content):
        logger.info("该订阅为base64订阅")
        nodes = _parse_base64_sub(sub_content)
    elif is_ss_sub(sub_content):
        # ss订阅 https://sspool.herokuapp.com/ss/sub
        logger.info('该订阅为ss订阅')
        nodes = _parse_ss_sub(sub_content)
    else:
        logger.warning('非订阅内容或者未支持订阅格式')
        nodes = []
    return nodes


def is_str_node(node: str):
    node = node.strip()
    protocols = parser_map.keys()
    for protocol in protocols:
        if node.startswith(protocol + '://'):
            return True
    return False


def resolve_sub_content(resp):
    if resp:
        if user_info := resp.headers.get('subscription-userinfo'):
            splited_info = user_info.split(';')
            upload = None
            download = None
            total = None
            expire = None
            for info in splited_info:
                pair_info = info.strip().split('=')
                if len(pair_info) == 2:
                    k, v = pair_info
                    if v and v.isnumeric():
                        if k == 'upload':
                            upload = int(v)
                        elif k == 'download':
                            download = int(v)
                        elif k == 'total':
                            total = int(v)
                        elif k == 'expire':
                            expire = int(v)

            if expire is not None and expire < time.time():  # 过期
                logger.info('订阅过期')
                return None

            if upload is not None and download is not None and total is not None:
                if (upload + download) >= total:  # 流量用完
                    logger.info('订阅流量用尽')
                    return None

        if text := resp.text.strip():
            if '<html>' not in text and '<title>' not in text and '<div>' not in text:
                return text
            else:
                logger.warning(f'疑似无效订阅: {text}')

    logger.info('无效订阅')
    return None


def parse(proxies: Union[str, Dict, List[str], List[Dict]]) -> List[NodeInfo]:
    if isinstance(proxies, str) or isinstance(proxies, Dict):
        proxies = [proxies]

    nodes = []
    for i in proxies:
        if isinstance(i, str):
            sub_content = i
            if is_sub_url(i):
                logger.info(f"订阅地址: {i}")
                try:
                    # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}
                    resp = request(i, text_return=False)
                    sub_content = resolve_sub_content(resp)
                except Exception as e:
                    logger.error(f"获取订阅出错: {e}")
                    continue
            elif is_str_node(i):
                logger.info(f"节点: {i}")
                if node := _parse(i):
                    nodes.append(node)
                continue

            if sub_content:
                logger.debug(f"[{i}] 内容: {sub_content}")
                node_list = _parse_sub(sub_content)
                logger.info(f"[{i}] 节点个数: {len(node_list)}")
                node_list and nodes.extend(node_list)

        elif isinstance(i, dict):
            if proxies := i.get('proxies') and isinstance(proxies, List):
                for proxy in proxies:
                    if node := _parse(proxy):
                        nodes.append(node)
            elif is_clash_proxy(i):
                if node := _parse(i):
                    nodes.append(node)
            else:
                logger.warning(f'该字典内容暂无法解析: {i}')
        else:
            logger.warning(f'不支持解析该内容类型: {type(i)}={i}')

    valid_nodes = []
    for node in nodes:
        if is_valid_node(node):
            valid_nodes.append(node)

    return valid_nodes


if __name__ == '__main__':
    parse('ss://2022-blake3-aes-128-gcm:aHU5RjJFU3lWUTNSc2VNVmZqNzdwdU1lWFYyMWhBdXE=@217.145.236.128:21506#HKG')
