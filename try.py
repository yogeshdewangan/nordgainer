import truedata
from classes.Order import Order
import conf_reader


def main():
    for stock in  conf_reader.MYDEF:

        current_price = truedata.get_current_data(stock.req_code)
        order = Order("buy", current_price, current_price-10)
        stock.orders.append(order)

    pass


if __name__ == '__main__':
    main()
