import bs4
from bs4 import BeautifulSoup
import pandas as pd
import logging
import openpyxl
import requests
import re


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

print('크롤링을 시작합니다.')

for url in urls:
    req = requests.get(url)
    html = req.text
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.select_one('pre').select_one('p:nth-child(2)').text
    courses = text.split('\n \n')
    for course in courses:
        lines = course.split('\n')
        first_line = lines[0]
        pattern = r"(?<=\n )(\d{3}.+)(?=\n)"
        sections = re.findall(pattern, course)
        for section in sections:
            data = [first_line, section]
            result.append(data)
    counter += 1
    logging.info("{:.2f}".format((counter / total) * 100))

col_name=['First_Line', 'Section']
upenn = pd.DataFrame(result, columns=col_name)
upenn['Code'] = upenn.First_Line.str.extract(r'(\w{3,4}-\d{3})') + '-' + upenn.Section.str.extract(r'(^\d{3})')
upenn['Course_Name'] = upenn.First_Line.str.extract(r'(?<=-\d{3})(.+)(?=\s\s)')
upenn['Credit'] = upenn.First_Line.str.extract(r'(?<=\s\s)(\d\s.+$|\d\.\d.+$)')
upenn['Professor'] = upenn.Section.str.extract(r'(?<=\s\s\s)(.+$)')
upenn['Professor'] = upenn.Professor.str.strip()
upenn['Room'] = upenn.Section.str.extract(r'(?<=AM|PM)(.+)(?=\s\s\s)')
upenn['Time'] = upenn.Section.str.extract(r'(?<=^\d{3}\s[A-Z]{3}\s)(.+PM|.+AM)')
upenn['Days'] = upenn.Time.str.extract(r'(^[MTWRFS]+)(?=\s\d)')
upenn['Time'] = upenn.Time.str.extract(r'(\d{1,2}\:\d{2}.+?PM|\d{1,2}\:\d{2}.+?AM)')
upenn = upenn[['Code', 'Course_Name', 'Credit', 'Professor', 'Room', 'Days', 'Time']]
upenn.to_excel('./crawl_results/upenn.xlsx')