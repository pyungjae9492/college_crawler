from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import bs4
from bs4 import BeautifulSoup
import time
from time import sleep
import pandas as pd
import logging
import openpyxl
import pyautogui

# 완료

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

base_url = 'https://www.coursicle.com/'

schools = ['harvard']

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'}

options = webdriver.ChromeOptions()
options.add_argument('headless')
driver = webdriver.Chrome(
    'chromedriver.exe')  # mac의 경우 chromedriver
driver.implicitly_wait(3)
driver.get(base_url + schools[0], headers=headers)

result = []

driver.find_element_by_css_selector('#searchBox').send_keys(' ')
WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, '#cardContainer > div > div.wrap')))

SCROLL_PAUSE_SEC = 1

last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    # 끝까지 스크롤 다운
    pyautogui.press('pagedown')
    pyautogui.press('pagedown')
    pyautogui.press('pagedown')
    # 1초 대기
    time.sleep(SCROLL_PAUSE_SEC)

    # 스크롤 다운 후 스크롤 높이 다시 가져옴
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        time.sleep(SCROLL_PAUSE_SEC)
    if new_height == last_height:
        break
    last_height = new_height

# col_name = ['Course_Information', 'Schedule']
# bc = pd.DataFrame(result, columns=col_name)
# bc['Code'] = bc.Course_Information.str.extract(r'(?<=\()(.+)(?=\))')
# bc['Course_Name'] = bc.Course_Information.str.extract(r'^.+(?=\s\()')
# bc['Credit'] = bc.Course_Information.str.extract(
#     r'(?<=[cC][rR][eE][dD][iI][tT][sS]\:)[0-9]+(?=\n)')
# bc['Professor'] = bc.Course_Information.str.extract(r'')
# bc['Course_Name'] = bc.Course_Information.str.extract(r'')
# bc['Course_Name'] = bc.Course_Information.str.extract(r'')
# bc.to_excel('./crawl_results/bc.xlsx')
