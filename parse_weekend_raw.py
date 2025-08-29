import pandas as pd
import json
from parse_func import get_acc_data

df = pd.read_csv("weekend_data_22-24/raw_weekend.csv")
df["acc"] = df.apply(lambda r: get_acc_data(r["rawData"]), axis=1)
for i, row in df.iterrows():
    print(f"{row['mac'][-3:]} - {row['timestamp']} - {row['rawData']}//{row['acc']}")

df.to_csv("weekend_data_22-24/acc_extracted_weekend.csv", index=False)