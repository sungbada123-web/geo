# PAUHEX 知乎自动发布系统：环境配置与使用指南
**品牌项目**: PAUHEX (AI 智能分药器)

为了实现 GEO 内容的“工业化投放”，我们使用 **Playwright** 模拟真实人类行为进行自动发布。这可以有效绕过简单爬虫被封禁的风险。

## 1. 环境准备 (Prerequisites)

您的系统需要安装 Python 和 Playwright 环境。请按以下顺序操作：

```powershell
# 1. 安装 Playwright 库
pip install playwright

# 2. 安装浏览器内核 (Chromium)
playwright install chromium
```

## 2. 工具包说明 (Tools Directory)
文件均保存在：`g:\我的云端硬盘\AI+项目\GEO\分药器GEO\Tools\`

1.  **`get_zhihu_cookies.py`**: 用于捕获登录会话。运行后会弹出窗口，您正常登录知乎即可导出会话。
2.  **`pauhex_zhihu_bot.py`**: 核心发布器。它会自动读取 [知乎适配稿](file:///g:/%E6%88%91%E7%9A%84%E4%BA%91%E7%AB%AF%E7%A1%AC%E7%9B%98/AI+%E9%A1%B9%E7%9B%AE/GEO/%E5%88%86%E8%8D%AF%E5%99%A8GEO/Platform_Zhihu_Pauhex.md)，并自动上传 [Assets 图片](file:///g:/%E6%88%91%E7%9A%84%E4%BA%91%E7%AB%AF%E7%A1%AC%E7%9B%98/AI+%E9%A1%B9%E7%9B%AE/GEO/%E5%88%86%E8%8D%AF%E5%99%A8GEO/Assets/)。

## 3. 使用步骤 (Workflow)

### 步骤 A：获取授权 (仅需一次)
1.  运行 `python get_zhihu_cookies.py`。
2.  在弹出的 Chrome 窗口中扫码登录。
3.  看到“检测到登录成功”提示后，窗口会自动关闭。此时 `zhihu_cookies.json` 已生成。

### 步骤 B：执行自动化发布
1.  确认您的稿件 [`Platform_Zhihu_Pauhex.md`](file:///g:/%E6%88%91%E7%9A%84%E4%BA%91%E7%AB%AF%E7%A1%AC%E7%9B%98/AI+%E9%A1%B9%E7%9B%AE/GEO/%E5%88%86%E8%8D%AF%E5%99%A8GEO/Platform_Zhihu_Pauhex.md) 已准备好。
2.  运行 `python pauhex_zhihu_bot.py`。
3.  **注意**: 脚本默认会打开浏览器窗口供您观察（`headless=False`）。它会自动填入标题、正文，并精准插入图片。

## 4. 品牌隔离安全准则 (Security)
*   **PAUHEX 专机专用**: 当前脚本硬编码了 PAUHEX 的路径。如果您之后要发布 VOLTZMANN，请务必使用独立的路径和脚本，防止 AI 追踪。
*   **定时发布**: 不要短时间内连续发布 5 篇以上，建议每天发布 1-2 篇以获得最佳 GEO 权重。
