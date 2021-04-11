from nsetools import Nse
nse = Nse()

def get_current_price(symbol):
    res = nse.get_quote(symbol)
    current_price = float(res["basePrice"]) + float(res["change"])
    last_price = float(res["lastPrice"])
    return last_price

