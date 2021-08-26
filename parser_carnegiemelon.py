from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import bs4
import time
from bs4 import BeautifulSoup
import pandas as pd
import logging
import openpyxl

logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

options = webdriver.ChromeOptions()
options.add_argument('headless')
driver = webdriver.Chrome('chromedriver.exe')
driver.implicitly_wait(3)
driver.get('https://enr-apps.as.cmu.edu/open/SOC/SOCServlet/search')
# 웹이 전부 파싱되기를 기다렸다가 클릭
WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#searchbuttons > button.btn.btn-default.form-button.submit-button')))
term_select = Select(
    driver.find_element_by_css_selector('#semester'))
term_options = driver.find_elements_by_css_selector(
    '#semester > option')
term_count = 0
for term_option in term_options:
    print(f'{ term_count } = ' + term_option.text)
    term_count += 1
term = input('Term:')
term_select.select_by_index(term)

driver.find_element_by_css_selector('#searchbuttons > button.btn.btn-default.form-button.submit-button').click()
WebDriverWait(driver, 30).until(EC.presence_of_element_located(
    (By.CSS_SELECTOR, '.table > tbody > tr')))
soup = BeautifulSoup(driver.page_source, 'html.parser')
courses = soup.select('.table > tbody > tr')

total = len(courses)
counter = 0
logging.info('total:' + str(total))
result = []

driver.quit()

for course in courses:
    code = course.select_one('td:nth-child(1)').text.strip()
    course_name = course.select_one('td:nth-child(2)').text.strip()
    cred = course.select_one('td:nth-child(3)').text.strip()
    sec = course.select_one('td:nth-child(4)').text.strip()
    days = course.select_one('td:nth-child(6)').text.strip()
    time_begin = course.select_one('td:nth-child(7)').text.strip()
    time_end = course.select_one('td:nth-child(8)').text.strip()
    room = course.select_one('td:nth-child(10)').text.strip()
    prof = course.select_one('td:nth-child(12)').text.strip()
    data = [code, course_name, cred, sec, prof, room, days, time_begin, time_end]
    result.append(data)
    counter += 1
    logging.info("{:.2f}".format((counter / total) * 100))

col_name = ['Code', 'Course_Name', 'Credit', 'Section', 'Professor', 'Room', 'Days', 'Time_Begin', 'Time_End']
carnegiemelon = pd.DataFrame(result, columns=col_name)
carnegiemelon.to_excel('./crawl_results/carnegiemelon.xlsx')


