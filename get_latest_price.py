import os
import csv
import truedata
import conf_reader


def get_stock_code(symbol):
    for stock in conf_reader.MYDEF:
        if stock.symbol == symbol:
            return stock.req_code


def clean(input):
    tmpFile = "data_latest.csv"
    with open(input, "r") as file, open(tmpFile, "w") as outFile:
        reader = csv.reader(file, delimiter=',')
        writer = csv.writer(outFile, delimiter=',')
        header = next(reader)
        writer.writerow(header)
        for row in reader:
            price = truedata.get_current_data(get_stock_code(row[1]))
            colValues = []
            count=0
            for col in row:
                if count ==9:
                    col = price
                colValues.append(col)
                count+=1
            writer.writerow(colValues)
        pass
    #os.rename(tmpFile, input)


clean("data1.csv")
pass