from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import bs4
from bs4 import BeautifulSoup
import time
from time import sleep
import pandas as pd
import logging
import openpyxl
import asyncio
import requests
from functools import partial

# 크롤링 막혀있음

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

options = webdriver.ChromeOptions()
options.add_argument('headless')
driver = webdriver.Chrome('chromedriver.exe', chrome_options=options)
driver.implicitly_wait(3)
driver.get('https://www.bu.edu/phpbin/course-search/search.php?page=w0&pagesize=5&adv=1&nolog=&search_adv_all=&yearsem_adv=2021-FALL&credits=*&pathway=&hub_match=all&pagesize=-1')

# 웹이 전부 파싱되기를 기다렸다가 클릭
soup = BeautifulSoup(driver.page_source, 'html.parser')
courses = soup.select('.coursearch-result')
url_and_credits = []

for course in courses:
    a = ['http://bu.edu' + course.select_one('a').get('href'), course.select_one(
        '.coursearch-result-content-description > p:nth-child(6)').text]
    url_and_credits.append(a)

result = []
counter = 0
total = len(url_and_credits)
logging.info("TOTAL " + str(total))

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'}

for url_and_credit in url_and_credits:
    cred = url_and_credit[1][3]
    url = url_and_credit[0]
    try:
        req = requests.get(url, headers=headers)
    except:
        print('request denied!')
        continue
    sleep(4)
    html = req.text
    soup = BeautifulSoup(html, 'html.parser')
    course_name = soup.select_one('#body-tag > main > div > h1').text
    prof = soup.select('.first-row')[1].select('td')[2].text
    code = soup.select_one('#body-tag > main > div > h6').text
    room = soup.select('.first-row')[1].select('td')[4].text
    time = soup.select('.first-row')[1].select('td')[5].text
    data = [code, course_name, cred, prof, room, time]
    counter += 1
    logging.info("{:.2f}".format((counter / total) * 100))
    result.append(data)
    if counter < 25:
        break

col_name = ['Code', 'Course Name', 'Credit', 'Professor', 'Room', 'Time']
bu = pd.DataFrame(result, columns=col_name)
bu.to_excel('./crawl_results/bu.xlsx')
