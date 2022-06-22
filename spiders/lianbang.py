#!/usr/bin/python3
# -*- coding: utf-8 -*-

import hashlib
import pprint
import time
from urllib.parse import urlencode

import requests

from common.log_out import log_err
from dbs.pipelines import MongoPipeline
from rules import r_market_filter

requests.packages.urllib3.disable_warnings()
pp = pprint.PrettyPrinter(indent=4)

# https://data.10jqka.com.cn/dataapi/limit_up/continuous_limit_pool?page=1&limit=1000&field=199112,10,330329,330325,133971,133970,1968584,3475914,3541450,9004&filter=HS,GEM2STAR&order_field=330329&order_type=0&date=&_=1655790923953

# 运行时间   每天下午18：00

# mongo db
db = 'stock'

# mongo collections
lianbang = 'lianbang'  # 连榜


def get_lianbang_stocks():
    hour_now = int(time.strftime("%H", time.localtime(time.time())))
    if hour_now >= 18:
        date = time.strftime("%Y%m%d", time.localtime(time.time()))
    else:
        date = time.strftime("%Y%m%d", time.localtime(time.time() - 86400))
    url = "https://data.10jqka.com.cn/dataapi/limit_up/continuous_limit_pool"
    params = {
        "page": "1",
        "limit": "1000",
        "field": "199112,10,330329,330325,133971,133970,1968584,3475914,3541450,9004",
        "filter": "HS,GEM2STAR",
        "order_field": "330329",
        "order_type": "0",
        "date": f"{date}"
    }
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Host': 'data.10jqka.com.cn',
        'Pragma': 'no-cache',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
    }
    try:
        req = requests.get(url=url, headers=headers, params=urlencode(params), verify=False)
        if req.status_code == 200:
            if req.json().get('status_code') == 0 and req.json().get('status_msg') == 'success':
                result = req.json().get('data')
                all_data = result.get('info')
                print(f'---------- {date} 连榜 {len(all_data)} 只 ----------')
                for data in all_data:
                    try:
                        if str(data['code'])[:3] not in r_market_filter: continue
                        hash_key = hashlib.md5((date + data['code']).encode("utf8")).hexdigest()
                        data.update({'hash_key': hash_key, 'date': date})
                        MongoPipeline(lianbang).update_item({'hash_key': None}, data)
                    except:
                        pass
            else:
                print(req.json())
    except Exception as error:
        log_err(error)


if __name__ == '__main__':
    get_lianbang_stocks()
