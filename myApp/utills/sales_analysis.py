import pandas as pd
import streamlit as st
import pymysql
from mydb.connectDB import openDB

# DB 연결 및 커서 생성
conn = openDB()
cursor = conn.cursor(pymysql.cursors.DictCursor)

# 브랜드명 캐싱 함수
@st.cache_data(ttl=3600)
def get_brands():
    cursor.execute("SELECT DISTINCT brand FROM brand_logo")
    brands = ['전체'] + sorted([row['brand'] for row in cursor.fetchall()])
    priority_brands = ['현대', '기아', '르노', '테슬라', 'BMW', '아우디', '벤츠', '폭스바겐', '쌍용', '쉐보레']
    brands_no_total = [b for b in brands if b != '전체']
    priority_in_brands = [b for b in priority_brands if b in brands_no_total]
    others = [b for b in brands_no_total if b not in priority_in_brands]
    final_brands = ['전체'] + priority_in_brands + sorted(others)
    return final_brands

# 차종 캐싱 함수
@st.cache_data(ttl=3600)
def get_car_types():
    cursor.execute("SELECT DISTINCT carType FROM car_model")
    return ['전체'] + sorted([row['carType'] for row in cursor.fetchall() if row['carType']])

# 모델명 캐싱 함수
@st.cache_data(ttl=3600)
def get_model_names():
    cursor.execute("SELECT DISTINCT model_name FROM car_model")
    return ['전체'] + sorted([row['model_name'] for row in cursor.fetchall() if row['model_name']])

years = ['전체'] + list(range(2012, 2026))
months = ['전체'] + list(range(1, 13))

st.header("👑 자동차 판매 TOP 10")

final_brands = get_brands()

col1, col2 = st.columns(2)
with col1:
    year = st.selectbox('연도 선택', years, key='top10_year')
with col2:
    brand = st.selectbox('브랜드 선택', final_brands, key='top10_brand')
st.write(f"선택한 브랜드 : {brand}, 연도: {year}")

if st.button('검색', key='top10_search'):
    # 1. SQL문 선택
    if year != '전체' and int(year) > 2012:
        last_year = int(year) - 1
        if brand == '전체':
            sql = f"""
            WITH this_year AS (
                SELECT
                    a.model_name as 모델명,
                    b.brand as 제조사,
                    SUM(a.volume) AS 총 판매량,
                    RANK() OVER (ORDER BY SUM(a.volume) DESC) AS 연간순위(변동)
                FROM car_model a
                LEFT JOIN brand_logo b ON a.brand_code = b.codes
                WHERE a.years = {year}
                GROUP BY a.model_name, b.brand
            ),
            last_year AS (
                SELECT
                    a.model_name,
                    b.brand,
                    RANK() OVER (ORDER BY SUM(a.volume) DESC) AS last_year_rank
                FROM car_model a
                LEFT JOIN brand_logo b ON a.brand_code = b.codes
                WHERE a.years = {last_year}
                GROUP BY a.model_name, b.brand
            )
            SELECT
                t.model_name,
                t.brand,
                t.total_volume,
                t.year_rank,
                l.last_year_rank
            FROM this_year t
            LEFT JOIN last_year l ON t.model_name = l.model_name AND t.brand = l.brand
            ORDER BY t.year_rank
            LIMIT 10;
            """
        else:
            sql = f"""
            WITH this_year AS (
                SELECT
                    a.model_name,
                    b.brand,
                    SUM(a.volume) AS total_volume,
                    RANK() OVER (ORDER BY SUM(a.volume) DESC) AS year_rank
                FROM car_model a
                LEFT JOIN brand_logo b ON a.brand_code = b.codes
                WHERE a.years = {year} AND b.brand = '{brand}'
                GROUP BY a.model_name, b.brand
            ),
            last_year AS (
                SELECT
                    a.model_name,
                    RANK() OVER (ORDER BY SUM(a.volume) DESC) AS last_year_rank
                FROM car_model a
                LEFT JOIN brand_logo b ON a.brand_code = b.codes
                WHERE a.years = {last_year} AND b.brand = '{brand}'
                GROUP BY a.model_name
            )
            SELECT
                t.model_name,
                t.brand,
                t.total_volume,
                t.year_rank,
                l.last_year_rank
            FROM this_year t
            LEFT JOIN last_year l ON t.model_name = l.model_name
            ORDER BY t.year_rank
            LIMIT 10;
            """
    else:
        if brand == '전체' and year == '전체':
            sql = """
            SELECT
                a.model_name,
                b.brand,
                SUM(a.volume) AS total_volume,
                RANK() OVER (ORDER BY SUM(a.volume) DESC) AS year_rank
            FROM car_model a
            LEFT JOIN brand_logo b ON a.brand_code = b.codes
            GROUP BY a.model_name, b.brand
            ORDER BY year_rank
            LIMIT 10;
            """
        elif brand == '전체':
            sql = f"""
            SELECT
                a.model_name,
                b.brand,
                SUM(a.volume) AS total_volume,
                RANK() OVER (ORDER BY SUM(a.volume) DESC) AS year_rank
            FROM car_model a
            LEFT JOIN brand_logo b ON a.brand_code = b.codes
            WHERE a.years = {year}
            GROUP BY a.model_name, b.brand
            ORDER BY year_rank
            LIMIT 10;
            """
        elif year == '전체':
            sql = f"""
            SELECT
                a.model_name,
                b.brand,
                SUM(a.volume) AS total_volume,
                RANK() OVER (ORDER BY SUM(a.volume) DESC) AS year_rank
            FROM car_model a
            LEFT JOIN brand_logo b ON a.brand_code = b.codes
            WHERE b.brand = '{brand}'
            GROUP BY a.model_name, b.brand
            ORDER BY year_rank
            LIMIT 10;
            """
        else:
            sql = f"""
            SELECT
                a.model_name,
                b.brand,
                SUM(a.volume) AS total_volume,
                RANK() OVER (ORDER BY SUM(a.volume) DESC) AS year_rank
            FROM car_model a
            LEFT JOIN brand_logo b ON a.brand_code = b.codes
            WHERE a.years = {year} AND b.brand = '{brand}'
            GROUP BY a.model_name, b.brand
            ORDER BY year_rank
            LIMIT 10;
            """

    # 2. SQL 실행 및 데이터프레임 변환
    cursor.execute(sql)
    rows = cursor.fetchall()
    df = pd.DataFrame(rows)

    # 3. 전년 순위 변화 표기
    if 'last_year_rank' in df.columns:
        def rank_with_change(row):
            if pd.isnull(row['last_year_rank']):
                return f"{int(row['year_rank'])}(NEW)"
            diff = int(row['last_year_rank']) - int(row['year_rank'])
            if diff > 0:
                return f"{int(row['year_rank'])}(+{diff})"
            elif diff < 0:
                return f"{int(row['year_rank'])}({diff})"
            else:
                return f"{int(row['year_rank'])}(0)"
        df['year_rank_display'] = df.apply(rank_with_change, axis=1)
        new_df=df[['model_name', 'brand', 'total_volume', 'year_rank_display']].rename(columns={'year_rank_display': 'year_rank'})

        st.dataframe(new_df)
    else:
        df['year_rank'] = df['year_rank'].astype(int)
        new_df=df[['model_name', 'brand', 'total_volume', 'year_rank']]

        st.dataframe(new_df)
    
