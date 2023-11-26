import re

from loguru import logger

from converter import Client, convert
from parsers import parse


def test(fn):
    def inner():
        links = fn()
        if isinstance(links,dict):
            for type_, link in links.items():
                logger.info(f'{type_}')
                node = parse(link)
                convert(node, Client.v2rayN)
                logger.info('')
        elif isinstance(links,list):
            for link in links:
                node = parse(link)
                convert(node, Client.v2rayN)
                logger.info('')
    return inner


@test
def test_ss():
    links = {
        'type1': 'ss://YWVzLTI1Ni1nY206MTE0NTE0@173.82.232.224:56634#%E6%B5%8B%E8%AF%95',
        'type2': 'ss://YWVzLTI1Ni1nY206WTZSOXBBdHZ4eHptR0NAMTcyLjk5LjE5MC4zNTozMzA2#🇺🇸US_1950',
        'sr_base': 'ss://Y2hhY2hhMjAtYXV0aDpzc3Bhc3N3b3JkQGJhaWR1LmNvbTo0NDM?tfo=1&uot=1#test',
        'sr_obfs_tls': 'ss://Y2hhY2hhMjA6c3NwYXNzd29yZA@baidu.com:443?plugin=obfs-local;obfs=tls;obfs-host=%7B%22Host%22:%22we.com%22%7D;obfs-uri=/wspath&tfo=1&uot=1#test',
        'sr_obfs_http': 'ss://Y2hhY2hhMjA6c3NwYXNzd29yZA@baidu.com:443?plugin=obfs-local;obfs=http;obfs-host=httphost;obfs-uri=/httppath&tfo=1&uot=1#test',
        'sr_v2ray_plugin_ws': 'ss://Y2hhY2hhMjAtYXV0aDpzc3Bhc3N3b3JkQGJhaWR1LmNvbTo0NDM?v2ray-plugin=eyJhZGRyZXNzIjoidGVzdC5jb20iLCJwb3J0IjoiNDQzIiwibXV4Ijp0cnVlLCJtb2RlIjoid2Vic29ja2V0IiwiYWxsb3dJbnNlY3VyZSI6dHJ1ZSwidGxzIjp0cnVlLCJob3N0IjoiY2xvdWRmcm9udC5jb20iLCJwZWVyIjoicGVlci5jb20iLCJ0Zm8iOnRydWUsInBhdGgiOiJcL3BhdGgifQ#test',
    }
    return links


