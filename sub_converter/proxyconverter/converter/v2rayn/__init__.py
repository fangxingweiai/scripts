import os
from typing import List

from . import trojan, vless, ss, vmess, socks
from ...helper import base64_encode

converter_map = {
    'socks': socks.convert,
    'socks5': socks.convert,
    'ss': ss.convert,
    'trojan': trojan.convert,
    'vless': vless.convert,
    'vmess': vmess.convert,
}


def gen_config(proxies: List[str]):
    sub_content = base64_encode(os.linesep.join(proxies))
    return sub_content
