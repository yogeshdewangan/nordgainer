import csv
from classes import STOCK
import logging

import logging, os, configparser

logger = logging.getLogger("IndiBotLog")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(filename)s - %(levelname)s - %(message)s')
fh = logging.FileHandler('IndiBot.log', 'w+')
fh.setFormatter(formatter)
fh.setLevel(logging.INFO)
logger.addHandler(fh)

log = logging.getLogger("IndiBotLog")

# Read credentials from config.ini
configParser = configparser.ConfigParser()
configParser.read("config.ini")
props = dict(configParser.items("DEFAULT"))

MYDEF = []
ALLSTOCKS = []

with open('data1.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    stock_req_code = 2000
    for row in csv_reader:
        if line_count == 0:
            line_count += 1
        else:
            if row[3].lower() == "yes":
                stock = STOCK.STOCK()
                stock.symbol = row[1]
                ALLSTOCKS.append(stock.symbol)
                stock.quantity = int(row[2])
                stock.req_code = stock_req_code
                stock_req_code += 1
                MYDEF.append(stock)
                line_count += 1
                print_str = "Stock: {} | Quantity: {} | Request Code: {}".format(stock.symbol, stock.quantity, stock.req_code)
                print(print_str)
                log.info(print_str)
    print(f'Total  {line_count - 1} stocks found in data.csv.')
    log.info("Total {} stocks found in data.csv".format(line_count - 1))
