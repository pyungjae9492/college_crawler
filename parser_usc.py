from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import bs4
import time
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
driver = webdriver.Chrome('chromedriver.exe')
driver.implicitly_wait(3)
driver.get('https://classes.usc.edu/term-20213/')

# 웹이 전부 파싱되기를 기다렸다가 클릭
WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
    (By.CSS_SELECTOR, '#header > header > nav > select.term-select')))
term_select = Select(driver.find_element_by_css_selector('#header > header > nav > select.term-select'))
terms = driver.find_elements_by_css_selector('#header > header > nav > select.term-select > option')
del terms[0]

root = Tk()
root.title('USC Crawler')
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

term_select.select_by_visible_text(term)
WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
    (By.CSS_SELECTOR, '#sorter-classes > li:nth-child(2) > a')))

urls = []

a_tags = driver.find_elements_by_css_selector('#sortable-classes > li > a')

for a_tag in a_tags:
    urls.append(a_tag.get_attribute('href'))

count = 0
total = len(urls)
logging.info('Total:' + str(total))
result = []

print('크롤링을 시작합니다.')

progress = Tk()
progress.title('크롤링 진행률')
p_var2 = DoubleVar()
prog_label = Label(progress, text='크롤링 진행률')
prog_label.pack()
progressbar2 = ttk.Progressbar(progress, maximum=100, length=500, variable=p_var2)
progressbar2.pack()
btn = Button(progress, text='시작', command=lambda: crawl(driver=driver, count=count, total=total, result=result))
btn.pack()

def crawl(driver, count, total, result):
    for url in urls:
        driver.get(url)

        WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '#content-main > div.course-table')))
        if driver.find_elements_by_css_selector('#content-main > div.course-table > p.empty'):
            count += 1
            logging.info("{:.2f}".format((count / total) * 100))
            p_var2.set((count / total) * 100)
            progressbar2.update()
            continue
        driver.find_element_by_css_selector('#content-main > a.expand').click()
        WebDriverWait(driver, 60).until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, '.course-details')))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        courses = soup.select('.course-table > div.course-info.expanded')
        for course in courses:
            course_name = course.select_one('.course-id > h3 > a').text
            cred = course.select_one('.course-id > h3 > a > span.units').text
            sections = course.select('table > tbody > tr')
            del sections[0]
            for section in sections:
                if section.select_one('.section'):
                    code = section.select_one('.section').text
                else:
                    continue
                time = section.select_one('.time').text
                days = section.select_one('.days').text
                prof = section.select_one('.instructor').text
                room = section.select_one('.location').text
                data = [code, course_name, cred, prof, room, days, time]
                result.append(data)
        count += 1
        logging.info("{:.2f}".format((count / total) * 100))
        p_var2.set((count / total) * 100)
        progressbar2.update()
    progress.destroy()

progress.mainloop()

driver.quit()

col_name = ['Code', 'Course_Name', 'Credit', 'Professor', 'Room', 'Days', 'Time']
usc = pd.DataFrame(result, columns=col_name)
usc['Course_Name'] = usc.Course_Name.str.extract(r'(?<=\:\s)(.+)(?=\s\()')
usc['Credit'] = usc.Credit.str.extract(r'(?<=\()(.+)(?=\))')
usc.to_excel('./crawl_results/usc.xlsx')