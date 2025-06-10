import streamlit as st
import pandas as pd
import pymysql
import plotly.express as px

st.set_page_config(layout="wide")
st.title("🚗 지역별 차량 등록 트렌드 분석")

# 📌 데이터 조회
query = """
SELECT
    D.years,
    D.months,
    D.city_1,
    D.city_2,
    T.name AS car_type_name,
    SUM(D.volume) AS total_volume
FROM
    car_region_type_data D
JOIN
    car_type T ON D.carType = T.codes
GROUP BY
    D.years, D.months, D.city_1, D.city_2, T.name
ORDER BY
    D.years, D.months, D.city_1, D.city_2, T.name;
"""

df = pd.read_sql(query, conn)
conn.close()

# 📌 날짜 컬럼 생성
df['date'] = pd.to_datetime(df['years'].astype(str) + '-' + df['months'].astype(str) + '-01')

# ================================
# ✅ 사이드바 필터 구성 (아코디언 형태)
# ================================
with st.sidebar.expander("🔍 필터 선택", expanded=True):

    min_year, max_year = int(df['years'].min()), int(df['years'].max())
    year_range = st.slider("연도 범위", min_value=min_year, max_value=max_year,
                           value=(min_year, max_year), step=1)

    city_options = sorted(df['city_1'].unique())
    selected_cities = st.multiselect("도시 선택", options=city_options, default=city_options)

    filtered_districts = df[df['city_1'].isin(selected_cities)]['city_2'].unique()
    selected_districts = st.multiselect("시군구 선택", options=sorted(filtered_districts),
                                        default=sorted(filtered_districts))

    car_types = st.multiselect("차량 종류", sorted(df['car_type_name'].unique()),
                               default=sorted(df['car_type_name'].unique()))

# ✅ 전체 필터 적용
filtered = df[
    (df['years'] >= year_range[0]) &
    (df['years'] <= year_range[1]) &
    (df['city_1'].isin(selected_cities)) &
    (df['city_2'].isin(selected_districts)) &
    (df['car_type_name'].isin(car_types))
]

# ================================
# ✅ KPI 카드
# ================================
col1, col2, col3 = st.columns(3)
col1.metric("총 등록 대수", f"{filtered['total_volume'].sum():,} 대")

if not filtered.empty:
    top_car_type = filtered.groupby('car_type_name')['total_volume'].sum().idxmax()
    col2.metric("최다 차량 종류", top_car_type)
    yearly_sum = filtered.groupby('years')['total_volume'].sum()
    if len(yearly_sum) >= 2:
        delta = yearly_sum.iloc[-1] - yearly_sum.iloc[-2]
        rate = (delta / yearly_sum.iloc[-2]) * 100
        col3.metric("전년 대비 변화율", f"{rate:.2f}%", delta=f"{delta:+,} 대")
    else:
        col3.metric("전년 대비 변화율", "데이터 부족")
else:
    col2.metric("최다 차량 종류", "없음")
    col3.metric("전년 대비 변화율", "없음")

# ================================
# ✅ 트렌드 차트
# ================================
st.subheader("📈 연도별 차량 등록 추이")
if not filtered.empty:
    trend_chart = filtered.groupby(['date', 'car_type_name'])['total_volume'].sum().reset_index()
    fig = px.line(trend_chart, x='date', y='total_volume', color='car_type_name', markers=True,
                  labels={'total_volume': '등록 대수', 'date': '날짜', 'car_type_name': '차량 종류'})
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("선택된 조건에 해당하는 데이터가 없습니다.")

# ================================
# ✅ 도시별 등록 분포
# ================================
st.subheader("📍 도시별 차량 등록 분포")
if not filtered.empty:
    region_chart = filtered.groupby('city_1')['total_volume'].sum().reset_index()
    fig2 = px.bar(region_chart, x='city_1', y='total_volume', color='city_1',
                  labels={'city_1': '도시', 'total_volume': '등록 대수'})
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("도시별 차트 데이터를 찾을 수 없습니다.")

# ================================
# ✅ 시도별 차량 종류 등록 분포
# ================================
st.subheader("🚙 시도별 차량 종류 등록 분포")
if not filtered.empty:
    type_region_chart = (
        filtered.groupby(['city_1', 'car_type_name'])['total_volume']
        .sum()
        .reset_index()
    )

    fig3 = px.bar(
        type_region_chart,
        x='city_1',
        y='total_volume',
        color='car_type_name',
        barmode='group',
        labels={
            'city_1': '도시',
            'car_type_name': '차량 종류',
            'total_volume': '등록 대수'
        },
        title="시도별 차량 종류별 등록 대수"
    )

    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("차량 종류별 분포 데이터를 찾을 수 없습니다.")
