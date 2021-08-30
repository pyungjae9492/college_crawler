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

root = Tk()
root.title('UCBerkeley Crawler')
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
WebDriverWait(driver, 20).until(EC.presence_of_element_located(
    (By.CSS_SELECTOR, '#edit-submit')))

result = []
counter = 0
total = int(driver.find_element_by_css_selector('.current-search-item-number-of-items').text[13:17])
logging.info('Total:' + str(total))

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
### 웹 긁어오기

def crawl(driver, counter, total, result):
    while True:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        courses = soup.select('body > div:nth-child(2) > div.layout-center.layout-3col.layout-swap > main > div > div > ol > li')
        for course in courses:
            code = course.select_one('.ls-section-number').text
            course_name = course.select_one(
                '.ls-course-title').text
            cred = course.select_one('.ls-details-units').text
            try:
                prof = course.select_one('ls-instructors > span:nth-child(2)').text
            except:
                prof = 'Not Noticed'
            try:
                room = course.select_one('.ls-location > a').text
            except:
                room = 'Not Noticed'
            try:
                days = course.select_one('.ls-days').text
            except:
                days = 'Not Noticed'
            try:
                time = course.select_one('.ls-time').text
            except:
                time = 'Not Noticed'
            data = [code, course_name, cred, prof, room, days, time]
            result.append(data)
            counter += 1
            logging.info("{:.2f}".format((counter / int(total)) * 100))
            p_var2.set((counter / int(total)) * 100)
            progressbar2.update()
        if counter == int(total):
            break
        WebDriverWait(driver, 30).until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'body > div:nth-child(2) > div.layout-center.layout-3col.layout-swap > main > div > div > div.item-list > ul > li.pager-next > a')))
        driver.find_element_by_css_selector(
            'body > div:nth-child(2) > div.layout-center.layout-3col.layout-swap > main > div > div > div.item-list > ul > li.pager-next > a').click()
        WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, 'body > div:nth-child(2) > div.layout-center.layout-3col.layout-swap > main > div > div > ol > li > div > div > div.hbr > div.col-wrapper > div.left-col > h2')))
    progress.destroy()

progress.mainloop()

col_name = ['Code', 'Course Name', 'Cred', 'Professor', 'Room', 'Days', 'Time']
ucberkeley = pd.DataFrame(result, columns=col_name)
ucberkeley.to_excel('./crawl_results/ucberkeley.xlsx')
