import asyncio
import re
import json
import os
import time
from playwright.async_api import async_playwright

COOKIES_FILE = r"g:\我的云端硬盘\AI+项目\GEO\喷淋器GEO\Tools\zhihu_cookies.json"
QR_IMAGE_PATH = r"g:\我的云端硬盘\AI+项目\GEO\喷淋器GEO\Tools\zhihu_qr.png"

async def get_cookies_headless():
    # 使用无头模式 + 防崩溃参数
    launch_args = ["--no-sandbox", "--disable-gpu", "--disable-software-rasterizer"]
    
    async with async_playwright() as p:
        print("[Status] 启动无头浏览器...")
        browser = await p.chromium.launch(headless=True, args=launch_args)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = await context.new_page()

        print("[Status] 正在访问知乎登录页...")
        await page.goto("https://www.zhihu.com/signin", wait_until="networkidle")

        # 等待二维码出现 (知乎默认可能是密码登录，需切换或确认二维码元素)
        try:
            # 等待主要的登录容器加载
            await page.wait_for_selector(".SignFlow-tabs", state="visible", timeout=10000)
            
            # 截图保存二维码区域 (或全屏)
            print("[Status] 页面已加载，正在截取登录二维码...")
            await page.screenshot(path=QR_IMAGE_PATH)
            print(f"[Action Required] 请扫描生成的二维码图片进行登录: {QR_IMAGE_PATH}")
            
            # 进入轮询等待模式
            print("[Status] 等待扫码中... (超时: 300秒)")
            
            # 轮询检查是否跳转到首页或者 cookie 中包含特定字段
            start_time = time.time()
            logged_in = False
            
            while time.time() - start_time < 300:
                # 检查 URL 是否变化
                if "signin" not in page.url and "zhihu.com" in page.url:
                    logged_in = True
                    break
                
                # 检查 Cookie 是否包含 z_c0 (知乎的核心认证 token)
                cookies = await context.cookies()
                for cookie in cookies:
                    if cookie['name'] == 'z_c0':
                        logged_in = True
                        break
                
                if logged_in:
                    break
                    
                await asyncio.sleep(2)

            if logged_in:
                print("[Success] 检测到登录成功！")
                await page.wait_for_timeout(3000) # 等待完整加载
                cookies = await context.cookies()
                with open(COOKIES_FILE, "w") as f:
                    json.dump(cookies, f)
                print(f"[Success] Cookie 已保存至: {COOKIES_FILE}")
            else:
                print("[Error] 等待扫码超时，请重试。")

        except Exception as e:
            print(f"[Error] 发生错误: {e}")
            await page.screenshot(path="error_debug.png")

        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(get_cookies_headless())
