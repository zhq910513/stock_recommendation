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

# https://eq.10jqka.com.cn/lhbEnhanced/public/indexV2.html

# 运行时间   每天下午18：00

# mongo db
db = 'stock'

# mongo collections
longhu_all = 'longhu_all'  # 总榜
longhu_capital = 'longhu_capital'  # 机构榜
longhu_org = 'longhu_org'  # 游资榜


def get_all_stocks(date='2022-06-21'):
    url = f'https://eq.10jqka.com.cn/lhbclient/data/method/indexData/date/{date}/'
    headers = {
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Host': 'eq.10jqka.com.cn',
        'Pragma': 'no-cache',
        'Referer': 'https://eq.10jqka.com.cn/lhbEnhanced/public/indexV2.html',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }

    try:
        req = requests.get(url=url, headers=headers, verify=False)
        if req.status_code == 200:
            if req.json().get('status_code') == '0' and req.json().get('status_msg') == 'ok':
                result = req.json().get('data')
                # 总榜
                all_data = result.get('all').get('list')
                print(f'---------- {date} 龙虎榜 {len(all_data)} 只 ----------')
                for data in all_data:
                    try:
                        if data['marketId'] not in r_market_filter: continue
                        hash_key = hashlib.md5((date + data['stockCode']).encode("utf8")).hexdigest()
                        data.update({'hash_key': hash_key, 'date': date})
                        MongoPipeline(longhu_all).update_item({'hash_key': None}, data)
                    except:
                        pass

                # 机构榜
                capital_data = result.get('capital').get('list')
                print(f'---------- {date} 机构榜 {len(capital_data)} 只 ----------')
                for data in capital_data:
                    try:
                        if data['marketId'] not in r_market_filter: continue
                        hash_key = hashlib.md5((date + data['stockCode']).encode("utf8")).hexdigest()
                        data.update({'hash_key': hash_key, 'date': date})
                        MongoPipeline(longhu_capital).update_item({'hash_key': None}, data)
                    except:
                        pass

                # 游资榜
                org_data = result.get('org').get('list')
                print(f'---------- {date} 游资榜 {len(org_data)} 只 ----------')
                for data in org_data:
                    try:
                        if data['marketId'] not in r_market_filter: continue
                        hash_key = hashlib.md5((date + data.get('stockCode')).encode("utf8")).hexdigest()
                        data.update({'hash_key': hash_key, 'date': date})
                        MongoPipeline(longhu_org).update_item({'hash_key': None}, data)
                    except:
                        pass
            else:
                print(req.json())
    except Exception as error:
        log_err(error)


if __name__ == '__main__':
    date_now = time.strftime("%Y-%m-%d", time.localtime(time.time()))
    get_all_stocks(date_now)
