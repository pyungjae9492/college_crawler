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

logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

options = webdriver.ChromeOptions()
options.add_argument('headless')
driver = webdriver.Chrome('chromedriver.exe') # mac의 경우 chromedriver
driver.implicitly_wait(4)
driver.get('https://courses.yale.edu/?srcdb=202103&stat=A,F')

term_select = Select(driver.find_element_by_css_selector('#crit-srcdb'))
terms = driver.find_elements_by_css_selector('#crit-srcdb > option')

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
    (By.CSS_SELECTOR, 'body > main > div.panel.panel--kind-results.panel--visible > div > div.panel__body > div:nth-child(1) > a')))

counter = 0
total = driver.find_element_by_css_selector('.panel__info-bar > div > strong').text
exceptions = 0
result = []
logging.info('total:' + total)
courses = driver.find_elements_by_css_selector('.result__link')

print('크롤링을 시작합니다.')

progress = Tk()
progress.title('크롤링 진행률')
p_var2 = DoubleVar()
prog_label = Label(progress, text='크롤링 진행률')
prog_label.pack()
progressbar2 = ttk.Progressbar(progress, maximum=100, length=500, variable=p_var2)
progressbar2.pack()
btn = Button(progress, text='시작', command=lambda: crawl(driver=driver, counter=counter, total=total, result=result))
btn.pack()

def crawl(driver, counter, total, result):
    for course in courses:
        course.click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.dtl-course-code')))
        sections = driver.find_elements_by_css_selector('.course-section--matched')
        section_num = 1
        for section in sections:
            if len(sections) == 1:
                pass
            else:
                driver.find_element_by_css_selector(f'.course-sections > a:nth-child({ section_num })').click()
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.dtl-course-code')))
            course_name = driver.find_element_by_css_selector('.detail-title').text
            code = driver.find_element_by_css_selector('.dtl-section').text
            cred = driver.find_element_by_css_selector('.detail-credit_html').text[0]
            if driver.find_elements_by_css_selector('.section--meeting_html > div'):
                room_time = driver.find_element_by_css_selector('.section--meeting_html > div').text
            else:
                room_time = 'TBA'
            if driver.find_elements_by_css_selector('.instructor-name'):
                prof = driver.find_element_by_css_selector('.instructor-name').text
            else:
                prof = 'TBA'
            data = [code, course_name, cred, prof, room_time]
            result.append(data)
            section_num += 1
            counter += 1
            logging.info("{:.2f}".format((counter / int(total)) * 100))
            p_var2.set((counter / int(total)) * 100)
            progressbar2.update()
        driver.find_element_by_css_selector('body > main > div.panel.panel--2x.panel--kind-details.panel--visible > div > div.panel__head > a.panel__back.icon-link').click()
        sleep(0.1)
        if counter > 40:
            break
    progress.destroy()

progress.mainloop()

driver.quit()
print(exceptions)
col_name=['Code', 'Course Name', 'Credit', 'Professor', 'Room_Time']
yale = pd.DataFrame(result, columns=col_name)
yale.to_excel('./crawl_results/yale.xlsx')




