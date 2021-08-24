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
    driver.get('https://registrar.princeton.edu/course-offerings?term=1222')
    # 웹이 전부 파싱되기를 기다렸다가 클릭
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, '#class-search > div.results > div:nth-child(3) > a:nth-child(5)')))
    driver.find_element_by_css_selector(
        '#class-search > div.results > div:nth-child(3) > a:nth-child(5)').click()
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    courses = soup.select(
        '#class-search > div.results > section > table > tbody > tr')
    links_names_codes = []
    for course in courses:
        link = 'https://registrar.princeton.edu' + \
            course.select_one('.class-info > div > a').get('href')
        name = course.select_one('.class-info > div > a').text
        code = course.select_one('.class-info > div > small').text
        data = [link, name, code]
        links_names_codes.append(data)
    driver.quit()
    return links_names_codes


def get_content(link, course_name, code):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome('chromedriver.exe', options=options)
    driver.implicitly_wait(3)
    driver.get(link)
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, '#course-details > div.container > div.row.row-title-container > h2')))
    prof = driver.find_element_by_css_selector('.instructors > ul').text
    meetings = driver.find_element_by_css_selector('.class-meetings').text
    data = [code, course_name, prof, meetings]
    driver.quit()
    return data


def to_excel(result):
    col_name = ['Code', 'Course Name', 'Professor', 'Meetings']
    princeton = pd.DataFrame(result, columns=col_name)
    princeton.to_excel('./crawl_results/princeton.xlsx')


if __name__ == '__main__':

    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

    links_names_codes = get_links()
    total = len(links_names_codes)
    counter = 0
    logging.info('total:' + str(total))
    result = []

    for i in links_names_codes:
        result.append(get_content(i[0], i[1], i[2]))
        counter += 1
        logging.info("{:.2f}".format((counter / total) * 100))

    to_excel(result)
