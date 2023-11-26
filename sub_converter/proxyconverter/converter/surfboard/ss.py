from ...model import NodeInfo


def convert(node: NodeInfo) -> str:
    encrypt_method = f', encrypt-method={node.crypto_method}' if node.crypto_method else ''

    password = f', password={node.crypto_str}' if node.crypto_str else ''

    udp_relay = ''
    if node.udp is True:
        udp_relay = f', udp-relay=true'
    elif node.udp is False:
        udp_relay = f', udp-relay=false'

    obfs = ''
    obfs_host = ''
    obfs_uri = ''
    if node.plugin_param_mode == 'tls':
        obfs = ', obfs=tls'
        obfs_host = f', obfs-host={node.sni}' if node.sni else ''
    elif node.plugin_param_mode == 'http':
        obfs = ', obfs=http'
        obfs_host = f', obfs-host={node.fake_host}' if node.fake_host else ''
        obfs_uri = f', obfs-uri={node.path}' if node.path else ''

    link = f'{node.protocol}, {node.server}, {node.port}{encrypt_method}{password}{udp_relay}{obfs}{obfs_host}{obfs_uri}'
    return link
