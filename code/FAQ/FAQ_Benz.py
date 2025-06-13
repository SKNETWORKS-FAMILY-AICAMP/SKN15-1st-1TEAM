#벤츠 최종


import requests
import json
from bs4 import BeautifulSoup
import pymysql
from mydb.connectDB import openDB

url="https://us.api.oneweb.mercedes-benz.com/mbc/nuxt/v1/dcp-api/v2/dcp-mbc-kr/connect/cms/pages?fields=DCP&pageLabelOrId=faqPage&lang=ko_KR"
r=requests.get(url)
data=r.json()



# JSON 데이터를 변수 json_data로 받았다고 가정

faq_items = data['contentSlots']['contentSlot'][0]['components']['component']
benz_faq = []

for item in faq_items:
    headline = None
    content_html = None

    for prop in item.get('otherProperties', []):
        if prop['key'] == 'headline':
            headline = prop['value']['value']
        elif prop['key'] == 'content':
            content_html = prop['value']['value']

    if headline and content_html:
        soup = BeautifulSoup(content_html, 'html.parser')
        content_text = soup.get_text(separator='\n').strip()

        benz_faq.append([headline,content_text])

mfr_id = ""  # 브랜드명을 여기서 지정

# DB 연결
conn = openDB()

cursor = conn.cursor()

# SQL문
sql = "INSERT INTO FAQ (id, mfr_id, category, question, answer) VALUES (%s, %s, %s, %s, %s)"

# id 값은 1부터 시작해서 직접 카운트
for idx, (category, question, answer) in enumerate(benz_faq, start=1):
    cursor.execute(sql, (idx, mfr_id, category, question, answer))

conn.commit()
cursor.close()
conn.close()