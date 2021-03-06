from classes.Order import Order
import conf_reader
import traceback
from classes import alpha as bridge
import truedata
import logging
import time
from classes.STOCK import Type
import os
import shutil
import datetime
import sys
from classes.BACKTEST import  BACKTEST

# Enable below to trade with fyers
# from classes import bridge as bridge
# broker_name = "Fyers"

# # Enable below to trade with sas onlne alpha


broker_name = "SAS Online"
log = logging.getLogger("IndiBotLog")

for root, dirs, files in os.walk('stock_data'):
    try:
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))
    except:
        pass

profit = 0

back_test = conf_reader.props["back_test"]
if back_test.lower() == 'true':
    back_test = True
else:
    back_test = False

loop_wait_time_sec = int(conf_reader.props["loop_wait_time_sec"])


def calculate_percentage(price, percentage):
    price = float(price)
    percentage = float(percentage)
    positive = price + (price * (percentage / 100))
    negative = price - (price * (percentage / 100))
    return __round_nearest(round(positive, 2)), __round_nearest(round(negative, 2))


def calculate_price_margin(price):
    price = float(price)
    positive = price + float(conf_reader.props["price_margin_ps"])
    negative = price - float(conf_reader.props["price_margin_ps"])
    return __round_nearest(round(positive, 2)), __round_nearest(round(negative, 2))


def log_stock(symbol, data):
    from datetime import datetime
    try:
        if not os.path.exists("stock_data"):
            os.mkdir("stock_data")
        dir_name = str(datetime.now().date())
        if not os.path.exists("stock_data/" + dir_name):
            os.mkdir("stock_data/" + dir_name)
    except:
        dir_name = "stocks"

    try:
        with open("stock_data/" + dir_name + "/" + symbol + ".txt", "a") as f:
            f.write(str(datetime.now()) + " - " + str(data) + "\n")
    except Exception as e:
        print(str(e))


def print_and_log(data):
    log.info(data)
    print(data)


def word_count(str):
    counts = dict()
    words = str.split()

    for word in words:
        if word in counts:
            counts[word] += 1
        else:
            counts[word] = 1

    return counts


def __round_nearest(x, a=0.05):
    return round((round(x / a) * a), 2)


def do_trade(stock, current_pri, buy_or_sell, quantity, message=""):
    is_placed, order_id = bridge.purchase_stock(symbol=stock.symbol, quantity=int(quantity), buy_or_sell=buy_or_sell, current_price=current_pri)
    if is_placed:
        stock.ltp = current_pri
        print_str = "[Order Placed] " + stock.symbol + " | " + buy_or_sell + " | price: " + str(current_pri) + " | quantity: " + str(int(quantity)) + " | " + message
        print_and_log(print_str)
        log_stock(stock.symbol, print_str)
        print_and_log("==================================================================")
        return True
    return False


def close_all_positions(profit):
    # square off all positions
    for stock in conf_reader.MYDEF:
        if stock.symbol not in stop_list:
            if back_test:
                current_price = stock.price_list[stock.count]
                stock.count += 1
            else:
                current_price = truedata.get_current_data(stock.req_code)
            if stock.purchased:
                if stock.total_quantity>0:
                    do_trade(stock, current_price, Type.Sell, stock.total_quantity, "Closed")
                    stock.purchased = False
                else:
                    do_trade(stock, current_price, Type.Buy, abs(stock.total_quantity), "Closed")
                    stock.purchased = False

    if not back_test:
        print("P & L : " + str(bridge.get_m2m()))
        print("Margin: " + str(bridge.get_balace()))
    print_and_log("All positions closed")
    print_and_log("Profit: " + str(round(profit, 2)))
    sys.exit()


def check_15_min_candle():
    for stock in conf_reader.MYDEF:
        try:
            high, low, open, close = truedata.get_historic_data(stock.symbol)
            print_and_log(str(stock.symbol) + " | First 15 min high: " + str(high) + " | low: " + str(low) + " | open: " + str(open) + " | close: " + str(close))
            log_stock(stock.symbol, "First 15 min high: " + str(high) + " | low: " + str(low) + " | open: " + str(open) + " | close: " + str(close))
            stock.first15_high = high
            stock.first15_low = low
            stock.first15_open = open
            stock.first15_close = close
            if back_test:
                stock.price_list = truedata.get_price_list_for_back_test(symbol=stock.symbol)
                print(stock.symbol + " | Price List: " + str(stock.price_list))

        except Exception:
            print_and_log("Exception while getting high, low and open price for first 15 min candle")
            print_and_log("Exception: {}".format(traceback.print_exc()))


