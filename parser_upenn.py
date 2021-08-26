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
    text = soup.select_one('pre').select_one('p > p').text
    courses = text.split('  \n \n')
    for course in courses:
        data = [course]
        result.append(data)
    counter += 1
    logging.info("{:.2f}".format((counter / total) * 100))


col_name=['Course_Data']
upenn = pd.DataFrame(result, columns=col_name)
upenn.to_excel('./crawl_results/upenn.xlsx')