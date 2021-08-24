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

# 완료

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


def wellesley_crawl():
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(
        'chromedriver.exe', options=options)  # mac의 경우 chromedriver
    driver.implicitly_wait(3)
    driver.get('https://courses.wellesley.edu/')

    # 로깅을 위한 변수
    count = 0
    # 최종 결과물 리스트
    result = []

    every_courses = driver.find_elements_by_css_selector(
        '#course_listing > section > div > a')
    total = every_courses.__len__()
    logging.info("TOTAL " + str(total))

    # 클릭하고 해당 과목 크롤링
    for i in every_courses:
        i.click()
        WebDriverWait(driver, 5).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, f'#data_{ count } > div')))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        code = soup.select_one(
            f'#data_{ count } > div.coursedetail > div:nth-child(2)').text[5:10]
        course_name = soup.select_one(f'#course_listing > section:nth-child({ count + 3}) > div > a > div.coursename_big > p').text
        credit = soup.select_one(
            f'#data_{ count } > div.coursedetail > div:nth-child(2)').text[26:27]
        prof = soup.select_one(f'#data_{ count } > a')
        location = soup.select_one(
            f'#data_{ count } > div.coursedetail.col-xs-12 > div:nth-child(3) > a')
        time = soup.select_one(
            f'#data_{ count } > div.coursedetail.col-xs-12 > div:nth-child(3)')
        if prof:
            prof = prof.text
        else:
            prof = 'Not Noticed'
        if location:
            location = location.text
        else:
            location = 'Not Noticed'
        if time:
            time = time.text
        else:
            time = 'Not Noticed'
        data = [code, course_name, credit, prof, location, time]
        # 진행 상황 로깅
        count += 1
        logging.info("{:.2f}".format((count / total) * 100))

        result.append(data)

    driver.quit()
    # 2차원 배열 -> .xlsx
    col_name = ['Code', 'Course Name', 'Credit', 'Professor', 'Room', 'Time']
    wellesley = pd.DataFrame(result, columns=col_name)
    wellesley['Time'] = wellesley.Time.str.extract(
        r'([A-Z]+\s\S\s[0-9]+\:[0-9]+\s[A-Z]+\s\S\s[0-9]+\:[0-9]+\s[A-Z]+)')
    wellesley.to_excel('./crawl_results/wellesley.xlsx')


wellesley_crawl()
