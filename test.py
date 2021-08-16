import pandas as pd
import openpyxl

wellesley = pd.read_excel('wellesley.xlsx')
wellesley['Code'] = wellesley['Code'].str.slice(start=0, stop=5)
wellesley['Time'] = wellesley['Time'].str.findall(pat='[A-Z]+\s\S\s[0-9]+\:[0-9]+\s[A-Z]+\s\S\s[0-9]+\:[0-9]+\s[A-Z]+')
wellesley = wellesley.drop(wellesley.columns[0], axis=1)
wellesley.to_excel('wellesley.xlsx')

