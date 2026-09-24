import subprocess
import time
from playwright.sync_api import sync_playwright

def main():
    server = subprocess.Popen(['python', '-m', 'http.server', '8080'], cwd='../scratch_fix')
    time.sleep(1)
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            
            for width in [1200, 375]:
                print(f"\\n--- Testing width {width} ---")
                page = browser.new_page(viewport={"width": width, "height": 800})
                errors = []
                page.on("pageerror", lambda err: errors.append(err.message))
                page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
                
                page.goto("http://localhost:8080")
                page.wait_for_selector("nav.nav")
                
                nav_buttons = page.locator("nav.nav button")
                count = nav_buttons.count()
                print(f"Found {count} nav buttons")
                
                for i in range(count):
                    btn = nav_buttons.nth(i)
                    view_id = btn.get_attribute("data-view")
                    btn.click()
                    time.sleep(0.1)
                    print(f"Clicked {view_id}")
                
                if width == 1200:
                    page.locator('button[data-view="results"]').click()
                    page.evaluate('window.scrollTo(0, 0)')
                    time.sleep(0.5)
                    page.screenshot(path="../header_nav.png")
                    
                    page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                    time.sleep(0.5)
                    page.screenshot(path="../footer.png")
                    
                    # Scroll to E2
                    e2_header = page.locator('h3:has-text("E2")')
                    e2_header.scroll_into_view_if_needed()
                    time.sleep(0.5)
                    page.screenshot(path="../e2_results.png")
                    
                    # Extract E2 data
                    e2_rows = page.locator('#e2_section table tbody tr').all()
                    print("\\nExtracted E2 rows from UI:")
                    for r in e2_rows:
                        text = r.inner_text().replace('\\n', ' | ')
                        print(text)
                
                if errors:
                    print(f"Errors found: {errors}")
                else:
                    print("No console errors found.")
                    
            browser.close()
    finally:
        server.terminate()
        server.wait()

if __name__ == '__main__':
    main()
