from requests.api import get
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
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
driver = webdriver.Chrome('chromedriver.exe', options=options) # mac의 경우 chromedriver
driver.implicitly_wait(3)
driver.get('https://courses.yale.edu/?srcdb=202103&stat=A,F')

counter = 0
total = driver.find_element_by_css_selector('.panel__info-bar > div > strong').text
exceptions = 0
result = []
logging.info('total:' + total)
courses = driver.find_elements_by_css_selector('.result__link')
for course in courses:
    course.click()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.dtl-course-code')))
    sections = driver.find_elements_by_css_selector('.course-section--matched')
    section_num = 1
    exceptions = 0
    for section in sections:
        if len(sections) == 1:
            pass
        else:
            try:
                driver.find_element_by_css_selector(f'.course-sections > a:nth-child({ section_num })').click()
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.dtl-course-code')))
            except:
                exceptions += 1
                continue
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        content = soup.select_one('body > main > div.panel.panel--2x.panel--kind-details.panel--visible > div > div.panel__body')
        course_name = content.select_one('.detail-title').text
        code = content.select_one('.dtl-section').text
        cred = content.select_one('.detail-credit_html').text[0]
        try:
            room_time = content.select_one('.section--meeting_html > div').text
        except:
            room_time = 'TBA'
        try:
            prof = content.select_one('.instructor-name').text
        except:
            prof = 'TBA'
        data = [code, course_name, cred, prof, room_time]
        result.append(data)
        section_num += 1
    driver.find_element_by_css_selector('body > main > div.panel.panel--2x.panel--kind-details.panel--visible > div > div.panel__head > a.panel__back.icon-link').click()
    sleep(0.1)
    counter += 1
    logging.info("{:.2f}".format((counter / int(total)) * 100))

driver.quit()
print(exceptions)
col_name=['Code', 'Course Name', 'Credit', 'Professor', 'Room_Time']
yale = pd.DataFrame(result, columns=col_name)
yale.to_excel('./crawl_results/yale.xlsx')




