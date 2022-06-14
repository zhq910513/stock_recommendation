#!/usr/bin/python3
# -*- coding:utf-8 -*-
import sys

from pyhive import hive

sys.path.append("../")

import pymysql
from pymongo import MongoClient
from pymysql.err import IntegrityError
from pymongo.errors import DuplicateKeyError
from dbs import mongo_setting, mysql_setting, hive_setting
from common.log_out import log_err


class MongoPipeline:
    def __init__(self, COLLECTION):
        if not mongo_setting.MONGO_USR and not mongo_setting.MONGO_PWD:
            client = MongoClient(f'mongodb://{mongo_setting.MONGO_HOST}:{mongo_setting.MONGO_PORT}')
        else:
            client = MongoClient(f'mongodb://{mongo_setting.MONGO_HOST}:{mongo_setting.MONGO_PORT}')
        self.coll = client[mongo_setting.MONGO_DB][COLLECTION]

    def insert_item(self, item):
        status = False
        if not item:
            return False
        elif isinstance(item, list):
            for _i in item:
                try:
                    self.coll.insert_one(_i)
                    print(_i)
                except DuplicateKeyError:
                    status = True
                except Exception as error:
                    log_err(error)
                    status = True
        elif isinstance(item, dict):
            try:
                self.coll.insert_one(item)
                print(item)
            except DuplicateKeyError:
                status = True
                pass
            except Exception as error:
                log_err(error)
                status = True
        else:
            status = False
        return status

    @staticmethod
    def field_query(model, data):
        new_data = {}
        for key in model.keys():
            new_data.update({
                key: data.get(key)
            })
        return new_data

    def update_item(self, query, item):
        if not item: return
        if isinstance(item, list):
            for _i in item:
                print(_i)
                try:
                    self.coll.update_one(self.field_query(query, _i), {'$set': _i}, upsert=True)
                except DuplicateKeyError:
                    pass
                except Exception as error:
                    log_err(error)
        elif isinstance(item, dict):
            print(item)
            try:
                self.coll.update_one(self.field_query(query, item), {'$set': item}, upsert=True)
            except Exception as error:
                log_err(error)

    def find(self, query):
        return self.coll.find(query)

    def find_one(self, query):
        return self.coll.find_one(query)

    def count(self, query):
        return self.coll.count_documents(query)


