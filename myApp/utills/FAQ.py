import streamlit as st
import pymysql
import pandas as pd
from mydb.connectDB import openDB

def faq_info():
    conn = openDB()
    query = """
    SELECT
        F.mfr_id,
        M.brand,
        F.categories,
        F.question,
        F.answer
    FROM FAQ F
    LEFT JOIN brand_logo M
        ON F.mfr_id = M.codes
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

df = faq_info()

# 브랜드별 분리
brand_list = df['brand'].dropna().unique().tolist()
brand_list.sort()

# 탭: 브랜드
brand_tabs = st.tabs(brand_list)

for i, brand in enumerate(brand_list):
    with brand_tabs[i]:
        brand_df = df[df['brand'] == brand]
        category_list = brand_df['categories'].dropna().unique().tolist()
        category_list.sort()

        # 카테고리 하위 탭
        if category_list:
            category_tabs = st.tabs(category_list)
            for j, category in enumerate(category_list):
                with category_tabs[j]:
                    category_df = brand_df[brand_df['categories'] == category]

                    # 검색 입력창 (카테고리 탭 아래로 이동)
                    st.markdown("### 🔍 질문 키워드 검색")
                    keyword = st.text_input("질문에 포함된 단어를 입력하세요", key=f"kw_{brand}_{category}")
                    if keyword:
                        filtered_df = category_df[category_df['question'].str.contains(keyword, case=False, na=False)]
                    else:
                        filtered_df = category_df

                    # 페이지네이션
                    total = len(filtered_df)
                    PAGE_SIZE = 5
                    if total > 0:
                        num_pages = (total - 1) // PAGE_SIZE + 1
                        page = st.number_input(f"{category} 페이지", min_value=1, max_value=num_pages, step=1, key=f"pg_{brand}_{category}")
                        start = (page - 1) * PAGE_SIZE
                        end = min(start + PAGE_SIZE, total)
                        sliced = filtered_df.iloc[start:end].reset_index(drop=True)

                        st.markdown(f"**총 {total}건 중 {start+1}~{end}건 표시 (총 {num_pages} 페이지)**")

                        for _, row in sliced.iterrows():
                            with st.expander(f"Q. {row['question']}", expanded=False):
                                st.markdown(f"**[{row['brand']}] [{row['categories']}]**")
                                st.markdown(row['answer'])
                    else:
                        st.info("해당 카테고리에 검색 결과가 없습니다.")
        else:
            st.warning("카테고리 정보가 없습니다.")

