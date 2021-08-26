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

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

options = webdriver.ChromeOptions()
options.add_argument('headless')
driver = webdriver.Chrome(
    'chromedriver.exe', options=options)  # mac의 경우 chromedriver
driver.implicitly_wait(3)
driver.get('https://courses.my.harvard.edu/psp/courses/EMPLOYEE/EMPL/h/?tab=HU_CLASS_SEARCH&SearchReqJSON=%7B%22ExcludeBracketed%22%3Atrue%2C%22PageNumber%22%3A1%2C%22PageSize%22%3A%22%22%2C%22SortOrder%22%3A%5B%22IS_SCL_DESCR_IS_SCL_DESCRJ%22%5D%2C%22Facets%22%3A%5B%22IS_SCL_DESCR_IS_SCL_DESCRH%3A2021%20Fall%3ATerm%22%5D%2C%22Category%22%3A%22HU_SCL_SCHEDULED_BRACKETED_COURSES%22%2C%22SearchPropertiesInResults%22%3Atrue%2C%22FacetsInResults%22%3Atrue%2C%22SaveRecent%22%3Atrue%2C%22TopN%22%3A%22%22%2C%22SearchText%22%3A%22*%22%2C%22DeepLink%22%3Afalse%7D')

WebDriverWait(driver, 30).until(EC.presence_of_element_located(
    (By.CSS_SELECTOR, '#IS_SCL_ResultsPlaceholder > div:nth-child(1)')))
course_count = 0
course_total = driver.find_element_by_css_selector(
    '#IS_SCL_TotalHitCount').text
logging.info("Total:" + course_total)
result = []

driver.find_element_by_css_selector(
    '#IS_SCL_ResultsPlaceholder > div:nth-child(1)').click()
WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, '#lbContentMain')))

while True:
    course_name = driver.find_element_by_css_selector(
        '.isSCL_LBTop > div:nth-child(1) > h2').text
    code = driver.find_element_by_css_selector(
        '.isSCL_LBTop > div.isSCL_LBINS > ul > li:nth-child(1)').text
    if driver.find_element_by_css_selector('.isSCL_LBAttr > ul > li:nth-child(5) > span').text == 'Units:':
        cred = driver.find_element_by_css_selector(
            '.isSCL_LBAttr > ul > li:nth-child(5)').text
    else:
        cred = driver.find_element_by_css_selector(
            '.isSCL_LBAttr > ul > li:nth-child(4)').text
    prof = driver.find_element_by_css_selector(
        '.isSCL_LBTop > div:nth-child(1) > h3:nth-child(3)').text
    room = driver.find_element_by_css_selector(
        '.isSCL_LBTop > div.isSCL_LBMTG > div.isSCL_LBLOC').text
    days_list = driver.find_elements_by_css_selector(
        '.isSCL_LBTop > div.isSCL_LBMTG > div.isSCL_LBRBM.isSCL_SecCompMTG > ul > li.selected')
    days = ''
    if len(days_list) != 0:
        for day in days_list:
            days += (day.text + ' ')
    time = driver.find_element_by_css_selector(
        '.isSCL_LBTop > div.isSCL_LBMTG > div.isSCL_LBTime').text
    data = [code, course_name, cred, prof, room, days, time]
    result.append(data)
    course_count += 1
    logging.info("{:.2f}".format((course_count / int(course_total)) * 100))
    if course_count < int(course_total):
        driver.find_element_by_css_selector(
            '.isFSA_PrfHdr > a.isFSA_PrfHdrNext').click()
        WebDriverWait(driver, 30).until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, '.isFSA_PrfHdr > a.isFSA_PrfHdrNext')))
        continue
    break

col_name = ['Code', 'Course_Name', 'Credit',
            'Professor', 'Room', 'Days', 'Time']
harvard = pd.DataFrame(result, columns=col_name)
harvard['Code'] = harvard.Code.str.extract(r'(?<=Class Number:)(.+)')
harvard['Credit'] = harvard.Credit.str.extract(r'(?<=Units:)(.+)')
harvard['Days'] = harvard.Days.str.extract(r'(.+)(?=,)')
harvard.to_excel('./crawl_results/harvard.xlsx')
