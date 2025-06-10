import streamlit as st
import pandas as pd
import pymysql
import matplotlib.pyplot as plt
import seaborn as sns
import platform
from mydb.connectDB import openDB


st.header("차량 등록대수 연간 누적 / 증가 Top 3 (용도별 / 차종별 기준)")


# 한글 폰트 설정
if platform.system() == 'Windows':
    plt.rcParams['font.family'] = 'Malgun Gothic'  # Windows: 맑은 고딕
else:  # Linux 등
    plt.rcParams['font.family'] = 'NanumGothic'

# 마이너스 깨짐 방지
plt.rcParams['axes.unicode_minus'] = False

# 매핑 정보
usage_map = {1: "자가용", 2: "영업용", 3: "관용"}
type_map = {1: "승용", 2: "승합", 3: "특수", 4: "화물"}

# DB 연결 함수
@st.cache_data
def get_data(query):
    conn = openDB()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# 쿼리들
query_usage_total = """
SELECT years, city_1, city_2, carUsage, SUM(volume) AS total_volume
FROM car_region_type_data
WHERE months = 1 AND years BETWEEN 2020 AND 2024
GROUP BY years, city_1, city_2, carUsage
"""

query_usage_diff = """
WITH monthly_base AS (
  SELECT years, city_1, city_2, carUsage,
         SUM(volume) AS volume
  FROM car_region_type_data
  WHERE months = 1 AND years BETWEEN 2020 AND 2024
  GROUP BY years, city_1, city_2, carUsage
)
SELECT a.years, a.city_1, a.city_2, a.carUsage,
       (a.volume - b.volume) AS diff_volume
FROM monthly_base a
JOIN monthly_base b
  ON a.city_1 = b.city_1 AND a.city_2 = b.city_2 AND a.carUsage = b.carUsage
  AND a.years = b.years + 1
"""

query_type_total = """
SELECT years, city_1, city_2, carType, SUM(volume) AS total_volume
FROM car_region_type_data
WHERE months = 1 AND years BETWEEN 2020 AND 2024
GROUP BY years, city_1, city_2, carType
"""

query_type_diff = """
WITH monthly_base AS (
  SELECT years, city_1, city_2, carType,
         SUM(volume) AS volume
  FROM car_region_type_data
  WHERE months = 1 AND years BETWEEN 2020 AND 2024
  GROUP BY years, city_1, city_2, carType
)
SELECT a.years, a.city_1, a.city_2, a.carType,
       (a.volume - b.volume) AS diff_volume
FROM monthly_base a
JOIN monthly_base b
  ON a.city_1 = b.city_1 AND a.city_2 = b.city_2 AND a.carType = b.carType
  AND a.years = b.years + 1
"""

# 데이터 로딩

df_usage_total = get_data(query_usage_total)

df_usage_diff = get_data(query_usage_diff)
df_type_total = get_data(query_type_total)
df_type_diff = get_data(query_type_diff)

# 탭 UI
tab1, tab2, tab3, tab4 = st.tabs(["용도 누적", "용도 증가", "차종 누적", "차종 증가"])

# --- 탭1: 용도 누적 ---
with tab1:
    df = df_usage_total.copy()
    df['구분'] = df['carUsage'].map(usage_map)
    df.rename(columns={"years": "연도", "total_volume": "누적대수"}, inplace=True)
    selected = st.selectbox("용도 선택", sorted(df['구분'].unique()), key="usage_total")
    filtered = df[df['구분'] == selected]
    result_rows = []
    for year, group in filtered.groupby("연도"):
        top3 = group.sort_values("누적대수", ascending=False).head(3)
        for rank, (_, row) in enumerate(top3.iterrows(), start=1):
            result_rows.append({
                "연도": year, "순위": rank,
                "시도": row["city_1"], "시군구": row["city_2"],
                "누적대수": row["누적대수"]
            })
    result_df = pd.DataFrame(result_rows)
    st.dataframe(result_df)
    st.subheader(f"{selected} - 연도별 누적 등록대수 Top 3 지역")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=result_df, x="연도", y="누적대수", hue="순위", ax=ax)

    st.pyplot(fig)

# --- 탭2: 용도 증가 ---
with tab2:
    df = df_usage_diff.copy()
    df['구분'] = df['carUsage'].map(usage_map)
    df.rename(columns={"years": "연도", "diff_volume": "증가대수"}, inplace=True)
    selected = st.selectbox("용도 선택", sorted(df['구분'].unique()), key="usage_diff")
    filtered = df[df['구분'] == selected]
    result_rows = []
    for year, group in filtered.groupby("연도"):
        top3 = group.sort_values("증가대수", ascending=False).head(3)
        for rank, (_, row) in enumerate(top3.iterrows(), start=1):
            result_rows.append({
                "연도": year, "순위": rank,
                "시도": row["city_1"], "시군구": row["city_2"],
                "증가대수": row["증가대수"]
            })
    result_df = pd.DataFrame(result_rows)
    st.dataframe(result_df)
    st.subheader(f"{selected} - 연도별 증가 등록대수 Top 3 지역")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=result_df, x="연도", y="증가대수", hue="순위", ax=ax)

    st.pyplot(fig)

# --- 탭3: 차종 누적 ---
with tab3:
    df = df_type_total.copy()
    df['구분'] = df['carType'].map(type_map)
    df.rename(columns={"years": "연도", "total_volume": "누적대수"}, inplace=True)
    selected = st.selectbox("차종 선택", sorted(df['구분'].unique()), key="type_total")
    filtered = df[df['구분'] == selected]
    result_rows = []
    for year, group in filtered.groupby("연도"):
        top3 = group.sort_values("누적대수", ascending=False).head(3)
        for rank, (_, row) in enumerate(top3.iterrows(), start=1):
            result_rows.append({
                "연도": year, "순위": rank,
                "시도": row["city_1"], "시군구": row["city_2"],
                "누적대수": row["누적대수"]
            })
    result_df = pd.DataFrame(result_rows)
    st.dataframe(result_df)
    st.subheader(f"{selected} - 연도별 누적 등록대수 Top 3 지역")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=result_df, x="연도", y="누적대수", hue="순위", ax=ax)

    st.pyplot(fig)

# --- 탭4: 차종 증가 ---
with tab4:
    df = df_type_diff.copy()
    df['구분'] = df['carType'].map(type_map)
    df.rename(columns={"years": "연도", "diff_volume": "증가대수"}, inplace=True)
    selected = st.selectbox("차종 선택", sorted(df['구분'].unique()), key="type_diff")
    filtered = df[df['구분'] == selected]
    result_rows = []
    for year, group in filtered.groupby("연도"):
        top3 = group.sort_values("증가대수", ascending=False).head(3)
        for rank, (_, row) in enumerate(top3.iterrows(), start=1):
            result_rows.append({
                "연도": year, "순위": rank,
                "시도": row["city_1"], "시군구": row["city_2"],
                "증가대수": row["증가대수"]
            })
    result_df = pd.DataFrame(result_rows)
    st.dataframe(result_df)
    st.subheader(f"{selected} - 연도별 증가 등록대수 Top 3 지역")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=result_df, x="연도", y="증가대수", hue="순위", ax=ax)

    st.pyplot(fig)