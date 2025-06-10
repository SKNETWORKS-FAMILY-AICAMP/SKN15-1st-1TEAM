import pandas as pd
import streamlit as st
import pymysql
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
from mydb.connectDB import openDB

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

conn = openDB()
cursor = conn.cursor(pymysql.cursors.DictCursor)

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

@st.cache_data(ttl=3600)
def get_car_types():
    cursor.execute("SELECT DISTINCT carType FROM car_model")
    return ['전체'] + sorted([row['carType'] for row in cursor.fetchall() if row['carType']])

years = ['전체'] + list(range(2012, 2026))

st.title("차종별 판매 데이터 분석")

car_types = get_car_types()
final_brands = get_brands()

with st.form("filter_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        car_type = st.selectbox('차종 선택', car_types, key='type_cartype')
    with col2:
        brand = st.selectbox('브랜드 선택', final_brands, key='type_brand')
    with col3:
        year = st.selectbox('연도 선택', years, key='type_year')
    submitted = st.form_submit_button("검색")

tab5, tab1, tab2, tab3, tab4 = st.tabs([
    "차종별 판매 비중",
    "차종별 판매 TOP10",
    "연도별 추이",
    "브랜드별 점유율",
    "월별 차종 판매량"
])

def make_condition(year, brand, car_type):
    year_condition = "1=1" if year == '전체' else f"a.years = {year}"
    brand_condition = "1=1" if brand == '전체' else f"b.brand = '{brand}'"
    car_type_condition = "1=1" if car_type == '전체' else f"a.carType = '{car_type}'"
    return year_condition, brand_condition, car_type_condition

# 1. 차종별 판매 비중 (그래프+표 모두 출력)
with tab5:
    if not submitted or year == '전체':
        st.info("연도를 선택하세요.")
    else:
        target_year = int(year)
        st.subheader(f"{target_year}년 차종별 판매 비중")
        sql_type = f"""
        SELECT
            a.carType,
            SUM(a.volume) AS total_volume
        FROM car_model a
        WHERE a.years = {target_year}
        GROUP BY a.carType
        ORDER BY total_volume DESC
        """
        cursor.execute(sql_type)
        type_rows = cursor.fetchall()
        df_type = pd.DataFrame(type_rows)
        sql_type_prev = f"""
        SELECT
            a.carType,
            SUM(a.volume) AS total_volume
        FROM car_model a
        WHERE a.years = {target_year-1}
        GROUP BY a.carType
        """
        cursor.execute(sql_type_prev)
        type_prev_rows = cursor.fetchall()
        df_type_prev = pd.DataFrame(type_prev_rows)
        if not df_type.empty and 'total_volume' in df_type.columns:
            df_type['total_volume'] = pd.to_numeric(df_type['total_volume'], errors='coerce')
            total_sum = int(df_type['total_volume'].sum())
            if not df_type_prev.empty:
                df_type_prev['total_volume'] = pd.to_numeric(df_type_prev['total_volume'], errors='coerce')
                prev_map = df_type_prev.set_index('carType')['total_volume'].to_dict()
                df_type['전년대비(%)'] = df_type.apply(
                    lambda row: (
                        ((row['total_volume'] - prev_map.get(row['carType'], np.nan)) / prev_map.get(row['carType'], np.nan) * 100)
                        if pd.notnull(prev_map.get(row['carType'], np.nan)) and prev_map.get(row['carType'], np.nan) != 0
                        else np.nan
                    ),
                    axis=1
                ).round(1)
            else:
                df_type['전년대비(%)'] = np.nan
            valid = df_type['total_volume'].notnull() & (df_type['total_volume'] > 0)
            df_type_valid = df_type[valid].sort_values('total_volume', ascending=False)
            if len(df_type_valid) >= 2:
                if len(df_type_valid) > 9:
                    top9 = df_type_valid.iloc[:9]
                    other = pd.DataFrame({
                        'carType': ['기타'],
                        'total_volume': [df_type_valid.iloc[9:]['total_volume'].sum()],
                        '전년대비(%)': [np.nan]
                    })
                    pie_df = pd.concat([top9, other], ignore_index=True)
                else:
                    pie_df = df_type_valid
                fig, ax = plt.subplots()
                ax.pie(
                    pie_df['total_volume'],
                    labels=pie_df.apply(
                        lambda row: (
                            f"{row['carType']} ({row['전년대비(%)']:+.1f}%)" if pd.notnull(row['전년대비(%)']) else row['carType']
                        ), axis=1
                    ),
                    autopct=lambda p: f'{p:.1f}%' if p > 2 else '',
                    startangle=140,
                    counterclock=False
                )
                ax.set_title("")  # 제목 제거
                plt.figtext(0.5, 0.01, f'총 판매 대수: {total_sum:,}대', ha='center', fontsize=12)
                st.pyplot(fig)
                # 표
                pie_df = pie_df.rename(columns={'carType': '차종', 'total_volume': '판매량'})
                def color_change(val):
                    if pd.isnull(val):
                        return ''
                    elif val > 0:
                        return 'color: blue'
                    elif val < 0:
                        return 'color: red'
                    else:
                        return ''
                styled_df = pie_df[['차종', '판매량', '전년대비(%)']].style.format({
                    '판매량': '{:,.0f}',
                    '전년대비(%)': '{:+.1f}'
                }, na_rep="").applymap(color_change, subset=['전년대비(%)'])
                st.dataframe(styled_df)
            else:
                st.info("시각화할 수 있는 차종별 판매량 데이터가 없습니다.")
        else:
            st.info(f"{target_year}년 차종별 데이터가 없습니다.")

with tab1:
    if not submitted or year == '전체':
        st.info("연도를 선택하세요.")
    else:
        st.subheader("차종별 판매 TOP10")
        year_cond, brand_cond, car_type_cond = make_condition(year, brand, car_type)
        sql = f"""
        SELECT
            a.model_name,
            b.brand,
            a.carType,
            SUM(a.volume) AS total_volume
        FROM car_model a
        LEFT JOIN brand_logo b ON a.brand_code = b.codes
        WHERE
            {year_cond}
            AND {brand_cond}
            AND {car_type_cond}
        GROUP BY a.model_name, b.brand, a.carType
        ORDER BY total_volume DESC
        LIMIT 10;
        """
        cursor.execute(sql)
        rows = cursor.fetchall()
        df = pd.DataFrame(rows)
        if not df.empty and 'total_volume' in df.columns:
            df['total_volume'] = pd.to_numeric(df['total_volume'], errors='coerce')
            df = df.rename(columns={'model_name': '모델명', 'brand': '제조사', 'carType': '차종', 'total_volume': '판매량'})
            st.dataframe(df)
        else:
            st.info("해당 조건에 해당하는 데이터가 없습니다.")

with tab2:
    if not submitted or car_type == '전체' or year == '전체':
        st.info("차종(필수)과 브랜드, 연도를 선택하세요.")
    else:
        st.subheader("연도별 판매 추이")
        _, brand_cond, car_type_cond = make_condition('전체', brand, car_type)
        sql_trend = f"""
        SELECT
            a.years,
            SUM(a.volume) AS total_volume
        FROM car_model a
        LEFT JOIN brand_logo b ON a.brand_code = b.codes
        WHERE
            {brand_cond}
            AND {car_type_cond}
        GROUP BY a.years
        ORDER BY a.years
        """
        cursor.execute(sql_trend)
        trend_rows = cursor.fetchall()
        df_trend = pd.DataFrame(trend_rows)
        if not df_trend.empty and 'total_volume' in df_trend.columns:
            df_trend['total_volume'] = pd.to_numeric(df_trend['total_volume'], errors='coerce')
            df_trend = df_trend.sort_values('years')
            valid = df_trend['total_volume'].notnull() & (df_trend['total_volume'] > 0)
            if valid.any():
                fig, ax = plt.subplots()
                ax.plot(df_trend['years'], df_trend['total_volume']/1000, marker='o', color='tab:blue')
                ax.set_title('')  # 제목 제거
                ax.set_xlabel('연도')
                ax.set_ylabel('판매량 (단위: 천대)')
                ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'{x:,.0f}K'))
                ax.grid(True, linestyle='--', alpha=0.5)
                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.info("시각화할 수 있는 연도별 판매량 데이터가 없습니다.")
        else:
            st.info("해당 조건에 해당하는 연도별 데이터가 없습니다.")

