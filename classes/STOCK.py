from classes import Order


class STOCK:
    symbol = ""
    quantity = 0
    at = 0,
    buy_or_sell = "buy"
    stop_loss_per = 0
    req_code = 0
    purchased = False
    total_quantity = 0
    stop_loss_hit = False
    count = 0
    ltp = 0
    open =0
    first15_high = 0
    first15_low = 0
    first15_open = 0
    first15_close = 0
    profit_booked = False
    price_list =[]
    current_price = 0
    profit_booked_count = 0


class Type:
    Sell = "sell"
    Buy = "buy"
