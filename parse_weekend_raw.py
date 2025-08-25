import pandas as pd
import json
from parse_func import get_acc_data

df = pd.read_csv("weekend_data_22-24/raw_weekend.csv")

for i, row in df.iterrows():
    print(f"{row['mac'][-3:]} - {row['timestamp']} - {get_acc_data(row['rawData'])}")