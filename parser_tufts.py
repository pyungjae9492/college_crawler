from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import bs4
from bs4 import BeautifulSoup
from time import sleep
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


root = Tk()
root.title('Tufts Crawler')

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
driver.get(site_url)

# 웹이 전부 파싱되기를 기다렸다가 클릭
WebDriverWait(driver, 120).until(EC.presence_of_element_located(
    (By.CSS_SELECTOR, '#TFP_CLSSRCH_accordion > div:nth-child(2554) > a > span:nth-child(2)')))
sleep(1)
driver.find_element_by_css_selector(
    '#tfp_head_actions > div > div > label:nth-child(2) > input').click()


soup = BeautifulSoup(driver.page_source, 'html.parser')
every_courses = soup.select('#TFP_CLSSRCH_accordion > div')
total = len(every_courses)
logging.info("TOTAL " + str(total))
result = []
counter = 0
print('Starting Scrapying!')


progress = Tk()
progress.title('크롤링 진행률')
p_var2 = DoubleVar()
prog_label = Label(progress, text='크롤링 진행률')
prog_label.pack()
progressbar2 = ttk.Progressbar(progress, maximum=100, length=150, variable=p_var2)
progressbar2.pack()
btn = Button(progress, text='시작', command=lambda: crawl(every_courses=every_courses, counter=counter, total=total, result=result))
btn.pack()

def crawl(every_courses, counter, total, result):
    for course in every_courses:
        course_name = course.select_one('a > span:nth-child(2)').text.strip()
        sections = course.select(
            'div > div.tfp-sections > div > table > tbody > tr')
        for section in sections:
            code = section.select_one('td:nth-child(2)').text.strip()
            cred = section.select_one('td:nth-child(5)').text.strip()
            prof = section.select_one(
                'td:nth-child(4) > div > div.tfp-ins').text.strip()
            room = section.select_one(
                'td:nth-child(4) > div > div.tfp-loc').text.strip()
            time = section.select_one(
                'td:nth-child(4) > div > div.tfp-loc').text.strip()
            data = [code, course_name, cred, prof, room, time]
        counter += 1
        logging.info("{:.2f}".format((counter / total) * 100))
        p_var2.set((counter / total)*100)
        progressbar2.update()
        result.append(data)
    progress.destroy()

progress.mainloop()

col_name = ['Code', 'Course Name', 'Credit', 'Professor', 'Room', 'Time']
tufts = pd.DataFrame(result, columns=col_name)
tufts['Room'] = tufts.Room.str.extract(r'(?<=\n)(.+)')
tufts['Time'] = tufts.Time.str.extract(r'(.+)(?=\n)')
tufts.to_excel('./crawl_results/tufts.xlsx')
