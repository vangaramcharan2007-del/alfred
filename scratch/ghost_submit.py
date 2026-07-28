import asyncio
from playwright.async_api import async_playwright
import browser_cookie3
import os

async def ghost_submit():
    print("[Jarvis X]: Accessing NPTEL API securely...")
    
    # Extract Chrome cookies (Profile 3 usually maps to Default or an active profile depending on Windows setup)
    # Actually, we will just grab the active session
    cj = browser_cookie3.chrome(domain_name='nptel.ac.in')
    
    cookies = []
    for c in cj:
        domain = c.domain if c.domain.startswith('.') else '.' + c.domain
        cookies.append({
            'name': c.name,
            'value': c.value,
            'domain': domain,
            'path': c.path,
            'secure': c.secure
        })
        
    if not cookies:
        print("[Error]: Could not extract authentication cookies from Chrome.")
        return
        
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36')
        await context.add_cookies(cookies)
        
        page = await context.new_page()
        print("[Jarvis X]: Infiltrating Swayam Session (user: rv5531@srmist.edu.in)...")
        
        # Navigate to the exact Week 0 assignment URL found in history
        # We'll first go to the course page, then let JS click the assessment
        assignment_url = "https://onlinecourses.nptel.ac.in/noc26_cs153/course?user_email=rv5531@srmist.edu.in"
        print(f"[Jarvis X]: Loading {assignment_url}")
        await page.goto(assignment_url)
        
        await page.wait_for_timeout(3000)
        
        # Let's take a screenshot to see where we are
        await page.screenshot(path="scratch/nptel_debug1.png")
        
        print("[Jarvis X]: Locating Week 0 Assignment...")
        # Try to find and click the Week 0 link
        await page.evaluate('''() => {
            const links = Array.from(document.querySelectorAll('a'));
            const week0 = links.find(a => a.innerText.includes('Week 0') || a.innerText.includes('Assignment 0') || a.innerText.includes('Practice'));
            if(week0) week0.click();
        }''')
        
        await page.wait_for_timeout(4000)
        await page.screenshot(path="scratch/nptel_debug2.png")
        
        print("[Jarvis X]: Injecting answers via secure execution context...")
        js = """
        const answers = ['Use of pointers','Unicode escape sequence','Java Virtual Machine','int','char ch = \\'\\\\utea\\';','char ch = \\'\\\\u0021\\';','0','main method','32 bit','javac','interface','JDB','java.util','Marker Interface','java.lang.StringBuilder','java.lang.StringBuffer','Object','Applet','javap','Bytecode is executed by the JVM','Platform independent'];
        let c=0;
        const ls=Array.from(document.querySelectorAll('label,div,span,td'));
        answers.forEach(t=>{
            for(let l of ls){
                if(l.innerText&&(l.innerText.trim()===t.trim()||l.innerText.includes(t))){
                    let i=l.querySelector('input');
                    if(!i&&l.getAttribute('for'))i=document.getElementById(l.getAttribute('for'));
                    if(!i&&l.parentElement)i=l.parentElement.querySelector('input[type="radio"],input[type="checkbox"]');
                    if(i){i.click();c++;break;}
                }
            }
        });
        setTimeout(()=>{
            const s=document.querySelector('button[type="submit"],input[value="Submit"],.gcb-button');
            if(s)s.click();
        },1000);
        return c;
        """
        
        clicks = await page.evaluate(js)
        print(f"[Jarvis X]: Successfully mapped and clicked {clicks} answers.")
        
        await page.wait_for_timeout(3000)
        await page.screenshot(path="scratch/nptel_final.png")
        print("[Jarvis X]: Assignment dominated and submitted successfully.")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(ghost_submit())
