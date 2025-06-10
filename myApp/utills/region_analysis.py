import streamlit as st
import pandas as pd
import pymysql
import plotly.express as px
from mydb.connectDB import openDB

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

conn=openDB()
df = pd.read_sql(query, conn)
conn.close()

# 📌 날짜 컬럼 생성
df['date'] = pd.to_datetime(df['years'].astype(str) + '-' + df['months'].astype(str) + '-01')

# ================================
# ✅ 사이드바 필터 구성 (아코디언 형태)
# ================================
with st.sidebar.expander("🔍 필터 선택", expanded=True):

    if not df.empty:
        # 연도 슬라이더 (데이터에 years 컬럼 있어야 함)
        if 'years' in df.columns and pd.api.types.is_numeric_dtype(df['years']):
            min_year, max_year = int(df['years'].min()), int(df['years'].max())
            year_range = st.slider("연도 범위", min_value=min_year, max_value=max_year,
                                value=(min_year, max_year), step=1)
        else:
            st.warning("연도 데이터가 없거나 형식이 올바르지 않습니다.")
            # 데이터프레임이 비어있지 않다면 최소/최대값 사용, 아니면 0,0
            year_range = (df['years'].min() if 'years' in df.columns and not df.empty else 0,
                            df['years'].max() if 'years' in df.columns and not df.empty else 0)


        # 도시 선택 (데이터에 city_1 컬럼 있어야 함)
        if 'city_1' in df.columns:
            city_options = sorted(df['city_1'].unique())
            # --- 👇 이 부분을 수정했어! 👇 ---
            # 기본 선택 도시 목록 정의
            default_cities_list = ['서울', '경기', '대전', '부산', '제주']
            # 실제 city_options에 있는 도시만 기본으로 선택되도록 필터링
            initial_selected_cities = [city for city in default_cities_list if city in city_options]
            # --- 👆 이 부분을 수정했어! 👆 ---

            selected_cities = st.multiselect("도시 선택", options=city_options, default=initial_selected_cities)
        else:
            st.warning("도시 (city_1) 데이터가 없습니다.")
            selected_cities = []

        # 시군구 선택 (데이터에 city_1, city_2 컬럼 있어야 함)
        if 'city_1' in df.columns and 'city_2' in df.columns and selected_cities:
            # 선택된 도시에 따라 시군구 옵션 필터링
            filtered_districts_options = df[df['city_1'].isin(selected_cities)]['city_2'].unique()
            # default 값 설정 시, 선택된 도시 내에 있는 시군구만 기본으로 선택되도록 조정
            default_districts = sorted(filtered_districts_options) if not filtered_districts_options.size == 0 else []
            selected_districts = st.multiselect("시군구 선택", options=sorted(filtered_districts_options),
                                                default=default_districts)
        else:
            st.warning("시군구 (city_2) 데이터가 없거나 도시 선택이 필요합니다.")
            selected_districts = []


        # 차량 종류 선택 (데이터에 car_type_name 컬럼 있어야 함)
        if 'car_type_name' in df.columns:
            car_type_options = sorted(df['car_type_name'].unique())
            selected_car_types = st.multiselect("차량 종류", car_type_options,
                                                default=car_type_options)
        else:
            st.warning("차량 종류 (car_type_name) 데이터가 없습니다.")
            selected_car_types = []

    else:
        st.warning("데이터를 불러오지 못했습니다. 필터를 설정할 수 없습니다.")
        year_range = (0, 0)
        selected_cities = []
        selected_districts = []
        selected_car_types = []


# ✅ 전체 필터 적용 (필터링 조건이 유효한 경우에만)
if not df.empty and year_range and selected_cities and selected_districts and selected_car_types:
    # years와 date 컬럼이 모두 존재하는지 확인
    if 'years' in df.columns and 'date' in df.columns:
        filtered = df[
            (df['years'] >= year_range[0]) &
            (df['years'] <= year_range[1]) &
            (df['city_1'].isin(selected_cities)) &
            (df['city_2'].isin(selected_districts)) &
            (df['car_type_name'].isin(selected_car_types))
        ].copy() # SettingWithCopyWarning 방지를 위해 .copy() 추가

        # 날짜 컬럼 기준으로 정렬 (트렌드 차트를 위해)
        filtered = filtered.sort_values('date')
    else:
        st.error("🚨 필터링에 필요한 'years' 또는 'date' 컬럼이 데이터에 없습니다.")
        filtered = pd.DataFrame() # 필요한 컬럼 없으면 빈 데이터프레임

else:
    filtered = pd.DataFrame() # 데이터가 없거나 필터 조건이 유효하지 않을 경우 빈 DataFrame 생성
    if not df.empty: # 데이터 자체는 있지만 필터 결과가 없는 경우
        st.info("선택된 필터 조건에 맞는 데이터가 없습니다.")
    # 데이터가 처음부터 비어있다면 위의 초기 로드 오류 메시지가 나올 것임.


