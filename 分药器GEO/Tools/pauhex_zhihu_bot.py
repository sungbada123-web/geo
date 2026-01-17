import asyncio
import os
import re
import json
from playwright.async_api import async_playwright

# --- 配置区 (Paths) ---
BASE_PATH = r"g:\我的云端硬盘\AI+项目\GEO\分药器GEO"
CONTENT_FILE = os.path.join(BASE_PATH, "Platform_Zhihu_Pauhex.md")
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

            title_match = re.search(r"^# (.*)", full_content)
            title = title_match.group(1).strip() if title_match else "PAUHEX 深度解析"
            body = re.sub(r"^# .*\n", "", full_content)

            # 4. 访问发布页
            print("[Status] 正在后台访问知乎创作中心...")
            await page.goto("https://zhuanlan.zhihu.com/write", wait_until="domcontentloaded", timeout=60000)
            
            # 验证登录
            if "signin" in page.url:
                print("[Error] 登录已失效！Cookie 可能过期。")
                # 截图保存现场
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
            # await page.focus(editor_selector) # click 已经包含了 focus

            segments = re.split(r"(!\[.*?\]\(.*?\))", body)
            print(f"[Status] 正文解析为 {len(segments)} 个片段，准备写入...")

            # --- 文案清洗函数 ---
            def clean_markdown(text):
                # 去除标题符号
                text = re.sub(r"^#+\s*", "", text)
                # 去除加粗符号
                text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
                # 去除链接格式
                text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)
                return text.strip()

            from urllib.parse import unquote
            
            # 先截一张工具栏的图，便于后续排查选择器是否正确
            try:
                await page.screenshot(path="debug_toolbar.png", clip={"x":0, "y":0, "width":1000, "height":300})
            except:
                pass

            for i, seg in enumerate(segments):
                img_match = re.match(r"!\[(.*?)\]\((.*?)\)", seg)
                if img_match:
                    raw_path = img_match.group(2).replace("file:///", "").replace("/", os.sep)
                    img_path = unquote(raw_path)
                    
                    if not os.path.exists(img_path):
                        continue
                        
                    print(f"  [{i+1}/{len(segments)}] 正在上传图片: {os.path.basename(img_path)}")
                    
                    try:
                        await page.click(editor_selector)
                        
                        # 【策略C：广撒网式 Input 注入】
                        # 知乎编辑器内通常有一个 hidden input。我们不点击按钮，直接找这个 input。
                        # 如果找不到，就强行注入 JS 创建一个 input 并触发上传（Playwright 黑科技）
                        
                        # 1. 尝试查找页面上现存的所有 file input
                        inputs = page.locator('input[type="file"]')
                        count = await inputs.count()
                        print(f"  [Debug] 页面上发现了 {count} 个文件输入框")
                        
                        uploaded = False
                        if count > 0:
                            # 给每一个 input 都塞入文件 (宁可错杀，不可放过)
                            for idx in range(count):
                                try:
                                    await inputs.nth(idx).set_input_files(img_path)
                                    uploaded = True
                                    print(f"  [Info] 已向第 {idx} 个输入框注入文件")
                                except:
                                    pass
                        
                        if not uploaded:
                            # 2. 如果没有 input，尝试点击按钮激发出 input
                            print("  [Info] 没找到 input，尝试点击图标...")
                            # 尝试多种图标选择器
                            icon_selectors = [
                                'button[aria-label="插入图片"]',
                                '.UploadPicture-wrapper button', # 常见类名
                                'svg[width="24"]', # 盲猜图标大小
                            ]
                            
                            file_chooser_future = page.wait_for_event("filechooser", timeout=5000)
                            
                            clicked_icon = False
                            for sel in icon_selectors:
                                if await page.locator(sel).count() > 0:
                                    await page.click(sel)
                                    clicked_icon = True
                                    break
                            
                            if clicked_icon:
                                try:
                                    file_chooser = await file_chooser_future
                                    await file_chooser.set_files(img_path)
                                    print("  [Success] 成功捕获 filechooser 并上传！")
                                    uploaded = True
                                except:
                                    print("  [Warning] 点击了图标但没捕捉到 filechooser 事件")
                        
                        if uploaded:
                            print("  [Info] 等待渲染 8s...")
                            await page.wait_for_timeout(8000)
                            await page.press(editor_selector, "Enter")
                        else:
                            print("  [Error] 所有上传手段均失效，跳过此图")

                    except Exception as e:
                         print(f"[Error] 上传异常: {e}")
                else:
                    # 文本处理
                    cleaned = clean_markdown(seg)
                    if cleaned:
                        await page.type(editor_selector, cleaned)
                        await page.press(editor_selector, "Enter")
                        await page.wait_for_timeout(500)
