#!/usr/bin/env python3
# src/convert_to_yogadns.py
import os
import requests
from urllib.parse import urlparse

TRACKER_LIST_URL = "https://raw.githubusercontent.com/fengyanfengyusuisuinian/tracker-aggregator/main/TrackerServer/tracker.txt"
OUTPUT_FILE      = "output/yogadns_hosts.txt"

def main():
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    # 1. 下载
    print("🚀 正在下载最新 tracker 列表…")
    resp = requests.get(TRACKER_LIST_URL, timeout=30)
    resp.raise_for_status()
    raw_lines = [l.strip() for l in resp.text.splitlines() if l.strip()]
    print(f"✅ 下载了 {len(raw_lines)} 条 tracker")

    # 2. 提取 hostname 并去重
    host_set = set()
    for line in raw_lines:
        try:
            if line.startswith(("http://", "https://", "udp://", "ws://", "wss://")):
                host = urlparse(line).hostname
                if host:
                    host_set.add(host)
        except Exception:
            continue

    # 3. 为二级域生成泛域名 *.domain
    wildcard_set = set()
    for host in host_set:
        parts = host.split(".")
        if len(parts) >= 3:                      # 必须是二级及以上
            wildcard_set.add(f"*.{'.'.join(parts[-2:])}")

    # 4. 合并并按长度升序
    unique_hosts = sorted(host_set | wildcard_set, key=len)
    dropped = len(raw_lines) - len(host_set)
    print(f"❌ 已剔除 {dropped} 条无效/重复记录")
    print(f"📏 按 hostname 长度升序完成（含 {len(wildcard_set)} 条泛域名）")

    # 5. 写入文件
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for host in unique_hosts:
            f.write(f"{host}\n")

    print(f"🎉 最终生成 {len(unique_hosts)} 条规则，已写入 {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
