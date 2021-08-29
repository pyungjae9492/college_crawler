from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import bs4
from time import sleep
from bs4 import BeautifulSoup
import pandas as pd
import logging
import openpyxl
from tkinter import *
import tkinter.ttk as ttk

# 완료!

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

options = webdriver.ChromeOptions()
options.add_argument('headless')
driver = webdriver.Chrome('chromedriver.exe', options=options)
driver.implicitly_wait(3)
driver.get(
    'https://nubanner.neu.edu/StudentRegistrationSsb/ssb/term/termSelection?mode=search')
# 웹이 전부 파싱되기를 기다렸다가 클릭
WebDriverWait(driver, 20).until(EC.presence_of_element_located(
    (By.CSS_SELECTOR, '#term-go')))
driver.find_element_by_css_selector('#s2id_txt_term > a').click()
terms = driver.find_elements_by_css_selector(
    '#select2-results-1 > li > div > div')

root = Tk()
root.title('Northeastern Crawler')
choice = StringVar()

def getTextInput():
    global term
    term = choice.get()
    root.destroy()

label = Label(root, text= 'Term을 골라주세요')
label.pack()
for i in terms:
    Radiobutton(root, text=i.text, padx=20, variable=choice, value=i.text).pack(anchor=W)
btnRead=Button(root, height=1, width=10, text="OK", 
                    command=getTextInput)
btnRead.pack()
root.mainloop()

term_selector = driver.find_element_by_css_selector('#s2id_autogen1_search')
term_selector.send_keys(term)
sleep(4)
driver.find_element_by_css_selector(
    '#select2-results-1 > li > div > div').click()
WebDriverWait(driver, 20).until(EC.presence_of_element_located(
    (By.CSS_SELECTOR, '#term-go')))
driver.find_element_by_css_selector('#term-go').click()
WebDriverWait(driver, 20).until(EC.presence_of_element_located(
    (By.CSS_SELECTOR, '#search-go')))
driver.find_element_by_css_selector('#search-go').click()
WebDriverWait(driver, 20).until(EC.presence_of_element_located(
    (By.CSS_SELECTOR, '.page-size-select')))
page_size_selector = Select(
    driver.find_element_by_css_selector('.page-size-select'))
page_size_selector.select_by_value("50")
WebDriverWait(driver, 20).until(EC.presence_of_element_located(
    (By.CSS_SELECTOR, '#table1 > tbody > tr:nth-child(50)')))

result = []
page_count = 1
page_total = driver.find_element_by_css_selector('.total-pages').text
logging.info('Total:' + page_total)

progress = Tk()
progress.title('크롤링 진행률')
p_var2 = DoubleVar()
prog_label = Label(progress, text='크롤링 진행률')
prog_label.pack()
progressbar2 = ttk.Progressbar(progress, maximum=100, length=150, variable=p_var2)
progressbar2.pack()
btn = Button(progress, text='시작', command=lambda: crawl(driver=driver, page_count=page_count, page_total=page_total, result=result))
btn.pack()
### 웹 긁어오기

def crawl(driver, page_count, page_total, result):
    while True:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        courses = soup.select('#table1 > tbody > tr')
        for course in courses:
            code = course.select_one('td:nth-child(6)').text
            course_name = course.select_one(
                'td.expand.footable-first-column > a').text
            cred = course.select_one('td:nth-child(5)').text
            prof = course.select_one('td:nth-child(8)').text
            meeting = course.select_one('td:nth-child(9)')
            room = course.select_one('td:nth-child(9) > div > span:nth-child(4)').text + course.select_one('td:nth-child(9) > div > span:nth-child(5)').text
            days_list = course.select(
                '.ui-pillbox > ul > li.ui-state-highlight')
            days = ''
            for day in days_list:
                days += (day.text + ',')
            time = course.select_one(
                'td:nth-child(9) > div > span:nth-child(2)').text.strip()
            data = [code, course_name, cred, prof, room, days, time]
            result.append(data)
        page_count += 1
        logging.info("{:.2f}".format((page_count / int(page_total)) * 100))
        p_var2.set((page_count / int(page_total)) * 100)
        progressbar2.update()
        if page_count == int(page_total):
            break
        WebDriverWait(driver, 30).until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, '#searchResultsTable > div.bottom.ui-widget-header > div > button.paging-control.next.ltr.enabled')))
        sleep(6)
        driver.find_element_by_css_selector(
            '#searchResultsTable > div.bottom.ui-widget-header > div > button.paging-control.next.ltr.enabled').click()
        WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, '#table1 > tbody > tr')))
    progress.destroy()

progress.mainloop()

col_name = ['Code', 'Course Name', 'Cred', 'Professor', 'Room', 'Days', 'Time']
northeastern = pd.DataFrame(result, columns=col_name)
northeastern['Room'] = northeastern['Room'].str.strip()
northeastern['Days'] = northeastern['Days'].str.slice(start=0, stop=-1)
northeastern.to_excel('./crawl_results/northeastern.xlsx')
