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
import re

# 완료

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

options = webdriver.ChromeOptions()
options.add_argument('headless')
driver = webdriver.Chrome('chromedriver.exe')  # mac의 경우 chromedriver
driver.implicitly_wait(3)
driver.get('https://services.bc.edu/PublicCourseInfoSched/courseinfoschedResults!displayInput.action?authenticated=false&keyword=&presentTerm=2021SPRG&registrationTerm=2021FALL&termsString=2021SUMM%2C2021FALL&selectedTerm=2021FALL&selectedSort=&selectedSchool=6CSOM&selectedSubject=nullAll&selectedNumberRange=&selectedLevel=&selectedMeetingDay=&selectedMeetingTime=&selectedCourseStatus=&selectedCourseCredit=&canvasSearchLink=&personResponse=jd2F8Wjcdc86u6uFR5RHpF8rsH&googleSiteKey=6LdV2EYUAAAAACy8ROcSlHHznHJ64bn87jvDqwaf')



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
        course_raw = course.select_one('td:nth-child(1)').text
        course_name = course.select_one('.course-name').text
        if course.select_one('.instructors'):
            prof = course.select_one('.instructors').text
        else:
            prof = ''
        schedule = course.select_one('.schedule')
        week_list = schedule.select('.weekdisplay')
        if week_list:
            days1 = ''
            days1_list = week_list[0].select('.meet')
            for day in days1_list:
                days1 += (day.text + ' ')
            if schedule.select_one('.time'):
                time1 = schedule.select_one('.time').text
            else:
                time1 = ''
            if schedule.select_one('.location'):
                room1 = schedule.select_one('.location').text
            else:
                room1 = ''
            days2 = ''
            time2 = ''
            room2 = ''
            if len(week_list) == 2:
                days2_list = week_list[1].select('.meet')
                for day in days2_list:
                    days2 += (day.text + ' ')
                if schedule.select_one('.time'):
                    time2 = schedule.select_one('.time').text
                else:
                    time2 = ''
                if schedule.select_one('.location'):
                    room2 = schedule.select_one('.location').text
                else:
                    room2 = ''
            data = [course_raw, course_name, prof, days1, time1, room1, days2, time2, room2]
        else:
            days1 = 'TBA'
            time1 = 'TBA'
            room1 = 'TBA'
            days2 = ''
            time2 = ''
            room2 = ''
            
        data = [course_raw, course_name, prof, days1, time1, room1, days2, time2, room2]
        result.append(data)
        course_count += 1
        logging.info("{:.2f}".format((course_count / course_total) * 100))

    school_count += 1
    logging.info("{:.2f}".format((school_count / school_total) * 100))

driver.quit()

col_name = ['Course_Information', 'Course_Name', 'Professor', 'Days1', 'Time1', 'Room1', 'Days2', 'Time2', 'Room2']
bc = pd.DataFrame(result, columns=col_name)
bc['Code'] = bc.Course_Information.str.extract(r'(?<=\()(.+)(?=\))')
bc['Course_Name'] = bc.Course_Name.str.extract(r'^(.+)(?=\s\()')
bc['Credit'] = bc.Course_Information.str.extract(
    r'(?<=[cC][rR][eE][dD][iI][tT][sS]\:)([0-9]+)(?=\n)')
bc = bc[['Code', 'Course_Name', 'Credit', 'Professor', 'Days1', 'Time1', 'Room1', 'Days2', 'Time2', 'Room2']]
bc.to_excel('./crawl_results/bc.xlsx')
