# TrackerToYogaDNS

从 GitHub tracker 列表自动生成 YogaDNS 域名配置文件，用于指定 DNS 服务器解析 BitTorrent tracker 域名。

## 功能
- 从 GitHub raw URL 下载 tracker 列表（https://raw.githubusercontent.com/fengyanfengyusuisuinian/tracker-aggregator/main/TrackerServer/tracker.txt）。
- 剔除包含 IP 地址（IPv4 和 IPv6）的 tracker。
- 提取域名，忽略协议（http, https, udp, wss），并去重。
- 生成纯域名列表，兼容 YogaDNS 的 Hostnames 配置。
- 通过 GitHub Actions 每周更新两次（周一和周四）。

## 安装
1. 克隆项目：
   ```bash
   git clone https://github.com/<your-username>/TrackerToYogaDNS.git
   cd TrackerToYogaDNS
