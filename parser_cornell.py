import bs4
from bs4 import BeautifulSoup
import pandas as pd
import logging
import openpyxl
import requests

#완료!

logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')
req = requests.get('https://classes.cornell.edu/browse/roster/FA21')
html = req.text
soup = BeautifulSoup(html, 'html.parser')
base_url = 'https://classes.cornell.edu/browse/roster/FA21/subject/'
subjects = soup.select('.browse-subjectcode > a')


result = []
counter = 0
total = len(subjects)
logging.info("TOTAL " + str(total))

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


col_name=['Code', 'Course Name', 'Credit', 'Professor_Room_Time']
cornell = pd.DataFrame(result, columns=col_name)
cornell['Professor'] = cornell.Professor_Room_Time.str.extract(r'(?<=[I][n][s][t][r][u][c][t][o][r][s])(.+)')
cornell.to_excel('./crawl_results/cornell.xlsx')