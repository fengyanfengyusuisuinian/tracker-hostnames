#!/usr/bin/env python3
# src/convert_to_yogadns.py
import os
import re
import requests
from urllib.parse import urlparse

TRACKER_LIST_URL = "https://raw.githubusercontent.com/fengyanfengyusuisuinian/tracker-aggregator/main/TrackerServer/tracker.txt"
OUTPUT_FILE      = "output/yogadns_hosts.txt"

IP_RE = re.compile(r'^\d+\.\d+\.\d+\.\d+$|^([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$')

def main():
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    print("🚀 正在下载最新 tracker 列表…")
    resp = requests.get(TRACKER_LIST_URL, timeout=30)
    resp.raise_for_status()
    raw_lines = [l.strip() for l in resp.text.splitlines() if l.strip()]
    print(f"✅ 下载了 {len(raw_lines)} 条 tracker")

    # 1. 提取 hostname（含端口）并过滤 IP
    host_set = set()
    for line in raw_lines:
        try:
            if line.startswith(("http://", "https://", "udp://", "ws://", "wss://")):
                host = urlparse(line).hostname
                if host and not IP_RE.fullmatch(host):
                    host_set.add(host)
        except Exception:
            continue

    # 2. 显式：去重 + 排序
    unique_hosts = sorted(host_set)          # 字典序
    dropped = len(raw_lines) - len(unique_hosts)
    print(f"❌ 已剔除 {dropped} 条无效/IP/重复记录")
    print(f"🎉 最终生成 {len(unique_hosts)} 条纯 hostname（已去重 & 排序），已写入 {OUTPUT_FILE}")

    # 3. 写入文件
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for host in unique_hosts:
            f.write(f"{host}\n")

if __name__ == "__main__":
    main()
