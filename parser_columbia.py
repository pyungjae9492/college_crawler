from tkinter.font import ROMAN
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import bs4
from time import sleep
from bs4 import BeautifulSoup
import pandas as pd
import logging
import openpyxl
from tkinter import *
import tkinter.ttk as ttk

def to_excel(result):
    col_name = ['Code', 'Course_Name', 'Credit', 'Professor', 'Meetings']
    columbia = pd.DataFrame(result, columns=col_name)
    columbia['Code'] = columbia.Code.str.extract(
    r'(?<=/)(\d+$)')
    columbia['Days'] = columbia.Meetings.str.extract(
    r'(^.+?)(?=\s\d)')
    columbia['Room'] = columbia.Meetings.str.extract(
    r'(?<=am|pm)(\S.+?$)')
    columbia['Time'] = columbia.Meetings.str.extract(
    r'(\d+:\d+.+-.+am|\d+:\d+.+-.+pm)')
    columbia = columbia[['Code', 'Course_Name', 'Credit', 'Professor', 'Room', 'Days', 'Time']]
    columbia.to_excel('./crawl_results/columbia.xlsx')


if __name__ == '__main__':

    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

    root = Tk()
    root.title('Columbia Crawler')

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
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, '.courseblock')))
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    courses = soup.select('.courseblock')
    total = len(courses)
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
    btn = Button(progress, text='시작', command=lambda: crawl(courses=courses, counter=counter, total=total, result=result))
    btn.pack()

    def crawl(courses, counter, total, result):
        for course in courses:
            course_name = course.select_one('.courseblocktitle > strong:nth-child(1)').text
            sections = course.select('table > tbody > tr')
            for section in sections:
                a = section.select('.unifyRow1') 
                if a:
                    code = section.select_one('td:nth-child(2)').text
                    cred = section.select_one('td:nth-child(5)').text
                    prof = section.select_one('td:nth-child(4)').text
                    room_time = section.select_one('td:nth-child(3)').text
                    data = [code, course_name, cred, prof, room_time]
                    result.append(data)
            counter += 1
            logging.info("{:.2f}".format((counter / total) * 100))
            p_var2.set((counter / total)*100)
            progressbar2.update()
        progress.destroy()
    progress.mainloop()  

    to_excel(result)
