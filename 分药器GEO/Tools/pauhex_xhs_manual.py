import asyncio
from playwright.async_api import async_playwright
import os
import re

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

async def publish_xhs_manual():
    print("=" * 60)
    print("   PAUHEX 小红书半自动发布助手 (GUI 模式)")
    print("   您将看到一个真实的浏览器窗口")
    print("=" * 60)
    
    # 读取 Cookie
    import json
    with open(COOKIE_FILE, 'r', encoding='utf-8') as f:
        cookies_data = json.load(f)
    
    # 解析内容
    title, body, images = parse_content(CONTENT_FILE)
    print(f"\n[内容预览]")
    print(f"标题: {title}")
    print(f"正文: {len(body)} 字")
    print(f"图片: {len(images)} 张")
    print(f"\n[操作提示]")
    print("1. 浏览器窗口将自动打开并登录")
    print("2. 请手动点击'上传图片'按钮")
    print("3. 在弹出的文件选择器中，选择以下图片：")
    for i, img in enumerate(images, 1):
        print(f"   {i}. {os.path.basename(img)}")
    print("4. 上传完成后，脚本会自动填充标题和正文")
    print("5. 最后请您手动点击'发布'按钮\n")
    
    input("按 Enter 键启动浏览器...")
    
    async with async_playwright() as p:
        # === 启动有界面浏览器 ===
        browser = await p.chromium.launch(
            headless=False,  # 关键：显示浏览器窗口
            args=["--start-maximized"]
        )
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            viewport=None,  # 使用窗口默认大小
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
        
        print("\n[Status] 正在打开小红书创作者平台...")
        await page.goto("https://creator.xiaohongshu.com/publish/publish")
        
        print("\n[提示] 请在浏览器窗口中手动上传图片...")
        print("       上传完成后，在此按 Enter 键继续...")
        input()
        
        # 填充标题
        print("\n[Status] 正在填充标题...")
        try:
            title_input = page.locator('input[placeholder*="标题"]').first
            await title_input.click()
            await title_input.fill(title)
            print(f"[Success] 标题已填充")
        except Exception as e:
            print(f"[Warning] 标题填充失败: {e}")
        
        # 填充正文
        print("[Status] 正在填充正文...")
        try:
            content_editor = page.locator('div[contenteditable="true"], textarea').first
            await content_editor.click()
            await content_editor.fill(body)
            print(f"[Success] 正文已填充 ({len(body)} 字)")
        except Exception as e:
            print(f"[Error] 正文填充失败: {e}")
        
        print("\n[提示] 内容已填充完毕！")
        print("       请在浏览器中检查内容，然后手动点击'发布'按钮")
        print("       发布完成后，在此按 Enter 键关闭浏览器...")
        input()
        
        await browser.close()
        print("\n[Success] 发布流程完成！")

if __name__ == "__main__":
    asyncio.run(publish_xhs_manual())
