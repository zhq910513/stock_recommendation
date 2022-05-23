import pprint
pp = pprint.PrettyPrinter(indent=4)

set_amount = 10000


# 计算买进后自动卖出的价格
def handle_price(buy_price):
    buy_pice = int(set_amount / buy_price / 100)
    print(f'可购买 {buy_pice} 手')

    buy_count = buy_pice * 100

    used_money = round(buy_price * buy_count, 0)

    income_rate = 0.19
    sale_price = round(buy_price * (1 + income_rate), 3)

    buy_cost_rate = 0.0149
    buy_cost = round(buy_price * buy_count * buy_cost_rate, 0)

    sale_cost_rate = 0.0149
    sale_cost = round(sale_price * buy_count * sale_cost_rate, 0)
    costs = buy_cost + sale_cost

    incomes = round((buy_count * (sale_price - buy_price)) - costs, 0)
    return f'本次花费 {used_money} 元\n卖出价格 {sale_price} 元\n预计收益 {incomes} 元'


if __name__ == '__main__':
    buy = 17.017
    print(handle_price(buy))
