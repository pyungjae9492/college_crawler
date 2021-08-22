from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import bs4
from bs4 import BeautifulSoup
from time import sleep
import pandas as pd
import logging
import openpyxl

# 완료!

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

options = webdriver.ChromeOptions()
options.add_argument('headless')
driver = webdriver.Chrome('chromedriver.exe')
driver.implicitly_wait(3)
driver.get('https://sis.uit.tufts.edu/psp/paprd/EMPLOYEE/EMPL/h/?tab=TFP_CLASS_SEARCH#search_results/term/2218/career/ALL/subject/course/attr/keyword/instructor')

# 웹이 전부 파싱되기를 기다렸다가 클릭
WebDriverWait(driver, 120).until(EC.presence_of_element_located(
    (By.CSS_SELECTOR, '#TFP_CLSSRCH_accordion > div:nth-child(2554) > a > span:nth-child(2)')))
sleep(1)
driver.find_element_by_css_selector(
    '#tfp_head_actions > div > div > label:nth-child(2) > input').click()

total = int(driver.find_element_by_css_selector(
    '#tfp_head_title > div > h1').text[:5])
logging.info("TOTAL " + str(total))

soup = BeautifulSoup(driver.page_source, 'html.parser')
every_courses = soup.select('#TFP_CLSSRCH_accordion > div')
result = []
counter = 0
print('Starting Scrapying!')
for course in every_courses:
    course_name = course.select_one('a > span:nth-child(2)').text.strip()
    sections = course.select(
        'div > div.tfp-sections > div > table > tbody > tr')
    for section in sections:
        code = section.select_one('td:nth-child(2)').text.strip()
        cred = section.select_one('td:nth-child(5)').text.strip()
        prof = section.select_one(
            'td:nth-child(4) > div > div.tfp-ins').text.strip()
        room = section.select_one(
            'td:nth-child(4) > div > div.tfp-loc').text.strip()
        time = section.select_one(
            'td:nth-child(4) > div > div.tfp-loc').text.strip()
        data = [code, course_name, cred, prof, room, time]
    counter += 1
    logging.info("{:.2f}".format((counter / total) * 100))
    result.append(data)

col_name = ['Code', 'Course Name', 'Credit', 'Professor', 'Room', 'Time']
tufts = pd.DataFrame(result, columns=col_name)

tufts['Room'] = tufts.Room.str.extract(r'(?<=\n)(.+)')
tufts['Time'] = tufts.Time.str.extract(r'(.+)(?=\n)')
tufts.to_excel('./crawl_results/tufts.xlsx')
