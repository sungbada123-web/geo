# GCP 全自动发布系统部署指南

本指南将协助您在 Google Cloud Platform (GCP) 上部署一台**全自动发布服务器**。

## 1. 创建 VM 实例 (虚拟机)

请在 Google Cloud Console 中进行以下操作：

1.  **打开 Compute Engine**: [点击这里前往 VM 实例页面](https://console.cloud.google.com/compute/instances)
2.  如果是第一次使用，点击 **"启用 COMPUTE ENGINE API"** (Enable API)，等待几分钟。
3.  点击 **"创建实例" (Create Instance)**。
4.  **配置参数**:
    *   **名称 (Name)**: `geo-auto-bot`
    *   **区域 (Region)**: `asia-east1` (台湾) 或 `us-central1` (美国-便宜)
        *   *建议选台湾，连接国内平台速度快；或者美国，IP 纯净度高。*
    *   **机器配置 (Machine configuration)**:
        *   通用 (General-purpose) -> **E2**
        *   预设 (Preset) -> **e2-medium** (2 vCPU, 4 GB 内存)
        *   *这是运行 Headless 浏览器的最低推荐配置。*
    *   **启动磁盘 (Boot disk)**:
        *   点击 "更改" (Change)
        *   操作系统 (OS): **Ubuntu**
        *   版本 (Version): **Ubuntu 22.04 LTS** (x86/64)
        *   大小 (Size): **30 GB** (标准永久磁盘)
    *   **防火墙 (Firewall)**:
        *   勾选 "允许 HTTP 流量" 和 "允许 HTTPS 流量" (可选，主要用于未来扩展 N8N)
5.  点击底部的 **"创建" (Create)**。

---

## 2. 自动化环境配置

等待实例创建成功（状态变为绿色对勾 ✅）后：

1.  点击实例名称右侧的 **"SSH"** 按钮，会弹出一个黑色命令行窗口。
2.  **一键安装环境**:
    复制下面的代码块，在黑色 SSH 窗口中粘贴并回车：

```bash
# 下载并运行初始化脚本
cat << 'EOF' > setup.sh
#!/bin/bash
echo ">>> 开始系统更新..."
sudo apt-get update && sudo apt-get upgrade -y

echo ">>> 安装基础工具..."
sudo apt-get install -y python3-pip python3-venv git unzip fontconfig fonts-noto-cjk

echo ">>> 安装 Google Drive 同步工具 (Rclone)..."
sudo -v ; curl https://rclone.org/install.sh | sudo bash

echo ">>> 配置 Python 环境..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install playwright asyncio nest_asyncio

echo ">>> 安装浏览器驱动..."
playwright install chromium firefox
playwright install-deps

echo ">>> 创建项目目录..."
mkdir -p ~/GEO

echo "✅ 环境安装完成！"
EOF

chmod +x setup.sh
./setup.sh
```

---

## 3. 挂载 Google Drive (实现自动同步)

在 SSH 窗口中继续操作：

1.  **配置 Rclone**:
    ```bash
    rclone config
    ```
    *   输入 `n` (New remote)
    *   name: `gdrive`
    *   Storage: 输入 `drive` (Google Drive)
    *   `client_id`: 留空回车
    *   `client_secret`: 留空回车
    *   `scope`: 选 `1` (Full access)
    *   `service_account_file`: 留空回车
    *   `Use auto config?`: **选 `n` (No)** (因为是远程服务器)
    *   **关键步骤**: 它会给您一条长链接。**复制该链接**，在您**本地电脑**的浏览器打开，登录 Google 账号授权，然后把生成的 **验证码 (Verification Code)** 复制回 SSH 窗口。
    *   `Configure this as a team drive?`: `n`
    *   `Quit config`: `q`

2.  **挂载云端硬盘**:
    ```bash
    # 创建挂载点
    mkdir -p ~/gdrive
    
    # 后台挂载 (将云端硬盘映射到 ~/gdrive 目录)
    nohup rclone mount gdrive: ~/gdrive --vfs-cache-mode writes --allow-non-empty &
    ```

3.  **连接 GEO 目录**:
    ```bash
    # 建立软链接，让 ~/GEO 直接指向您的云端项目
    ln -s ~/gdrive/AI+项目/GEO ~/GEO_Cloud
    ```

现在，您在本地电脑 `g:\我的云端硬盘` 里修改的文件，会实时出现在云服务器的 `~/GEO_Cloud` 目录下！

---

## 4. 设置定时任务 (Cron)

在 SSH 窗口中输入：
```bash
crontab -e
```
(如果是第一次，选 `1` 使用 nano 编辑器)

在文件末尾添加以下两行（每天北京时间 10:00 发布，服务器通常是 UTC 时间，即 02:00）：

```bash
# 每天 UTC 02:00 (北京时间 10:00) 运行小红书发布
0 2 * * * /home/user/venv/bin/python /home/user/GEO_Cloud/分药器GEO/Tools/pauhex_xhs_final_cloud.py >> /home/user/xhs_log.txt 2>&1

# 每天 UTC 02:30 (北京时间 10:30) 运行知乎发布
30 2 * * * /home/user/venv/bin/python /home/user/GEO_Cloud/分药器GEO/Tools/pauhex_zhihu_bot.py >> /home/user/zhihu_log.txt 2>&1
```
按 `Ctrl+O` 保存，`Ctrl+X` 退出。

---

## ✅ 部署完成！

现在的状态：
1. **内容**：您在本地编辑 Markdown 即可。
2. **发布**：云服务器每天自动拉取最新内容并发布。
3. **监控**：您可以随时查看 `xhs_log.txt` 了解发布结果。
