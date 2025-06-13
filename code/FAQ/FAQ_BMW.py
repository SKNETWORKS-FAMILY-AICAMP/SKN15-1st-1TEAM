from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
from selenium import webdriver
from bs4 import BeautifulSoup as bs
import time
import pymysql

driver = webdriver.Chrome()
time.sleep(1)
url = "https://faq.bmw.co.kr/s/?language=ko"
faq_bmw = []
driver.get(url)
time.sleep(1)

# 1. 부모 Shadow root 접근
host = driver.find_element("css selector", "c-scp-generic-article-list")
shadow_root = driver.execute_script("return arguments[0].shadowRoot", host)

# 2. 질문 컨테이너에서 아이템 추출
container = shadow_root.find_element("css selector", ".article-list-items-container")
items = container.find_elements("css selector", "c-scp-article-list-item-expandable")

for idx, item in enumerate(items, 1):
    try:
        # 3. 각 질문 아이템의 Shadow Root 접근
        item_shadow = driver.execute_script("return arguments[0].shadowRoot", item)
        # 4. 질문 버튼 클릭
        q_btn = item_shadow.find_element("css selector", "h2 > button")
        driver.execute_script("arguments[0].scrollIntoView(true);", q_btn)
        driver.execute_script("arguments[0].click();", q_btn)
        time.sleep(0.5)
        question = q_btn.text.strip()
        # 5. 답변 추출 (.slds-rich-text-area)
        answer_div = item_shadow.find_element("css selector", ".slds-rich-text-area")
        answer = answer_div.text.strip()
        faq_bmw.append([question, answer])
    except Exception as e:
        print(f"{idx}번째 질문에서 오류 발생:", e)

soup = bs(driver.page_source, "html.parser")

faq_bmw = []
seen = set()
for item in soup.select("div.article-list-item"):
    # 질문 추출
    q_btn = item.select_one("h2.article-headline > button")
    question = q_btn.text.strip() if q_btn else ""
    # 답변 추출
    answer_div = item.select_one("div.article-body lightning-formatted-rich-text")
    answer = answer_div.text.strip() if answer_div else ""
    # 질문이 비어있지 않고, (질문, 답변) 쌍이 중복되지 않을 때만 추가
    key = (question, answer)
    if question and key not in seen:
        faq_bmw.append([question, answer])
        seen.add(key)

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
for idx, (category, question, answer) in enumerate(faq_bmw, start=1):
    cursor.execute(sql, (idx, mfr_id, category, question, answer))

conn.commit()
cursor.close()
conn.close()