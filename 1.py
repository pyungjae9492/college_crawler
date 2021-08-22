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

def wellesley_crawl():
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome('chromedriver.exe', chrome_options=options) # mac의 경우 chromedriver
    driver.implicitly_wait(3)
    driver.get('https://courses.wellesley.edu/')

    #로깅을 위한 변수
    count = 0
    #최종 결과물 리스트
    result = []

    every_courses = driver.find_elements_by_css_selector('#course_listing > section > div > a')
    total = every_courses.__len__()
    logging.info("TOTAL " + str(total))

    click_count = 0
    #클릭하고 해당 과목 크롤링
    for i in every_courses:
        i.click()
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    courses = soup.select('.courseitem')
    for course in courses:    
        code_cred = course.select_one('.coursedetail > div:nth-child(2)')
        course_name = course.select_one('.coursename_big > p').text
        data = [code_cred, course_name]
        #비어 있을 가능성이 있는 정보들
        prof = course.select_one('a')
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
            data.append(time.text)
        else:
            data.append('Not Noticed')

        #진행 상황 로깅
        count += 1
        logging.info("{:.2f}".format((count / total) * 100))

        result.append(data)

    #2차원 배열 -> .xlsx    
    col_name=['Code_Cred', 'Course Name', 'Professor', 'Room', 'Time']
    wellesley = pd.DataFrame(result, columns=col_name)
    wellesley['Time'] = wellesley['Time'].str.findall(pat='[A-Z]+\s\S\s[0-9]+\:[0-9]+\s[A-Z]+\s\S\s[0-9]+\:[0-9]+\s[A-Z]+')
    wellesley['Code'] = wellesley['Code_Cred'].str.slice(5,10)
    wellesley['Credit'] = wellesley['Code_Cred'].str.slice(26,27)
    wellesley.to_excel('./crawl_results/wellesley1.xlsx')

wellesley_crawl()
