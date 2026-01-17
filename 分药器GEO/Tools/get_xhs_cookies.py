import asyncio
from playwright.async_api import async_playwright
import time
import os
import sys

# 基础配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIES_FILE = os.path.join(BASE_DIR, "xhs_cookies.json")
QR_FILE = os.path.join(BASE_DIR, "xhs_qr.png")

async def get_cookies():
    print("----------------------------------------------------------------")
    print("   PAUHEX Xiaohongshu (XHS) Login Tool (Headless Edition)")
    print("   Powered by SpherLab SOP v1.0")
    print("----------------------------------------------------------------")

    # 特别针对家庭云环境的防崩溃参数 (Extreme Low-Resource Mode)
    launch_args = [
        "--no-sandbox", 
        "--disable-gpu", 
        "--disable-dev-shm-usage",
        "--disable-software-rasterizer", 
        "--disable-setuid-sandbox",
        "--no-zygote",
        # 新增轻量化参数
        "--single-process", # 单进程模式(极大节省内存但略不稳定，防死机优先)
        "--disable-extensions",
        "--disable-background-networking",
        "--disable-default-apps",
        "--disable-sync",
        "--mute-audio",
        "--no-first-run"
    ]

    async with async_playwright() as p:
        print("[Status] 启动 Headless 浏览器 (Stealth Mode w/ Low-Resource)...")
        # 强制使用极小窗口，减少渲染压力
        browser = await p.chromium.launch(
            headless=True, 
            args=launch_args,
            ignore_default_args=["--enable-automation"]  # 关键：移除自动化提示条
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            device_scale_factor=1,
            has_touch=False
        )
        
        # --- 注入 Stealth 脚本 (核心反爬) ---
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            window.navigator.chrome = {
                runtime: {},
            };
            Object.defineProperty(navigator, 'languages', {
                get: () => ['zh-CN', 'zh', 'en'],
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
        """)

        page = await context.new_page()

        print("[Status] 正在前往小红书创作服务平台...")
        try:
            # 增加随机延迟
            await page.goto("https://creator.xiaohongshu.com/login", timeout=60000)
            await page.wait_for_timeout(2000)
        except Exception as e:
            print(f"[Error] 页面加载超时: {e}")
            await browser.close()
            return

        print("[Status] 等待二维码加载 (Stealth已启用)...")
        try:
            # 增加等待时间
            await page.wait_for_timeout(5000)
            
            # --- 多重选择器策略 ---
            # 1. 直接定位二维码图片 (src 包含 qr)
            qr_elem = page.locator('img[src*="qr"]').first
            
            # 2. 如果没找到，尝试找 canvas (有些版本是 canvas 绘制)
            if await qr_elem.count() == 0:
                 qr_elem = page.locator('canvas').first
            
            # 3. 如果还没找到，可能是要先点一下“扫码登录”
            if await qr_elem.count() == 0:
                 print("[Info] 尝试点击'扫码登录'切换...")
                 # 模糊匹配点击
                 await page.click('text=扫码登录', timeout=2000)
                 await page.wait_for_timeout(2000)
                 qr_elem = page.locator('img[src*="qr"], canvas').first

            if await qr_elem.count() > 0:
                # 滚动并截图
                try:
                    await qr_elem.scroll_into_view_if_needed()
                except:
                    pass
                    
                await page.wait_for_timeout(1000)
                await qr_elem.screenshot(path=QR_FILE)
                print(f"[Success] 二维码已捕获: {QR_FILE}")
                
                # 同时也截取全屏作为参考，防止二维码是个白板
                await page.screenshot(path="debug_full_login_verify.png")
                
                print("[Action] 请查看图片并使用小红书 APP 扫码！")
            else:
                print("[Error] 彻底无法定位二维码区域，已保存全屏截图 debug_xhs_login_page.png")
                await page.screenshot(path="debug_xhs_login_page.png")
                await browser.close()
                return

        except Exception as e:
            print(f"[Error] 二维码获取失败: {e}")
            await browser.close()
            return

        # 轮询等待登录成功
        print("[Status] 正在等待扫码确认 (有效期 120s)...")
        logged_in = False
        for i in range(120): # 延长等待至 120秒
            # 检查 URL 是否跳转
            if "creator.xiaohongshu.com/publish" in page.url or "creator.xiaohongshu.com/home" in page.url:
                print("[Success] 检测到 URL 跳转，登录成功！")
                logged_in = True
                break
            
            # 或者检查是否出现了用户头像等标志性元素
            if await page.locator('.user-avatar').count() > 0:
                print("[Success] 检测到用户头像，登录成功！")
                logged_in = True
                break
                
            print(f"  [{i}/120] 等待中...", end="\r")
            await asyncio.sleep(1)

        if logged_in:
            cookies = await context.cookies()
            import json
            with open(COOKIES_FILE, "w") as f:
                json.dump(cookies, f)
            print(f"\n[Success] Cookies 已保存至 {COOKIES_FILE}")
        else:
            print("\n[Timeout] 登录超时或失败。")
            await page.screenshot(path="login_failed.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(get_cookies())