def check_time():
    if back_test:
        return "run"
    trade_start_time = conf_reader.props["trade_start_time"]
    trade_stop_time = conf_reader.props["trade_stop_time"]
    datetime.time()

    start_time = datetime.time(int(trade_start_time.split('.')[0]), int(trade_start_time.split('.')[1]), 00)
    stop_time = datetime.time(int(trade_stop_time.split('.')[0]), int(trade_stop_time.split('.')[1]), 00)

    current_time = datetime.datetime.now().time()

    if current_time >= start_time:
        if current_time < stop_time:
            return "run"
        elif current_time > stop_time:
            return "close"
    else:
        time.sleep(30)
        return "wait"


def print_details(stock, current_price, positive_range, negative_range, which=""):
    print("***************** " + str(stock.symbol) + "********************")
    print("---- " + which + " ----")
    print("Current Price: " + str(current_price))
    print("Positive Range: " + str(positive_range))
    print("Negative Range: " + str(negative_range))
    print("LTP: " + str(stock.ltp))


def get_stop_list():
    try:
        with open('stop.txt') as f:
            stop_list = f.read().splitlines()
        return stop_list
    except Exception as e:
        print("Exception while reading the stop list: " + str(e))
        return []


stop_loss_per = float(conf_reader.props["stop_loss_per"])
profit_per = float(conf_reader.props["profit_per"])
target_profit = int(conf_reader.props["profit"])
max_stop_loss_count = int(conf_reader.props["max_stop_loss_count"])
total_stop_loss_count = 0
total_profit_booked_count = 0

profit_list = []


if __name__ == '__main__':
    print("******** Broker : " + broker_name + " *********")

    first_time = False
    while True:

        stop_list = get_stop_list()

        what_next = check_time()
        print("What Next: " + str(what_next))

        if back_test:
            what_next = "run"

        if what_next == "run":

            if not first_time:
                check_15_min_candle()
                first_time = True

            for stock in conf_reader.MYDEF:
                if stock.symbol not in stop_list:
                    if stock.first15_high > 0 and stock.first15_low > 0:
                        try:

                            if back_test:
                                current_price = stock.price_list[stock.count]
                                stock.count += 1

                                if stock.count > len(stock.price_list) - 2:
                                    close_all_positions(profit)
                                    sys.exit()
                            else:
                                current_price = truedata.get_current_data(stock.req_code)
                            stock.current_price = current_price

                            # First time purchase
                            if not stock.purchased :
                                if stock.first15_high <= current_price:
                                    placed = do_trade(stock, current_price, Type.Buy, stock.quantity)
                                    stock.buy_or_sell = Type.Buy
                                    stock.purchased = True
                                    stock.total_quantity = stock.quantity

                                if stock.first15_low >= current_price:
                                    placed = do_trade(stock, current_price, Type.Sell, stock.quantity)
                                    stock.buy_or_sell = Type.Sell
                                    stock.purchased = True
                                    stock.total_quantity = stock.quantity

                            else:
                                pos_range, neg_range = calculate_percentage(stock.ltp, profit_per)

                                if pos_range <= current_price:
                                    placed = do_trade(stock, current_price, Type.Sell, stock.quantity)
                                    stock.total_quantity += stock.quantity

                                if neg_range >= current_price :
                                    placed = do_trade(stock, current_price, Type.Buy, stock.quantity)
                                    stock.total_quantity -= stock.quantity

                        except Exception as e:
                            print_and_log("Exception: {}".format(traceback.print_exc()))
                    else:
                        print_and_log("High and low price of the stock is zero or negative")
                else:
                    print_and_log("Stock found in stop list: {}".format(stock.symbol))
                profit_list.append(round(profit, 2))

            if not back_test:
                total_profit = bridge.get_m2m()
                print("P & L : " + str(bridge.get_m2m()))
                print("Margin: " + str(bridge.get_balace()))

            # Calculate floating PL
            try:
                floating_pl = 0
                for stock in conf_reader.MYDEF:
                    if stock.purchased:
                        if stock.buy_or_sell == Type.Buy:
                            floating_pl += (stock.current_price - stock.ltp) * stock.quantity
                        else:
                            floating_pl += (stock.ltp - stock.current_price) * stock.quantity
                print_and_log("Floating PL: " + str(round(floating_pl, 2)))
                print_and_log("Tool Calculated Profit: " + str(round(profit, 2)))
                print("Max Profit:" + str(round(max(profit_list), 2)))
                print("Profit + Floating PL: " + str(round(profit + floating_pl, 2)))
                try:
                    if total_profit > target_profit:
                        close_all_positions(profit)
                except:
                    pass
                print("Stop loss hit count - " + str(total_stop_loss_count))
                print("Profit booked count - " + str(total_profit_booked_count))
                print("#############################################################################################################")

                if not back_test:
                    print_and_log("Wating for {} seconds".format(loop_wait_time_sec))
                    time.sleep(loop_wait_time_sec)
            except:
                pass

        if what_next == "wait":
            print("Waiting for the configured start time")

        if what_next == "close" or "CLOSEALL" in stop_list:
            close_all_positions(profit)
