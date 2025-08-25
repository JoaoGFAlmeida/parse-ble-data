from __future__ import annotations
from dataclasses import dataclass
from pkgutil import get_data
from typing import List, Optional, Dict
import pandas as pd
import json

def hexstr_to_bytes(s: str) -> bytes:
    s = "".join(s.split())
    if len(s) % 2:
        raise ValueError("Hex com número ímpar de dígitos.")
    return bytes.fromhex(s)

def le16(b: bytes) -> int:
    return int.from_bytes(b, "little", signed=False)

def le16s(b: bytes) -> int:
    return int.from_bytes(b, "little", signed=True)

def be16(b: bytes) -> int:
    return int.from_bytes(b, "big", signed=False)

@dataclass
class AD:
    length: int
    ad_type: int
    value: bytes

def split_ad(payload: bytes) -> List[AD]:
    out: List[AD] = []
    i = 0
    while i < len(payload):
        L = payload[i]; i += 1
        if L == 0: break
        if i + L > len(payload):
            raise ValueError("Campo AD ultrapassa o tamanho.")
        t = payload[i]; v = payload[i+1:i+L]; i += L
        out.append(AD(L, t, v))
    return out

@dataclass
class AccFrame:
    product_model: int     
    battery_pct: int         
    accel_counts: Dict[str, int]  
    battery_mV: Optional[int]     
    steps: Optional[int]         
    status: Optional[int]        
    checksum: Optional[int]   

def parse_beaconplus_acc(payload_after_uuid: bytes) -> Optional[AccFrame]:
    if len(payload_after_uuid) < 3 + 6:
        return None
    frame_type = payload_after_uuid[0]
    product_model = payload_after_uuid[1]
    if frame_type != 0xA1 or product_model != 0x03:
        return None
    bat_pct = payload_after_uuid[2]

    if len(payload_after_uuid) < 3 + 6:
        return None
    x = le16s(payload_after_uuid[3:5])
    y = le16s(payload_after_uuid[5:7])
    z = le16s(payload_after_uuid[7:9])

    battery_mV = steps = status = checksum = None
    pos = 9
    if len(payload_after_uuid) >= pos + 2:
        battery_mV = be16(payload_after_uuid[pos:pos+2]); pos += 2
    if len(payload_after_uuid) >= pos + 2:
        steps = be16(payload_after_uuid[pos:pos+2]); pos += 2
    if len(payload_after_uuid) >= pos + 1:
        status = payload_after_uuid[pos]; pos += 1
    if len(payload_after_uuid) >= pos + 1:
        checksum = payload_after_uuid[pos]; pos += 1

    return AccFrame(
        product_model=product_model,
        battery_pct=bat_pct,
        accel_counts={"x": x, "y": y, "z": z},
        battery_mV=battery_mV,
        steps=steps,
        status=status,
        checksum=checksum,
    )

@dataclass
class Parsed:
    flags: Optional[int]
    uuids16: List[int]
    acc: Optional[AccFrame]

def parse_json_long_raw(hex_raw: str) -> Parsed:
    data = hexstr_to_bytes(hex_raw)
    ads = split_ad(data)

    flags = None
    uuids16: List[int] = []
    acc: Optional[AccFrame] = None

    for ad in ads:
        if ad.ad_type == 0x01 and ad.value:
            flags = ad.value[0]
        elif ad.ad_type in (0x02, 0x03):
            for i in range(0, len(ad.value), 2):
                if i+2 <= len(ad.value):
                    uuids16.append(le16(ad.value[i:i+2]))
        elif ad.ad_type == 0x16 and len(ad.value) >= 2:
            uuid16 = le16(ad.value[0:2])  
            sd_payload = ad.value[2:]
            if uuid16 == 0xFFE1 and acc is None:
                acc = parse_beaconplus_acc(sd_payload)

    return Parsed(flags=flags, uuids16=uuids16, acc=acc)

def get_acc_data(raw: str):
    parsed = parse_json_long_raw(raw)
    if parsed.acc is None:
        return "Sem dados de acelerômetro"
    else:
        return parsed.acc.accel_counts

if __name__ == "__main__":

    df = pd.read_csv("raw_comparison.csv")
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
