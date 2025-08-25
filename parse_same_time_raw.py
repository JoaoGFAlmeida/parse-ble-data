import pandas as pd
import json
from parse_func import get_acc_data 

df = pd.read_csv("same-timestamp/raw_comparison.csv")
def safe_acc(raw):
    try:
        v = get_acc_data(raw)
        if isinstance(v, (list, tuple, dict)):
            return json.dumps(v, ensure_ascii=False)
        return v
    except Exception:
        return None

out = pd.DataFrame({
    "Timestamp": df["timestamp"],
    "ACC_91C": [safe_acc(r) for r in df["raw_a"]],
    "ACC_912": [safe_acc(r) for r in df["raw_b"]],
})

out.to_csv("acc_extracted.csv", index=False) 
print("CSV criado: acc_extracted.csv")

raws_a = [raw for raw in df["raw_a"]]
raws_b = [raw for raw in df["raw_b"]]
times = [t for t in df["timestamp"]]

for t, raw_a, raw_b in zip(times, raws_a, raws_b):
    print(f"{t} - {get_acc_data(raw_a)} // {get_acc_data(raw_b)}")