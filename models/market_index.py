#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pprint
import time

import requests
from bs4 import BeautifulSoup

from dbs.pipelines import MongoPipeline

requests.packages.urllib3.disable_warnings()
pp = pprint.PrettyPrinter(indent=4)

# https://finance.pae.baidu.com/api/indexbanner?market=ab&finClientType=pc

# 运行时间   每天下午18：00

# mongo db
db = 'stock'

# mongo collections
market = 'market'


def get_history_data(code="000001"):
    year = str(time.strftime("%Y", time.localtime(time.time())))
    for s in [
        # 1,
        # 2,
        3,
        # 4
    ]:
        url = f'http://quotes.money.163.com/trade/lsjysj_zhishu_{code}.html?year={year}&season={s}'
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Host': 'quotes.money.163.com',
            'Pragma': 'no-cache',
            'Referer': 'http://quotes.money.163.com/trade/lsjysj_zhishu_000001.html',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
        }
        try:
            req = requests.get(url=url, headers=headers, verify=False, timeout=2)
            if req.status_code == 200:
                soup = BeautifulSoup(req.text, 'lxml')
                for tr in soup.find('table', {'class': 'table_bg001 border_box limit_sale'}).find_all('tr'):
                    try:
                        date_str = tr.find_all('td')[0].get_text()
                        timeStamp = int(time.mktime(time.strptime(date_str, "%Y%m%d")))
                        date = time.strftime("%Y-%m-%d", time.localtime(timeStamp))
                        kp = round(float(tr.find_all('td')[1].get_text().replace(',', '')), 2)
                        high = round(float(tr.find_all('td')[2].get_text().replace(',', '')), 2)
                        low = round(float(tr.find_all('td')[3].get_text().replace(',', '')), 2)
                        sp = round(float(tr.find_all('td')[4].get_text().replace(',', '')), 2)
                        zde = round(float(tr.find_all('td')[5].get_text().replace(',', '')), 2)
                        zdf = round(float(tr.find_all('td')[6].get_text().replace(',', '')), 2)
                        cjl = round(float(tr.find_all('td')[7].get_text().replace(',', '')), 2)
                        cje = round(float(tr.find_all('td')[8].get_text().replace(',', '')), 2)
                        data = {
                            'code': code,
                            'timeStamp': timeStamp,
                            "日期": date,
                            "开盘": kp,
                            "最高": high,
                            "收盘": sp,
                            "最低": low,
                            "涨跌额": zde,
                            "涨跌幅": zdf,
                            "成交量": cjl,
                            "成交额": cje,
                        }
                        try:
                            MongoPipeline(market).update_item({'code': None, 'timeStamp': None}, data)
                        except:
                            pass
                    except:
                        pass
        except:
            pass


def analysis():
    # 更新当天大盘数据
    # get_history_data()

    rate_data = {}
    for d in [1]:
        for info in MongoPipeline(market).find({"code": "000001"}).sort("timeStamp", -1).limit(d):
            rate_data[f'{d}d'] = info["涨跌幅"]

    for d in [5, 30, 60, 90]:
        infos = []
        for info in MongoPipeline(market).find({"code": "000001"}).sort("timeStamp", -1).limit(d):
            infos.append(float(info["收盘"]))
        rate = round(((infos[-1]-infos[0])/infos[0])*100, 2)
        if infos[-1] > infos[0]: rate = -rate
        rate_data[f'{d}d'] = rate
    return rate_data


if __name__ == '__main__':
    print(analysis())
