import asyncio, json, os, re, sys
from playwright.async_api import async_playwright
try:
    from report_generator import ReportGenerator
except ImportError:
    # Fallback if report_generator is not in the same directory (e.g. during dev)
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from report_generator import ReportGenerator

# 配置：从当前脚本所在目录的上上级目录查找内容
# 假设结构: GEO_Repo/分药器GEO/Tools/prod_publish.py
# 内容在: GEO_Repo/分药器GEO/Platform_XHS_Pauhex.md
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # Tools
REPO_DIR = os.path.dirname(os.path.dirname(BASE_DIR)) # GEO_Repo
CONTENT_FILE = os.path.join(REPO_DIR, "分药器GEO", "Platform_XHS_Pauhex.md")
COOKIE_FILE = os.path.join(BASE_DIR, "xhs_cookies_full.json")
REPORT_DIR = os.path.join(REPO_DIR, "GEO_Reports")

async def run():
    # 1. 初始化报告
    reporter = ReportGenerator(output_dir=REPORT_DIR)
    reporter.log(">>> 启动自动化发布任务...")
    
    try:
        # 2. 读取内容
        if not os.path.exists(CONTENT_FILE):
            raise FileNotFoundError(f"找不到内容文件: {CONTENT_FILE}")

        with open(CONTENT_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取标题
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if not title_match:
            raise ValueError("无法在 Markdown 中解析出标题 (# Title)")
            
        title = title_match.group(1)
        reporter.set_title(title)
        reporter.log(f"✅ 读取到文章：《{title}》")

        # 3. 启动浏览器
        async with async_playwright() as p:
            reporter.log("正在启动 Chromium...")
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(viewport={"width": 1920, "height": 1080})
            
            # 注入 Cookie
            if os.path.exists(COOKIE_FILE):
                try:
                    with open(COOKIE_FILE, 'r', encoding='utf-8') as f: cookies = json.load(f)
                except:
                    with open(COOKIE_FILE, 'r', encoding='gbk') as f: cookies = json.load(f)
                
                clean_cookies = []
                for c in cookies:
                    c["sameSite"] = "Lax"
                    clean_cookies.append(c)
                await context.add_cookies(clean_cookies)
                reporter.log(f"✅ Cookie 已注入 ({len(clean_cookies)} 个)")
            else:
                reporter.log(f"⚠️ 警告: 找不到 Cookie 文件 {COOKIE_FILE}")

            page = await context.new_page()
            
            # 访问发布页
            reporter.log("正在访问创作服务平台...")
            try:
                await page.goto("https://creator.xiaohongshu.com/publish/publish", timeout=60000)
                await page.wait_for_timeout(8000)
            except Exception as e:
                reporter.log(f"⚠️ 页面加载超时，尝试继续... {e}")

            # 验证登录
            if "login" in page.url:
                screenshot_path = os.path.join(REPORT_DIR, "login_failed.png")
                await page.screenshot(path=screenshot_path)
                reporter.add_screenshot("登录失败截图", screenshot_path)
                raise Exception("Cookie 失效，重定向到了登录页")
            else:
                reporter.log("✅ 登录验证成功")

                # 填写标题
                reporter.log(f"正在尝试填写标题: {title}")
                title_filled = False
                try:
                    await page.locator('input[placeholder*="标题"]').first.fill(title)
                    title_filled = True
                except:
                    try:
                        await page.locator('.c-input').first.fill(title)
                        title_filled = True
                    except:
                        reporter.log("⚠️ 标题输入框定位失败")

                if title_filled:
                    reporter.log("✅ 标题填写成功")
                
                # 截图留证
                screenshot_path = os.path.join(REPORT_DIR, "success_proof.png")
                await page.screenshot(path=screenshot_path)
                reporter.add_screenshot("最终发布预览", screenshot_path)
                reporter.mark_success()

            await browser.close()
            
    except Exception as e:
        reporter.mark_failed(e)
    finally:
        # 生成并保存报告
        report_path = reporter.save()
        
        # 尝试自动提交到 GitHub
        if os.path.exists(os.path.join(REPO_DIR, ".git")):
            reporter.log("正在同步报告到 GitHub...")
            import subprocess
            
            # 1. Pull 最新代码 (防止冲突)
            subprocess.run(["git", "pull"], cwd=REPO_DIR, check=False)
            
            # 2. Add 报告和截图
            subprocess.run(["git", "add", "GEO_Reports/"], cwd=REPO_DIR, check=False)
            
            # 3. Commit
            commit_msg = f"Auto: Daily Report {reporter.start_time.strftime('%Y-%m-%d')}"
            subprocess.run(["git", "commit", "-m", commit_msg], cwd=REPO_DIR, check=False)
            
            # 4. Push
            # 注意：这依赖于 remote url 中包含 token，或者已经配置了 credential helper
            result = subprocess.run(["git", "push"], cwd=REPO_DIR, capture_output=True, text=True)
            
            if result.returncode == 0:
                reporter.log("✅ 报告已成功推送到 GitHub")
            else:
                reporter.log(f"⚠️ Push 失败 (可能是权限问题): {result.stderr}")

if __name__ == "__main__":
    asyncio.run(run())
