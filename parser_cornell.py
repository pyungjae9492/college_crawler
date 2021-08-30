import bs4
from bs4 import BeautifulSoup
import pandas as pd
import logging
import openpyxl
import requests
from tkinter import *
import tkinter.ttk as ttk

#완료!

logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

root = Tk()
root.title('Cornell Crawler')
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
base_url = 'https://classes.cornell.edu/browse/roster/FA21/subject/'
subjects = soup.select('.browse-subjectcode > a')

result = []
counter = 0
total = len(subjects)
logging.info("TOTAL " + str(total))

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
    for subject in subjects:
        req = requests.get(base_url + subject.text)
        html = req.text
        soup = BeautifulSoup(html, 'html.parser')
        courses = soup.select('.node')
        del courses[0]
        for course in courses:
            course_name = course.select_one('.title-coursedescr').text
            sections = course.select('.sections')
            for section in sections:
                code = section.select_one('.class-numbers > p > strong').text.strip()
                cred = section.select_one('.credit-val').text
                prof_room_time = section.select_one('.meeting-pattern').text 
                data = [code, course_name, cred, prof_room_time]
                result.append(data)
        counter += 1
        logging.info("{:.2f}".format((counter / total) * 100))
        p_var2.set((counter / total)*100)
        progressbar2.update()
    progress.destroy()

progress.mainloop()

col_name=['Code', 'Course Name', 'Credit', 'Professor_Room_Time']
cornell = pd.DataFrame(result, columns=col_name)
cornell['Professor'] = cornell.Professor_Room_Time.str.extract(r'(?<=[I][n][s][t][r][u][c][t][o][r][s])(.+)')
cornell.to_excel('./crawl_results/cornell.xlsx')