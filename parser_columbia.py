from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import bs4
from time import sleep
from bs4 import BeautifulSoup
import pandas as pd
import logging
import openpyxl
from tkinter import *
import tkinter.ttk as ttk

def get_links(driver, site_url):
    
    # https://doc.search.columbia.edu/classes/+?semes=20213
    driver.get(site_url)

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
    return data


def get_content(link, code, prof, course_name, driver):
    driver.get(link)
    sleep(1.5)
    
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

    root = Tk()
    root.title('Columbia Crawler')

    def getTextInput():
        global site_url
        site_url = text.get(1.0, END+"-1c")
        root.destroy()

    label = Label(root, text= '긁어올 Url을 입력해주세요')
    label.pack()
    text = Text(root, height=10, )
    text.pack()
    btnRead=Button(root, height=1, width=10, text="OK", 
                        command=getTextInput)
    btnRead.pack()
    root.mainloop()

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome('chromedriver.exe', options=options)
    driver.implicitly_wait(3)

    data = get_links(driver, site_url)
    total = len(data)
    counter = 0
    logging.info('total:' + str(total))
    result = []

    progress = Tk()
    progress.title('크롤링 진행률')
    p_var2 = DoubleVar()
    prog_label = Label(progress, text='크롤링 진행률')
    prog_label.pack()
    progressbar2 = ttk.Progressbar(progress, maximum=100, length=150, variable=p_var2)
    progressbar2.pack()
    btn = Button(progress, text='시작', command=lambda: crawl(counter=counter, total=total, result=result))
    btn.pack()

    def crawl(counter, total, result):
        for i in data:
            result.append(get_content(i[0], i[1], i[2], i[3], driver))
            counter += 1
            logging.info("{:.2f}".format((counter / total) * 100))
            p_var2.set((counter / total)*100)
            progressbar2.update()
        to_excel(result)
        progress.destroy()

    progress.mainloop()

    
