import pandas as pd
import streamlit as st
import pymysql
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False


from mydb.connectDB import openDB

conn=openDB()
cursor = conn.cursor(pymysql.cursors.DictCursor)

@st.cache_data(ttl=3600)
def get_fuels():
    cursor.execute("SELECT DISTINCT engine FROM car_engine_data")
    fuels = ['전체'] + sorted([row['engine'] for row in cursor.fetchall() if row['engine']])
    return fuels

years = ['전체'] + sorted(list(pd.read_sql("SELECT DISTINCT years FROM car_engine_data", conn)['years']))


fuels = get_fuels()

with st.form("filter_form"):
    col1, col2 = st.columns(2)
    with col1:
        fuel = st.selectbox('연료 선택', fuels, key='fuel_type')
    with col2:
        year = st.selectbox('연도 선택', years, key='fuel_year')
    submitted = st.form_submit_button("검색")

tab1, tab2, tab3, tab4 = st.tabs([
    "연료별 판매 비중",
    "연료별 차량 판매 추이",
    "월별 판매량",
    "연료별 누적 판매량 변화"
])

def make_condition(year, fuel):
    year_condition = "1=1" if year == '전체' else f"years = {year}"
    fuel_condition = "1=1" if fuel == '전체' else f"engine = '{fuel}'"
    return year_condition, fuel_condition

# 1. 연료별 판매 비중
with tab1:
    if not submitted or year == '전체':
        st.info("연도를 선택하세요.")
    else:
        st.subheader(f"{year}년 연료별 판매 비중")
        sql = f"""
        SELECT engine, SUM(volume) AS total_volume
        FROM car_engine_data
        WHERE years = {year}
        GROUP BY engine
        ORDER BY total_volume DESC
        """
        cursor.execute(sql)
        rows = cursor.fetchall()
        df = pd.DataFrame(rows)
        if not df.empty:
            df['total_volume'] = pd.to_numeric(df['total_volume'], errors='coerce')
            # 전년 데이터
            sql_prev = f"""
            SELECT engine, SUM(volume) AS total_volume
            FROM car_engine_data
            WHERE years = {int(year)-1}
            GROUP BY engine
            """
            cursor.execute(sql_prev)
            prev_rows = cursor.fetchall()
            df_prev = pd.DataFrame(prev_rows)
            prev_map = {}
            if not df_prev.empty:
                df_prev['total_volume'] = pd.to_numeric(df_prev['total_volume'], errors='coerce')
                prev_map = df_prev.set_index('engine')['total_volume'].to_dict()
            # 증감률 계산
            def get_change(row):
                prev = prev_map.get(row['engine'], np.nan)
                if pd.notnull(prev) and prev != 0:
                    return (row['total_volume'] - prev) / prev * 100
                else:
                    return np.nan
            df['증감률'] = df.apply(get_change, axis=1).round(1)
            total_sum = int(df['total_volume'].sum())
            # Pie chart: 라벨 겹침 방지(labeldistance, pctdistance 사용)
            fig, ax = plt.subplots()
            wedges, texts, autotexts = ax.pie(
                df['total_volume'],
                labels=df['engine'],
                autopct=lambda p: f'{p:.1f}%' if p > 2 else '',
                labeldistance=1.15,         # 라벨을 바깥쪽으로
                pctdistance=0.8,            # 퍼센트는 조금 안쪽
                startangle=140,
                counterclock=False
            )
            # 라벨 폰트 크기, 굵기 조정
            for t in texts:
                t.set_fontsize(12)
            for at in autotexts:
                at.set_fontsize(11)
            plt.tight_layout()
            ax.set_title("")
            plt.figtext(0.5, 0.01, f'총 판매 대수: {total_sum:,}대', ha='center', fontsize=12)
            st.pyplot(fig)
            # 표: 전년 대비 증감률 컬러 표시
            df = df.rename(columns={'engine': '연료', 'total_volume': '판매량'})
            def color_change(val):
                try:
                    val = float(val)
                except:
                    return ''
                if pd.isnull(val):
                    return ''
                elif val > 0:
                    return 'color: blue'
                elif val < 0:
                    return 'color: red'
                else:
                    return ''
            df['판매량(전년대비)'] = df.apply(
                lambda row: f"{int(row['판매량']):,d}" +
                            (f" ({row['증감률']:+.1f}%)" if pd.notnull(row['증감률']) else ""),
                axis=1
            )
            show_cols = ['연료', '판매량(전년대비)']
            styled_df = df[show_cols].style.applymap(
                lambda v: color_change(float(v.split('(')[-1].replace('%)','').replace('+','').replace('-','-') if '(' in v else 0))
                if '(' in v else '', subset=['판매량(전년대비)']
            )
            st.dataframe(styled_df)
        else:
            st.info(f"{year}년 연료별 데이터가 없습니다.")

