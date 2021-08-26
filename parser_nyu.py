from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import bs4
from time import sleep
from bs4 import BeautifulSoup
import pandas as pd
import logging
import openpyxl
import requests

# 완료!
# search-options > div:nth-child(6) > button

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

# options = webdriver.ChromeOptions()
# options.add_argument('headless')
# driver = webdriver.Chrome('chromedriver.exe')
# driver.implicitly_wait(3)
# driver.get(
#     'https://m.albert.nyu.edu/app/catalog/classSearch/1218')

# WebDriverWait(driver, 20).until(EC.presence_of_element_located(
#     (By.CSS_SELECTOR, '#search-acad-group')))

# urls = []

# driver.find_element_by_css_selector('.search-check').click()
# college_select = Select(
#     driver.find_element_by_css_selector('#search-acad-group'))
# college_options = driver.find_elements_by_css_selector(
#     '#search-acad-group > option')
# del college_options[0]

# for college_option in college_options:
#     college_select.select_by_value(college_option.get_attribute('value'))
#     subject_select = Select(driver.find_element_by_css_selector('#subject'))
#     subject_options = driver.find_elements_by_css_selector('#subject > option.option-subject')

#     for subject_option in subject_options:
#         subject_select.select_by_value(subject_option.get_attribute('value'))
#         driver.find_element_by_css_selector('#buttonSearch').click()

#         try:
#             WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#search-results > a')))
#         except:
#             continue

#         a_tags = driver.find_elements_by_css_selector('#search-results > a')

#         for a_tag in a_tags:
#             urls.append(a_tag.get_attribute('href'))

# driver.quit()
# print('url crawling done!')
# url_data = [urls]
# nyu_urls = pd.DataFrame(url_data)
# nyu_urls.to_excel('./crawl_results/nyu_urls.xlsx')

urls = pd.read_excel('./crawl_results/nyu_urls.xlsx')
urls = urls.values.tolist()
urls = urls[0]
del urls[0]


result = []
count = 0
total = len(urls)
logging.info('Total:' + str(total))



for url in urls:
    req = requests.get(url)
    html = req.text
    soup = BeautifulSoup(html, 'html.parser')
    code = soup.select_one('body > section > section > div:nth-child(4) > div.pull-right > div').text
    course_name = soup.select_one('body > section > section > div:nth-child(1)').text.strip()
    cred = soup.select_one('body > section > section > div:nth-child(6) > div.pull-right > div').text
    rows = soup.select('div.section-content.clearfix')
    data = [code, course_name, cred]
    index = 0
    for row in rows:
        if row.select_one('.strong').text == 'Instructor(s)':
            data.append(row.select_one('.pull-right').text)
        del rows[index]
    data.append(rows[0].select_one('.pull-right > div').text)
    data.append(rows[2].select_one('.pull-right').text)
    result.append(data)
    count += 1
    logging.info("{:.2f}".format((count / total) * 100))
    if count > 15:
        break

# col_name = ['Code', 'Course Name', 'Cred', 'Professor', 'Room', 'Time']
nyu = pd.DataFrame(result)
nyu.to_excel('./crawl_results/nyu.xlsx')
