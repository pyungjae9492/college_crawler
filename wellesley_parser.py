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

logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

options = webdriver.ChromeOptions()
options.add_argument('headless')
driver = webdriver.Chrome('chromedriver.exe', chrome_options=options) # mac의 경우 chromedriver
driver.implicitly_wait(3)
driver.get('https://courses.wellesley.edu/')

count = 0
result = []
every_courses = driver.find_elements_by_css_selector('#course_listing > section > div > a')
total = every_courses.__len__()
logging.info("TOTAL " + str(total))
for i in every_courses:
    i.click()
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#data_{} > div'.format(count))))
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    code = soup.select_one('#data_{} > div.coursedetail > div:nth-child(2)'.format(count)).text[5:10]
    course_name = soup.select_one('.coursename_big > p'.format(count)).text
    credit = soup.select_one('#data_{} > div.coursedetail > div:nth-child(2)'.format(count)).text[26:27]
    data = [code, course_name, credit]
    #비어 있을 가능성이 있는 정보들
    prof = soup.select_one('#data_{} > a'.format(count))
    location = soup.select_one('#data_{} > div.coursedetail.col-xs-12 > div:nth-child(3) > a'.format(count))
    time = soup.select_one('#data_{} > div.coursedetail.col-xs-12 > div:nth-child(3)'.format(count))
    if prof:
        data.append(prof.text)
    else:
        data.append('Not Noticed')
    if location:
        data.append(location.text)
    else:
        data.append('Not Noticed')
    if time:
        data.append(time.text[17:40])
    else:
        data.append('Not Noticed')
    count += 1
    logging.info("{:.2f}".format((count / total) * 100))
    result.append(data)

col_name=['Code', 'Course Name', 'Credit', 'Professor', 'Room', 'Time']
wellesley = pd.DataFrame(result, columns=col_name)
wellesley.to_excel('wellesley.xlsx')
