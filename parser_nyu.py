from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import bs4
from time import sleep
from bs4 import BeautifulSoup
import pandas as pd
import logging
import openpyxl
import requests
from tkinter import *
import tkinter.ttk as ttk

# 완료!

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

# options = webdriver.ChromeOptions()
# options.add_argument('headless')
# driver = webdriver.Chrome('chromedriver.exe')
# driver.implicitly_wait(3)
# driver.get(
#     'https://m.albert.nyu.edu/app/catalog/classSearch/1218')

# WebDriverWait(driver, 20).until(EC.presence_of_element_located(
#     (By.CSS_SELECTOR, '#search-acad-group')))

# term_select = Select(driver.find_element_by_css_selector('#term'))
# terms = driver.find_elements_by_css_selector('#term > option')
# del terms[0]

# root = Tk()
# root.title('USC Crawler')
# choice = StringVar()

# def getTextInput():
#     global term
#     term = choice.get()
#     root.destroy()

# label = Label(root, text= 'Term을 골라주세요')
# label.pack()
# for i in terms:
#     Radiobutton(root, text=i.text, padx=20, variable=choice, value=i.text).pack(anchor=W)
# btnRead=Button(root, height=1, width=10, text="OK", 
#                     command=getTextInput)
# btnRead.pack()
# root.mainloop()

# term_select.select_by_visible_text(term)


# driver.find_element_by_css_selector('.search-check').click()
# college_select = Select(
#     driver.find_element_by_css_selector('#search-acad-group'))
# college_options = driver.find_elements_by_css_selector(
#     '#search-acad-group > option')
# del college_options[0]

# urls_times_profs = []
# college_counter = 0
# college_total = len(college_options)

# for college_option in college_options:
#     college_select.select_by_value(college_option.get_attribute('value'))
#     subject_select = Select(driver.find_element_by_css_selector('#subject'))
#     subject_options = driver.find_elements_by_css_selector('#subject > option.option-subject')

#     for subject_option in subject_options:
#         subject_select.select_by_value(subject_option.get_attribute('value'))
#         WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#buttonSearch')))
#         try:
#             driver.find_element_by_css_selector('#buttonSearch').click()
#         except:
#             sleep(10)
#             driver.find_element_by_css_selector('#buttonSearch').click()
#         try:
#             WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#search-results > a')))
#         except:
#             continue

#         soup = BeautifulSoup(driver.page_source, 'html.parser')
#         a_tags = soup.select('#search-results > a')

#         for a_tag in a_tags:
#             data = [a_tag.get('href'), a_tag.select_one('div > div:nth-child(4)').text, a_tag.select_one('div > div:nth-child(6)').text]
#             urls_times_profs.append(data)
    
#     college_counter += 1
#     logging.info("{:.2f}".format((college_counter / college_total) * 100))

# driver.quit()
# print('url crawling done!')
# nyu_urls = pd.DataFrame(urls_times_profs)
# nyu_urls.to_excel('./crawl_results/nyu_urls.xlsx', index=False)

urls_times_profs = pd.read_excel('./crawl_results/nyu_urls.xlsx')
urls_times_profs = urls_times_profs.drop(urls_times_profs.columns[0], axis=1)
urls_times_profs = urls_times_profs.values.tolist()

result = []
counter = 0
total = len(urls_times_profs)
logging.info('Total:' + str(total))

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
    for url_time_prof in urls_times_profs:
        req = requests.get(url_time_prof[0])
        html = req.text
        soup = BeautifulSoup(html, 'html.parser')
        course_name = soup.select_one('body > section > section > div:nth-child(1)').text.strip()
        rows = soup.select('div.section-content.clearfix')
        code = ''
        cred = ''
        room = ''
        for row in rows:
            if row.select_one('.strong').text == 'Class Number':
                code = row.select_one('.pull-right').text
                break
        for row in rows:
            if row.select_one('.strong').text == 'Units':
                cred = row.select_one('.pull-right').text
                break
        for row in rows:
            if row.select_one('.strong').text == 'Room':
                if (row.select_one('.pull-right > div').text + ' ') != room:
                    room += (row.select_one('.pull-right > div').text + ' ')
        data = [code, course_name, cred, url_time_prof[2], room, url_time_prof[1]]
        result.append(data)
        counter += 1
        logging.info("{:.2f}".format((counter / total) * 100))
        p_var2.set((counter / int(total)) * 100)
        progressbar2.update()
        if counter > 3:
            break
    progress.destroy()

progress.mainloop()

col_name = ['Code', 'Course Name', 'Cred', 'Professor', 'Room', 'Time']
nyu = pd.DataFrame(result, columns=col_name)
nyu.to_excel('./crawl_results/nyu.xlsx')
