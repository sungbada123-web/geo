import asyncio
from playwright.async_api import async_playwright
import os
import re
import json

# 基础配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIE_FILE = os.path.join(BASE_DIR, "xhs_cookies_full.json")
CONTENT_FILE = os.path.join(BASE_DIR, "..", "Platform_XHS_Pauhex.md")

def clean_markdown(text):
    """清理 Markdown 符号"""
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    return text.strip()

def parse_content(md_file):
    """解析内容文件"""
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else "PAUHEX 智能分药器"
    
    image_paths = []
    for match in re.finditer(r'!\[.*?\]\(file:///(.+?)\)', content):
        img_path = match.group(1).replace('/', '\\')
        if os.path.exists(img_path):
            image_paths.append(img_path)
    
    body = clean_markdown(content)
    body = body[:900] + "..." if len(body) > 900 else body
    
    return title, body, image_paths

async def publish_xhs_headful():
    print("=" * 70)
    print("   PAUHEX 小红书自动发布助手 (有界面模式 - 最终稳定版)")
    print("=" * 70)
    
    # 读取 Cookie
    with open(COOKIE_FILE, 'r', encoding='utf-8') as f:
        cookies_data = json.load(f)
    
    # 解析内容
    title, body, images = parse_content(CONTENT_FILE)
    print(f"\n[内容预览]")
    print(f"标题: {title}")
    print(f"正文: {len(body)} 字")
    print(f"图片: {len(images)} 张\n")
    
    async with async_playwright() as p:
        print("[Status] 启动浏览器（有界面模式，不会死机）...")
        
        # === 使用 Chromium 有界面模式 ===
        browser = await p.chromium.launch(
            headless=False,  # 关键：显示浏览器
            args=["--start-maximized"]
        )
        
        context = await browser.new_context(
            viewport=None,
            no_viewport=True
        )
        
        # 注入 Cookies
        playwright_cookies = []
        for cookie in cookies_data:
            pw_cookie = {
                "name": cookie["name"],
                "value": cookie["value"],
                "domain": cookie["domain"],
                "path": cookie["path"]
            }
            if "expirationDate" in cookie:
                pw_cookie["expires"] = cookie["expirationDate"]
            if cookie.get("httpOnly"):
                pw_cookie["httpOnly"] = True
            if cookie.get("secure"):
                pw_cookie["secure"] = True
            if "sameSite" in cookie:
                same_site = cookie["sameSite"]
                if same_site in ["unspecified", "no_restriction"]:
                    pw_cookie["sameSite"] = "Lax"
                elif same_site.lower() in ["strict", "lax", "none"]:
                    pw_cookie["sameSite"] = same_site.capitalize()
            playwright_cookies.append(pw_cookie)
        
        await context.add_cookies(playwright_cookies)
        
        page = await context.new_page()
        
        print("[Status] 正在打开小红书创作者平台...")
        await page.goto("https://creator.xiaohongshu.com/publish/publish")
        await page.wait_for_timeout(3000)
        
        # 检查登录状态
        if "login" in page.url:
            print("[Error] Cookie 已过期，请重新导出")
            await browser.close()
            return
        
        print("[Success] 登录成功！")
        print("\n[自动操作开始]")
        
        # 上传图片
        if images:
            print(f"[Status] 正在上传 {len(images)} 张图片...")
            try:
                await page.wait_for_timeout(2000)
                file_input = page.locator('input[type="file"]').first
                await file_input.set_input_files(images[:9])
                print("[Success] 图片已注入")
                await page.wait_for_timeout(5000)
            except Exception as e:
                print(f"[Warning] 图片上传失败: {e}")
        
        # 填充标题
        try:
            await page.wait_for_timeout(500)
            title_input = page.locator('input[placeholder*="标题"]').first
            await title_input.click()
            await title_input.fill(title)
            print(f"[Success] 标题已填充")
        except Exception as e:
            print(f"[Warning] 标题填充失败: {e}")
        
        # 填充正文
        try:
            await page.wait_for_timeout(500)
            content_editor = page.locator('div[contenteditable="true"], textarea').first
            await content_editor.click()
            await content_editor.fill(body)
            print(f"[Success] 正文已填充 ({len(body)} 字)")
        except Exception as e:
            print(f"[Warning] 正文填充失败: {e}")
        
        print("\n[提示] 内容已自动填充完毕！")
        print("       请在浏览器中检查内容，然后：")
        print("       1. 如需修改，请直接在浏览器中编辑")
        print("       2. 确认无误后，点击'发布'或'保存草稿'按钮")
        print("       3. 完成后关闭浏览器窗口即可\n")
        
        # 等待用户操作
        try:
            await page.wait_for_timeout(300000)  # 等待 5 分钟
        except:
            pass
        
        print("[Success] 流程完成！")

if __name__ == "__main__":
    asyncio.run(publish_xhs_headful())
