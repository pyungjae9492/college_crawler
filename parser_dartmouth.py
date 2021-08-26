from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import bs4
import time
from bs4 import BeautifulSoup
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
driver.get('http://oracle-www.dartmouth.edu/dart/groucho/timetable.main')
# 웹이 전부 파싱되기를 기다렸다가 클릭
WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
    (By.CSS_SELECTOR, '#content > table > tbody > tr:nth-child(3) > td > form > table:nth-child(23) > tbody > tr:nth-child(5) > td:nth-child(1) > input[type=submit]')))
driver.find_element_by_css_selector('#content > table > tbody > tr:nth-child(3) > td > form > table:nth-child(23) > tbody > tr:nth-child(5) > td:nth-child(1) > input[type=submit]').click()

terms = driver.find_elements_by_css_selector('#content > table:nth-child(1) > tbody > tr:nth-child(3) > td > form:nth-child(2) > table:nth-child(11) > tbody > tr > td:nth-child(2) > p')
term_num = 1
for term in terms:
    print(str(term_num)+'= ' + term.text)
    term_num += 1
term = input('Select Term_num: ')
driver.find_element_by_css_selector(f'#term{term}').click()
driver.find_element_by_css_selector('#alldelivery').click()
driver.find_element_by_css_selector('#allsubjects').click()
driver.find_element_by_css_selector('#content > table:nth-child(3) > tbody > tr:nth-child(8) > td:nth-child(1) > input[type=submit]').click()
WebDriverWait(driver, 60).until(EC.presence_of_all_elements_located(
    (By.CSS_SELECTOR, '#content > table > tbody > tr:nth-child(3) > td > form > div > table > tbody > tr')))

soup = BeautifulSoup(driver.page_source, 'html.parser')
courses = soup.select('#content > table > tbody > tr:nth-child(3) > td > form > div > table > tbody > tr')
del courses[0]

driver.quit()

count = 0
total = len(courses)
logging.info('Total:' + str(total))

result = []

for course in courses:
    code = course.select('td')[1].text
    course_name = course.select('td')[6].text
    # cred = course.select_one('td:nth-child(2)').text -> 크레딧 정보 제공 안됨
    prof = course.select('td')[13].text
    room = course.select('td')[11].text + course.select('td')[12].text
    time = course.select('td')[10].text
    data = [code, course_name, prof, room, time]
    result.append(data)
    count += 1
    logging.info("{:.2f}".format((count / total) * 100))

col_name = ['Code', 'Course Name', 'Professor', 'Room', 'Time']
dartmouth = pd.DataFrame(result, columns=col_name)
dartmouth.to_excel('./crawl_results/dartmouth.xlsx')