@test
def test_ssr():
    links = dict(
        sr1='ssr://YmFpZHUuY29tOjQ0MzpvcmlnaW46Y2hhY2hhMjA6cGxhaW46YzNOd1lYTnpkMjl5WkEvP3JlbWFya3M9ZEdWemRBJnByb3RvcGFyYW09Jm9iZnNwYXJhbT1kM05vYjNOMExtTnZiUSZ0Zm89MQ',
        sr2='ssr://YmFpZHUuY29tOjQ0MzphdXRoX2FlczEyOF9zaGExOmNoYWNoYTIwOnBsYWluOmMzTndZWE56ZDI5eVpBLz9yZW1hcmtzPWRHVnpkQSZwcm90b3BhcmFtPWRtaG9hR2hvYUdocWFnJm9iZnNwYXJhbT1kM05vYjNOMExtTnZiUSZ0Zm89MQ',

        type1='ssr://MTAzLjM5LjIxOC4yNDk6OTM2OTphdXRoX2FlczEyOF9zaGExOmNoYWNoYTIwLWlldGY6cGxhaW46Wm5aNFkzWnZjR2xxWVhOamFYTjJaMnhoLz9vYmZzcGFyYW09Wkd4elpIWnpaR3B2YXk1dGFXTnliM052Wm5RdVkyOXQmcHJvdG9wYXJhbT1PREUwT0RNeU5UTTRPbUUzTmpBNFlqVTNOV0k0WlRjNFlqVSZyZW1hcmtzPTZhYVo1cml2TGVTNGstZTZ2ekF6',

        type2='ssr://MjEzLjE4My41My4xNzc6OTAzMzpvcmlnaW46YWVzLTI1Ni1jZmI6cGxhaW46VlZSS1FUVTNlWEJyTWxoTFVYQnViUS8_b2Jmc3BhcmFtPSZwcm90b3BhcmFtPSZyZW1hcmtzPVUxTlM1NG01NXE2SzZJcUM1NEs1VkVkQVYyVnZkMjl5YTNN',
        type3='ssr://Y3N0d3JlbGF5Lm9ubGluZXRvLnh5ejo1NjU6YXV0aF9hZXMxMjhfbWQ1OmNoYWNoYTIwLWlldGY6cGxhaW46YldKc1lXNXJNWEJ2Y25RLz9vYmZzcGFyYW09JnByb3RvcGFyYW09TkRJME9EZzZabVl4TVRJeU16TSZyZW1hcmtzPTVZLXc1cm0tTVMzbW5wZmxqNVRwazRIbnNvbmt1SlBrdXFzJmdyb3VwPQ',
        type4='ssr://Y3VhbGxhei5kZXp4cmwueHl6OjU2NTphdXRoX2FlczEyOF9tZDU6Y2hhY2hhMjAtaWV0ZjpwbGFpbjpiV0pzWVc1ck1YQnZjblEvP29iZnNwYXJhbT0mcHJvdG9wYXJhbT1OREkwT0RnNlptWXhNVEl5TXpNJnJlbWFya3M9NlotcDVadTlNUzNtbnBmbGo1VHBrNEhuc29ua3VKUGt1cXMmZ3JvdXA9',
        type5='ssr://MjEzLjE4My41My4xNzc6OTAzMzpvcmlnaW46YWVzLTI1Ni1jZmI6cGxhaW46VlZSS1FUVTNlWEJyTWxoTFVYQnViUS8_b2Jmc3BhcmFtPSZwcm90b3BhcmFtPSZyZW1hcmtzPVUxTlM1NG01NXE2SzZJcUM1NEs1VkVkQVYyVnZkMjl5YTNN',
        type6='ssr://Y25nZGNzNC5sYW5ndGcueHl6OjU2MDphdXRoX2FlczEyOF9tZDU6Y2hhY2hhMjAtaWV0ZjpwbGFpbjpiV0pzWVc1ck1YQnZjblEvP2dyb3VwPVUxTlNVSEp2ZG1sa1pYSSZyZW1hcmtzPTVMaXQ1WnU5TFRFd01Ua3VOa3RDTDNNb1dXOTFkSFZpWlRya3VJM29pYV9tbnBjcCZvYmZzcGFyYW09JnByb3RvcGFyYW09TWpZek5EcDJSbkk1Um5neU0zaGFVaWd4S1E',
    )
    return links


@test
def test_vmess():
    links = dict(
        sr_base='vmess://YXV0bzpzc3Bhc3N3b3JkQGJhaWR1LmNvbTo0NDM?remarks=%E6%B5%8B%E8%AF%95224&path=/h2&obfs=none&tls=1&peer=dddd.com&allowInsecure=1&tfo=1&mux=1&alterId=25',
        sr_ws='vmess://YXV0bzpzc3Bhc3N3b3JkQGJhaWR1LmNvbTo0NDM?remarks=%E6%B5%8B%E8%AF%95224&obfsParam=hhhbbvhhxxf.com&path=/wspath&obfs=websocket&tls=1&peer=sni.com&allowInsecure=1&tfo=1&mux=1&alterId=25',
        sr_http='vmess://YXV0bzpzc3Bhc3N3b3JkQGJhaWR1LmNvbTo0NDM?remarks=%E6%B5%8B%E8%AF%95224&obfsParam=http.host.com&path=/httppath&obfs=http&tls=1&peer=sni.com&allowInsecure=1&tfo=1&mux=1&alterId=25',
        sr_grpc='vmess://YXV0bzpzc3Bhc3N3b3JkQGJhaWR1LmNvbTo0NDM?remarks=%E6%B5%8B%E8%AF%95224&obfsParam=%7B%22Host%22:%22grpc.host.com%22%7D&path=/grpcpath&obfs=grpc&tls=1&tfo=1&alterId=25',
        sr_quic='vmess://YXV0bzpzc3Bhc3N3b3JkQGJhaWR1LmNvbTo0NDM?remarks=%E6%B5%8B%E8%AF%95224&obfsParam=%7B%22header%22:%22wechat-video%22,%22Host%22:%22grpc.host.com%22%7D&path=/grpcpath&obfs=quic&allowInsecure=1&tfo=1&mux=1&alterId=25',
        sr_h2='vmess://YXV0bzpzc3Bhc3N3b3JkQGJhaWR1LmNvbTo0NDM?remarks=%E6%B5%8B%E8%AF%95224&obfsParam=%7B%22Host%22:%22h2.host.com%22,%22header%22:%22wechat-video%22%7D&path=/h2&obfs=h2&tls=1&allowInsecure=1&tfo=1&mux=1&alterId=25',
        sr_mkcp='vmess://YXV0bzpzc3Bhc3N3b3JkQGJhaWR1LmNvbTo0NDM?remarks=%E6%B5%8B%E8%AF%95224&obfsParam=%7B%22Host%22:%22h2.host.com%22,%22congestion%22:true,%22header%22:%22wechat-video%22,%22seed%22:%22hhhbbbb%22%7D&path=/h2&obfs=mkcp&tls=1&peer=dddd.com&allowInsecure=1&tfo=1&mux=1&alterId=25'
    )

    return links