with tab3:
    if not submitted or car_type == '전체' or year == '전체':
        st.info("차종과 연도를 선택하세요. ")
    else:
        st.subheader("브랜드별 점유율")
        year_cond, _, car_type_cond = make_condition(year, '전체', car_type)
        sql_brand_share = f"""
        SELECT
            b.brand,
            SUM(a.volume) AS total_volume
        FROM car_model a
        LEFT JOIN brand_logo b ON a.brand_code = b.codes
        WHERE
            {year_cond}
            AND {car_type_cond}
        GROUP BY b.brand
        ORDER BY total_volume DESC
        """
        cursor.execute(sql_brand_share)
        brand_rows = cursor.fetchall()
        df_brand = pd.DataFrame(brand_rows)
        if not df_brand.empty and 'total_volume' in df_brand.columns:
            df_brand['total_volume'] = pd.to_numeric(df_brand['total_volume'], errors='coerce')
            valid = df_brand['total_volume'].notnull() & (df_brand['total_volume'] > 0)
            df_brand_valid = df_brand[valid].sort_values('total_volume', ascending=False)
            if len(df_brand_valid) >= 2:
                if len(df_brand_valid) > 9:
                    top9 = df_brand_valid.iloc[:9]
                    other = pd.DataFrame({
                        'brand': ['기타'],
                        'total_volume': [df_brand_valid.iloc[9:]['total_volume'].sum()]
                    })
                    pie_df = pd.concat([top9, other], ignore_index=True)
                else:
                    pie_df = df_brand_valid
                pie_df = pie_df.rename(columns={'brand': '제조사', 'total_volume': '판매량'})
                fig, ax = plt.subplots()
                ax.pie(
                    pie_df['판매량'],
                    labels=pie_df['제조사'],
                    autopct=lambda p: f'{p:.1f}%' if p > 2 else '',
                    startangle=140,
                    counterclock=False
                )
                ax.set_title('')
                st.pyplot(fig)
            else:
                st.info("시각화할 수 있는 브랜드별 판매량 데이터가 없습니다.")
        else:
            st.info("해당 조건에 해당하는 브랜드별 데이터가 없습니다.")

