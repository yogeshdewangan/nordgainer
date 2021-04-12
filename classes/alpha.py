from alphatrade import AlphaTrade
from alphatrade import TransactionType
from alphatrade import OrderType
from alphatrade import ProductType
import conf_reader
import enum, logging, traceback

login_id = conf_reader.props["alpha_login_id"]
password = conf_reader.props["alpha_password"]
twofa = conf_reader.props["alpha_twofa"]

log = logging.getLogger("IndiBotLog")


def print_and_log(data):
    log.info(data)
    print(data)


class OrderType(enum.Enum):
    Market = 'MARKET'
    Limit = 'LIMIT'
    StopLossLimit = 'SL'
    StopLossMarket = 'SL-M'


try:
    access_token = open('access_token.txt', 'r').read().rstrip()
except Exception as e:
    print('Exception occurred :: {}'.format(e))
    access_token = None
# sas = AlphaTrade(login_id=login_id, password=password, twofa=twofa)

sas = AlphaTrade(login_id=login_id, password=password,
                 twofa=twofa, access_token=access_token, master_contracts_to_download=['NSE'])

profile = sas.get_profile()
print(profile)
# netwise = sas.get_netwise_positions()

def get_balace():
    try:
        balance = sas.get_balance()
        net_bal = balance["data"]["cash_positions"][0]["net"]
        return float(net_bal)
    except:
        return 0.0

def get_m2m():
    try:
        return sas.get_total_m2m()
    except:
        return 0.0

def purchase_stock(symbol, quantity, buy_or_sell="buy", current_price=0, stop_loss=None):
    # balance = get_balace()
    # if current_price> balance:
    #     print("Margin not available, Total margin : "+ str(balance))
    #     return False, 0
    #return True,100
    try:
        if buy_or_sell.upper() == "buy".upper():
            TransType = TransactionType.Buy
        else:
            TransType = TransactionType.Sell

        if stop_loss is None:
            order_type = OrderType.Market
            product_type = ProductType.Intraday
        else:
            order_type = OrderType.Market
            product_type = ProductType.CoverOrder

        res = sas.place_order(transaction_type=TransType,
                              instrument=sas.get_instrument_by_symbol('NSE', symbol),
                              quantity=int(quantity),
                              order_type=order_type,
                              product_type=product_type,
                              price=0.0,
                              trigger_price=stop_loss,
                              stop_loss=None,
                              square_off=None,
                              trailing_sl=None,
                              is_amo=False)

        if res["status"] == "success":
            order_id = res["data"]["oms_order_id"]

            return True, order_id

            order_history = sas.get_order_history(order_id)
            try:
                status = order_history["data"][0]["order_status"]
                if status == "rejected":
                    print_str = "Failed to place order for : Symbol: {} | Quantity: {} | Type: {} | at Price: {} ".format(symbol, quantity, buy_or_sell, current_price)
                    print_and_log(print_str)
                    return False, 0
                print_str = "Order Details : Symbol: {} | Quantity: {} | Type: {} | at Price: {}".format(symbol, quantity, buy_or_sell, current_price)
                print_and_log(print_str)
                return True, order_id
            except:
                return False, 0
        else:
            print_str = "Failed to place order for: Symbol: {} | Quantity: {} | Type: {} | at Price: {}".format(symbol, quantity, buy_or_sell, current_price)
            print_and_log(print_str)
            print_and_log(res["message"])
            return False, 0
    except:
        print_and_log("Exception while placing first order for symbol: {}  Exception: {}".format(str(symbol), traceback.print_exc()))
        return False, 0


def squareoff_all():
    res = sas.get_netwise_positions()
    for stock in conf_reader.MYDEF:
        for order in stock.orders:
            try:
                res = sas.cancel_order(order.order_id)
                res = sas.get_netwise_positions()
                print_and_log(res)
            except:
                pass


def get_historical_data(symbol, count):
    # price_list = [232.3, 231.65, 231.5, 231.75, 232.25, 232.75, 233.45, 233.95, 233.35, 234.05, 234.4, 232.85, 232.75, 235.85, 232.75, 232.75, 236.65, 232.75, 232.95, 232.8, 232.4, 232.65, 232.7, 232.5, 233.45, 233.3, 233.25, 233.2, 233.2, 233.05, 233.1, 233.15, 233.25, 233.95, 233.6, 233.7, 233.7, 233.75, 233.8, 233.7, 233.35, 233.15, 233.15, 233.3, 233.3, 233.0, 232.9, 232.9, 232.6, 232.5, 232.3, 232.35, 232.35, 232.45, 232.45, 231.75, 231.7, 231.3, 231.6, 231.15, 231.0, 231.1, 230.85, 230.95, 231.0, 230.95, 231.15, 231.35, 231.05, 230.9, 230.45, 230.45, 230.6, 230.7, 231.25, 231.35, 231.85, 231.75, 231.15, 231.2, 231.2, 231.05, 231.1, 231.3, 231.2, 231.3, 231.1, 231.1, 231.1, 230.9, 230.6, 230.4, 230.7, 230.65, 231.1, 230.95, 230.8, 230.7, 230.8, 230.9]
    # return price_list[count]
    data = sas.get_intraday_candles("NSE", symbol, 1)
    price_list = []
    d= len(data)
    if count <len(data):
        for i in range(len(data) - 1):
            price_list.append(float(data['close'].values[i]))
    else:
        count =0
        return 0
    # print(price_list)
    return price_list[count]
