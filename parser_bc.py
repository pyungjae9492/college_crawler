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
import re
from tkinter import *
import tkinter.ttk as ttk

# 완료

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

root = Tk()
root.title('BC Crawler')
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
driver = webdriver.Chrome('chromedriver.exe', options=options)  # mac의 경우 chromedriver
driver.implicitly_wait(3)
driver.get(site_url)

exceptions = 0
result = []

select_options = driver.find_elements_by_css_selector(
    '#school > ul > li > input')
counter = 0
total = len(select_options)

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
    for select_option in select_options:
        driver.find_element_by_css_selector(
            f'#selectedSchool-{ counter + 1 }').click()
        driver.find_element_by_css_selector('#search').click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '#resultTableBody')))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        courses = soup.select('.course')
        course_count = 0
        course_total = len(courses)


        for course in courses:
            course_raw = course.select_one('td:nth-child(1)').text
            course_name = course.select_one('.course-name').text
            if course.select_one('.instructors'):
                prof = course.select_one('.instructors').text
            else:
                prof = ''
            schedule = course.select_one('.schedule')
            week_list = schedule.select('.weekdisplay')
            if week_list:
                days1 = ''
                days1_list = week_list[0].select('.meet')
                for day in days1_list:
                    days1 += (day.text + ' ')
                if schedule.select_one('.time'):
                    time1 = schedule.select_one('.time').text
                else:
                    time1 = ''
                if schedule.select_one('.location'):
                    room1 = schedule.select_one('.location').text
                else:
                    room1 = ''
                days2 = ''
                time2 = ''
                room2 = ''
                if len(week_list) == 2:
                    days2_list = week_list[1].select('.meet')
                    for day in days2_list:
                        days2 += (day.text + ' ')
                    if schedule.select_one('.time'):
                        time2 = schedule.select_one('.time').text
                    else:
                        time2 = ''
                    if schedule.select_one('.location'):
                        room2 = schedule.select_one('.location').text
                    else:
                        room2 = ''
                data = [course_raw, course_name, prof, days1, time1, room1, days2, time2, room2]
            else:
                days1 = 'TBA'
                time1 = 'TBA'
                room1 = 'TBA'
                days2 = ''
                time2 = ''
                room2 = ''

            data = [course_raw, course_name, prof, days1, time1, room1, days2, time2, room2]
            result.append(data)
            course_count += 1
            logging.info("{:.2f}".format((course_count / course_total) * 100))

        counter += 1
        logging.info("{:.2f}".format((counter / total) * 100))
        p_var2.set((counter / total)*100)
        progressbar2.update()
    progress.destroy()
progress.mainloop()

driver.quit()

col_name = ['Course_Information', 'Course_Name', 'Professor', 'Days1', 'Time1', 'Room1', 'Days2', 'Time2', 'Room2']
bc = pd.DataFrame(result, columns=col_name)
bc['Code'] = bc.Course_Information.str.extract(r'(?<=\()(.+)(?=\))')
bc['Course_Name'] = bc.Course_Name.str.extract(r'^(.+)(?=\s\()')
bc['Credit'] = bc.Course_Information.str.extract(
    r'(?<=[cC][rR][eE][dD][iI][tT][sS]\:)([0-9]+)(?=\n)')
bc = bc[['Code', 'Course_Name', 'Credit', 'Professor', 'Days1', 'Time1', 'Room1', 'Days2', 'Time2', 'Room2']]
bc.to_excel('./crawl_results/bc.xlsx')