with tab4:
    if not submitted or car_type == '전체' or year == '전체':
        st.info("차종과 연도를 선택하세요.")
    else:
        st.subheader("월별 차종 판매량")
        year_cond, brand_cond, car_type_cond = make_condition(year, brand, car_type)
        sql_month = f"""
        SELECT
            a.years,
            a.months,
            SUM(a.volume) AS total_volume
        FROM car_model a
        LEFT JOIN brand_logo b ON a.brand_code = b.codes
        WHERE
            {year_cond}
            AND {brand_cond}
            AND {car_type_cond}
        GROUP BY a.years, a.months
        ORDER BY a.years, a.months
        """
        cursor.execute(sql_month)
        month_rows = cursor.fetchall()
        df_month = pd.DataFrame(month_rows)
        if not df_month.empty and 'total_volume' in df_month.columns:
            df_month['years'] = pd.to_numeric(df_month['years'], errors='coerce').astype('Int64')
            df_month['months'] = pd.to_numeric(df_month['months'], errors='coerce').astype('Int64')
            df_month['total_volume'] = pd.to_numeric(df_month['total_volume'], errors='coerce')
            df_month = df_month.sort_values(['years', 'months'])
            current_year = int(year)
            pivot = df_month.pivot(index='months', columns='years', values='total_volume')
            pivot.index = pivot.index.astype('Int64')
            pivot.columns = pivot.columns.astype('Int64')
            this_year = pivot.get(current_year)
            valid = this_year.notnull() & (this_year > 0) if this_year is not None else None
            if valid is not None and valid.any():
                fig, ax = plt.subplots()
                ax.bar(this_year.index[valid], this_year.values[valid], color='green')
                ax.set_xlabel('월')
                ax.set_ylabel('판매량')
                ax.set_title('')
                ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'{int(x):,}'))
                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.info("시각화할 수 있는 월별 판매량 데이터가 없습니다.")
        else:
            st.info("해당 조건에 해당하는 월별 데이터가 없습니다.")
