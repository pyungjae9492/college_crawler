import requests
import bs4
import time
from bs4 import BeautifulSoup
import multiprocessing as mp
from multiprocessing import Pool
import pandas as pd
import logging
import openpyxl
from functools import partial
from contextlib import contextmanager

# 코드 매칭이 잘 안되긴 하는데 일단 완료

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

req = requests.get('https://explorecourses.stanford.edu/')
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

col_name = ['Course_Name', 'Descriptions']
stanford = pd.DataFrame(result, columns=col_name)
stanford['Code'] = stanford.Descriptions.str.extract(
    r'(\d{5})')
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