# 2. 연료별 판매 추이
with tab2:
    if not submitted or fuel == '전체':
        st.info("연료를 선택하세요.")
    else:
        st.subheader(f"{fuel} 차량 판매 추이")
        year_cond, fuel_cond = make_condition('전체', fuel)
        sql = f"""
        SELECT years, SUM(volume) AS total_volume
        FROM car_engine_data
        WHERE {fuel_cond}
        GROUP BY years
        ORDER BY years
        """
        cursor.execute(sql)
        rows = cursor.fetchall()
        df = pd.DataFrame(rows)
        if not df.empty:
            df['total_volume'] = pd.to_numeric(df['total_volume'], errors='coerce')
            fig, ax = plt.subplots()
            ax.plot(df['years'], df['total_volume'], marker='o', color='tab:blue')
            ax.set_xlabel('연도')
            ax.set_ylabel('판매량')
            ax.set_title('')
            ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'{int(x):,}'))
            plt.tight_layout()
            st.pyplot(fig)
            df = df.rename(columns={'years': '연도', 'total_volume': '판매량'})
            st.dataframe(df)
        else:
            st.info("해당 조건에 해당하는 연도별 데이터가 없습니다.")
    # 전체 선택 시 연료별 꺾은선 그래프
    if submitted and fuel == '전체':
        st.subheader("전체 연료별 판매 추이")
        sql = """
        SELECT years, engine, SUM(volume) AS total_volume
        FROM car_engine_data
        GROUP BY years, engine
        ORDER BY years, engine
        """
        cursor.execute(sql)
        rows = cursor.fetchall()
        df = pd.DataFrame(rows)
        if not df.empty:
            df['total_volume'] = pd.to_numeric(df['total_volume'], errors='coerce')
            df_pivot = df.pivot(index='years', columns='engine', values='total_volume').fillna(0)
            fig, ax = plt.subplots()
            df_pivot.plot(ax=ax, marker='o')
            ax.set_xlabel('연도')
            ax.set_ylabel('판매량')
            ax.set_title('')
            ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'{int(x):,}'))
            ax.legend(title='연료')
            plt.tight_layout()
            st.pyplot(fig)
            st.dataframe(df_pivot.reset_index().rename(columns={'years': '연도'}))

# 3. 월별 판매량
with tab3:
    if not submitted or year == '전체' or fuel == '전체':
        st.info("연도와 연료를 선택하세요.")
    else:
        st.subheader(f"{year}년 {fuel} 월별 판매량")
        year_cond, fuel_cond = make_condition(year, fuel)
        sql = f"""
        SELECT months, SUM(volume) AS total_volume
        FROM car_engine_data
        WHERE {year_cond} AND {fuel_cond}
        GROUP BY months
        ORDER BY months
        """
        cursor.execute(sql)
        rows = cursor.fetchall()
        df = pd.DataFrame(rows)
        if not df.empty:
            df['total_volume'] = pd.to_numeric(df['total_volume'], errors='coerce')
            fig, ax = plt.subplots()
            ax.bar(df['months'], df['total_volume'], color='green')
            ax.set_xlabel('월')
            ax.set_ylabel('판매량')
            ax.set_title('')
            ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'{int(x):,}'))
            plt.tight_layout()
            st.pyplot(fig)
            df = df.rename(columns={'months': '월', 'total_volume': '판매량'})
            st.dataframe(df)
        else:
            st.info("해당 조건에 해당하는 월별 데이터가 없습니다.")

# 4. 연료별 누적 판매량 변화
with tab4:
    st.subheader("연료별 누적 판매량 변화")
    sql = """
    SELECT years, engine, SUM(volume) AS total_volume
    FROM car_engine_data
    GROUP BY years, engine
    ORDER BY years, engine
    """
    cursor.execute(sql)
    rows = cursor.fetchall()
    df = pd.DataFrame(rows)
    if not df.empty:
        df['total_volume'] = pd.to_numeric(df['total_volume'], errors='coerce')
        df_pivot = df.pivot(index='years', columns='engine', values='total_volume').fillna(0)
        df_cumsum = df_pivot.cumsum()
        fig, ax = plt.subplots()
        df_cumsum.plot(ax=ax, marker='o')
        ax.set_xlabel('연도')
        ax.set_ylabel('누적 판매량')
        ax.set_title('')
        ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'{int(x):,}'))
        ax.legend(title='연료')
        plt.tight_layout()
        st.pyplot(fig)
        st.dataframe(df_cumsum.reset_index().rename(columns={'years': '연도'}))
    else:
        st.info("누적 판매량 데이터가 없습니다.")
