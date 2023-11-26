from ...model import NodeInfo


def _normalize_params(node: NodeInfo) -> str:
    protocol = node.protocol
    if protocol == 'socks':
        protocol = 'socks5'

    if (node.tls or node.sni) and protocol == 'socks5':
        protocol = 'socks5-tls'

    return protocol


def convert(node: NodeInfo) -> str:
    # https://getsurfboard.com/docs/profile-format/proxy/
    protocol = _normalize_params(node)

    username = node.username if node.username else ''
    password = node.crypto_str if node.crypto_str else ''

    skip_cert_verify = ''
    if node.skip_cert_verify is True:
        skip_cert_verify = f', skip-cert-verify=true'
    elif node.skip_cert_verify is False:
        skip_cert_verify = f', skip-cert-verify=false'

    sni = f', sni={node.sni}' if node.sni else ''

    udp_relay = ''
    if node.udp is True:
        udp_relay = f', udp-relay=true'
    elif node.udp is False:
        udp_relay = f', udp-relay=false'

    # ProxySOCKS5 = socks5, 1.2.3.4, 443, username, password, udp-relay=false
    # ProxySOCKS5TLS = socks5-tls, 1.2.3.4, 443, username, password, skip-cert-verify=true, sni=www.google.com
    link = f'{protocol}, {node.server}, {node.port}, {username}, {password}{skip_cert_verify}{sni}{udp_relay}'
    return link
