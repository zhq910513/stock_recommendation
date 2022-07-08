import json
import re
import time

import requests


class LineType(object):
    @staticmethod
    def analysis_k_data(data: list):
        kp = float(data[1])
        sp = float(data[2])
        zg = float(data[3])
        zd = float(data[4])
        zdf = float(sp - kp)
        format_status = {
            'a': '倒T字',
            'b': 'T字',
            'c': '一字',
            'd': '大阳 短下影线',
            'e': '大阳 锤头线',
            'f': '大阴 短下影线',
            'g': '大阴 锤头线',
            'h': '大阳 短上影线',
            'i': '大阴 短上影线',
            'j': '双头大阳线',
            'k': '大阳 双头 上影线',
            'l': '大阳 双头 下影线',
            'm': '双头大阴线',
            'n': '大阴 双头 上影线',
            'o': '大阴 双头 下影线'
        }

        # 三天线状
        status = None
        try:
            st = abs(sp - kp)
            syx = abs(zg - sp)
            xyx = abs(zd - sp)

            if st == 0:
                if syx > 0 and xyx == 0:
                    status = 'a'
                elif syx == 0 and xyx > 0:
                    status = 'b'
                else:
                    status = 'c'
            else:
                if syx != 0:
                    syx_rate = round(syx / st, 2)
                else:
                    syx_rate = 0
                if xyx != 0:
                    xyx_rate = round(xyx / st, 2)
                else:
                    xyx_rate = 0
                if syx == 0 and xyx != 0:
                    if zdf > 0:
                        if xyx_rate > 0.3:
                            status = 'd'
                        else:
                            status = 'e'
                    elif zdf < 0:
                        if xyx_rate > 0.3:
                            status = 'f'
                        else:
                            status = 'g'
                    else:
                        status = f'[st!=0,syx==0,xyx!=0,zdf==0]{data}'
                elif syx != 0 and xyx == 0:
                    if zdf > 0:
                        if xyx_rate > 0.3:
                            status = 'h'
                        else:
                            status = 'e'
                    elif zdf < 0:
                        if xyx_rate > 0.3:
                            status = 'i'
                        else:
                            status = 'g'
                    else:
                        status = f'[st!=0,syx!=0,xyx==0,zdf==0]{data}'
                elif syx != 0 and xyx != 0:
                    if zdf > 0:
                        if syx_rate <= 0.3 and xyx <= 0.3:
                            status = 'j'
                        else:
                            if syx > xyx:
                                status = 'k'
                            else:
                                status = 'l'
                    elif zdf < 0:
                        if syx_rate <= 0.3 and xyx <= 0.3:
                            status = 'm'
                        else:
                            if syx > xyx:
                                status = 'n'
                            else:
                                status = 'o'
                    else:
                        status = f'[st!=0,zdf==0,syx==xyx]{data}'
                else:
                    if zdf > 0:
                        status = '强势 大 阳 线'
                    elif zdf < 0:
                        status = '强势 大 阴 线'
                    else:
                        status = f'[st!=0,syx==0,xyx!=0,zdf==0]{data}'
        except Exception as error:
            print(error)
        return status, format_status[status]


if __name__ == '__main__':
    def req_history_data(stock_code):
        try:
            l = LineType()

            url = f'http://78.push2his.eastmoney.com/api/qt/stock/kline/get' \
                  f'?cb=jQuery' \
                  f'&secid=0.{stock_code}' \
                  f'&ut=fa5fd1943c7b386f172d6893dbfba10b' \
                  f'&fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6' \
                  f'&fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58%2Cf59%2Cf60%2Cf61' \
                  f'&klt=101' \
                  f'&fqt=0' \
                  f'&end=20500101' \
                  f'&lmt=120' \
                  f'&_={int(time.time() * 1000)}'
            headers = {
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Connection': 'keep-alive',
                'Cookie': 'qgqp_b_id=e829d607b6454c6dde64109c61f936e2; st_si=21280292358923; HAList=a-sz-000756-%u65B0%u534E%u5236%u836F; em_hq_fls=js; st_pvi=94651109933561; st_sp=2022-06-11%2016%3A19%3A10; st_inirUrl=https%3A%2F%2Fwww.baidu.com%2Flink; st_sn=17; st_psi=20220611165158402-113200301201-7930304906; st_asi=delete',
                'Host': '46.push2his.eastmoney.com',
                'Referer': 'http://quote.eastmoney.com/',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
            }
            resp = requests.get(url=url, headers=headers)
            resp_data = json.loads(re.findall('\((.*?)\)', resp.text, re.S)[0]).get('data')
            for h in resp_data.get('klines')[-30:]:
                data = h.split(',')
                print(data)
                print(l.analysis_k_data(data))
        except Exception as error:
            print(error)
    req_history_data('000722')
