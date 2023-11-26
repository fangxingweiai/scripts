import os
import re
from datetime import datetime, timezone, timedelta

import toml
from dateutil.relativedelta import relativedelta

SHA_TZ = timezone(
    timedelta(hours=8),
    name='Asia/Shanghai',
)


def gen_expired_time(month=1) -> str:
    # 过期时间
    date_after_month = datetime.now(SHA_TZ) + relativedelta(months=month, days=1)
    expired_time = date_after_month.strftime('%d-%m-%Y')

    return expired_time


def get_current_timestamp() -> int:
    return int(datetime.now(SHA_TZ).timestamp())


def get_current_datetime() -> str:
    return datetime.now(tz=SHA_TZ).strftime('%Y-%m-%d %H:%M:%S')


# def timestamp_to_datetime(timestamp: int) -> str:
#     return datetime.fromtimestamp(timestamp, SHA_TZ).strftime('%Y-%m-%d %H:%M:%S')


def expired_time_to_timestamp(date_time: str) -> int:
    return int(datetime.strptime(date_time, '%d-%m-%Y').timestamp())


def is_expired(expire_time: str) -> bool:
    if expire_time != '-1' and get_current_timestamp() > expired_time_to_timestamp(expire_time):
        return True
    return False


############################################################
def normalize_proxy_name(name):
    return re.sub(r'tg|.+群|油管|电报|((http(s)?://|t.me)[a-zA-Z/?=&#.]*)', '***', name)


def load_config(path) -> dict:
    if os.path.exists(path) and os.path.isfile(path):
        with open(path, encoding='UTF-8') as f:
            dict_data = toml.load(f)
            return dict_data
    else:
        return {}


def save_config(path, json_data):
    with open(path, 'w', encoding='UTF-8') as f:
        # f.write(yaml.dump(json_data, allow_unicode=True, default_flow_style=False, sort_keys=False, width=2))
        f.write(toml.dumps(json_data))


if __name__ == '__main__':
    print(datetime.now())
