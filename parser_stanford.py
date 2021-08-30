import requests
import bs4
import time
from bs4 import BeautifulSoup
import pandas as pd
import logging
import openpyxl
from tkinter import *
import tkinter.ttk as ttk

# 코드 매칭이 잘 안되긴 하는데 일단 완료

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

root = Tk()
root.title('Stanford Crawler')
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

req = requests.get(site_url)
html = req.text
soup = BeautifulSoup(html, 'html.parser')
courses = soup.select('.departmentsContainer > ul > li > a')
urls = []
for course in courses:
    urls.append('https://explorecourses.stanford.edu/' +
                course.get('href').replace("catalog", "timeschedule"))

total = len(urls)
logging.info('total' + str(total))
result = []
counter = 0

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
    for url in urls:
        req = requests.get(url)
        html = req.text
        soup = BeautifulSoup(html, 'html.parser')
        courses = soup.select('.searchResult')
        for course in courses:
            course_name = course.select_one('.courseTitle').text
            sections = course.select('.sectionContainer')
            for section in sections:
                if section.select_one('h3').text == '2021-2022 Autumn':
                    for i in section.select('.sectionDetails'):
                        descr = i.text
                        data = [course_name, descr]
                        result.append(data)
        counter += 1
        logging.info("{:.2f}".format((counter / total) * 100))
        p_var2.set((counter / total)*100)
        progressbar2.update()
    progress.destroy()

progress.mainloop()


col_name = ['Course_Name', 'Descriptions']
stanford = pd.DataFrame(result, columns=col_name)
stanford['Code'] = stanford.Descriptions.str.extract(
    r'(\d{4,5})')
stanford['Credit'] = stanford.Descriptions.str.extract(
    r'(\d+)(?=\s[u][n][i][t][s])')
stanford['Professor'] = stanford.Descriptions.str.extract(
    r'(?<=[I][n][s][t][r][u][c][t][o][r][s]\:\s\s)(.+)')
stanford['Room'] = stanford.Descriptions.str.extract(
    r'(?<=[P][M]\s[a][t]\s)(.+)(?=\s[w][i][t][h])')
stanford['Days'] = stanford.Descriptions.str.extract(
    r'(?<=\d{2}\/\d{2}\/\d{4}\s.\s\d{2}\/\d{2}\/\d{4}\s)(.+)(?=\s\d+\:\d+\s.+\s\d+\:\d+\s)')
stanford['Time'] = stanford.Descriptions.str.extract(
    r'([0-9]+\:[0-9]+.+[AP][M])')
stanford = stanford[['Code', 'Course_Name', 'Credit', 'Professor', 'Room', 'Days', 'Time']]
stanford.to_excel('./crawl_results/stanford.xlsx')
