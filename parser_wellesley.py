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
# 완료

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
driver = webdriver.Chrome(
    'chromedriver.exe', options=options)  # mac의 경우 chromedriver
driver.implicitly_wait(3)
driver.get(site_url)


# 로깅을 위한 변수
count = 0
# 최종 결과물 리스트
result = []
every_courses = driver.find_elements_by_css_selector(
    '#course_listing > section > div > a')
total = len(every_courses)
logging.info("TOTAL " + str(total))
# 클릭하고 해당 과목 크롤링

progress = Tk()
progress.title('크롤링 진행률')
p_var2 = DoubleVar()
prog_label = Label(progress, text='크롤링 진행률')
prog_label.pack()
progressbar2 = ttk.Progressbar(progress, maximum=100, length=500, variable=p_var2)
progressbar2.pack()
btn = Button(progress, text='시작', command=lambda: crawl(every_courses=every_courses, count=count, total=total, result=result))
btn.pack()

def crawl(every_courses, count, total, result):
    for i in every_courses:
        i.click()
        WebDriverWait(driver, 30).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, f'#data_{ count } > div')))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        code = soup.select_one(
            f'#data_{ count } > div.coursedetail > div:nth-child(2)').text[5:10]
        course_name = soup.select_one(f'#course_listing > section:nth-child({ count + 3}) > div > a > div.coursename_big > p').text
        credit = soup.select_one(
            f'#data_{ count } > div.coursedetail > div:nth-child(2)').text[26:27]
        prof = soup.select_one(f'#data_{ count } > a')
        location = soup.select_one(
            f'#data_{ count } > div.coursedetail.col-xs-12 > div:nth-child(3) > a')
        time = soup.select_one(
            f'#data_{ count } > div.coursedetail.col-xs-12 > div:nth-child(3)')
        if prof:
            prof = prof.text
        else:
            prof = 'Not Noticed'
        if location:
            location = location.text
        else:
            location = 'Not Noticed'
        if time:
            time = time.text
        else:
            time = 'Not Noticed'
        data = [code, course_name, credit, prof, location, time]
        # 진행 상황 로깅
        count += 1
        logging.info("{:.2f}".format((count / total) * 100))
        p_var2.set((count / total)*100)
        progressbar2.update()
        result.append(data)
    progress.destroy()

progress.mainloop()
driver.quit()
# 2차원 배열 -> .xlsx
result = pd.read_excel('./crawl_results/wellesley(final).xlsx')
col_name = ['Code', 'Course Name', 'Credit', 'Professor', 'Room', 'Time']
wellesley = pd.DataFrame(result, columns=col_name)
wellesley['Days'] = wellesley.Time.str.extract(
    r'(?<=\:\s)([MTWRFS]+)(?=\s\S\s)')
wellesley['Time'] = wellesley.Time.str.extract(
    r'([0-9]+\:[0-9]+\s[A-Z]+\s\S\s[0-9]+\:[0-9]+\s[A-Z]+)')
wellesley = wellesley[['Code', 'Course Name', 'Credit', 'Professor', 'Room', 'Days', 'Time']]
wellesley.to_excel('./crawl_results/wellesley.xlsx')
