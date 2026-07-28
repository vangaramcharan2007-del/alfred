import asyncio
import os
import json
import re
from playwright.async_api import async_playwright

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from jarvisx.core.configuration import ConfigurationManager
from jarvisx.core.llm_router import OmniRouterClient

async def solve_nptel():
    print("\n[Alfred]: Initiating NPTEL Week 0 Autonomous Sequence...")
    
    print("\n[Alfred]: Launching a fresh automation browser window...")
    
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(
                headless=False,
                channel="chrome",
                args=["--start-maximized"]
            )
            context = await browser.new_context(no_viewport=True)
            page = await context.new_page()
            
            print("[Alfred]: Navigating to Swayam NPTEL Dashboard...")
            await page.goto("https://swayam.gov.in/nc_details/NPTEL")
            
            print("[Alfred]: Please sign in and navigate to the specific 'Programming in Java - Week 0' assignment page.")
            print("[Alfred]: I will wait for 90 seconds for you to open the assignment...")
            
            # Wait for user to navigate to an assessment page
            for _ in range(90):
                url = page.url
                if "assessment" in url.lower() or "unit" in url.lower():
                    print(f"\n[Alfred]: Detected assignment page: {url}")
                    break
                await asyncio.sleep(1)
                
            print("\n[Alfred]: Give me 5 seconds to analyze the DOM...")
            await asyncio.sleep(5)
            
            # Extract form HTML
            form_html = await page.evaluate("() => { const form = document.querySelector('form'); return form ? form.outerHTML : document.body.innerHTML; }")
            
            print("[Alfred]: Transmitting assignment data to OmniRoute for solving...")
            
            prompt = f"""
            You are an expert Java programmer and automation engineer. 
            Here is the HTML of an NPTEL Week 0 assignment for "Programming in Java".
            1. Read the questions and options.
            2. Determine the correct answers.
            3. Return a JSON array of the exact CSS selectors needed to click the correct <input type="radio"> or <input type="checkbox"> elements.
            4. Only output the raw JSON array of strings, nothing else. No markdown formatting.
            
            Example output:
            ["input[name='question1'][value='A']", "input[id='q2_option3']"]
            
            HTML Content:
            {form_html[:50000]}
            """
            
            router = OmniRouterClient()
            messages = [{"role": "user", "content": prompt}]
            
            # Use default model or specify one if desired
            result_text = await router.chat(messages, model="llama3")
            result_text = result_text.strip()
            
            # Clean up markdown if present
            if result_text.startswith("```json"):
                result_text = result_text.replace("```json", "").replace("```", "").strip()
            elif result_text.startswith("```"):
                result_text = result_text.replace("```", "").strip()
                
            try:
                selectors = json.loads(result_text)
                print(f"[Alfred]: Received {len(selectors)} answers. Executing clicks...")
                
                for selector in selectors:
                    print(f" -> Clicking: {selector}")
                    await page.click(selector, timeout=5000)
                    await asyncio.sleep(0.5)
                    
                print("\n[Alfred]: Answers have been filled!")
                print("[Alfred]: I am leaving the 'Submit' button for you to click manually to verify.")
                
            except json.JSONDecodeError:
                print(f"[Error]: Failed to parse LLM response: {result_text}")
                
            print("\n[Alfred]: Handing control back to you. The browser will stay open for 30 seconds.")
            await asyncio.sleep(30)
            await browser.close()
            
        except Exception as e:
            print(f"\n[Error]: Could not take control of Chrome. Error: {e}")
            print("\n[Alfred]: Did you completely close all Chrome windows (including background apps in the system tray)?")

if __name__ == "__main__":
    asyncio.run(solve_nptel())
