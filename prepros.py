import pandas as pd
import numpy as np

# Will fetch the last 22 days of data, split the data into a 21 day training-set and 1-day test-set  
def get_train_test(date=None):
    from influxdb import InfluxDBClient
    from datetime import datetime as dt, timedelta as td
    from dateutil import parser

    client = InfluxDBClient(host='influxus.itu.dk', port=8086, username='lsda', password='icanonlyread')
    client.switch_database('orkney')

    if date is None: date = "now()"
    else: date = "\'{}\'".format(date)

    # Perform a simple query
    results = client.query('SELECT mean(Total) AS mean FROM "Demand" WHERE time >= {0} - 22d AND time < {0} GROUP BY time(1h)'.format(date)) # Query written in InfluxQL
    points = results.get_points()
    values = results.raw["series"][0]["values"]
    columns = results.raw["series"][0]["columns"]
    df = pd.DataFrame(values, columns=columns)
    df.index = [parser.parse(d) for d in df["time"].values]
    split_time = df.index[-1]-td(days=1)

    train = df.loc[:split_time]
    test = df.loc[split_time+td(seconds=1):]
    train_x, train_y = split_labels(train)
    test_x, test_y = split_labels(test)
    return train_x, train_y, test_x, test_y


def split_labels(df):
    x = df[["time"]].rename(columns={"time": "Time"})
    y = df[["mean"]].rename(columns={"mean": "Demand"})
    x.index = list(range(len(x)))
    y.index = list(range(len(y)))
    return x,y


if __name__ == "__main__":
    train_x, train_y, test_x, test_y = get_train_test(date="2020-03-01")
    print(train_x,train_y)  

