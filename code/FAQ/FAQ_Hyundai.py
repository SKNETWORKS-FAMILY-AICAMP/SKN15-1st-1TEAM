#현대 최종

import requests
import re
import html
import pymysql

# HTML 태그 및 개행문자 제거 함수
def clean_text(text):
    # 1. HTML 태그 제거
    text = re.sub('<.*?>', '', text)
    # 2. HTML 엔티티 디코딩
    text = html.unescape(text)
    # 3. URL 제거 (http/https로 시작하는 거 싹 삭제)
    text = re.sub(r'http[s]?://\S+', '', text)
    text = re.sub(r'www\.\S+', '', text)
    # 4. 개행, nbsp, 여분 공백 정리
    text = text.replace('\n', ' ').replace('\r', ' ').replace('\xa0', ' ').replace('&nbsp;', ' ')
    text = re.sub(' +', ' ', text)
    # 5. 한글, 숫자, 기본 문장부호만 남김
    text = re.sub(r"[^가-힣0-9\s.,?!()\[\]\"'’]", '', text)
    return text.strip()

result = []

for category in range(1, 9):  # 1~8
    payload = {
        "siteTypeCode": "H",
        "faqCategoryCode": f"0{category}",  # '01', '02', ..., '08'
        "faqSeq": "914",
        "searchKeyword": "",
        "pageNo": 1,
        "pageSize": "100",
        "externalYn": ""
    }
    head = {
        "Content-Type": "application/json;charset=UTF-8",
        "User-Agent": "Mozilla/5.0",
        "Origin": "https://www.hyundai.com",
        "Referer": "https://www.hyundai.com/kr/ko/e/customer/center/faq",
    }
    url = "https://www.hyundai.com/kr/ko/gw/customer-support/v1/customer-support/faq/list"
    r = requests.post(url, json=payload, headers=head)
    data=r.json()['data']['list']
    for faq in data:
        category_name = clean_text(faq.get('faqCategoryName', ''))
        question = clean_text(faq.get('faqQuestion', ''))
        answer = clean_text(faq.get('faqAnswer', ''))
        if category_name and question and answer:
            result.append([category_name, question, answer])

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