@test
def test_trojan():
    links = dict(
        sr_base='trojan://password238;$@baidu.com:443?allowInsecure=1&peer=sni.com&tfo=1&mux=1&xtls=1&alpn=http/1.1#%E6%B5%8B%E8%AF%95trojan',
        sr_ws='trojan://password238;$@baidu.com:443?allowInsecure=1&peer=sni.com&tfo=1&mux=1&alpn=http/1.1&plugin=obfs-local;obfs=websocket;obfs-host=ws.com;obfs-uri=/path#%E6%B5%8B%E8%AF%95trojan',
        sr_grpc='trojan://password238;$@baidu.com:443?allowInsecure=1&peer=sni.com&tfo=1&alpn=http/1.1&obfs=grpc&obfsParam=%7B%22Host%22:%22grpc.com%22%7D&path=/path#%E6%B5%8B%E8%AF%95trojan',
        v2rayN_base='trojan://passwordtrojan@baidu.com:443?flow=xtls-rprx-origin&security=tls&sni=test.sni.com&alpn=h2%2Chttp%2F1.1&type=tcp&headerType=none&host=fake.com#v2rayN%E7%9A%84trojan',
        v2rayN_ws='trojan://passwordtrojan@baidu.com:443?flow=xtls-rprx-origin&security=tls&sni=test.sni.com&alpn=h2%2Chttp%2F1.1&type=ws&host=fake.com&path=%2Fwspath#v2rayN%E7%9A%84trojan',
        v2rayN_http='trojan://passwordtrojan@baidu.com:443?flow=xtls-rprx-origin&security=tls&sni=test.sni.com&alpn=h2%2Chttp%2F1.1&type=tcp&headerType=http&host=fake.com#v2rayN%E7%9A%84trojan',
        v2rayN_grpc='trojan://passwordtrojan@baidu.com:443?flow=xtls-rprx-origin&security=tls&sni=test.sni.com&alpn=h2%2Chttp%2F1.1&type=grpc&serviceName=%2Fwspath&mode=gun#v2rayN%E7%9A%84trojan',
    )
    return links


