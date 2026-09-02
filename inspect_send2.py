from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import os, time

profile_path = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'WhatsAppBot')
options = webdriver.ChromeOptions()
options.add_argument(f'user-data-dir={profile_path}')
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument('--window-size=1280,1024')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get('https://web.whatsapp.com')

print('Waiting for search box...')
search_box = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, '//*[@data-tab="3"]')))
search_box.clear()
search_box.send_keys('9849379819')
time.sleep(2)
search_box.send_keys(Keys.ENTER)
time.sleep(3)

print('Typing message...')
msg_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@data-tab="10"]')))
msg_box.click()
time.sleep(1)

actions = ActionChains(driver)
actions.send_keys('hi dady test 3')
actions.perform()
time.sleep(2)

print('Taking screenshot BEFORE enter...')
driver.save_screenshot('before_enter2.png')

actions = ActionChains(driver)
actions.send_keys(Keys.ENTER)
actions.perform()
time.sleep(3)

print('Taking screenshot AFTER enter...')
driver.save_screenshot('after_enter2.png')

driver.quit()
