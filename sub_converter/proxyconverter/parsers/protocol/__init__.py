from . import ss, ssr, socks, http, snell, vmess, vless, trojan, hysteria, hysteria2

parser_map = {
    'ss': ss.parse,
    'ssr': ssr.parse,
    'socks': socks.parse,
    'socks5': socks.parse,
    'http': http.parse,
    'snell': snell.parse,
    'vmess': vmess.parse,
    'vless': vless.parse,
    'trojan': trojan.parse,
    'hysteria': hysteria.parse,
    'hysteria2': hysteria2.parse,
}
