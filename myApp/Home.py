import streamlit as st
from streamlit_option_menu import option_menu

import pandas as pd

# 페이지 기본 설정
st.set_page_config(
    page_title="자동차 선호 트렌드 분석 시스템",
    page_icon="🚗",
    layout="wide"
)

# 스타일 설정 (글씨체/색상/정렬)
st.markdown("""
    <style>
    /* 메인 메뉴 타이틀 */
    .sidebar-title {
        font-size: 18px;
        font-weight: 600;
        color: #1a7ee6;  /* 원하는 색상 */
        padding: 10px 0 5px 15px;  /* 약간 왼쪽 들여쓰기 */
    }

    /* 오른쪽 정렬용 */
    .sidebar-footer {
        text-align: right;
        padding: 20px 15px 0 0;
        font-size: 13px;
        color: #999999;
    }
    </style>
""", unsafe_allow_html=True)

menu_list=["홈", "별별 랭킹", '선호 트렌드 분석', 'FAQ' ]

# 1. 메인메뉴 - 사이드바
with st.sidebar:
    st.title("메뉴")
    main_selected = option_menu("", menu_list, 
                            icons=['house', 'bar-chart', 'graph-up-arrow','question-circle-fill'], 
                            menu_icon="list", 
                            default_index=0,
                            styles={
                            "container": {"padding": "0!important", "background-color": "#fafafa"},
                            "icon": {"color": "black", "font-size": "20px"},
                            "nav-link": {"font-size": "18px", "text-align": "left", "margin":"0px", "--hover-color": "#eee", "color": "black"},
                            "nav-link-selected": {"background-color": "#a3dfff"}
                            })
    st.markdown('<div class="sidebar-footer">Made By. 처음아니조 @2025.06.</div>', unsafe_allow_html=True)


# 1. PAGE: HOME
if main_selected==menu_list[0]:
    st.title(":house_with_garden: Home Page")
    st.write("이곳은 홈 화면입니다.")


# 2. PAGE: RANKING
ranking_list=["브랜드별",  "모델별", '엔진별']
if main_selected==menu_list[1]:
    # 타이틀
    st.title(f":trophy: {menu_list[1]} ⭐")
    
    # 보조 메뉴
    selected_ranking = option_menu(None, ranking_list, 
        icons=['flag-fill', "car-front-fill", 'battery-charging'], 
        menu_icon="cast", default_index=0, orientation="horizontal",
        styles={
                "container": {"padding": "0!important", "background-color": "#fafafa"},
                "icon": {"color": "black", "font-size": "20px"},
                "nav-link": {"font-size": "18px", "text-align": "left", "margin":"0px", "--hover-color": "#eee", "color": "black"},
                "nav-link-selected": {"background-color": "#a3dfff"}
                })
    
    # 보조 메뉴별 화면
    if selected_ranking==ranking_list[0]:
        st.write(f"{ranking_list[0]} 조회")
        st.write("연령대별 선호 브랜드 순위 페이지입니다.")


    if selected_ranking==ranking_list[1]:
        st.write(f"{ranking_list[1]} 조회")
        st.write("연령대별 선호 모델 순위 페이지입니다.")
    

    if selected_ranking==ranking_list[2]:
        st.write(f"{ranking_list[2]} 조회")
        st.write("연령대별 선호 연료 순위 페이지입니다.")
    


# 3. PAGE: ANALYSIS
analysis_list=["연령별", "브랜드별",  "모델별", '엔진별', "지역별"]
if main_selected==menu_list[2]:
    # 타이틀
    st.title(f":bar_chart: {menu_list[2]}")

    # 보조 메뉴
    selected_analysis = option_menu(None, analysis_list, 
        icons=['people-fill', 'flag-fill', "car-front-fill", 'battery-charging', 'geo-alt-fill'], 
        menu_icon="cast", default_index=0, orientation="horizontal",
        styles={
                "container": {"padding": "0!important", "background-color": "#fafafa"},
                "icon": {"color": "black", "font-size": "20px"},
                "nav-link": {"font-size": "18px", "text-align": "left", "margin":"0px", "--hover-color": "#eee", "color": "black"},
                "nav-link-selected": {"background-color": "#a3dfff"}
                })

    # 보조 메뉴별 화면
    if selected_analysis==analysis_list[0]:
        st.write(f"{analysis_list[0]} 분석")
        st.write("연령대별 분석 페이지입니다.")


    if selected_analysis==analysis_list[1]:
        st.write(f"{analysis_list[1]} 분석")
        st.write("브랜드별 분석 페이지입니다.")
    

    if selected_analysis==analysis_list[2]:
        st.write(f"{analysis_list[2]} 분석")
        st.write("모델별 분석 페이지입니다.")
    

    if selected_analysis==analysis_list[3]:
        st.write(f"{analysis_list[3]} 분석")
        st.write("엔진별 분석 페이지입니다.")
    

    if selected_analysis==analysis_list[4]:
        st.write(f"{analysis_list[4]} 분석")
        st.write("지역별 분석 페이지입니다.")




# 4. PAGE: FAQ
brand_list=["전체", "현대", "기아", "르노", "벤츠", "쉐보레", "제네시스"]
if main_selected==menu_list[3]:
    st.title(f":loudspeaker: {menu_list[3]}")

    col1, col2 = st.columns([2, 1], vertical_alignment="bottom")
    with col1:
        search_keyword = st.text_input("검색어 입력")
    with col2:
        search_button = st.button("검색")

    # 보조 메뉴
    selected_brand = option_menu(None, brand_list, 
        #icons=['house', 'cloud-upload', "list-task", 'gear'], 
        menu_icon="cast", default_index=0, orientation="horizontal",
        styles={
                "container": {"padding": "0!important", "background-color": "#fafafa"},
                "icon": {"color": "black", "font-size": "20px"},
                "nav-link": {"font-size": "18px", "text-align": "left", "margin":"0px", "--hover-color": "#eee", "color": "black"},
                "nav-link-selected": {"background-color": "#a3dfff"}
                })

    # 보조 메뉴별 화면
    if selected_brand==brand_list[0]:
        st.write(f"{brand_list[0]} 분석")


    if selected_brand==brand_list[1]:
        st.write(f"{brand_list[1]} 분석")
    

    if selected_brand==brand_list[2]:
        st.write(f"{brand_list[2]} 분석")
    

    if selected_brand==brand_list[3]:
        st.write(f"{brand_list[3]} 분석")
    

    if selected_brand==brand_list[4]:
        st.write(f"{brand_list[4]} 분석")
    

    if selected_brand==brand_list[5]:
        st.write(f"{brand_list[5]} 분석")


    if selected_brand==brand_list[6]:
        st.write(f"{brand_list[6]} 분석")



