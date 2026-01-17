import asyncio
from playwright.async_api import async_playwright
import os
import re
import time

# 基础配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIE_FILE = os.path.join(BASE_DIR, "xhs_cookies_manual.txt")
CONTENT_FILE = os.path.join(BASE_DIR, "..", "Platform_XHS_Pauhex.md")
ASSETS_DIR = os.path.join(BASE_DIR, "..", "Assets")

def clean_markdown(text):
    """清理 Markdown 符号，保留纯文本"""
    # 移除标题符号
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # 移除粗体/斜体
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    # 移除链接但保留文本
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
    # 移除图片引用
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    return text.strip()

def parse_content(md_file):
    """解析 Markdown 文件，提取标题、正文和图片"""
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取标题（第一个一级标题）
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else "PAUHEX 智能分药器"
    
    # 提取图片路径
    image_paths = []
    for match in re.finditer(r'!\[.*?\]\(file:///(.+?)\)', content):
        img_path = match.group(1).replace('/', '\\')
        if os.path.exists(img_path):
            image_paths.append(img_path)
    
    # 清理正文
    body = clean_markdown(content)
    # 限制字数（小红书单篇限制 1000 字）
    body = body[:900] + "..." if len(body) > 900 else body
    
    return title, body, image_paths

async def publish_to_xhs():
    print("----------------------------------------------------------------")
    print("   PAUHEX Xiaohongshu (XHS) Publishing Bot")
    print("   Using Manual Cookie Authentication")
    print("----------------------------------------------------------------")
    
    # 读取完整 Cookie JSON
    cookie_json_file = os.path.join(BASE_DIR, "xhs_cookies_full.json")
    if not os.path.exists(cookie_json_file):
        print(f"[Error] Cookie 文件不存在: {cookie_json_file}")
        print("[Info] 请先按照 COOKIE_IMPORT_GUIDE.md 导出完整 Cookie JSON")
        return
    
    import json
    with open(cookie_json_file, 'r', encoding='utf-8') as f:
        cookies_data = json.load(f)
    
    print(f"[Status] 已加载 {len(cookies_data)} 个 Cookies")
    
    # 解析内容
    print("[Status] 正在解析内容文件...")
    title, body, images = parse_content(CONTENT_FILE)
    print(f"[Status] 标题: {title}")
    print(f"[Status] 正文长度: {len(body)} 字")
    print(f"[Status] 图片数量: {len(images)}")
    
    # 启动浏览器
    launch_args = [
        "--no-sandbox",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--disable-software-rasterizer"
    ]
    
    async with async_playwright() as p:
        print("[Status] 启动 Firefox 浏览器 (Headless Mode - 轻量级)...")
        # === 使用 Firefox 替代 Chromium（更稳定） ===
        browser = await p.firefox.launch(
            headless=True,
            firefox_user_prefs={
                "media.navigator.enabled": False,  # 禁用媒体设备
                "media.peerconnection.enabled": False,  # 禁用 WebRTC
            }
        )
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
            viewport={"width": 1280, "height": 800}
        )
        
        # 转换并注入所有 Cookies
        playwright_cookies = []
        for cookie in cookies_data:
            pw_cookie = {
                "name": cookie["name"],
                "value": cookie["value"],
                "domain": cookie["domain"],
                "path": cookie["path"]
            }
            # 可选字段
            if "expires" in cookie or "expirationDate" in cookie:
                pw_cookie["expires"] = cookie.get("expirationDate", cookie.get("expires", -1))
            if cookie.get("httpOnly"):
                pw_cookie["httpOnly"] = True
            if cookie.get("secure"):
                pw_cookie["secure"] = True
            # sameSite 处理：unspecified -> Lax
            if "sameSite" in cookie:
                same_site = cookie["sameSite"]
                if same_site == "unspecified" or same_site == "no_restriction":
                    pw_cookie["sameSite"] = "Lax"
                elif same_site.lower() in ["strict", "lax", "none"]:
                    pw_cookie["sameSite"] = same_site.capitalize()
            
            playwright_cookies.append(pw_cookie)
        
        await context.add_cookies(playwright_cookies)
        print(f"[Status] 已注入 {len(playwright_cookies)} 个 Cookies")
        
        page = await context.new_page()
        
        print("[Status] 正在访问创作者平台...")
        await page.goto("https://creator.xiaohongshu.com/publish/publish", timeout=60000)
        await page.wait_for_timeout(3000)
        
        # 检查是否登录成功
        if "login" in page.url:
            print("[Error] Cookie 已过期或无效，请重新导出")
            await page.screenshot(path="xhs_login_failed.png")
            await browser.close()
            return
        
        print("[Success] 登录成功！开始填充内容并保存草稿...")
        
        # === 第一步：上传图片 ===
        if images:
            print(f"[Status] 准备上传 {len(images)} 张图片...")
            try:
                await page.wait_for_timeout(2000)
                
                # 查找所有文件输入框
                all_file_inputs = page.locator('input[type="file"]')
                input_count = await all_file_inputs.count()
                print(f"[Info] 找到 {input_count} 个文件输入框")
                
                if input_count > 0:
                    # 只注入第一个（通常就是图片上传）
                    await all_file_inputs.first.set_input_files(images[:9])
                    print(f"[Success] 图片已注入")
                    await page.wait_for_timeout(5000)  # 缩短等待时间
                else:
                    print("[Warning] 未找到文件输入框，跳过图片上传")
                        
            except Exception as e:
                print(f"[Warning] 图片上传失败: {e}，继续执行...")
        
        # === 第二步：填充标题 ===
        try:
            await page.wait_for_timeout(500)
            title_input = page.locator('input[placeholder*="标题"]').first
            await title_input.click()
            await title_input.fill(title)
            print(f"[Success] 标题已填充")
        except Exception as e:
            print(f"[Warning] 标题填充失败: {e}")
        
        # === 第三步：填充正文 ===
        try:
            await page.wait_for_timeout(500)
            content_editor = page.locator('div[contenteditable="true"], textarea').first
            await content_editor.click()
            await content_editor.fill(body)
            print(f"[Success] 正文已填充 ({len(body)} 字)")
        except Exception as e:
            print(f"[Warning] 正文填充失败: {e}")
        
        # === 第四步：保存草稿 ===
        print("[Status] 准备保存草稿...")
        try:
            # 小红书通常有自动保存功能，也可能有"保存草稿"按钮
            # 先尝试点击"保存草稿"按钮
            save_draft_btn = page.locator('button:has-text("保存草稿"), button:has-text("存草稿")').first
            if await save_draft_btn.count() > 0:
                await save_draft_btn.click()
                print("[Success] 已点击'保存草稿'按钮")
                await page.wait_for_timeout(2000)
            else:
                # 如果没有明确的按钮，等待自动保存
                print("[Info] 未找到'保存草稿'按钮，等待自动保存...")
                await page.wait_for_timeout(3000)
            
            # 截图保存最终状态
            await page.screenshot(path="xhs_draft_saved.png")
            print(f"[Success] 草稿已保存！")
            print(f"[Success] 截图: xhs_draft_saved.png")
            print(f"[Success] 当前 URL: {page.url}")
            print(f"\n[提示] 请登录小红书创作者平台，在草稿箱中找到这篇笔记并手动发布。")
            
        except Exception as e:
            print(f"[Error] 保存草稿失败: {e}")
            await page.screenshot(path="xhs_save_draft_error.png")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(publish_to_xhs())
