import streamlit as st
import pymysql
import pandas as pd

@st.cache_data
def load_data():
    conn = pymysql.connect(
        host='',
        user='',
        password='',
        db='',
        port=,
        charset=''
    )
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

df = load_data()
st.title('FAQ 조회시스템')

# -- 1. 제조사/카테고리 선택 or 검색어 입력 --
mfr_ids = df['mfr_id'].unique()
brands = df.drop_duplicates('mfr_id')[['mfr_id', 'brand']].set_index('mfr_id')['brand'].to_dict()
brand_options = [f"{brands[mid]} ({mid})" for mid in mfr_ids if pd.notnull(brands[mid])]
brand_option_map = {f"{brands[mid]} ({mid})": mid for mid in mfr_ids if pd.notnull(brands[mid])}
selected_brand_str = st.selectbox("제조사를 선택하세요", ["- 선택 안함 -"] + brand_options)
filtered = df

if selected_brand_str != "- 선택 안함 -":
    selected_brand_id = brand_option_map[selected_brand_str]
    filtered = filtered[filtered['mfr_id'] == selected_brand_id]
    categories = filtered['categories'].dropna().unique().tolist()
    selected_category = st.selectbox("카테고리(소분류)를 선택하세요", ["- 전체 -"] + categories)
    if selected_category != "- 전체 -":
        filtered = filtered[filtered['categories'] == selected_category]
    keyword = st.text_input('질문에 포함된 단어로 추가 검색(선택)')
    if keyword:
        filtered = filtered[filtered['question'].str.contains(keyword, case=False, na=False)]
else:
    keyword = st.text_input('질문에 포함된 단어를 입력하세요')
    if keyword:
        filtered = filtered[filtered['question'].str.contains(keyword, case=False, na=False)]
    else:
        filtered = pd.DataFrame()

# -- 2. 페이지네이션 (질문이 많을 때만) --
PAGE_SIZE = st.selectbox("한 페이지 질문 수", [5, 10, 20], index=0)
total = len(filtered)
if total > 0:
    num_pages = (total - 1) // PAGE_SIZE + 1
    page = st.number_input("페이지", min_value=1, max_value=num_pages, step=1)
    start = (page - 1) * PAGE_SIZE
    end = min(start + PAGE_SIZE, total)
    questions = filtered.iloc[start:end].reset_index(drop=True)
    st.write(f"{total}건 중 {start+1}~{end}번 질문 (총 {num_pages}페이지)")
    # 3. 카드형 큼직하게 보여주기 + 클릭시 답변(Expander)
    for i, row in questions.iterrows():
        with st.expander(f"Q. {row['question']}", expanded=False):
            st.markdown(f"**[{row['brand']}] [{row['categories']}]**")
            st.markdown(row['answer'])
else:
    st.info("질문을 검색하거나 제조사/카테고리를 선택하세요.")