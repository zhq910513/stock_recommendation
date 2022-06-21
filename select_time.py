# 获取最近两周工作日列表、节假日列表
import datetime
import chinese_calendar
import time
import pandas as pd

# 将时间戳转换成格式化日期
def timestamp_to_str(timestamp=None, format='%Y-%m-%d %H:%M:%S'):
    if timestamp:
        time_tuple = time.localtime(timestamp)  # 把时间戳转换成时间元祖
        result = time.strftime(format, time_tuple)  # 把时间元祖转换成格式化好的时间
        return result
    else:
        return time.strptime(format)

def get_normal_special_day_list(day_nums=20):
    normal_day_list_start = []
    special_day_list_start = []
    normal_day_list_end = []
    special_day_list_end = []
    # 获取当天凌晨时间
    today = datetime.date.today()
    today_time = int(time.mktime(today.timetuple()))
    oneday_time = 86400
    for i in range(day_nums):
        today_time -= oneday_time
        today_time_str = timestamp_to_str(today_time)
        today_end_time_str = timestamp_to_str(today_time + oneday_time - 1)
        t = pd.Timestamp(today_time_str)
        if chinese_calendar.is_holiday(t.date()) == True:
            special_day_list_start.append(today_time_str)
            special_day_list_end.append(today_end_time_str)
        else:
            normal_day_list_start.append(today_time_str)
            normal_day_list_end.append(today_end_time_str)
    return normal_day_list_start, special_day_list_start, normal_day_list_end, special_day_list_end

normal_day_list_start, special_day_list_start, normal_day_list_end, special_day_list_end = get_normal_special_day_list()
print(normal_day_list_start)
print(normal_day_list_end)
print(special_day_list_start)
print(special_day_list_end)
