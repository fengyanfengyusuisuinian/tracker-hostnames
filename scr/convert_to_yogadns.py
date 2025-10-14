import re
import requests
from urllib.parse import urlparse
from pathlib import Path

# 正则表达式匹配 IPv4 和 IPv6 地址
IPV4_PATTERN = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?::\d+)?(/.*)?$"
IPV6_PATTERN = r"^\[([0-9a-fA-F:]+)\](?::\d+)?(/.*)?$"

def is_ip_address(url):
    """检查 URL 是否包含 IP 地址（IPv4 或 IPv6）"""
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        if not hostname:
            return False
        if re.match(IPV4_PATTERN, hostname) or re.match(IPV6_PATTERN, hostname):
            return True
        return False
    except:
        return False

def extract_hostname(url):
    """从 URL 提取主机名"""
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        if hostname:
            return hostname.lower()  # 转换为小写以规范化
        return None
    except:
        return None

def fetch_trackers_from_github(raw_url):
    """从 GitHub raw URL 下载 tracker 列表"""
    try:
        response = requests.get(raw_url, timeout=10)
        response.raise_for_status()
        return [line.strip() for line in response.text.splitlines() if line.strip()]
    except requests.RequestException as e:
        print(f"Error fetching trackers from {raw_url}: {e}")
        return []

def convert_to_yogadns(trackers, output_file):
    """将 tracker 列表转换为 YogaDNS 格式"""
    hostnames = set()  # 使用集合去重
    for tracker in trackers:
        if not is_ip_address(tracker):
            hostname = extract_hostname(tracker)
            if hostname:
                hostnames.add(hostname)
    
    # 确保输出目录存在
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    # 保存到文件
    with open(output_file, 'w', encoding='utf-8') as f:
        for hostname in sorted(hostnames):
            f.write(f"{hostname}\n")
    print(f"Generated YogaDNS config with {len(hostnames)} hostnames at {output_file}")

# 主程序
if __name__ == "__main__":
    # GitHub raw URL
    tracker_raw_url = "https://raw.githubusercontent.com/fengyanfengyusuisuinian/tracker-aggregator/main/TrackerServer/tracker.txt"
    
    # 下载 tracker 列表
    trackers = fetch_trackers_from_github(tracker_raw_url)
    if not trackers:
        print("No trackers retrieved. Exiting.")
        exit(1)
    
    print(f"Downloaded {len(trackers)} trackers from GitHub.")
    
    # 转换为 YogaDNS 格式
    convert_to_yogadns(trackers, "output/yogadns_hosts.txt")
