import json
import csv

input_file = "2025-08-20_21-41-23.655.txt"
output_file = f"{input_file.split('.')[0]}.csv"

fields = ["timestamp", "type", "mac", "rawData", "bleName", "bleNo", "rssi", "gatewayFree", "gatewayLoad", "seq"]

rows = []
with open(input_file, "r") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
            for obj in data:
                row = {field: obj.get(field, "") for field in fields}
                rows.append(row)
        except json.JSONDecodeError as e:
            print("Linha ignorada (erro JSON):", line[:80], "...")

with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

print(f"Arquivo CSV gerado: {output_file}")
