# 小红书 Cookie 手动导入指南

> **为什么需要手动导入？**  
> 小红书的登录页面使用了极强的反爬虫技术（Canvas指纹、滑块验证），无头浏览器很难稳定通过。  
> 全球最佳实践：**人工登录一次 → 导出 Cookies → 脚本复用**。

---

## 步骤 1：在真实浏览器中登录

1. 打开 **Chrome 浏览器**（或 Edge）
2. 访问：`https://creator.xiaohongshu.com/`
3. 使用手机扫码或密码登录，**确保成功进入创作者后台**

---

## 步骤 2：导出 Cookies

### 方法 A：使用开发者工具（推荐）

1. 在已登录的页面按 `F12` 打开开发者工具
2. 切换到 **"Application"** 标签（中文版可能叫"应用程序"）
3. 左侧菜单找到 **Storage → Cookies → https://creator.xiaohongshu.com**
4. 找到名为 `web_session` 的 Cookie
5. 双击其 `Value` 列，复制整个字符串（通常很长，类似 `MTY4NjQ...`）

### 方法 B：使用浏览器插件

安装 Chrome 插件 "EditThisCookie" 或 "Cookie-Editor"，一键导出所有 Cookies 为 JSON 格式。

---

## 步骤 3：保存到本地

将复制的 Cookie 值粘贴到以下文件：

**文件路径**:  
`g:\我的云端硬盘\AI+项目\GEO\分药器GEO\Tools\xhs_cookies_manual.txt`

**内容格式**（仅需 `web_session` 的值）:
```
MTY4NjQxMjM0NTY3ODkwMTIzNDU2Nzg5MDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTIzNDU2Nzg5MDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTIzNDU2Nzg5MDEyMzQ1Njc4OTAxMjM0NTY3ODkw...
```

---

## 步骤 4：运行发布脚本

一旦 Cookie 文件就绪，运行：
```bash
python pauhex_xhs_bot.py
```

脚本会自动加载 Cookie 并跳过登录，直接进入发布流程。

---

## 常见问题

**Q: Cookie 会过期吗？**  
A: 会。通常有效期 7-30 天。过期后重复上述步骤即可。

**Q: 为什么不能自动化登录？**  
A: 小红书的反爬虫系统会检测 WebDriver 特征、Canvas 指纹等，成功率极低。手动登录是唯一稳定方案。

**Q: 安全吗？**  
A: Cookie 文件仅保存在本地，不会上传。但请勿分享给他人，避免账号被盗用。
