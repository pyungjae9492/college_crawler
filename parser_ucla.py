from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import bs4
import time
from bs4 import BeautifulSoup
import pandas as pd
import logging
import openpyxl
from tkinter import *
import tkinter.ttk as ttk

logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

options = webdriver.ChromeOptions()
options.add_argument('headless')
driver = webdriver.Chrome('chromedriver.exe')
driver.implicitly_wait(3)
driver.get('https://sa.ucla.edu/ro/public/soc')
# 웹이 전부 파싱되기를 기다렸다가 클릭
WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#searchbuttons > button.btn.btn-default.form-button.submit-button')))
term_select = driver.find_element_by_css_selector('#div_subject')
term_options = driver.find_elements_by_css_selector('#dropdownitems > div')

root = Tk()
root.title('Carnegiemellon Crawler')
choice = StringVar()

def getTextInput():
    global term
    term = choice.get()
    root.destroy()

label = Label(root, text= 'Term을 골라주세요')
label.pack()

for i in term_options:
    Radiobutton(root, text=i.text, padx=20, variable=choice, value=i.text).pack(anchor=W)
btnRead=Button(root, height=1, width=10, text="OK", 
                    command=getTextInput)
btnRead.pack()
root.mainloop()

term_select.select_by_visible_text(term)

driver.find_element_by_css_selector('#searchbuttons > button.btn.btn-default.form-button.submit-button').click()
WebDriverWait(driver, 30).until(EC.presence_of_element_located(
    (By.CSS_SELECTOR, '.table > tbody > tr')))
soup = BeautifulSoup(driver.page_source, 'html.parser')
courses = soup.select('.table > tbody > tr')

total = len(courses)
counter = 0
logging.info('total:' + str(total))
result = []

driver.quit()
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
    for course in courses:
        code = course.select_one('td:nth-child(1)').text.strip()
        course_name = course.select_one('td:nth-child(2)').text.strip()
        cred = course.select_one('td:nth-child(3)').text.strip()
        sec = course.select_one('td:nth-child(4)').text.strip()
        days = course.select_one('td:nth-child(6)').text.strip()
        time_begin = course.select_one('td:nth-child(7)').text.strip()
        time_end = course.select_one('td:nth-child(8)').text.strip()
        room = course.select_one('td:nth-child(10)').text.strip()
        prof = course.select_one('td:nth-child(12)').text.strip()
        data = [code, course_name, cred, sec, prof, room, days, time_begin, time_end]
        result.append(data)
        counter += 1
        logging.info("{:.2f}".format((counter / total) * 100))
        p_var2.set((counter / total)*100)
        progressbar2.update()
    progress.destroy()

progress.mainloop()

col_name = ['Code', 'Course_Name', 'Credit', 'Section', 'Professor', 'Room', 'Days', 'Time_Begin', 'Time_End']
carnegiemelon = pd.DataFrame(result, columns=col_name)
carnegiemelon.to_excel('./crawl_results/carnegiemelon.xlsx')


