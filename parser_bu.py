from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import bs4
from bs4 import BeautifulSoup
import time
from time import sleep
import pandas as pd
import logging
import openpyxl
import requests
from tkinter import *
import tkinter.ttk as ttk

# 크롤링 막혀있음

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

root = Tk()
root.title('BU Crawler')
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
driver = webdriver.Chrome('chromedriver.exe', chrome_options=options)
driver.implicitly_wait(3)
driver.get(site_url)

# 웹이 전부 파싱되기를 기다렸다가 클릭
soup = BeautifulSoup(driver.page_source, 'html.parser')
courses = soup.select('.coursearch-result')
url_and_credits = []

for course in courses:
    a = ['http://bu.edu' + course.select_one('a').get('href'), course.select_one(
        '.coursearch-result-content-description > p:nth-child(6)').text]
    url_and_credits.append(a)

result = []
rejected_url = []
counter = 0
total = len(url_and_credits)
logging.info("TOTAL " + str(total))

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'}

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

def requesting(url, failed_num):
    sleep(1)
    req = requests.get(url, headers=headers)
    if failed_num > 4:
        rejected_url.append(url)
        return
    print('request denied!')
    failed_num += 1
    requesting(url, failed_num)


def crawl(counter, total, result): 
    for url_and_credit in url_and_credits:
        cred = url_and_credit[1][3]
        url = url_and_credit[0]
        failed_num = 0
        try:
            req = requests.get(url, headers=headers)
        except:
            requesting(url, failed_num)
            continue
        sleep(1)
        html = req.text
        soup = BeautifulSoup(html, 'html.parser')
        course_name = soup.select_one('#body-tag > main > div > h1').text
        table = soup.select_one('.coursearch-course-section > div > table')
        sections = table.select('tr')
        del sections[0]
        for section in sections:
            prof = section.select('td')[2].text
            code = soup.select_one('#body-tag > main > div > h6').text + section.select('td')[0].text
            room = section.select('td')[4].text
            time = section.select('td')[5].text
            data = [code, course_name, cred, prof, room, time]
        counter += 1
        logging.info("{:.2f}".format((counter / total) * 100))
        p_var2.set((counter / int(total)) * 100)
        progressbar2.update()
        result.append(data)
    progress.destroy()

progress.mainloop()

col_name = ['Code', 'Course_Name', 'Credit', 'Professor', 'Room', 'Time']
bu = pd.DataFrame(result, columns=col_name)
bu.to_excel('./crawl_results/bu.xlsx')
