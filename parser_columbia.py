from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import bs4
import time
from bs4 import BeautifulSoup
import pandas as pd
import logging
import openpyxl

def get_links():
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome('chromedriver.exe', options=options)
    driver.implicitly_wait(3)
    driver.get('https://doc.search.columbia.edu/classes/+?semes=20213')
    # 웹이 전부 파싱되기를 기다렸다가 클릭
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, '#search-results > li:nth-child(1) > div > h3 > a')))
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    data = []
    courses = soup.select('#search-results > li')
    for course in courses:
        link = course.select_one('div > h3 > a').get('ng-href')
        code = course.select_one('li > div > div:nth-child(3) > table > tbody > tr > td:nth-child(2)').text
        prof = course.select_one('div > div:nth-child(3) > table > tbody > tr > td:nth-child(4)').text.strip()
        course_name = course.select_one('div > h3 > a').text
        data.append([link, code, prof, course_name])
    driver.quit()
    return data


def get_content(link, code, prof, course_name):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome('chromedriver.exe')
    driver.implicitly_wait(3)
    driver.get(link)
    WebDriverWait(driver, 60).until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, '#col-right > table > tbody > tr:nth-child(3) > td:nth-child(2)')))
    second_row = driver.find_element_by_css_selector(
        '#col-right > table > tbody > tr:nth-child(4) > td:nth-child(1)').text
    if second_row == 'Day & Time\nLocation':
        cred = driver.find_element_by_css_selector(
            '#col-right > table > tbody > tr:nth-child(5) > td:nth-child(2)').text
        meetings = driver.find_element_by_css_selector(
            '#col-right > table > tbody > tr:nth-child(4) > td:nth-child(2)').text
        data = [code, course_name, cred, prof, meetings]
    else:
        cred = driver.find_element_by_css_selector(
            '#col-right > table > tbody > tr:nth-child(4) > td:nth-child(2)').text
        meetings = 'TBA'
        data = [code, course_name, cred, prof, meetings]
    driver.quit()
    return data


def to_excel(result):
    col_name = ['Code', 'Course Name', 'Cred', 'Professor', 'Meetings']
    columbia = pd.DataFrame(result, columns=col_name)
    columbia.to_excel('./crawl_results/columbia.xlsx')


if __name__ == '__main__':

    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

    data = get_links()
    test = [ data[0], data[1], data[2] ]
    total = len(data)
    counter = 0
    logging.info('total:' + str(total))
    result = []

    for i in test:
        result.append(get_content(i[0], i[1], i[2], i[3]))
        counter += 1
        logging.info("{:.2f}".format((counter / total) * 100))

    to_excel(result)
