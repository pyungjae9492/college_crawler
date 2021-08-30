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
driver = webdriver.Chrome('chromedriver.exe', options=options)
driver.implicitly_wait(3)
driver.get('http://oracle-www.dartmouth.edu/dart/groucho/timetable.main')
# 웹이 전부 파싱되기를 기다렸다가 클릭
WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
    (By.CSS_SELECTOR, '#content > table > tbody > tr:nth-child(3) > td > form > table:nth-child(23) > tbody > tr:nth-child(5) > td:nth-child(1) > input[type=submit]')))
driver.find_element_by_css_selector('#content > table > tbody > tr:nth-child(3) > td > form > table:nth-child(23) > tbody > tr:nth-child(5) > td:nth-child(1) > input[type=submit]').click()

terms = driver.find_elements_by_css_selector('#content > table:nth-child(1) > tbody > tr:nth-child(3) > td > form:nth-child(2) > table:nth-child(11) > tbody > tr > td:nth-child(2) > p')

root = Tk()
root.title('Dartmouth Crawler')
choice = IntVar()

def getTextInput():
    global term
    term = choice.get()
    root.destroy()

label = Label(root, text= 'Term을 골라주세요')
label.pack()
term_num = 1
for i in terms:
    Radiobutton(root, text=i.text, padx=20, variable=choice, value=term_num).pack(anchor=W)
    term_num +=1
btnRead=Button(root, height=1, width=10, text="OK", 
                    command=getTextInput)
btnRead.pack()
root.mainloop()

driver.find_element_by_css_selector(f'#term{term}').click()
driver.find_element_by_css_selector('#alldelivery').click()
driver.find_element_by_css_selector('#allsubjects').click()
driver.find_element_by_css_selector('#content > table:nth-child(3) > tbody > tr:nth-child(8) > td:nth-child(1) > input[type=submit]').click()
WebDriverWait(driver, 60).until(EC.presence_of_all_elements_located(
    (By.CSS_SELECTOR, '#content > table > tbody > tr:nth-child(3) > td > form > div > table > tbody > tr')))

soup = BeautifulSoup(driver.page_source, 'html.parser')
courses = soup.select('#content > table > tbody > tr:nth-child(3) > td > form > div > table > tbody > tr')
del courses[0]

driver.quit()

counter = 0
total = len(courses)
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
btn = Button(progress, text='시작', command=lambda: crawl(counter=counter, total=total, result=result))
btn.pack()

def crawl(counter, total, result):
    for course in courses:
        code = course.select('td')[1].text
        course_name = course.select('td')[6].text
        # cred = course.select_one('td:nth-child(2)').text -> 크레딧 정보 제공 안됨
        prof = course.select('td')[13].text
        room = course.select('td')[11].text + course.select('td')[12].text
        time = course.select('td')[10].text
        data = [code, course_name, prof, room, time]
        result.append(data)
        counter += 1
        logging.info("{:.2f}".format((counter / total) * 100))
        p_var2.set((counter / total)*100)
        progressbar2.update()
    progress.destroy()

progress.mainloop()

col_name = ['Code', 'Course Name', 'Professor', 'Room', 'Time']
dartmouth = pd.DataFrame(result, columns=col_name)
dartmouth.to_excel('./crawl_results/dartmouth.xlsx')

