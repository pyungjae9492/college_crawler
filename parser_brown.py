from requests.api import get
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import bs4
from bs4 import BeautifulSoup
from time import sleep
import pandas as pd
import logging
import openpyxl
from tkinter import *
import tkinter.ttk as ttk

# 완료

logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

options = webdriver.ChromeOptions()
options.add_argument('headless')
driver = webdriver.Chrome('chromedriver.exe', options=options) # mac의 경우 chromedriver
driver.implicitly_wait(3)
driver.get('https://cab.brown.edu/')

term_select = Select(
    driver.find_element_by_css_selector('#crit-srcdb'))
term_options = driver.find_elements_by_css_selector(
    '#crit-srcdb > option')

root = Tk()
root.title('Brown Crawler')
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

counter = 0
total = 0
result = []
values = ['Half Credit', 'Full Credit', 'Double Credit']

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
    for value in values:
        select = Select(driver.find_element_by_id('crit-hours'))
        select.select_by_visible_text(value)
        sleep(2)
        driver.find_element_by_css_selector('#search-button-sticky').click()
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.result__link')))
        total += int(driver.find_element_by_css_selector('.panel__info-bar > div > strong').text)
        logging.info('total:' + str(total))
        courses = driver.find_elements_by_css_selector('.result__link')
        for course in courses:
            course.click()
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.dtl-course-code')))
            sections = driver.find_elements_by_css_selector('.course-section')
            section_num = 2
            if len(sections) == 1:
                course_name = driver.find_element_by_css_selector('.detail-title').text
                code = driver.find_element_by_css_selector('.dtl-section').text
                try:
                    room_time = driver.find_element_by_css_selector('.section--meeting_html > div').text
                except:
                    room_time = 'TBA'
                prof = driver.find_element_by_css_selector('.instructor-detail > div > h4').text
                data = [code, course_name, value, prof, room_time]
                result.append(data)
            else:
                try:
                    for section in sections:
                        driver.find_element_by_css_selector(f'.course-sections > a:nth-child({ section_num })').click()
                        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.dtl-course-code')))
                        course_name = driver.find_element_by_css_selector('.detail-title').text
                        code = driver.find_element_by_css_selector('.dtl-section').text
                        try:
                            room_time = driver.find_element_by_css_selector('.section--meeting_html > div').text
                        except:
                            room_time = 'TBA'
                        prof = driver.find_element_by_css_selector('.instructor-detail > div > h4').text
                        if value == 'Half Credit':
                            value = 0.5
                        elif value == 'Full Credit':
                            value = 1
                        else:
                            value = 2
                        data = [code, course_name, value, prof, room_time]
                        result.append(data)
                        section_num += 1
                except:
                    pass        
            driver.find_element_by_css_selector('body > main > div.panel.panel--2x.panel--kind-details.panel--visible > div > div.panel__head > a.panel__back.icon-link').click()
            sleep(0.3)
            counter += 1
            logging.info("{:.2f}".format((counter / total) * 100))
            p_var2.set((counter / total)*100)
            progressbar2.update()
        driver.find_element_by_css_selector('body > main > div.panel.panel--kind-results.panel--visible > div > div.panel__head > a.panel__back.icon-link').click()
        sleep(2)
    progress.destroy()

progress.mainloop()

col_name=['Code', 'Course Name', 'Credit', 'Professor', 'Room_Time']
brown = pd.DataFrame(result, columns=col_name)
brown.to_excel('./crawl_results/brown.xlsx')
