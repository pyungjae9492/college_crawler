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

# 완료

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

options = webdriver.ChromeOptions()
options.add_argument('headless')
driver = webdriver.Chrome(
    'chromedriver.exe', options=options)  # mac의 경우 chromedriver
driver.implicitly_wait(3)
driver.get('https://services.bc.edu/PublicCourseInfoSched/courseinfoschedResults!displayInput.action?authenticated=false&keyword=&presentTerm=2021SPRG&registrationTerm=2021FALL&termsString=2021SUMM%2C2021FALL&selectedTerm=2021FALL&selectedSort=default&selectedSchool=6CSOM&selectedSubject=nullAll&selectedNumberRange=All&selectedLevel=&selectedMeetingDay=All&selectedMeetingTime=All&selectedCourseStatus=All&selectedCourseCredit=All&canvasSearchLink=&personResponse=8dRFz5dHGWpnu6zWplj5dn8csF&googleSiteKey=6LdV2EYUAAAAACy8ROcSlHHznHJ64bn87jvDqwaf')

exceptions = 0
result = []

select_options = driver.find_elements_by_css_selector(
    '#school > ul > li > input')
school_count = 0
school_total = len(select_options)

for select_option in select_options:
    driver.find_element_by_css_selector(
        f'#selectedSchool-{ school_count + 1 }').click()
    driver.find_element_by_css_selector('#search').click()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, '#resultTableBody')))
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    courses = soup.select('.course')
    course_count = 0
    course_total = len(courses)

    for course in courses:
        course_information = course.select_one('td:nth-child(1)').text
        schedule = course.select_one('td:nth-child(2)').text
        data = [course_information, schedule]
        result.append(data)
        course_count += 1
        logging.info("{:.2f}".format((course_count / course_total) * 100))

    school_count += 1
    logging.info("{:.2f}".format((school_count / school_total) * 100))

driver.quit()

col_name = ['Course_Information', 'Schedule']
bc = pd.DataFrame(result, columns=col_name)
bc['Code'] = bc.Course_Information.str.extract(r'(?<=\()(.+)(?=\))')
bc['Course_Name'] = bc.Course_Information.str.extract(r'^.+(?=\s\()')
bc['Credit'] = bc.Course_Information.str.extract(
    r'(?<=[cC][rR][eE][dD][iI][tT][sS]\:)[0-9]+(?=\n)')
bc['Professor'] = bc.Course_Information.str.extract(r'')
bc['Course_Name'] = bc.Course_Information.str.extract(r'')
bc['Course_Name'] = bc.Course_Information.str.extract(r'')
bc.to_excel('./crawl_results/bc.xlsx')
