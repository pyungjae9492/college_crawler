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

req = requests.get('https://explorecourses.stanford.edu/')
html = req.text
soup = BeautifulSoup(html, 'html.parser')
courses = soup.select('.departmentsContainer > ul > li > a')
urls = []
for course in courses:
    urls.append('https://explorecourses.stanford.edu/' + course.get('href').replace("catalog", "timeschedule"))

total = len(urls)
logging.info('total'+ str(total))
result = []
counter = 0

for url in urls:
    req = requests.get(url)
    html = req.text
    soup = BeautifulSoup(html, 'html.parser')
    courses = soup.select('.searchResult')
    for course in courses:
        course_name = course.select_one('.courseTitle').text
        sections = course.select('.sectionDetails')
        for section in sections:
            descr = section.text
            data = [course_name, descr]
            result.append(data)
            logging.info("{:.2f}".format((counter / total) * 100))

col_name=['Code', 'Descriptions']
stanford = pd.DataFrame(result)
stanford.to_excel('./crawl_results/stanford.xlsx')
