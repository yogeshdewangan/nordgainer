# Real Time Data Sample - Using TrueData Websocket Python Library

from truedata_ws.websocket.TD import TD
from copy import deepcopy
import time, json
from datetime import datetime
import conf_reader

username = conf_reader.props["truedata_userid"]
password = conf_reader.props["truedata_password"]

# Default ports are 8082 / 8092 in the library
realtime_port = 8082
history_port = 8092

td_app = TD(username, password, live_port=realtime_port, historical_port=history_port)

symbols = conf_reader.ALLSTOCKS
req_ids = td_app.start_live_data(symbols)
time.sleep(2)

counter1 = 0


def get_current_data(stock_code):
    # print(stock_code)

    try:
        live_data_objs = {}
        for req_id in req_ids:
            live_data_objs[req_id] = deepcopy(td_app.live_data[req_id])

        data = str(live_data_objs[stock_code])
        json_data = json.loads(data.split("ltp': ")[1].split(",")[0])
    except Exception as e:
        print("Exception while getting the current price" + str(e))
        return 0
    return json_data


def get_historic_data(symbol):
    day = datetime.now().day
    month = datetime.now().month
    year = datetime.now().year

    back_test = conf_reader.props["back_test"]
    if back_test.lower()== 'true':
        back_test = True
    else:
        back_test= False
    if back_test:
        back_test_date = conf_reader.props["back_test_date"]
        temp_date = back_test_date.split('/')
        day = int(temp_date[0])
        month = int(temp_date[1])
        year = int(temp_date[2])

    hist_data_1 = td_app.get_historic_data(symbol, bar_size="5 min", start_time=datetime(year, month, day, 9, 15), end_time=datetime(year, month, day, 9, 30))  # remove duration for current date
    high = hist_data_1[0]["h"]
    low = hist_data_1[0]["l"]
    open = hist_data_1[0]["o"]
    return high, low, open


def get_price_list_for_back_test(symbol):
    back_test_date = conf_reader.props["back_test_date"]
    temp_date = back_test_date.split('/')
    day = int(temp_date[0])
    month = int(temp_date[1])
    year = int(temp_date[2])
    price_list = []
    hist_data_1 = td_app.get_historic_data(symbol, bar_size="1 min", start_time=datetime(year, month, day, 9, 15), end_time=datetime(year, month, day, 12, 10))  # remove duration for current date
    for i in hist_data_1:
        price_list.append(i["c"])
    return price_list
