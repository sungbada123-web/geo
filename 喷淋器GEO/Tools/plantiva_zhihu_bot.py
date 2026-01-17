import asyncio
import os
import re
import json
from playwright.async_api import async_playwright

# --- 配置区 (Paths) ---
BASE_PATH = r"g:\我的云端硬盘\AI+项目\GEO\喷淋器GEO"
CONTENT_FILE = os.path.join(BASE_PATH, "GEO_Content_Draft_Sprinkler.md")
ASSETS_DIR = os.path.join(BASE_PATH, "Assets")
COOKIES_FILE = os.path.join(BASE_PATH, "Tools", "zhihu_cookies.json")

async def publish_to_zhihu():
    # 启用无头模式以提高稳定性，避免图形界面卡死
    async with async_playwright() as p:
        print("[Status] 启动浏览器引擎...")
        # 添加防崩溃参数，确保后台运行稳健
        launch_args = ["--no-sandbox", "--disable-gpu", "--disable-software-rasterizer"]
        browser = await p.chromium.launch(headless=True, args=launch_args)
        
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        context = await browser.new_context(user_agent=user_agent)

        if os.path.exists(COOKIES_FILE):
            with open(COOKIES_FILE, "r") as f:
                cookies = json.load(f)
                await context.add_cookies(cookies)
            print(f"[Status] 已加载 Cookie: {len(cookies)} 条")
        else:
            print("[Error] 未找到 Cookie 文件！请先运行 get_zhihu_cookies.py")
            await browser.close()
            return

        page = await context.new_page()

        try:
            # 3. 读取内容
            if not os.path.exists(CONTENT_FILE):
                print(f"[Error] 找不到文案文件: {CONTENT_FILE}")
                return
                
            with open(CONTENT_FILE, "r", encoding="utf-8") as f:
                full_content = f.read()

            title_match = re.search(r"^# (.*)", full_content) # 尝试匹配 # 标题
            if not title_match:
                 title_match = re.search(r"\*\*拟定标题\*\*: (.*)", full_content) # 尝试匹配 **拟定标题**:
                 
            title = title_match.group(1).strip() if title_match else "PLANTIVA AI 智慧喷淋深度解析"
            body = re.sub(r"^# .*\n", "", full_content) # 简单清理

            # 4. 访问发布页
            print("[Status] 正在后台访问知乎创作中心...")
            await page.goto("https://zhuanlan.zhihu.com/write", wait_until="domcontentloaded", timeout=60000)
            
            # 验证登录
            if "signin" in page.url:
                print("[Error] 登录已失效！Cookie 可能过期。")
                await page.screenshot(path="login_failed.png")
                await browser.close()
                return

            print("[Status] 成功进入编辑器。")
            
            # 5. 输入标题
            await page.wait_for_selector(".WriteIndex-titleInput textarea", timeout=30000)
            await page.fill(".WriteIndex-titleInput textarea", title)
            print(f"[Status] 标题已填入: {title}")

            # 6. 处理内容
            # 使用更通用的选择器，避免 class 变化导致找不到元素
            editor_selector = 'div[contenteditable="true"]'
            
            # 使用 click 确保激活编辑器
            await page.click(editor_selector)

            segments = re.split(r"(!\[.*?\]\(.*?\))", body)
            print(f"[Status] 正文解析为 {len(segments)} 个片段，准备写入...")

            for i, seg in enumerate(segments):
                img_match = re.match(r"!\[(.*?)\]\((.*?)\)", seg)
                if img_match:
                    # 图片处理
                    img_path = img_match.group(2).replace("file:///", "").replace("/", os.sep)
                    if not os.path.exists(img_path):
                        print(f"[Warning] 图片不存在，跳过: {img_path}")
                        continue
                        
                    print(f"  [{i+1}/{len(segments)}] 上传图片: {os.path.basename(img_path)}")
                    
                    try:
                        async with page.expect_file_chooser(timeout=10000) as fc_info:
                            # 尝试多种可能的上传按钮选择器
                            await page.click('button[aria-label="插入图片"]', timeout=5000) 
                        
                        file_chooser = await fc_info.value
                        await file_chooser.set_files(img_path)
                        # 等待上传完成
                        await page.wait_for_timeout(5000)
                    except Exception as e:
                         print(f"[Error] 图片上传失败: {e}")
                else:
                    # 文本处理
                    if seg.strip():
                        clean_text = seg.strip()
                        await page.type(editor_selector, clean_text)
                        await page.press(editor_selector, "Enter")
                        await page.wait_for_timeout(500) 

            print("[Status] 内容填充完毕，正在保存草稿...")
            
            # 7. 保存草稿
            await page.wait_for_timeout(5000)
            
            await page.screenshot(path="draft_saved.png")
            print(f"[Success] 操作完成！已截图保存至 draft_saved.png")

        except Exception as e:
            print(f"[Critical Error] 脚本执行出错: {e}")
            await page.screenshot(path="error_snapshot.png")
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(publish_to_zhihu())
