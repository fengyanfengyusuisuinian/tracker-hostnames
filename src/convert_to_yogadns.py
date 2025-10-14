#!/usr/bin/env python3
import os, re, requests
from urllib.parse import urlparse

URL = "https://raw.githubusercontent.com/fengyanfengyusuisuinian/tracker-aggregator/main/TrackerServer/tracker.txt"
OUT = "output/yogadns_hosts.txt"

IP_RE = re.compile(r'^\d+\.\d+\.\d+\.\d+$|^([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$')

os.makedirs(os.path.dirname(OUT), exist_ok=True)
print("🚀 下载中…")
lines = requests.get(URL, timeout=30).text.splitlines()
print(f"✅ 下载 {len(lines)} 行")

hosts = {urlparse(l.strip()).hostname for l in lines
         if l.startswith(("http://", "https://", "udp://", "ws://", "wss://"))}
hosts = {h for h in hosts if h and not IP_RE.fullmatch(h)}

with open(OUT, 'w', encoding='utf-8') as f:
    for h in sorted(hosts):
        f.write(f"{h}\n")

print(f"🎉 输出 {len(hosts)} 个纯 hostname 到 {OUT}")
