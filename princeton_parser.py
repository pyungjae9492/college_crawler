from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import bs4
from bs4 import BeautifulSoup
from time import sleep
import pandas as pd
import logging
import openpyxl

logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

options = webdriver.ChromeOptions()
options.add_argument('headless')
driver = webdriver.Chrome('chromedriver.exe', chrome_options=options)
driver.implicitly_wait(3)
driver.get('https://registrar.princeton.edu/course-offerings?term=1222')

#웹이 전부 파싱되기를 기다렸다가 클릭
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#class-search > div.results > div:nth-child(3) > a:nth-child(5)')))
driver.find_element_by_css_selector('#class-search > div.results > div:nth-child(3) > a:nth-child(5)').click()

courses = driver.find_elements_by_css_selector('.class-info > div > a')
urls = []
for course in courses:
    urls.append(course.get_attribute('href'))

total = len(urls)
counter = 0
result = []
cred = 'Not Noticed'
for url in urls:
    driver.get(url)
    course_name = driver.find_element_by_css_selector('#course-details > div.container > div.row.row-title-container > h2').text
    prof = driver.find_element_by_css_selector('#course-details > div.container > div.row.row-content-container > div.sidebar.col-md-4.col-lg-3 > div > div.instructors > ul > li').text
    rows = driver.find_elements_by_css_selector('#course-details > div.container > div.row.row-schedule-container > div > section > table > tbody > tr')
    for row in rows:
        code = driver.find_element_by_css_selector('.class-number').text
        meetings = driver.find_element_by_css_selector('.class-meetings').text
        data = [code, course_name, cred, prof, meetings]
    counter += 1
    logging.info("{:.2f}".format((counter / total) * 100))
    result.append(data)
    
col_name=['Code', 'Course Name', 'Credit', 'Professor', 'Meetings']
princeton = pd.DataFrame(result, columns=col_name)
# tufts['Room'] = tufts['Room'].str.findall(pat='\n.+')
# tufts['Time'] = tufts['Time'].str.findall(pat='.+\n')
princeton.to_excel('princeton.xlsx')