# 稍微节制输入速度

            print("[Status] 内容填充完毕，准备发布...")
            
            # 7. 执行发布流程 - 增强版点击策略
            print("[Status] 内容填充完毕，等待自动保存同步 (5s)...")
            await page.wait_for_timeout(5000)
            
            # --- 6.5 自动添加话题 (新逻辑) ---
            print("[Status] 正在自动添加话题...")
            try:
                # 尝试打开话题编辑栏 (如果还没打开)
                # 知乎有时候默认折叠，有时候是直接展示 input
                # 常见选择器: "添加话题" 按钮 或 input[placeholder="搜索话题"]
                
                # 策略: 先找 input，找不到就找加号按钮
                topic_input_sel = 'input.TopicTagInput-input, input[placeholder="搜索话题"]'
                
                if await page.locator(topic_input_sel).count() == 0:
                     print("  [Action] 未直接找到话题框，尝试点击'添加话题'按钮...")
                     await page.click('button:has-text("添加话题")', timeout=2000)
                     await page.wait_for_timeout(1000)
                
                # 核心话题列表
                topics = ["医疗器械", "养老", "黑科技"]
                
                topic_input = page.locator(topic_input_sel).first
                
                if await topic_input.count() > 0:
                    for topic in topics:
                        print(f"  [Action] 添加话题: {topic}")
                        await topic_input.click()
                        await topic_input.fill(topic)
                        await page.wait_for_timeout(1500) # 等待联想菜单
                        await topic_input.press("Enter")
                        await page.wait_for_timeout(1000)
                else:
                    print("  [Warning] 无法定位话题输入框，跳过话题添加。")

            except Exception as e:
                print(f"  [Warning] 添加话题失败: {e} (不影响继续尝试发布)")

            # --- 7. 循环触发发布弹窗 (死磕模式) ---
            print("[Status] 进入强制发布循环，直到弹窗出现...")
            
            # 定义弹窗出现的标志 (容器或按钮)
            confirm_selector = 'button:has-text("确认发布")'
            next_step_selector = 'button:has-text("下一步")'
            modal_selector = '.PublishPanel'
            
            modal_found = False
            import time
            loop_start = time.time()
            
            while time.time() - loop_start < 60: # 最多尝试 60秒
                # 1. 检查弹窗是否已经出来了
                if await page.locator(modal_selector).count() > 0 or \
                   await page.locator(confirm_selector).count() > 0 or \
                   await page.locator(next_step_selector).count() > 0:
                    print("[Success] 捕捉到发布弹窗！")
                    modal_found = True
                    break
                
                # 2. 如果没出来，执行点击
                print(f"[Action] 尝试点击发布按钮 (已耗时 {int(time.time()-loop_start)}s)...")
                
                # 优先使用 JS 点击，最稳
                clicked_via_js = await page.evaluate('''() => {
                    const btns = Array.from(document.querySelectorAll('button'));
                    // 精确匹配 "发布" 两个字，防止点到其他带发布字样的东西
                    const pBtn = btns.find(b => b.innerText.trim() === '发布');
                    if (pBtn) {
                        pBtn.click();
                        return true;
                    }
                    return false;
                }''')
                
                if not clicked_via_js:
                    # 备用：常规点击
                    try:
                        await page.click('button:has-text("发布")', timeout=1000)
                    except:
                        pass
                
                # 3. 等待反应
                await page.wait_for_timeout(3000)
            
            if not modal_found:
                raise Exception("死循环尝试 60秒后仍未触发发布弹窗，请检查页面状态。")

            # --- 8. 处理弹窗逻辑 ---
            print("[Status] 正在处理弹窗确认...")
            await page.wait_for_timeout(1000)
            
            # 这里的逻辑：如果有下一步点下一步，有确认点确认
            # 循环几次确保点过去
            for _ in range(5):
                if await page.locator(next_step_selector).is_visible():
                    print("  [Action] 点击'下一步'")
                    await page.click(next_step_selector)
                    await page.wait_for_timeout(1500)
                
                if await page.locator(confirm_selector).is_visible():
                    print("  [Action] 点击'确认发布'")
                    await page.click(confirm_selector)
                    await page.wait_for_timeout(2000)
                    # 点完确认后，通常弹窗会消失，或者页面跳转
                    break
                    
                await page.wait_for_timeout(1000)

            # --- 9. 最终验证跳转 ---
            print("[Status] 等待跳转文章详情页...")
            try:
                # 成功后 URL 结构通常是 zhihu.com/p/123456
                # 增加超时时间到 30s
                await page.wait_for_url(lambda u: "/p/" in u and "edit" not in u, timeout=30000)
                print(f"[Success] 发布成功！文章 URL: {page.url}")
                
                # 保存 URL
                with open("published_url.txt", "w") as f:
                    f.write(page.url)
                    
            except Exception as e:
                print(f"[Warning] 页面未跳转或超时: {page.url}")
                # 可能是进入了审核状态，或者 URL 规则变了
                if "/p/" in page.url:
                     print(f"[Success]虽然超时但 URL 看起来是对的: {page.url}")
                     with open("published_url.txt", "w") as f:
                        f.write(page.url)
            
            # 截图验证
            await page.wait_for_timeout(3000)
            await page.screenshot(path="published_final_result.png")
            print(f"[Success] 流程结束，截图已保存至 published_final_result.png")

        except Exception as e:
            print(f"[Critical Error] 脚本执行出错: {e}")
            await page.screenshot(path="error_snapshot.png")
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(publish_to_zhihu())
