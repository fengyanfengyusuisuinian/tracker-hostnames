#!/usr/bin/env python3
# src/convert_to_yogadns.py
# 功能：1. 原列表（纯 hostname） 2. 裸域+通配（无 CDN）双输出
import os
import re
import requests
from urllib.parse import urlparse
from tld import get_fld
import pathlib
import sys

# ====== 可自定义 ======
# ① tracker 源（可换别的列表）
TRACKER_LIST_URL = "https://raw.githubusercontent.com/fengyanfengyusuisuinian/tracker-aggregator/main/TrackerServer/tracker.txt"
# ② 社区 CDN 白名单（可多地址）
CDN_URLS = [
    "https://raw.githubusercontent.com/fellerts/cdn-domains/master/cdn_domains.txt"
]
# ③ 输出文件
OUTPUT_HOSTS    = "output/yogadns_hosts.txt"      # 功能①：纯 hostname
OUTPUT_WILDCARD = "output/tracker_wildcard.txt"  # 功能②：裸域 + 通配
# ======================

IP_RE = re.compile(r'^\d+\.\d+\.\d+\.\d+$|^([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$')

def pull_cdn_white() -> set[str]:
    """内存拉取合并多个 CDN 一级域列表"""
    white = set()
    for u in CDN_URLS:
        try:
            white.update(requests.get(u, timeout=15).text.splitlines())
        except Exception as e:
            print(f"⚠️ CDN 白名单拉取失败 {u} : {e}", file=sys.stderr)
    return white

def stream_flds(url: str):
    """流式提取一级域（去 IP+去 CDN）"""
    cdn = pull_cdn_white()
    with requests.get(url, stream=True, timeout=15) as r:
        r.raise_for_status()
        for line in r.iter_lines(decode_unicode=True):
            line = line.strip()
            if not line:
                continue
            try:
                # 只处理带协议的 tracker 行
                if line.startswith(("http://", "https://", "udp://", "ws://", "wss://")):
                    host = urlparse(line).hostname
                    if host and not IP_RE.fullmatch(host):
                        fld = get_fld(host, fix_protocol=True)
                        if fld not in cdn:
                            yield fld          # 只返回一级域（str）
            except Exception:
                continue

def main():
    os.makedirs(os.path.dirname(OUTPUT_HOSTS), exist_ok=True)

    print("🚀 正在下载最新 tracker 列表…")
    # ① 纯 hostname 列表（保留原功能）
    hosts = sorted(set(stream_flds(TRACKER_LIST_URL)))
    # 统计：原始行数 - 最终行数 = 剔除数
    raw_cnt = len(requests.get(TRACKER_LIST_URL, timeout=15).text.splitlines())
    dropped = raw_cnt - len(hosts)
    print(f"✅ 下载了 {len(hosts)} 条 tracker")
    print(f"❌ 已剔除 {dropped} 条无效/IP/重复记录")
    print(f"🎉 最终生成 {len(hosts)} 条纯 hostname，已写入 {OUTPUT_HOSTS}")

    # 写出功能①：原列表
    with open(OUTPUT_HOSTS, "w", encoding="utf-8") as f:
        for h in hosts:
            f.write(f"{h}\n")

    # ② 裸域 + 通配（新功能）
    fld_set = set(hosts)                      # 直接用上面结果
    rules   = {fld for fld in fld_set} | {f"*.{fld}" for fld in fld_set}
    pathlib.Path(OUTPUT_WILDCARD).write_text("\n".join(sorted(rules)))
    print(f"🎉 额外输出 {len(rules)} 条（裸域+通配，已剔除 CDN）→ {OUTPUT_WILDCARD}")

if __name__ == "__main__":
    main()