class MysqlPipeline:
    @staticmethod
    def MySql():
        # 实例化 Mysql
        host = mysql_setting.MYSQL_HOST
        mysqldb = mysql_setting.MYSQL_DB
        user = mysql_setting.MYSQL_USR
        pwd = mysql_setting.MYSQL_PWD
        conn = pymysql.Connect(
            host=host,
            port=3306,
            user=user,
            password=pwd,
            db=mysqldb,
            charset='utf8mb4',
            autocommit=True
        )
        return conn

    # 插入元数据
    def process_insert_models(self, item):
        try:
            print(item['category_name'])
            conn = self.MySql()

            # insertSql = '''INSERT INTO food_nutrition_category(category_link,category_name) VALUES('%s','%s')'''
            insertSql = '''INSERT INTO food_nutrition_list(food_link,food_name,category_name,calories,carbohydrate,axunge,protein,cellulose) VALUES('%s','%s','%s','%d','%d','%d','%d','%d')'''
            food_link = str(item.get('food_link'))
            food_name = str(item.get('food_name'))
            category_name = item.get('category_name')
            calories = item.get('热量(大卡)', 0)
            if calories == '一':
                calories = 0
            carbohydrate = item.get('碳水化合物(克)', 0)
            if carbohydrate == '一':
                carbohydrate = 0
            axunge = item.get('脂肪(克)', 0)
            if axunge == '一':
                axunge = 0
            protein = item.get('蛋白质(克)', 0)
            if protein == '一':
                protein = 0
            cellulose = item.get('纤维素(克)', 0)
            if cellulose == '一':
                cellulose = 0
            print(calories, carbohydrate, axunge, protein, cellulose)

            insertData = (
                # str(item.get('category_link')),
                # str(item.get('category_name'))

                food_link,
                food_name,
                category_name,
                float(calories),
                float(carbohydrate),
                float(axunge),
                float(protein),
                float(cellulose)
            )

            # updateSql = "update food_nutrition_category set category_name='%s' where category_link='%s'"
            updateSql = "update food_nutrition_list set food_name='%s',food_name='%s',calories='%d',carbohydrate='%d',axunge='%d',protein='%d',cellulose='%d' where food_link='%s'"
            updateData = (
                # str(item.get('category_name')),
                # str(item.get('category_link'))

                food_name,
                category_name,
                float(calories),
                float(carbohydrate),
                float(axunge),
                float(protein),
                float(cellulose),
                food_link
            )

            if insertData and updateData:
                self.UpdateToMysql(conn, insertSql, insertData, updateSql, updateData)

            conn.cursor().close()
        except Exception as error:
            print(item)
            log_err(error)

    # 修改已下载状态
    def update_model_status(self, full_name):
        try:
            print(full_name)
            conn = self.MySql()

            updateSql = "update huggingface_models set download_status='%d' where full_name='%s'"
            updateData = (
                1,
                full_name
            )

            if updateData:
                try:
                    cursor = conn.cursor()
                    cursor.execute(updateSql % updateData)
                    conn.commit()
                except Exception as error:
                    log_err(error)
                    log_err(updateData)
                    conn.commit()

            conn.cursor().close()
        except Exception as error:
            print(full_name)
            log_err(error)

    # 插入数据集
    def process_insert_datasets(self, item):
        try:
            print(item['dataset_name'])
            conn = self.MySql()

            insertSql = '''INSERT INTO huggingface_datasets(dataset_name,link,file_path,downloads,last_modified,likes,
            download_status,spider_time,tasks,task_categories,languages,multilinguality,size_categories,licenses,
            language_creators,annotations_creators,source_datasets) VALUES('%s','%s','%s','%d','%s','%d','%d','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')'''

            insertData = (
                str(item.get('dataset_name')),
                str(item.get('link')),
                str(item.get('file_path')),
                item.get('downloads', 0),
                str(item.get('last_modified')),
                item.get('likes', 0),
                item.get('download_status', 0),
                str(item.get('spider_time')),
                str(item.get('tasks')),
                str(item.get('task_categories')),
                str(item.get('languages')),
                str(item.get('multilinguality')),
                str(item.get('size_categories')),
                str(item.get('licenses')),
                str(item.get('language_creators')),
                str(item.get('annotations_creators')),
                str(item.get('source_datasets'))
            )

            updateSql = "update huggingface_datasets set link='%s',file_path='%s',downloads='%d',last_modified='%s',likes='%d',spider_time='%s',tasks='%s',task_categories='%s',languages='%s',multilinguality='%s',size_categories='%s',licenses='%s',language_creators='%s',annotations_creators='%s',source_datasets='%s' where dataset_name='%s'"
            updateData = (
                str(item.get('link')),
                str(item.get('file_path')),
                item.get('downloads', 0),
                str(item.get('last_modified')),
                item.get('likes', 0),
                str(item.get('spider_time')),
                str(item.get('tasks')),
                str(item.get('task_categories')),
                str(item.get('languages')),
                str(item.get('multilinguality')),
                str(item.get('size_categories')),
                str(item.get('licenses')),
                str(item.get('language_creators')),
                str(item.get('annotations_creators')),
                str(item.get('source_datasets')),

                str(item.get('dataset_name'))
            )

            if insertData and updateData:
                self.UpdateToMysql(conn, insertSql, insertData, updateSql, updateData)

            conn.cursor().close()
        except Exception as error:
            print(item)
            log_err(error)

    # 修改已下载状态
    def update_dataset_status(self, dataset_name):
        try:
            print(dataset_name)
            conn = self.MySql()

            updateSql = "update huggingface_datasets set download_status='%d' where dataset_name='%s'"
            updateData = (
                1,
                dataset_name
            )

            if updateData:
                try:
                    cursor = conn.cursor()
                    cursor.execute(updateSql % updateData)
                    conn.commit()
                except Exception as error:
                    log_err(error)
                    log_err(updateData)
                    conn.commit()

            conn.cursor().close()
        except Exception as error:
            print(dataset_name)
            log_err(error)

    # 更新数据到MySQL
    @staticmethod
    def UpdateToMysql(conn, insertSql, insertData, updateSql, updateData):
        cursor = conn.cursor()

        try:
            cursor.execute(insertSql % insertData)
            conn.commit()
        except IntegrityError:
            try:
                cursor.execute(updateSql % updateData)
                conn.commit()
            except Exception as error:
                log_err(error)
                log_err(updateData)
                conn.commit()


class HivePipeline:
    def __init__(self, env):
        self.env = hive_setting.hive_config[env]

    def Hive(self):
        # 实例化 Hive
        host = self.env['host']
        port = self.env['port']
        db = self.env['db']
        user = self.env['usr']
        conn = hive.Connection(host=host, port=port, username=user, database=db)
        return conn

    # 插入元数据
    def execute_sql(self, sql):
        result_list = []
        try:
            conn = self.Hive()
            cursor = conn.cursor()
            cursor.execute(sql)
            for result in cursor.fetchall():
                if not result:continue
                result_list.append(str(result[0]))
            cursor.close()
            return result_list
        except Exception as error:
            print(sql)
            log_err(error)


"""
            # sql = '''INSERT INTO test(city,date,province,city_link,weather_link,天气状况,气温,风力风向) VALUES('%s','%s','%s','%s','%s','%s','%s','%s')'''
            # cursor.execute(sql % insertData)

            # insertData = (1, 'hshsh')
            # sql = '''INSERT INTO student(id,name) VALUES(1,'ssfasfas')'''
            # cursor.execute(sql)

            cursor.execute('truncate table epidemic_history')
            # cursor.execute('show tables')
            # cursor.execute('desc city_info')
"""

if __name__ == '__main__':
    env = 'dev'
    hp = HivePipeline(env)

    # 查询所有表
    # hp_sql = "insert overwrite table epidemic_knowledge select * from epidemic_knowledge where detail in('detail')"

    # 清空表数据
    table_name = "epidemic_history"
    hp_sql = f"truncate table {table_name}"

    # 查询表信息
    # hp_sql = f"desc {table_name}"

    print(hp.execute_sql(hp_sql))
