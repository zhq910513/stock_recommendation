import pandas as pd
from pymongo import MongoClient

"""
    用户配置
"""
MONGO_HOST = '192.168.50.22'
MONGO_DB = 'public_city'
MONGO_COLLECTION = 'city_weather'

# DOWNLOAD_FILE_NAME = f'./{MONGO_DB}_{MONGO_COLLECTION}.csv'  # 默认保存在当前执行目录  以数据 库_表 命名
DOWNLOAD_FILE_NAME = f'./{MONGO_COLLECTION}.csv'  # 默认保存在当前执行目录  以数据 库_表 命名

query = {}  # 查询条件
SKIP = 0  # 跳过前面几条数据
LIMIT = 20  # 返回几条数据  默认 None 表示返回全部

HEADER = None

client = MongoClient('mongodb://{}:27017'.format(MONGO_HOST))
coll = client[MONGO_DB][MONGO_COLLECTION]

FILTTER_KEYS = ['city_link', 'weather_link']


def select_all_data():
    data_list = []
    key_list = []
    if LIMIT:
        _mongo = coll.find(query).skip(SKIP).limit(LIMIT)
    else:
        _mongo = coll.find(query).skip(SKIP)
    for num, info in enumerate(_mongo):
        if num == 0:
            for key in info.keys():
                if key != '_id':
                    if key not in FILTTER_KEYS:
                        key_list.append(key)

        try:
            del info['_id']
        except:
            pass

        data_list.append(info)
    return key_list, data_list


def tarnsform_data():
    key_list, data_list = select_all_data()
    print(key_list)
    if data_list and key_list:
        info = pd.DataFrame(data_list, columns=key_list)
        info.to_csv(DOWNLOAD_FILE_NAME, index=False, header=HEADER)


if __name__ == '__main__':
    tarnsform_data()
