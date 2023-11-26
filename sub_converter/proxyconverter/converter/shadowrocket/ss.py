import json
import urllib.parse
from typing import Tuple

from loguru import logger

from ...helper import base64_encode, remove_none_value_item
from ...model import NodeInfo


def _normalize_params(node: NodeInfo) -> Tuple:
    plugin = node.plugin
    if plugin == 'obfs':
        plugin = 'obfs-local'

    host = node.fake_host
    if node.plugin_param_mode == 'tls':
        host = node.sni
        if host:
            dict_host = {'Host': host}
            json_host = json.dumps(dict_host)
            host = urllib.parse.quote(json_host)

    return plugin, host


def convert(node: NodeInfo) -> str:
    plugin, host = _normalize_params(node)
    if plugin and plugin not in ['obfs-local', 'v2ray-plugin']:
        logger.warning(f'Shadowrocket:ss:plugin={plugin},暂不支持')
        return ''

    if node.plugin_param_mode and node.plugin_param_mode not in ['tls', 'http', 'websocket']:
        logger.warning(f'Shadowrocket:ss:{plugin}:mode={host},暂不支持')
        return ''

    cry_info = f'{node.crypto_method}:{node.crypto_str}'
    server_and_port = f'{node.server}:{node.port}'

    partial_base64_main_info = f'{base64_encode(cry_info)}@{server_and_port}'
    base64_main_info = base64_encode(f'{cry_info}@{server_and_port}')

    tfo = f'&tfo=1' if node.tfo else ''
    uot = f'&uot=1' if node.udp_over_tcp else ''

    params = f'{tfo}{uot}'
    name = urllib.parse.quote(node.name)

    link = ''
    if plugin:
        if plugin == 'obfs-local':
            # ss://Y2hhY2hhMjA6c3NwYXNzd29yZA@baidu.com:443?plugin=obfs-local;obfs=tls;obfs-host=%7B%22Host%22:%22we.com%22%7D;obfs-uri=/wspath&tfo=1&uot=1#test
            # ss://Y2hhY2hhMjA6c3NwYXNzd29yZA@baidu.com:443?plugin=obfs-local;obfs=http;obfs-host=httphost;obfs-uri=/httppath&tfo=1&uot=1#test
            plugin = ';plugin=obfs-local'
            obfs = f';obfs={node.plugin_param_mode}' if node.plugin_param_mode else ''
            obfs_host = f';obfs-host={host}' if host else ''
            obfs_uri = f';obfs-uri={node.path}' if node.path else ''

            obfs_params = f'{plugin}{obfs}{obfs_host}{obfs_uri}'
            obfs_params = obfs_params.lstrip(';')

            if obfs_params == '':
                params = params.lstrip('&')
            link = f'ss://{partial_base64_main_info}?{obfs_params}{params}#{name}'

        elif plugin == 'v2ray-plugin':
            # ss://Y2hhY2hhMjAtYXV0aDpzc3Bhc3N3b3JkQGJhaWR1LmNvbTo0NDM?v2ray-plugin=eyJhZGRyZXNzIjoidGVzdC5jb20iLCJwb3J0IjoiNDQzIiwibXV4Ijp0cnVlLCJtb2RlIjoid2Vic29ja2V0IiwiYWxsb3dJbnNlY3VyZSI6dHJ1ZSwidGxzIjp0cnVlLCJob3N0IjoiY2xvdWRmcm9udC5jb20iLCJwZWVyIjoicGVlci5jb20iLCJ0Zm8iOnRydWUsInBhdGgiOiJcL3BhdGgifQ#test
            plugin_opts = {
                'mux': node.mux,
                'mode': 'websocket',
                'allowInsecure': node.skip_cert_verify,
                'tls': node.tls,
                'host': host,
                'peer': node.sni,
                'tfo': node.tfo,
                'path': node.path
            }

            plugin_opts = remove_none_value_item(plugin_opts)
            json_opts = json.dumps(plugin_opts)
            base64_opts = base64_encode(json_opts)

            v2ray_plugin_params = f'v2ray-plugin={base64_opts}'

            link = f'ss://{base64_main_info}?{v2ray_plugin_params}#{name}'
    else:
        params = params.lstrip('&')
        # ss://Y2hhY2hhMjAtYXV0aDpzc3Bhc3N3b3JkQGJhaWR1LmNvbTo0NDM?tfo=1&uot=1#test
        link = f'ss://{base64_main_info}?{params}#{name}'

    return link
