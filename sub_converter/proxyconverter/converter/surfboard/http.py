from ...model import NodeInfo


def _normalize_params(node: NodeInfo) -> str:
    protocol = node.protocol

    if (node.tls or node.sni) and protocol == 'http':
        protocol = 'https'

    return protocol


def convert(node: NodeInfo) -> str:
    protocol = _normalize_params(node)

    username = node.username if node.username else ''
    password = node.crypto_str if node.crypto_str else ''

    # https://getsurfboard.com/docs/profile-format/proxy/

    skip_cert_verify = ''
    if node.skip_cert_verify is True:
        skip_cert_verify = f', skip-cert-verify=true'
    elif node.skip_cert_verify is False:
        skip_cert_verify = f', skip-cert-verify=false'

    sni = f', sni={node.sni}' if node.sni else ''

    # ProxyHTTP = http, 1.2.3.4, 443, username, password
    # ProxyHTTPS = https, 1.2.3.4, 443, username, password, skip-cert-verify=true, sni=www.google.com
    link = f'{protocol}, {node.server}, {node.port}, {username}, {password}{skip_cert_verify}{sni}'
    return link
