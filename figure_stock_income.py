import pprint
pp = pprint.PrettyPrinter(indent=4)

set_capital = 10000


# 计算买进后自动卖出的价格
def handle_price(buy_price):
    buy_pice = int(set_capital / buy_price / 100)
    buy_count = buy_pice * 100

    used_money = round(buy_price * buy_count, 0)

    income_rate = 0.19
    sale_price = round(buy_price * (1 + income_rate), 3)

    cost_rate = 0.009569
    cost = round((sale_price-buy_price) * buy_count * cost_rate, 2)

    incomes = round(((sale_price-buy_price) * buy_count) - cost, 2)
    print(f'可购买 {buy_pice} 手\n本次花费 {used_money} 元\n卖出价格 {sale_price} 元\n预计收益 {incomes} 元')


if __name__ == '__main__':
    buy = 26.017
    handle_price(buy)

