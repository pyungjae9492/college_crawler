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

logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

options = webdriver.ChromeOptions()
options.add_argument('headless')
driver = webdriver.Chrome('chromedriver.exe', options=options)
driver.implicitly_wait(3)
driver.get('http://oracle-www.dartmouth.edu/dart/groucho/timetable.main')
# 웹이 전부 파싱되기를 기다렸다가 클릭
WebDriverWait(driver, 20).until(EC.presence_of_element_located(
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
WebDriverWait(driver, 20).until(EC.presence_of_element_located(
    (By.CSS_SELECTOR, '#term-go')))
driver.find_element_by_css_selector('#term-go').click()
WebDriverWait(driver, 20).until(EC.presence_of_element_located(
    (By.CSS_SELECTOR, '#search-go')))
driver.find_element_by_css_selector('#search-go').click()
WebDriverWait(driver, 20).until(EC.presence_of_element_located(
    (By.CSS_SELECTOR, '.page-size-select')))
page_size_selector = Select(driver.find_element_by_css_selector('.page-size-select'))
page_size_selector.select_by_value("50")
WebDriverWait(driver, 20).until(EC.presence_of_element_located(
    (By.CSS_SELECTOR, '#table1 > tbody > tr:nth-child(50)')))

page_count = 1
page_total = driver.find_element_by_css_selector('.total-pages').text
logging.info('Total:' + page_total )

result = []

while True:
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    courses = soup.select('#table1 > tbody > tr')
    for course in courses:
        code = course.select_one('td:nth-child(6)').text
        course_name = course.select_one('td.expand.footable-first-column > a').text
        cred = course.select_one('td:nth-child(5)').text
        prof = course.select_one('td:nth-child(8)').text
        room = course.select_one('td:nth-child(9) > div > span:nth-child(4)').text + course.select_one('td:nth-child(9) > div > span:nth-child(5)').text
        days_list = driver.find_elements_by_css_selector('.ui-pillbox > ul > li.ui-state-highlight')
        days = ''
        for day in days_list:
            days += (day.text + ',')
        time = course.select_one('td:nth-child(9) > div > span:nth-child(2)').text.strip()
        data = [code, course_name, cred, prof, room, days, time]
        result.append(data)

    page_count += 1
    logging.info("{:.2f}".format((page_count / int(page_total)) * 100))
    if page_count < int(page_total):
        driver.find_element_by_css_selector('#searchResultsTable > div.bottom.ui-widget-header > div > button.paging-control.next.ltr.enabled').click()
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#searchResults')))
    else:
        break

col_name = ['Code', 'Course Name', 'Cred', 'Professor', 'Room', 'Days', 'Time']
northeastern = pd.DataFrame(result, columns=col_name)
northeastern.to_excel('./crawl_results/northeastern.xlsx')

