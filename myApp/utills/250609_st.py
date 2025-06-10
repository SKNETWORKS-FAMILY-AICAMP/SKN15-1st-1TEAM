import pandas as pd
import streamlit as st
import pymysql

# DB 연결 및 커서 생성
# conn = pymysql.connect()
# cursor = conn.cursor(pymysql.cursors.DictCursor)

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

years = ['전체'] +list(range(2012, 2026))
months = ['전체'] +list(range(1, 13))

def app():
    st.title('자동차 판매량 데이터 분석')

    # 캐시된 리스트 불러오기
    final_brands = get_brands()
    car_types = get_car_types()
    model_names = get_model_names()

    tab1, tab2, tab3, tab4 = st.tabs([
        "전체 판매 TOP10",
        "차종별 판매 순위",
        "모델별 판매 순위",
        "기간별 맞춤 검색"
    ])

    with tab1:
        st.header("전체 판매 TOP10")
        col1, col2 = st.columns(2)
        with col1:
            year = st.selectbox('연도 선택', years, key='top10_year')
        with col2:
            brand = st.selectbox('브랜드 선택', final_brands, key='top10_brand')
        st.write(f"선택한 브랜드 :   {brand},   연도: {year}")

        if st.button('검색', key='top10_search'):
            if brand != '전체' and year != '전체' and int(year) > 2012:
                last_year = int(year) - 1
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
                # 기존 쿼리, 단 brand 컬럼 포함
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
            cursor.execute(sql)
            rows = cursor.fetchall()
            df = pd.DataFrame(rows)

            # 전년 순위 변화 표기
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
                st.dataframe(df[['model_name', 'brand', 'total_volume', 'year_rank_display']].rename(columns={'year_rank_display': 'year_rank'}))
            else:
                df['year_rank'] = df['year_rank'].astype(int)
                st.dataframe(df[['model_name', 'brand', 'total_volume', 'year_rank']])

    with tab2:
        st.header("차종별 판매 분석")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            car_type = st.selectbox('차종 선택', car_types, key='type_cartype')  # 차종 드롭박스 추가!
        with col2:
            brand = st.selectbox('브랜드 선택', final_brands, key='type_brand')
        with col3:
            year = st.selectbox('연도 선택', years, key='type_year')
            
        st.write(f"선택한 연도: {year}, 차종: {car_type}, 브랜드: {brand}")
        # TODO: 쿼리 실행 및 결과 출력

    with tab3:
        st.header("모델별 판매 분석")
        col1, col2, col3 = st.columns(3)
        with col1:
            brand = st.selectbox('브랜드 선택', final_brands, key='trend_brand')
        with col2:
            car_type = st.selectbox('차종 선택', car_types, key='trend_cartype')
        with col3:
            model = st.selectbox('모델 선택', model_names, key='trend_model')
        st.write(f"선택한 브랜드: {brand}, 차종: {car_type}, 모델: {model}")
        # TODO: 쿼리 실행 및 결과 출력

    with tab4:
        st.header("기간별 맞춤 검색")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            brand = st.selectbox('브랜드 선택', final_brands, key='period_brand')
        with col2:
            car_type = st.selectbox('차종 선택', car_types, key='period_cartype')
        with col3:
            model_name = st.text_input('모델명 검색', key='period_model')
        with col4:
            pass  # 필요시 다른 조건 추가

        col5, col6, col7, col8 = st.columns(4)
        with col5:
            start_year = st.selectbox('시작 연도', years, key='period_start_year')
        with col6:
            start_month = st.selectbox('시작 월', months, key='period_start_month')
        with col7:
            end_year = st.selectbox('종료 연도', years, index=len(years)-1, key='period_end_year')
        with col8:
            end_month = st.selectbox('종료 월', months, index=11, key='period_end_month')

        st.write(f"브랜드: {brand}, 차종: {car_type}, 모델명: {model_name}")
        st.write(f"기간: {start_year}년 {start_month}월 ~ {end_year}년 {end_month}월")
        # TODO: 쿼리 실행 및 결과 출력

if __name__ == '__main__':
    app()
