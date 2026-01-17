import asyncio
from playwright.async_api import async_playwright

async def run():
    print("Trying to launch browser...")
    try:
        async with async_playwright() as p:
            print("Playwright context created.")
            browser = await p.chromium.launch(headless=True)
            print(f"Browser launched: {browser}")
            page = await browser.new_page()
            await page.goto("http://www.baidu.com")
            print(f"Page title: {await page.title()}")
            await browser.close()
            print("Browser closed successfully.")
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(run())