@test
def test_vless():
    links = dict(
        sr_tcp='vless://YXV0bzoyMDNkNmY2Ni1iZDljLTQ3ZjMtOTgyYi00YWRlOTFiNWFmMDRAYmFpZHUuY29tOjQ0Mw?remarks=%E6%B5%8B%E8%AF%95ed&obfs=none&tls=1&peer=peer.com&allowInsecure=1&tfo=1&mux=1&xtls=1',
        sr_http='vless://YXV0bzoyMDNkNmY2Ni1iZDljLTQ3ZjMtOTgyYi00YWRlOTFiNWFmMDRAYmFpZHUuY29tOjQ0Mw?remarks=%E6%B5%8B%E8%AF%95ed&obfsParam=http.com&path=/path&obfs=http&tls=1&peer=peer.com&allowInsecure=1&tfo=1&mux=1&xtls=1',
        sr_ws='vless://YXV0bzoyMDNkNmY2Ni1iZDljLTQ3ZjMtOTgyYi00YWRlOTFiNWFmMDRAYmFpZHUuY29tOjQ0Mw?remarks=%E6%B5%8B%E8%AF%95ed&obfsParam=%7B%22Host%22:%22ws.com%22%7D&path=/path&obfs=websocket&tls=1&peer=peer.com&allowInsecure=1&tfo=1&mux=1&xtls=1',
        sr_grpc='vless://YXV0bzoyMDNkNmY2Ni1iZDljLTQ3ZjMtOTgyYi00YWRlOTFiNWFmMDRAYmFpZHUuY29tOjQ0Mw?remarks=%E6%B5%8B%E8%AF%95ed&obfsParam=grpc.com&path=/path&obfs=grpc&tls=1&peer=peer.com&allowInsecure=1&tfo=1',
        v2rayN_http='vless://cba4a4a4-5651-4424-b3b7-14ebd3a4bbfc@baidu.com:443?encryption=none&flow=xtls-rprx-origin&security=tls&sni=sni.com&alpn=h2%2Chttp%2F1.1&type=tcp&headerType=http&host=fake.http.com#v2rayN%E7%9A%84vless',
        v2rayN_ws='vless://cba4a4a4-5651-4424-b3b7-14ebd3a4bbfc@baidu.com:443?encryption=none&flow=xtls-rprx-origin&security=tls&sni=sni.com&alpn=h2%2Chttp%2F1.1&type=ws&host=fake.http.com&path=%2Fpathdddddddddfdfsdf#v2rayN%E7%9A%84vless',
        v2rayN_ws_xtls='vless://cba4a4a4-5651-4424-b3b7-14ebd3a4bbfc@baidu.com:443?encryption=none&flow=xtls-rprx-origin&security=xtls&sni=sni.com&alpn=h2%2Chttp%2F1.1&type=ws&host=fake.http.com&path=%2Fpathdddddddddfdfsdf#v2rayN%E7%9A%84vless',
        v2rayN_grpc='vless://cba4a4a4-5651-4424-b3b7-14ebd3a4bbfc@baidu.com:443?encryption=none&flow=xtls-rprx-origin&security=xtls&sni=sni.com&alpn=h2%2Chttp%2F1.1&type=grpc&serviceName=%2Fpathdddddddddfdfsdf&mode=gun#v2rayN%E7%9A%84vless'
    )
    return links
