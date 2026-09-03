'''
用 requests 调通 Codeforces 官方 API，打印前 10 道题的标题和难度。
'''
import requests
from bs4 import BeautifulSoup
import json
import fake_useragent

BASE_URL = 'https://codeforces.com'
INDEX_URL = '/problemset/page/114'


response = requests.get(BASE_URL + INDEX_URL, headers={'User-Agent': fake_useragent.UserAgent().random})

soup = BeautifulSoup(response.content, 'html.parser')

problems = soup.find_all('tr')
print(problems)
# for problem in problems[1:11]:  # 前 10 道题