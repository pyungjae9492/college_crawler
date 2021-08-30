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
from tkinter import *
import tkinter.ttk as ttk
#완료! (날짜랑 장소가 2개인 것은 어떻게 할까?)

def get_links(site_url):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome('chromedriver.exe', options=options)
    driver.implicitly_wait(3)
    driver.get(site_url)
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
    col_name = ['Code', 'Course_Name', 'Professor', 'Meetings']
    princeton = pd.DataFrame(result, columns=col_name)
    princeton.to_excel('./crawl_results/princeton.xlsx')


if __name__ == '__main__':

    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')
    
    root = Tk()
    root.title('Princeton Crawler')

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

    links_names_codes = get_links(site_url)
    total = len(links_names_codes)
    counter = 0
    logging.info('total:' + str(total))
    result = []

    print('크롤링을 시작합니다.')

    progress = Tk()
    progress.title('크롤링 진행률')
    p_var2 = DoubleVar()
    prog_label = Label(progress, text='크롤링 진행률')
    prog_label.pack()
    progressbar2 = ttk.Progressbar(progress, maximum=100, length=500, variable=p_var2)
    progressbar2.pack()
    btn = Button(progress, text='시작', command=lambda: crawl(counter=counter, total=total, result=result))
    btn.pack()

    def crawl(counter, total, result):
        for i in links_names_codes:
            result.append(get_content(i[0], i[1], i[2]))
            counter += 1
            logging.info("{:.2f}".format((counter / total) * 100))
            p_var2.set((counter / total)*100)
            progressbar2.update()
        to_excel(result)
        progress.destroy()
    progress.mainloop()
