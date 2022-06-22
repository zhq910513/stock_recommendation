#!/usr/bin/python3
# -*- coding: utf-8 -*-


# import json
# import pprint
# from multiprocessing.pool import ThreadPool
#
import hashlib
# from bs4 import BeautifulSoup
# from pylab import *
import pprint

import requests

from common.log_out import log_err
from dbs.pipelines import MongoPipeline
from rules import r_market_filter

requests.packages.urllib3.disable_warnings()
pp = pprint.PrettyPrinter(indent=4)

# https://data.10jqka.com.cn/dataapi/limit_up/block_top?filter=HS&date=20220621

# 运行时间   每天早上8：00

# mongo db
db = 'stock'

# mongo collections
block_top = 'block_top'  # 最强风口


# 查询条件   $or date + name + code


def get_block_top_stocks(date='20220601'):
    url = f'https://data.10jqka.com.cn/dataapi/limit_up/block_top?filter=HS&date={date}'
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
        req = requests.get(url=url, headers=headers, verify=False)
        if req.status_code == 200:
            if req.json().get('status_code') == 0 and req.json().get('status_msg') == 'success':
                result = req.json().get('data')
                for type_info in result:
                    base_info = {
                        'date': date,
                        'change': type_info['change'],
                        'code': type_info['code'],
                        'continuous_plate_num': type_info['continuous_plate_num'],
                        'days': type_info['days'],
                        'high': type_info['high'],
                        'high_num': type_info['high_num'],
                        'limit_up_num': type_info['limit_up_num'],
                        'name': type_info['name']
                    }
                    stock_list = type_info['stock_list']
                    print(f'---------- {base_info["name"]} 板块 最强风口 {len(stock_list)} 只 ----------')
                    for stock in stock_list:
                        stock.update(base_info)
                        try:
                            if stock['market_id'] not in r_market_filter: continue
                            hash_key = hashlib.md5((stock['date'] + stock['name'] + stock['code']).encode("utf8")).hexdigest()
                            stock.update({'hash_key': hash_key})
                            MongoPipeline(block_top).update_item({'hash_key': None}, stock)
                        except:
                            pass
            else:
                print(req.json())
    except Exception as error:
        log_err(error)


if __name__ == '__main__':
    # date_now = time.strftime("%Y-%m-%d", time.localtime(time.time()))
    # get_block_top_stocks(date_now)

    get_block_top_stocks()
