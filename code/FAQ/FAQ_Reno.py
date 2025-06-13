import requests
from bs4 import BeautifulSoup as bs

url = "https://www.renaultkoream.com/e-guide/etc/ifm_faq.html"
r = requests.get(url)
r.encoding = 'utf-8'

soup = bs(r.text, 'html.parser')
faq_renault = []

for faq_dl in soup.find_all('dl', class_='faq'):
    category_tag = faq_dl.find('dt')
    category = category_tag.get_text(strip=True) if category_tag else ''
    for dd in faq_dl.find_all('dd'):
        question_tag = dd.find('a')
        question = question_tag.get_text(strip=True) if question_tag else ''
        table = dd.find('table', class_='tbl')
        if table:
            answer_parts = []
            for tr in table.find('tbody').find_all('tr'):
                tds = tr.find_all('td')
                if len(tds) == 2:
                    cause = tds[0].get_text(separator=' ', strip=True).replace('\n', ' ').strip()
                    action = tds[1].get_text(separator=' ', strip=True).replace('\n', ' ').strip()
                    answer_parts.append(f"[원인] {cause}[조치] {action}")
            answer = ' '.join(answer_parts)
            faq_renault.append([category, question, answer])
        else:
            faq_renault.append([category,question, ''])

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
for idx, (category, question, answer) in enumerate(faq_renault, start=1):
    cursor.execute(sql, (idx, mfr_id, category, question, answer))

conn.commit()
cursor.close()
conn.close()