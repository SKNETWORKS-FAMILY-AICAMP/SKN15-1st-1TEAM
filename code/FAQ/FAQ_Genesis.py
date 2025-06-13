#제네시스 최종

import requests
from bs4 import BeautifulSoup
import re
import pymysql

url = "https://www.genesis.com/kr/ko/support/faq.html"
r = requests.get(url)
data = r.text

soup = BeautifulSoup(data, 'html.parser')

categories = [c.get_text(strip=True) for c in soup.select('strong.accordion-label')]
questions  = [q.get_text(strip=True) for q in soup.select('p.accordion-title')]
answers    = [a.get_text(strip=True) for a in soup.select('div.accordion-panel-inner > p')]

# 대괄호 제거 함수
def remove_brackets(text):
    return re.sub(r'^\[|\]$', '', text).strip()

# 리스트 안의 리스트 + 카테고리 대괄호 제거
result = [ [remove_brackets(cat), q, a] for cat, q, a in zip(categories, questions, answers) ]

mfr_id = ""  # 브랜드명을 여기서 지정

# DB 연결
conn = pymysql.connect(
    host='',
    user='',
    password='',
    db='',
)
cursor = conn.cursor()

# SQL문
sql = "INSERT INTO FAQ (id, mfr_id, category, question, answer) VALUES (%s, %s, %s, %s, %s)"

# id 값은 1부터 시작해서 직접 카운트
for idx, (category, question, answer) in enumerate(result, start=1):
    cursor.execute(sql, (idx, mfr_id, category, question, answer))

conn.commit()
cursor.close()
conn.close()