# ================================
# ✅ 전체 분석 현황 (KPI 카드)
# KPI 카드는 필터링된 전체 데이터를 기준으로 보여줌
# ================================
st.subheader("📊 전체 분석 현황")
col1, col2, col3 = st.columns(3)
if not filtered.empty:
    total_volume_sum = filtered['total_volume'].sum()
    col1.metric("총 등록 대수", f"{total_volume_sum:,} 대")

    # 최다 차량 종류 (filtered 데이터 기준)
    # car_type_name 컬럼이 있는지 확인
    if 'car_type_name' in filtered.columns:
        top_car_type_overall = filtered.groupby('car_type_name')['total_volume'].sum().idxmax()
        col2.metric("전체 최다 차량 종류", top_car_type_overall)
    else:
        col2.metric("전체 최다 차량 종류", "데이터 부족")


    # 전년 대비 변화율 (filtered 데이터 기준)
    # years, total_volume 컬럼이 모두 있는지 확인
    if 'years' in filtered.columns and 'total_volume' in filtered.columns:
        yearly_sum_overall = filtered.groupby('years')['total_volume'].sum()
        if len(yearly_sum_overall) >= 2:
            # 마지막 연도 데이터가 있는지 확인
            last_year_volume = yearly_sum_overall.iloc[-1]
            second_last_year_volume = yearly_sum_overall.iloc[-2]
            if second_last_year_volume != 0: # 0으로 나누는 경우 방지
                delta_overall = last_year_volume - second_last_year_volume
                rate_overall = (delta_overall / second_last_year_volume) * 100
                col3.metric("전년 대비 변화율 (전체)", f"{rate_overall:.2f}%", delta=f"{delta_overall:+,} 대")
            else:
                col3.metric("전년 대비 변화율 (전체)", "전년도 데이터 부족 또는 0")
        else:
            col3.metric("전년 대비 변화율 (전체)", "데이터 부족")
    else:
        col3.metric("전년 대비 변화율 (전체)", "데이터 부족")

else:
    col1.metric("총 등록 대수", "0 대")
    col2.metric("전체 최다 차량 종류", "없음")
    col3.metric("전년 대비 변화율 (전체)", "없음")

st.write("----") # KPI와 탭 구분선

# ================================
# ✅ 상세 분석 탭 구성
# 여기에 각 그래프를 담을 탭을 만든다!
# ================================
st.subheader("✨ 상세 분석 차트")

# 탭 이름 정의
tab_titles = ["📈 연도별 전체 추이", "📍 도시별 분포", "🚙 시도별 차량 종류 분포"]

# 탭 생성
tabs = st.tabs(tab_titles)

# 탭 1: 연도별 전체 추이
with tabs[0]:
    st.write("### 📈 연도별 차량 등록 추이 (전체 필터 기준)")
    # 필요한 컬럼 있는지 다시 확인
    if not filtered.empty and 'date' in filtered.columns and 'car_type_name' in filtered.columns and 'total_volume' in filtered.columns:
        # 트렌드 차트 (전체 필터 기준)
        trend_chart_data = filtered.groupby(['date', 'car_type_name'])['total_volume'].sum().reset_index()
        fig_trend = px.line(trend_chart_data, x='date', y='total_volume', color='car_type_name', markers=True,
                            labels={'total_volume': '등록 대수', 'date': '날짜', 'car_type_name': '차량 종류'})
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("차트 생성에 필요한 데이터가 없습니다.")

# 탭 2: 도시별 등록 분포
with tabs[1]:
    st.write("### 📍 도시별 차량 등록 분포 (전체 필터 기준)")
    # 필요한 컬럼 있는지 다시 확인
    if not filtered.empty and 'city_1' in filtered.columns and 'total_volume' in filtered.columns:
        # 도시별 분포 차트 (전체 필터 기준)
        region_chart_data = filtered.groupby('city_1')['total_volume'].sum().reset_index()
        fig_region = px.bar(region_chart_data, x='city_1', y='total_volume', color='city_1',
                            labels={'city_1': '도시', 'total_volume': '등록 대수'})
        st.plotly_chart(fig_region, use_container_width=True)
    else:
        st.info("차트 생성에 필요한 데이터가 없습니다.")


# 탭 3: 시도별 차량 종류 등록 분포
with tabs[2]:
    st.write("### 🚙 시도별 차량 종류 등록 분포 (전체 필터 기준)")
    # 필요한 컬럼 있는지 다시 확인
    if not filtered.empty and 'city_1' in filtered.columns and 'car_type_name' in filtered.columns and 'total_volume' in filtered.columns:
        # 시도별 차량 종류 분포 차트 (전체 필터 기준)
        type_region_chart_data = (
            filtered.groupby(['city_1', 'car_type_name'])['total_volume']
            .sum()
            .reset_index()
        )

        fig_type_region = px.bar(
            type_region_chart_data,
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
        st.plotly_chart(fig_type_region, use_container_width=True)
    else:
        st.info("차트 생성에 필요한 데이터가 없습니다.")

