from spiders.geguzhangfu import get_geguzhangfu_stocks
from spiders.lianbang import get_lianbang_stocks
from spiders.longhubang import get_all_stocks
from spiders.select_quality_stocks import Stock

def run():
    # 获取龙虎榜
    get_all_stocks()

    # 获取连榜
    get_lianbang_stocks()

    # 获取个股榜
    get_geguzhangfu_stocks()

    # 最后推荐结果
    s = Stock('geguzhangfu')
    s.get_result()

if __name__ == '__main__':
    run()