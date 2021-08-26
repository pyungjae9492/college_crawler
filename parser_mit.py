import bs4
from bs4 import BeautifulSoup
import pandas as pd
import logging
import openpyxl
import requests



logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')
req = requests.get('https://srfs.upenn.edu/registration-catalog-calendar/rosters/main')
html = req.text
soup = BeautifulSoup(html, 'html.parser')
subjects = soup.select('tbody > tr > td:nth-child(2) > a')
urls = []
for subject in subjects:
    urls.append(subject.get('href'))


result = []
counter = 0
total = len(subjects)
logging.info("TOTAL " + str(total))

for url in urls:
    req = requests.get(url)
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


col_name=['Code', 'Course Name', 'Credit', 'Professor_Room_Time']
upenn = pd.DataFrame(result, columns=col_name)
# upenn = pd.read_csv('./crawl_results/upenn.xlsx')
upenn['Professor'] = upenn.Professor_Room_Time.str.extract(r'(?<=[I][n][s][t][r][u][c][t][o][r][s])(.+)')
upenn.to_excel('./crawl_results/upenn.xlsx')