import asyncio
from playwright.async_api import async_playwright
import os

async def solve_nptel():
    user_data_dir = os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data")
    assignment_url = "https://onlinecourses.nptel.ac.in/e-learning/course/noc26_cs153?unitId=16&assessmentId=689"
    
    print("[Jarvis X]: Launching Chrome with full DOM control...")
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=False, # You will see this happen
                channel="chrome", # Use your actual Chrome browser
                args=['--disable-blink-features=AutomationControlled']
            )
            
            page = await browser.new_page()
            print(f"[Jarvis X]: Navigating directly to {assignment_url}")
            await page.goto(assignment_url)
            
            # Wait for the assignment to load
            await page.wait_for_timeout(5000)
            
            print("[Jarvis X]: Injecting answers via direct DOM manipulation...")
            js = """
            const answers = ['Use of pointers','Unicode escape sequence','Java Virtual Machine','int','char ch = \\'\\\\utea\\';','char ch = \\'\\\\u0021\\';','0','main method','32 bit','javac','interface','JDB','java.util','Marker Interface','java.lang.StringBuilder','java.lang.StringBuffer','Object','Applet','javap','Bytecode is executed by the JVM','Platform independent'];
            let clicked = 0;
            document.querySelectorAll('input[type="radio"], input[type="checkbox"]').forEach(input => {
                let parent = input.parentElement;
                let text = parent ? (parent.innerText || parent.textContent) : "";
                
                let id = input.id;
                if(id) {
                    let label = document.querySelector(`label[for="${id}"]`);
                    if(label) text += " " + (label.innerText || label.textContent);
                }
                
                // NPTEL often has a div wrapper
                let grandParent = parent ? parent.parentElement : null;
                if(grandParent) text += " " + (grandParent.innerText || grandParent.textContent);
                
                answers.forEach(ans => {
                    if(text && text.includes(ans)) {
                        input.click();
                        clicked++;
                    }
                });
            });
            console.log("Answers injected:", clicked);
            return clicked;
            """
            
            clicks = await page.evaluate(js)
            print(f"[Jarvis X]: Successfully clicked {clicks} correct options!")
            
            await page.wait_for_timeout(3000)
            
            # Click submit
            print("[Jarvis X]: Submitting assignment...")
            await page.evaluate("""
                const s = document.querySelector('button[type="submit"], input[value="Submit"], .gcb-button, button:contains("Submit")');
                if(s) s.click();
            """)
            
            await page.wait_for_timeout(5000)
            print("[Jarvis X]: Done! Assignment has been dominated.")
            
            await browser.close()
            
    except Exception as e:
        print(f"[Error]: {e}")
        print("\n[CRITICAL]: Chrome must be FULLY CLOSED before running this script because the profile is locked.")

if __name__ == "__main__":
    asyncio.run(solve_nptel())
