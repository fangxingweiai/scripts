import os
from typing import List

from . import ss, ssr, trojan, vless, vmess
from ...helper import base64_encode

converter_map = {
    'ss': ss.convert,
    'ssr': ssr.convert,
    'trojan': trojan.convert,
    'vless': vless.convert,
    'vmess': vmess.convert,
}


def gen_config(proxies: List[str]):
    sub_content = base64_encode(os.linesep.join(proxies))
    return sub_content
