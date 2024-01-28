import json


class NodeInfo(object):
    __slots__ = (
        'protocol', 'name', 'server', 'port', 'crypto_str', 'crypto_method', 'network', 'fake_host', 'path', 'tls',
        'sni', 'skip_cert_verify', 'udp', 'alter_id', 'v', 'xtls_flow', 'alpn', 'tfo', 'fake_type', 'grpc_mode',
        'plugin', 'ssr_protocol', 'ssr_obfs', 'ssr_obfs_param', 'ssr_protocol_param', 'psk', 'version', 'username',
        'max_early_data', 'early_data_header_name', 'udp_over_tcp', 'plugin_param_mode', 'mux', 'congestion', 'seed',
        'xtls', 'up', 'down', 'hy_protocol', 'hy_ports', 'hy_obfs', 'disable_mtu_discovery', 'fingerprint',
        'public_key', 'short_id', 'hy2_obfs', 'obfs_password'
    )

    def __init__(self):
        self.protocol = None  # 注意socks socks5 socks5-tls
        self.name = None
        self.server = None
        self.port = None

        self.crypto_str = None  # vmess:uuid trojan:password socks:password http:password hysteria:auth_str
        self.crypto_method = None  # sr:vless:tcp=auto  v2rayN:vless:tcp?encryption=none

        self.network = None  # 注意ws=websocket tcp(sr:trojan:默认 vless:tcp) http grpc mkcp h2 quic none(sr:vless:tcp)
        # trojan
        # v2rayN: tcp(注意headerType) ws grpc
        # Shadowrocket: None=tcp? ws grcp
        # clash: ws grpc None=tcp?

        # vless
        # Shadowrocket: tcp http ws grpc quic h2 mkcp
        # v2rayN: tcp(注意headerType=none) tcp+http ws grpc
        # clashmeta: None=tcp? ws grpc

        self.grpc_mode = None  # v2rayN:grpc

        self.congestion = None  # sr:vmess:mkcp 拥塞
        self.seed = None  # sr:vmess:mkcp

        self.fake_type = None  # none v2rayN:vmess  trojan:headerType vless:headerType sr:vmess:quic:obfsParam:header
        self.fake_host = None  # 多个统一以,分割
        self.path = None  # 多个统一以,分割 v2rayN:grpc:serviceName  ss:obfs-(local):tls:uri

        self.tls = None  # vless,trojan:security vless
        self.xtls = None  # vless,trojan:security vless  sr:trojan:xtls=1->xtls-rprx-drect

        self.xtls_flow = None  # trojan:flow  sr:vless:1,0  sr:trojan:xtls=1->xtls-rprx-drect

        self.sni = None  # =peer
        self.skip_cert_verify = None  # =allowInsecure

        self.udp = None

        # vless
        self.public_key = None
        self.short_id = None

        # vmess
        self.alter_id = None

        # snell
        self.psk = None
        self.version = None

        # ss shadowrocket:vmess
        self.mux = None  # v2ray-plugin:mux

        # ss snell sr:trojan:ws
        self.plugin = None  # (obfs, obfs-local)=obfs;v2ray-plugin
        self.plugin_param_mode = None  # websocket; tls; http

        # ssr
        self.ssr_protocol = None
        self.ssr_protocol_param = None
        self.ssr_obfs = None
        self.ssr_obfs_param = None

        # http socks
        self.username = None

        # v2rayN
        self.v = None

        # Clash:vmess
        self.max_early_data = None
        self.early_data_header_name = None

        # shadowrocket:trojan:tfo=快速打开  ss:fast-open hysteria:fast-open
        self.tfo = None  # bool

        # hysteria
        self.up = None
        self.down = None
        self.hy_protocol = None
        self.hy_ports = None
        self.hy_obfs = None
        self.disable_mtu_discovery = None
        self.fingerprint = None  # clashmeta:vless

        # hysteria
        self.hy2_obfs = None
        self.obfs_password = None

        self.alpn = None  # torjan:alpn(逗号分割) v2rayN:vless 多个以，分割
        self.udp_over_tcp = None

    def __str__(self):
        res = []
        for k in self.__slots__:
            v = self.__getattribute__(k)
            if v is not None:
                res.append(f'{k}={v}')
        return json.dumps(res, ensure_ascii=False)
