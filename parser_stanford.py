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

@contextmanager
def poolcontext(*args, **kwargs):
    pool = Pool(*args, **kwargs)
    yield pool
    pool.terminate()

def get_links():
    req = requests.get('https://explorecourses.stanford.edu/')
    html = req.text
    soup = BeautifulSoup(html, 'html.parser')
    courses = soup.select('.departmentsContainer > ul > li > a')
    urls = []
    for course in courses:
        urls.append('https://explorecourses.stanford.edu/' + course.get('href').replace("catalog", "timeschedule"))
    return urls

def get_content(link):
    result = []
    req = requests.get(link)
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
            print('done!')
    return result

def toExcel(result):
    # col_name=['Code', 'Descriptions']
    stanford = pd.DataFrame(result)
    # tufts['Room'] = tufts['Room'].str.findall(pat='\n.+')
    # tufts['Time'] = tufts['Time'].str.findall(pat='.+\n')
    stanford.to_excel('./crawl_results/stanford.xlsx')

if __name__=='__main__':

    links = get_links()
    total = len(links)
    print('total'+ str(total))
    result = []

    with poolcontext(processes=4) as pool:
        result.extend(pool.map(get_content, links))

    toExcel(result)
