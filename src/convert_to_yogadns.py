#!/usr/bin/env python3
# src/convert_to_yogadns.py
# 功能：1. 原格式纯 hostname  2. 裸域+通配（无 CDN）双输出
import os
import re
import requests
from urllib.parse import urlparse
from tld import get_fld
import pathlib

# ====== 可自定义 ======
TRACKER_LIST_URL = "https://raw.githubusercontent.com/fengyanfengyusuisuinian/tracker-aggregator/main/TrackerServer/tracker.txt"
CDN_URLS = [
    "https://raw.githubusercontent.com/fellerts/cdn-domains/master/cdn_domains.txt"
]
OUTPUT_HOSTS    = "output/yogadns_hosts.txt"      # ① 原格式：纯 hostname
OUTPUT_WILDCARD = "output/tracker_wildcard.txt"  # ② 新格式：裸域 + 通配
# ======================

IP_RE = re.compile(r'^\d+\.\d+\.\d+\.\d+$|^([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$')

def pull_cdn_white() -> set[str]:
    """内存拉取合并多个 CDN 一级域列表"""
    white = set()
    for u in CDN_URLS:
        try:
            white.update(requests.get(u, timeout=15).text.splitlines())
        except Exception as e:
            print(f"⚠️ CDN 白名单拉取失败 {u} : {e}")
    return white

def main():
    os.makedirs(os.path.dirname(OUTPUT_HOSTS), exist_ok=True)

    # 1. 下载 tracker 列表
    print("🚀 正在下载最新 tracker 列表…")
    resp = requests.get(TRACKER_LIST_URL, timeout=30)
    resp.raise_for_status()
    raw_lines = [l.strip() for l in resp.text.splitlines() if l.strip()]
    print(f"✅ 下载了 {len(raw_lines)} 条 tracker")

    # 2. 提取 hostname（去端口）并过滤 IP
    host_set = set()
    for line in raw_lines:
        try:
            if line.startswith(("http://", "https://", "udp://", "ws://", "wss://")):
                host = urlparse(line).hostname
                if host and not IP_RE.fullmatch(host):
                    host_set.add(host)
        except Exception:
            continue

    # 3. 原功能①：纯 hostname（00.mercax.com 这种）
    unique_hosts = sorted(host_set)
    dropped = len(raw_lines) - len(unique_hosts)
    print(f"❌ 已剔除 {dropped} 条无效/IP/重复记录")
    print(f"🎉 最终生成 {len(unique_hosts)} 条纯 hostname，已写入 {OUTPUT_HOSTS}")

    with open(OUTPUT_HOSTS, "w", encoding="utf-8") as f:
        for host in unique_hosts:
            f.write(f"{host}\n")          # 原格式：00.mercax.com

    # 4. 新功能②：裸域 + 通配（无 CDN）
    cdn = pull_cdn_white()
    fld_set = set()
    for h in unique_hosts:
        try:
            fld = get_fld(h, fix_protocol=True)
            if fld not in cdn:
                fld_set.add(fld)
        except Exception:
            continue
    rules = {fld for fld in fld_set} | {f"*.{fld}" for fld in fld_set}
    pathlib.Path(OUTPUT_WILDCARD).write_text("\n".join(sorted(rules)))
    print(f"🎉 额外输出 {len(rules)} 条（裸域+通配，已剔除 CDN）→ {OUTPUT_WILDCARD}")

if __name__ == "__main__":
    main()
