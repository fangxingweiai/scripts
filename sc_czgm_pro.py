# Author: lindaye
# Update:2023-09-26
# 钢镚(充值购买)阅读
# 活动入口：http://2496831.sl4mwis5.gbl.avc14qvjzax7.cloud/?p=2496831
# 添加账号说明(青龙/本地)二选一
#   青龙: 青龙变量gbtoken 值{"ck":"gfsessionid的值","ts":"Wxpusher的UID"} 一行一个(回车分割)
#   本地: 脚本内置ck方法ck_token = [{"ck":"gfsessionid的值","ts":"Wxpusher的UID"},{"ck":"gfsessionid的值","ts":"Wxpusher的UID"}]
# 脚本使用说明:
#   1.(必须操作)扫码关注wxpusher获取UID: https://wxpusher.zjiecode.com/demo/
#   2.在1打开的网页中点击发送文本消息,查看是否收到,收到可继续
#   3.将1打开的网页中的UID或者以及操作过1的账号UID复制备用
#   4.根据提示说明填写账号变量
# 回调服务器开放说明:
#   1.仅针对授权用户开放,需配合授权软件使用
#   2.青龙变量设置LID变量名,值为授权软件的LID
# 软件版本
"""
cron: 3 * * * *
new Env('钢镚(充值购买)阅读');
"""
name = "充值购买(钢镚)"
linxi_token = "gbtoken"
linxi_tips = '{"ck":"gfsessionid的值","ts":"Wxpusher的UID"}'
import concurrent.futures
import hashlib
import json
import os
import random
import re
import threading
import time
from urllib.parse import quote

import requests

R = threading.Lock()

# 阅读等待时间
tsleep = 10
# 提现限制(元)
Limit = 2

# 充值购买(钢镚)域名(无法使用时请更换)
domain = 'http://2496831.marskkqh7ij0j.jpsl.u1jcnc75wwbyk.cloud'
# 保持连接,重复利用
ss = requests.session()

# 检测文章列表(如有未收录可自行添加)
check_list = [
    'MzkyMzI5NjgxMA==', 'MzkzMzI5NjQ3MA==', 'Mzg5NTU4MzEyNQ==', 'Mzg3NzY5Nzg0NQ==', 'MzU5OTgxNjg1Mg==',
    'Mzg4OTY5Njg4Mw==', 'MzI1ODcwNTgzNA==', 'Mzg2NDY5NzU0Mw=='
]


# 计算sign
def get_sign():
    current_time = str(int(time.time()))
    # 计算 sign
    sign_str = f"key=4fck9x4dqa6linkman3ho9b1quarto49x0yp706qi5185o&time={current_time}"
    sha256_hash = hashlib.sha256(sign_str.encode())
    sign = sha256_hash.hexdigest()
    data = f'time={current_time}&sign={sign}'
    return data


# 获取个人信息模块
def user_info(i, ck):
    # 请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 12; Redmi K30 Pro Build/SKQ1.220303.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/111.0.5563.116 Mobile Safari/537.36 XWEB/5279 MMWEBSDK/20230805 MMWEBID/3850 MicroMessenger/8.0.41.2441(0x28002951) WeChat/arm64 Weixin NetType/4G Language/zh_CN ABI/arm64",
        "Cookie": f"gfsessionid={ck['ck']};"
    }
    try:
        result = ss.get(domain + "/share", headers=headers, data=get_sign()).json()
        share_link = result["data"]["share_link"][0]
        userid = share_link.split("=")[1].split("&")[0]
    except:
        print(f"账号【{i + 1}】请检查你的CK({ck['ck']})是否正确!")
        return False
    result = ss.get(domain + "/read/info", headers=headers, data=get_sign()).json()
    if result["code"] == 0:
        remain = result["data"]["remain"]
        read = result["data"]["read"]
        print(f"账号【{i + 1}】UID:{userid} 余额:{remain} 今日:{read}篇 推广:{share_link}")
    else:
        print(f'账号【{i + 1}】用户信息获取失败:{result["message"]}')


