#쉐보레 최종


from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import re
import pymysql

driver = webdriver.Chrome()

chevro_faq = []

for faq_no in range(2, 12):
    driver.get("https://www.chevrolet.co.kr/faq")
    driver.find_element(By.CSS_SELECTOR,
        f"#gb-main-content > adv-grid.hide-for-small.hide-for-medium.hide-for-large.none-margin.grid-sm-fw > adv-col.col-sm-12.col-sm-bw-up-2.col-sm-gut-no.col-sm-bs-up-solid.q-cc-ag-lightgray-border > div > adv-grid > adv-col:nth-child({faq_no}) > div > a"
    ).click()
    time.sleep(1)

    for question_num in range(1, 50):
        try:
            driver.find_element(
                By.CSS_SELECTOR,
                f"#gb-main-content > gb-adv-grid.gb-large-margin > adv-col > div > div:nth-child({question_num}) > div > div.q-headline.q-expander-button.stat-expand-icon > h6"
            ).click()
            time.sleep(0.5)  # 클릭 후 잠시 대기
        except NoSuchElementException:
            continue

        bs = BeautifulSoup(driver.page_source, "html.parser")
        faq_items = bs.find_all('div', class_='q-mod q-mod-expander q-expander q-expander-default q-closed-xs q-closed-sm q-closed-med q-closed-lg q-closed-xl q-button-active active')

        for item in faq_items:
            question_tag = item.find('h6', class_='q-button-text q-headline-text')
            answer_tag = item.find('div', class_='q-text q-body1 q-invert')

            if question_tag and answer_tag:
                question_text = question_tag.get_text(strip=True)
                answer_text = answer_tag.get_text(strip=True)

                # 중복 저장 방지
                if not any(q[0] == question_text for q in chevro_faq):
                    chevro_faq.append([question_text, answer_text])

    manual_selectors = [
    "#gb-main-content > gb-adv-grid:nth-child(8) > adv-col > div > div:nth-child(1) > div > div.q-headline.q-expander-button.stat-expand-icon > h6",
    "#gb-main-content > gb-adv-grid:nth-child(8) > adv-col > div > div:nth-child(2) > div > div.q-headline.q-expander-button.stat-expand-icon > h6",
    "#gb-main-content > gb-adv-grid:nth-child(10) > adv-col > div > div:nth-child(1) > div > div.q-headline.q-expander-button.stat-expand-icon > h6",
    "#gb-main-content > gb-adv-grid:nth-child(10) > adv-col > div > div:nth-child(2) > div > div.q-headline.q-expander-button.stat-expand-icon > h6",
    "#gb-main-content > gb-adv-grid:nth-child(12) > adv-col > div > div:nth-child(1) > div > div.q-headline.q-expander-button.stat-expand-icon > h6",
    "#gb-main-content > gb-adv-grid:nth-child(12) > adv-col > div > div:nth-child(2) > div > div.q-headline.q-expander-button.stat-expand-icon > h6",
    "#gb-main-content > gb-adv-grid:nth-child(12) > adv-col > div > div:nth-child(3) > div > div.q-headline.q-expander-button.stat-expand-icon > h6",
    "#gb-main-content > gb-adv-grid:nth-child(12) > adv-col > div > div:nth-child(4) > div > div.q-headline.q-expander-button.stat-expand-icon > h6",
    "#gb-main-content > gb-adv-grid:nth-child(12) > adv-col > div > div:nth-child(5) > div > div.q-headline.q-expander-button.stat-expand-icon > h6",
    "#gb-main-content > adv-grid > adv-col > div > div:nth-child(1) > div > div.q-headline.q-expander-button.stat-expand-icon > h6",
    "#gb-main-content > adv-grid > adv-col > div > div:nth-child(2) > div > div.q-headline.q-expander-button.stat-expand-icon > h6",
    "#gb-main-content > adv-grid > adv-col > div > div:nth-child(3) > div > div.q-headline.q-expander-button.stat-expand-icon > h6",
    "#gb-main-content > adv-grid > adv-col > div > div:nth-child(4) > div > div.q-headline.q-expander-button.stat-expand-icon > h6",
    "#gb-main-content > gb-adv-grid.gb-small-margin > adv-col > div > div:nth-child(1) > div > div.q-headline.q-expander-button.stat-expand-icon > h6",
    "#gb-main-content > gb-adv-grid.gb-small-margin > adv-col > div > div:nth-child(2) > div > div.q-headline.q-expander-button.stat-expand-icon > h6",
    "#gb-main-content > gb-adv-grid.gb-small-margin > adv-col > div > div:nth-child(3) > div > div.q-headline.q-expander-button.stat-expand-icon > h6",
    "#gb-main-content > gb-adv-grid.gb-small-margin > adv-col > div > div:nth-child(4) > div > div.q-headline.q-expander-button.stat-expand-icon > h6",
    "#gb-main-content > gb-adv-grid.gb-small-margin > adv-col > div > div:nth-child(5) > div > div.q-headline.q-expander-button.stat-expand-icon > h6",
    "#gb-main-content > gb-adv-grid.gb-small-margin > adv-col > div > div:nth-child(6) > div > div.q-headline.q-expander-button.stat-expand-icon > h6",
    "#gb-main-content > gb-adv-grid.gb-small-margin > adv-col > div > div:nth-child(7) > div > div.q-headline.q-expander-button.stat-expand-icon > h6",
    "#gb-main-content > gb-adv-grid.gb-small-margin > adv-col > div > div:nth-child(8) > div > div.q-headline.q-expander-button.stat-expand-icon > h6",
    "#gb-main-content > gb-adv-grid.gb-small-margin > adv-col > div > div:nth-child(9) > div > div.q-headline.q-expander-button.stat-expand-icon > h6",
    "#gb-main-content > gb-adv-grid.gb-small-margin > adv-col > div > div:nth-child(10) > div > div.q-headline.q-expander-button.stat-expand-icon > h6",
    "#gb-main-content > gb-adv-grid.gb-small-margin > adv-col > div > div:nth-child(11) > div > div.q-headline.q-expander-button.stat-expand-icon > h6",
    "#gb-main-content > gb-adv-grid.gb-small-margin > adv-col > div > div:nth-child(12) > div > div.q-headline.q-expander-button.stat-expand-icon > h6"
]

# 리스트 반복하며 클릭
    for selector in manual_selectors:
        try:
            driver.find_element(By.CSS_SELECTOR, selector).click()
            time.sleep(0.5)
        except NoSuchElementException:
            continue    

        bs = BeautifulSoup(driver.page_source, "html.parser")
        faq_items = bs.find_all('div', class_='q-mod q-mod-expander q-expander q-expander-default q-closed-xs q-closed-sm q-closed-med q-closed-lg q-closed-xl q-button-active active')

        for item in faq_items:
            question_tag = item.find('h6', class_='q-button-text q-headline-text')
            answer_tag = item.find('div', class_='q-text q-body1 q-invert')

            if question_tag and answer_tag:
                question_text = question_tag.get_text(strip=True)
                answer_text = answer_tag.get_text(strip=True)

                # 중복 저장 방지
                if not any(q[0] == question_text for q in chevro_faq):
                    chevro_faq.append([question_text, answer_text])




result = []
for q, a in chevro_faq:
    m = re.match(r'\[(.*?)\]\s*(.*)', q)
    if m:
        category = m.group(1)
        question = m.group(2)
    else:
        category = ""
        question = q
    result.append([category, question, a])


driver.quit()



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