@test
def test_random():
    data = '''
vmess://eyJ2IjoiMiIsInBzIjoi8J+HqPCfh7NDTiAxMzYg4oaSIG9wZW5pdHN1Yi5jb20iLCJhZGQiOiJhbGl5dW4uaW5zdGFsbDAxLnZudXBnY24uY24iLCJwb3J0IjoiMTE5MzUiLCJ0eXBlIjoibm9uZSIsImlkIjoiMDI1M2I1NzQtODAyMC0zMTg2LWE2NDctMDI2NzI5NWFjOWJiIiwiYWlkIjoiMCIsIm5ldCI6InRjcCIsInBhdGgiOiIvIiwiaG9zdCI6ImFsaXl1bi5pbnN0YWxsMDEudm51cGdjbi5jbiIsInRscyI6IiJ9
vmess://eyJ2IjoiMiIsInBzIjoi8J+HqPCfh7NDTiAxNDgg4oaSIG9wZW5pdHN1Yi5jb20iLCJhZGQiOiJhbGl5dW4uaW5zdGFsbDA0LnZudXBnY24uY24iLCJwb3J0IjoiMTE5MzUiLCJ0eXBlIjoibm9uZSIsImlkIjoiMDI1M2I1NzQtODAyMC0zMTg2LWE2NDctMDI2NzI5NWFjOWJiIiwiYWlkIjoiMCIsIm5ldCI6InRjcCIsInBhdGgiOiIvIiwiaG9zdCI6ImFsaXl1bi5pbnN0YWxsMDQudm51cGdjbi5jbiIsInRscyI6IiJ9
vmess://eyJ2IjoiMiIsInBzIjoi8J+HqPCfh7NDTiAxMzEg4oaSIG9wZW5pdHN1Yi5jb20iLCJhZGQiOiJhbGl5dW4ubW9ibGUudm51cGdjbi5jbiIsInBvcnQiOiI5MDE1IiwidHlwZSI6Im5vbmUiLCJpZCI6IjAyNTNiNTc0LTgwMjAtMzE4Ni1hNjQ3LTAyNjcyOTVhYzliYiIsImFpZCI6IjAiLCJuZXQiOiJ0Y3AiLCJwYXRoIjoiLyIsImhvc3QiOiJhbGl5dW4ubW9ibGUudm51cGdjbi5jbiIsInRscyI6IiJ9
vmess://eyJ2IjoiMiIsInBzIjoi8J+HqPCfh7NDTiAxNDYg4oaSIG9wZW5pdHN1Yi5jb20iLCJhZGQiOiJhbGl5dW4uaW5zdGFsbDAyLnZudXBnY24uY24iLCJwb3J0IjoiMTE5MzUiLCJ0eXBlIjoibm9uZSIsImlkIjoiMDI1M2I1NzQtODAyMC0zMTg2LWE2NDctMDI2NzI5NWFjOWJiIiwiYWlkIjoiMCIsIm5ldCI6InRjcCIsInBhdGgiOiIvIiwiaG9zdCI6ImFsaXl1bi5pbnN0YWxsMDIudm51cGdjbi5jbiIsInRscyI6IiJ9
vmess://eyJ2IjoiMiIsInBzIjoi8J+HqPCfh7NDTiAyMDMg4oaSIG9wZW5pdHN1Yi5jb20iLCJhZGQiOiJhbGl5dW4uaW5zdGFsbDAxLnZudXBnY24uY24iLCJwb3J0IjoiMTE5MTkiLCJ0eXBlIjoibm9uZSIsImlkIjoiMDI1M2I1NzQtODAyMC0zMTg2LWE2NDctMDI2NzI5NWFjOWJiIiwiYWlkIjoiMCIsIm5ldCI6InRjcCIsInBhdGgiOiIvIiwiaG9zdCI6ImFsaXl1bi5pbnN0YWxsMDEudm51cGdjbi5jbiIsInRscyI6IiJ9
vmess://eyJ2IjoiMiIsInBzIjoi8J+HqPCfh7NDTiAxMzIg4oaSIG9wZW5pdHN1Yi5jb20iLCJhZGQiOiJhbGl5dW4uaW5zdGFsbDAxLnZudXBnY24uY24iLCJwb3J0IjoiMTE5MjkiLCJ0eXBlIjoibm9uZSIsImlkIjoiMDI1M2I1NzQtODAyMC0zMTg2LWE2NDctMDI2NzI5NWFjOWJiIiwiYWlkIjoiMCIsIm5ldCI6InRjcCIsInBhdGgiOiIvIiwiaG9zdCI6ImFsaXl1bi5pbnN0YWxsMDEudm51cGdjbi5jbiIsInRscyI6IiJ9
vmess://eyJ2IjoiMiIsInBzIjoi8J+HqPCfh7NDTiAxOTIg4oaSIG9wZW5pdHN1Yi5jb20iLCJhZGQiOiJhbGl5dW4uaW5zdGFsbDA0LnZudXBnY24uY24iLCJwb3J0IjoiMTE5MDIiLCJ0eXBlIjoibm9uZSIsImlkIjoiMDI1M2I1NzQtODAyMC0zMTg2LWE2NDctMDI2NzI5NWFjOWJiIiwiYWlkIjoiMCIsIm5ldCI6InRjcCIsInBhdGgiOiIvIiwiaG9zdCI6ImFsaXl1bi5pbnN0YWxsMDQudm51cGdjbi5jbiIsInRscyI6IiJ9
vmess://eyJ2IjoiMiIsInBzIjoi8J+HqPCfh7NDTiAxMzkg4oaSIG9wZW5pdHN1Yi5jb20iLCJhZGQiOiJhbGl5dW4uaW5zdGFsbDA0LnZudXBnY24uY24iLCJwb3J0IjoiMTE5MjkiLCJ0eXBlIjoibm9uZSIsImlkIjoiMDI1M2I1NzQtODAyMC0zMTg2LWE2NDctMDI2NzI5NWFjOWJiIiwiYWlkIjoiMCIsIm5ldCI6InRjcCIsInBhdGgiOiIvIiwiaG9zdCI6ImFsaXl1bi5pbnN0YWxsMDQudm51cGdjbi5jbiIsInRscyI6IiJ9
vmess://eyJ2IjoiMiIsInBzIjoi8J+HqPCfh7NDTiAxNTQg4oaSIG9wZW5pdHN1Yi5jb20iLCJhZGQiOiJhbGl5dW4uaW5zdGFsbDAzLnZudXBnY24uY24iLCJwb3J0IjoiMTE5MTEiLCJ0eXBlIjoibm9uZSIsImlkIjoiMDI1M2I1NzQtODAyMC0zMTg2LWE2NDctMDI2NzI5NWFjOWJiIiwiYWlkIjoiMCIsIm5ldCI6InRjcCIsInBhdGgiOiIvIiwiaG9zdCI6ImFsaXl1bi5pbnN0YWxsMDMudm51cGdjbi5jbiIsInRscyI6IiJ9
vmess://eyJ2IjoiMiIsInBzIjoi8J+HqPCfh7NDTiAyMDQg4oaSIG9wZW5pdHN1Yi5jb20iLCJhZGQiOiJhbGl5dW4uaW5zdGFsbDAzLnZudXBnY24uY24iLCJwb3J0IjoiMTE5MTYiLCJ0eXBlIjoibm9uZSIsImlkIjoiMDI1M2I1NzQtODAyMC0zMTg2LWE2NDctMDI2NzI5NWFjOWJiIiwiYWlkIjoiMCIsIm5ldCI6InRjcCIsInBhdGgiOiIvIiwiaG9zdCI6ImFsaXl1bi5pbnN0YWxsMDMudm51cGdjbi5jbiIsInRscyI6IiJ9
vmess://eyJ2IjoiMiIsInBzIjoi8J+HqPCfh7NDTiAxNzcg4oaSIG9wZW5pdHN1Yi5jb20iLCJhZGQiOiJhbGl5dW4ubW9ibGUudm51cGdjbi5jbiIsInBvcnQiOiI5MDExIiwidHlwZSI6Im5vbmUiLCJpZCI6IjAyNTNiNTc0LTgwMjAtMzE4Ni1hNjQ3LTAyNjcyOTVhYzliYiIsImFpZCI6IjAiLCJuZXQiOiJ0Y3AiLCJwYXRoIjoiLyIsImhvc3QiOiJhbGl5dW4ubW9ibGUudm51cGdjbi5jbiIsInRscyI6IiJ9
vmess://eyJ2IjoiMiIsInBzIjoi8J+HqPCfh7NDTiAyMTgg4oaSIG9wZW5pdHN1Yi5jb20iLCJhZGQiOiJhbGl5dW4uaW5zdGFsbDA0LnZudXBnY24uY24iLCJwb3J0IjoiMTE5MTUiLCJ0eXBlIjoibm9uZSIsImlkIjoiMDI1M2I1NzQtODAyMC0zMTg2LWE2NDctMDI2NzI5NWFjOWJiIiwiYWlkIjoiMCIsIm5ldCI6InRjcCIsInBhdGgiOiIvIiwiaG9zdCI6ImFsaXl1bi5pbnN0YWxsMDQudm51cGdjbi5jbiIsInRscyI6IiJ9
    '''
    data = data.strip()
    links = re.split('\r\n|\n|\r',data)
    return links

if __name__ == '__main__':
    # test_ss()
    # test_ssr()
    # test_vmess()
    # test_trojan()
    # test_vless()
    test_random()
