#!/usr/bin/python3
# -*- coding: utf-8 -*-

import hashlib
import pprint
import time

import requests

from common.log_out import log_err
from dbs.pipelines import MongoPipeline
from rules import r_market_filter

requests.packages.urllib3.disable_warnings()
pp = pprint.PrettyPrinter(indent=4)

# https://eq.10jqka.com.cn/open/api/wencai/zhangting5.txt

# 运行时间   每天下午18：00

# mongo db
db = 'stock'

# mongo collections
geguzhangfu = 'geguzhangfu'  # 个股涨幅


def get_geguzhangfu_stocks():
    hour_now = int(time.strftime("%H", time.localtime(time.time())))
    if hour_now >= 18:
        date = time.strftime("%Y%m%d", time.localtime(time.time()))
    else:
        date = time.strftime("%Y%m%d", time.localtime(time.time() - 86400))
    url = "https://eq.10jqka.com.cn/open/api/wencai/zhangting5.txt"
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Host': 'eq.10jqka.com.cn',
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
        req = requests.get(url=url, headers=headers, verify=False)
        if req.status_code == 200:
            result = req.json()
            print(f'---------- {date} 个股涨幅 {len(result)} 只 ----------')
            for data in result:
                try:
                    if str(data['code'])[:3] not in r_market_filter: continue
                    hash_key = hashlib.md5((date + data['code']).encode("utf8")).hexdigest()
                    data.update({'hash_key': hash_key, 'date': date})
                    MongoPipeline(geguzhangfu).update_item({'hash_key': None}, data)
                except:
                    pass
    except Exception as error:
        log_err(error)


if __name__ == '__main__':
    get_geguzhangfu_stocks()