# 阅读文章模块
def do_read(args):
    i, ck = args
    # 请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 12; Redmi K30 Pro Build/SKQ1.220303.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/111.0.5563.116 Mobile Safari/537.36 XWEB/5279 MMWEBSDK/20230805 MMWEBID/3850 MicroMessenger/8.0.41.2441(0x28002951) WeChat/arm64 Weixin NetType/4G Language/zh_CN ABI/arm64",
        "Cookie": f"gfsessionid={ck['ck']};"
    }
    while True:
        response = ss.get(domain + "/read/task", headers=headers, data=get_sign())
        try:
            response = response.json()
        except json.decoder.JSONDecodeError:
            print(f"账号【{i + 1}】请检查你的CK({ck['ck']})是否正确!")
            return False
        if response["code"] == 1:
            if "秒" in response['message']:
                print(f"账号【{i + 1}】即将开始:{response['message']}")
                time.sleep(5)
            elif response['message'] == "记录失效":
                print(f"账号【{i + 1}】阅读异常,重新获取:{response['message']}")
            else:
                print(f"账号【{i + 1}】{response['message']}")
                break
        else:
            try:
                s = random.randint(10, 12)
                # 检测是否是检测文章
                biz = re.findall("biz=(.*?)&", response["data"]["link"])[0]
                print(f"账号【{i + 1}】获取文章成功-{biz}-模拟{s}秒")
                if biz in check_list:
                    print(f"账号【{i + 1}】阅读检测文章-已推送微信,请40s内完成验证!")
                    # 过检测
                    check = check_status(ck['ts'], response["data"]["link"], i)
                    if check == True:
                        print(f"账号【{i + 1}】检测文章-过检测成功啦!")
                        response = ss.post(domain + "/read/finish", headers=headers, data=get_sign()).json()
                        print(
                            f'账号【{i + 1}】阅读文章成功-获得钢镚[{response["data"]["gain"]}]-已读{response["data"]["read"]}篇')
                    else:
                        print(f"账号【{i + 1}】检测文章-过检测失败啦!")
                        break
                else:
                    time.sleep(s)
                    response = ss.post(domain + "/read/finish", headers=headers, data=get_sign()).json()
                    # print(response)
                    if response["code"] == 0:
                        if response["data"]["check"] is False:
                            print(
                                f'账号【{i + 1}】阅读文章成功-获得钢镚[{response["data"]["gain"]}]-已读{response["data"]["read"]}篇')
                        else:
                            print(f"账号【{i + 1}】获取到未收录检测: {biz} 将自动停止脚本")
                            break
                    else:
                        if response['message'] == "记录无效":
                            print(f"账号【{i + 1}】记录无效,重新阅读")
                        else:
                            print(f"账号【{i + 1}】{response}")
                            break
            except KeyError:
                if response['code'] == 801:
                    print(f"账号【{i + 1}】今日任务已完成: {response['message']}")
                    break
                else:
                    print(f"账号【{i + 1}】获取文章失败,错误未知{response}")
                    break


# 提现模块
def get_money(i, ck):
    # 请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 12; Redmi K30 Pro Build/SKQ1.220303.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/111.0.5563.116 Mobile Safari/537.36 XWEB/5279 MMWEBSDK/20230805 MMWEBID/3850 MicroMessenger/8.0.41.2441(0x28002951) WeChat/arm64 Weixin NetType/4G Language/zh_CN ABI/arm64",
        "Cookie": f"gfsessionid={ck['ck']};"
    }
    response = ss.get(domain + "/read/info", headers=headers, data=get_sign())
    try:
        response = response.json()
    except json.decoder.JSONDecodeError:
        print(f"账号【{i + 1}】请检查你的CK({ck['ck']})是否正确!")
        return False
    if response["code"] == 0:
        remain = response["data"]["remain"]
    else:
        print(f'账号【{i + 1}】获取用户信息失败: {response["message"]}')
    if remain >= Limit * 10000:
        response = ss.get(domain + "/withdraw/wechat", headers=headers, data=get_sign()).json()
        if response["code"] == 0:
            print(f'账号【{i + 1}】开始提现:{response["message"]}')
        elif response["code"] == 1:
            print(f'账号【{i + 1}】开始提现:{response["message"]}')
        else:
            print(f'账号【{i + 1}】未知错误:{response}')
    else:
        print(f'账号【{i + 1}】当前余额为{remain} 未到达{Limit}元提现限制!')


# 微信推送模块
def check_status(key, link, index):
    with R:
        time.sleep(5)

    result = ss.get(
        f'https://wxpusher.zjiecode.com/demo/send/custom/{key}?content=检测文章-{name}%0A请在{tsleep}秒内完成验证!%0A%3Cbody+onload%3D%22window.location.href%3D%27{quote(link)}%27%22%3E').json()
    print(f"账号【{str(index + 1)}】微信消息推送: {result['msg']},等待{tsleep}s完成验证!")
    # print(f"手动微信阅读链接: {link}")
    time.sleep(tsleep)
    return True


def main():
    if os.getenv(linxi_token) is None:
        print(f'青龙变量异常: 请添加{linxi_token}变量示例:{linxi_tips} 确保一行一个')
        return

    ck_token = [json.loads(line) for line in os.getenv(linxi_token).splitlines()]

    print("==================开始阅读文章=================")
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(ck_token)) as executor:
        executor.map(do_read, list(enumerate(ck_token)))

    print("==================获取账号信息=================")
    for i, ck in list(enumerate(ck_token)):
        user_info(i, ck)

    print("==================开始账号提现=================")
    for i, ck in list(enumerate(ck_token)):
        get_money(i, ck)


if __name__ == "__main__":
    main()
