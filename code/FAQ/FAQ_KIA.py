import requests
from bs4 import BeautifulSoup as bs
import re

url = "https://www.kia.com/kr/services/ko/faq.search"
r = requests.get(url)
data = r.json()['data']['faqList']['items']

TAG_TO_KOR = {
    'kwp:kr/faq/purchase': '구매',
    'kwp:kr/faq/contract': '계약',
    'kwp:kr/faq/delivery': '출고',
    'kwp:kr/faq/registration': '등록',
    'kwp:kr/faq/insurance': '보험',
    'kwp:kr/faq/finance': '금융',
    'kwp:kr/faq/maintenance': '정비',
    'kwp:kr/faq/afterservice': 'AS',
    'kwp:kr/faq/etc': '기타',
    # 필요시 추가
}

kia_faq_clean = []
for item in data:
    answer_html = item['answer']['html'] if 'answer' in item and 'html' in item['answer'] else ''
    soup = bs(answer_html, 'html.parser')
    clean_answer = soup.get_text(separator='\n', strip=True).replace("\xa0", "")
    clean_answer = clean_answer.replace('\n', ' ')
    clean_answer = re.sub(r' +', ' ', clean_answer).strip()

    tags = item.get('tags', [])
    kor_tags = []
    if isinstance(tags, list):
        kor_tags = [TAG_TO_KOR[tag] for tag in tags if tag in TAG_TO_KOR]
    elif tags in TAG_TO_KOR:
        kor_tags = [TAG_TO_KOR[tags]]
    category = ', '.join(kor_tags)

    kia_faq_clean.append([
        category,
        item.get('question', '').replace('\n', ' ').strip(),
        clean_answer
    ])

import pymysql

# 예시 데이터


mfr_id = "307"  # 브랜드명을 여기서 지정

#category = "디지털서비스"

# DB 연결 (정보는 네 환경에 맞게 수정)
conn = pymysql.connect(
    host='',
    user='',
    password='',
    db=''

)
cursor = conn.cursor()

# SQL문
sql = "INSERT INTO FAQ (faq_nm, mfr_id, categories, question, answer) VALUES (%s, %s, %s, %s, %s)"

# id 값은 1부터 시작해서 직접 카운트
for idx, (category, question, answer) in enumerate(kia_faq_clean, start=595):
    cursor.execute(sql, (idx, mfr_id, category, question, answer))

conn.commit()
cursor.close()
conn.close()