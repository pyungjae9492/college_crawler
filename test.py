import re

p = '\nFinancial Accounting (ACCT1021-01)\nCarroll School of Management \xa0\xa0 Fall 2021\n      \nGallimberti,  Carlo Maria\n  \xa0 Credits:3\n      More Detail Less Detail\n'
pattern = r'(?<=Credits:)[0-9]+'
matchOB = re.findall(pattern, p)

print(matchOB[0])