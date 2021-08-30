from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import bs4
from bs4 import BeautifulSoup
import time
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

root = Tk()
root.title('Harvard Crawler')
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
driver = webdriver.Chrome(
    'chromedriver.exe', options=options)  # mac의 경우 chromedriver
driver.implicitly_wait(3)
driver.get(site_url)
WebDriverWait(driver, 30).until(EC.presence_of_element_located(
    (By.CSS_SELECTOR, '#IS_SCL_ResultsPlaceholder > div:nth-child(1)')))
course_count = 0
course_total = driver.find_element_by_css_selector(
    '#IS_SCL_TotalHitCount').text
logging.info("Total:" + course_total)
result = []

driver.find_element_by_css_selector(
    '#IS_SCL_ResultsPlaceholder > div:nth-child(1)').click()
WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, '#lbContentMain')))

print('크롤링을 시작합니다.')

progress = Tk()
progress.title('크롤링 진행률')
p_var2 = DoubleVar()
prog_label = Label(progress, text='크롤링 진행률')
prog_label.pack()
progressbar2 = ttk.Progressbar(progress, maximum=100, length=500, variable=p_var2)
progressbar2.pack()
btn = Button(progress, text='시작', command=lambda: crawl(course_count=course_count, course_total=course_total, result=result))
btn.pack()

def crawl(course_count, course_total, result):
    while True:
        sleep(0.1)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        course_name = soup.select_one(
            '.isSCL_LBTop > div:nth-child(1) > h2').text
        code = soup.select_one(
            '.isSCL_LBTop > div.isSCL_LBINS > ul > li:nth-child(1)').text
        if soup.select_one('.isSCL_LBAttr > ul > li:nth-child(5) > span').text == 'Units:':
            cred = soup.select_one(
                '.isSCL_LBAttr > ul > li:nth-child(5)').text
        else:
            cred = soup.select_one(
                '.isSCL_LBAttr > ul > li:nth-child(4)').text
        prof = soup.select_one(
            '.isSCL_LBTop > div:nth-child(1) > h3:nth-child(3)').text
        room = soup.select_one(
            '.isSCL_LBTop > div.isSCL_LBMTG > div.isSCL_LBLOC').text
        days_list = soup.select(
            '.isSCL_LBTop > div.isSCL_LBMTG > div.isSCL_LBRBM.isSCL_SecCompMTG > ul > li.selected')
        days = ''
        if len(days_list) != 0:
            for day in days_list:
                days += (day.text + ' ')
        time = soup.select_one(
            '.isSCL_LBTop > div.isSCL_LBMTG > div.isSCL_LBTime').text
        data = [code, course_name, cred, prof, room, days, time]
        result.append(data)
        course_count += 1
        logging.info("{:.2f}".format((course_count / int(course_total)) * 100))
        p_var2.set((course_count / int(course_total))*100)
        progressbar2.update()
        if course_count < int(course_total):
            driver.find_element_by_css_selector(
                '.isFSA_PrfHdr > a.isFSA_PrfHdrNext').click()
            try:
                WebDriverWait(driver, 30).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '.isSCL_LBTop > div:nth-child(1) > h2')))
            except:
                pass
            continue
        progress.destroy()
        break

progress.mainloop()

col_name = ['Code', 'Course_Name', 'Credit',
            'Professor', 'Room', 'Days', 'Time']
harvard = pd.DataFrame(result, columns=col_name)
harvard['Code'] = harvard.Code.str.extract(r'(?<=Class Number:)(.+)')
harvard['Credit'] = harvard.Credit.str.extract(r'(?<=Units:)(.+)')
harvard['Days'] = harvard.Days.str.extract(r'(.+)(?=,)')
harvard['Room'] = harvard.Room.str.extract(r'(.+)(?=\n)')
harvard.to_excel('./crawl_results/harvard.xlsx')
