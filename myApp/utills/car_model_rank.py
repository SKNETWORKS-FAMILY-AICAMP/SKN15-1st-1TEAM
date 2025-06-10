import streamlit as st
import pandas as pd
import pymysql
from mydb.connectDB import openDB

# 연령대별 선호 모델 순위
def model_ranking():

    conn = None
    cursor = None

    try:
        conn=openDB()
        cursor = conn.cursor()

        select_age_sql = """
            SELECT
                codes,
                `name`
            FROM age_group
            ORDER BY codes;
        """
        cursor.execute(select_age_sql)
        age_data = cursor.fetchall() 

        age_options = [name for code, name in age_data]
        age_code_map = {name: code for code, name in age_data}


        tabs = st.tabs(age_options)

        for i, tab_name in enumerate(age_options):
            with tabs[i]:
                selected_age_text = tab_name

                selected_age_code_for_query = age_code_map.get(selected_age_text, None)

                # 전체 건수 구하기
                if selected_age_text == "전체":
                    count_sql = "SELECT SUM(purchase_count) FROM car_365;"
                    cursor.execute(count_sql)
                else:
                    count_sql = "SELECT SUM(purchase_count) FROM car_365 WHERE age_group_code = %s;"
                    cursor.execute(count_sql, (selected_age_code_for_query,))

                total_count_result = cursor.fetchone()
                total_count_from_db = total_count_result[0] if total_count_result and total_count_result[0] is not None else 0

                if selected_age_text == "전체":
                    select_sql = """
                        SELECT
                            DENSE_RANK() OVER(ORDER BY model_engine_totals.model_engine_total_purchase_count DESC) as overall_ranking, -- 조합의 구매수 순위
                            model_engine_totals.brand AS 브랜드,       -- 브랜드
                            model_engine_totals.model_name AS 모델명,     -- 모델명
                            model_engine_totals.engine_name AS 배기량,     -- 배기량 이름
                            model_engine_totals.model_engine_total_purchase_count AS 구매수 -- 해당 조합의 총 구매수
                        FROM (
                            SELECT
                                c.brand,
                                c.model_name,
                                ed.`name` AS engine_name,
                                SUM(c.purchase_count) AS model_engine_total_purchase_count 
                            FROM car_365 c
                            INNER JOIN engine_displacement ed
                                ON c.engine_displacement_code = ed.codes
                            GROUP BY c.brand, c.model_name, engine_name
                        ) AS model_engine_totals
                        ORDER BY overall_ranking
                        LIMIT 10;
                    """
                    cursor.execute(select_sql)
                else:
                    select_sql = """
                        SELECT
                            DENSE_RANK() OVER(ORDER BY model_engine_totals.model_engine_total_purchase_count DESC) as overall_ranking, -- 조합의 구매수 순위
                            model_engine_totals.brand AS 브랜드,       -- 브랜드
                            model_engine_totals.model_name AS 모델명,     -- 모델명
                            model_engine_totals.engine_name AS 배기량,     -- 배기량 이름
                            model_engine_totals.model_engine_total_purchase_count AS 구매수 -- 해당 조합의 총 구매수
                        FROM (
                            SELECT
                                c.brand,
                                c.model_name,
                                ed.`name` AS engine_name,
                                SUM(c.purchase_count) AS model_engine_total_purchase_count 
                            FROM car_365 c
                            INNER JOIN engine_displacement ed
                                ON c.engine_displacement_code = ed.codes 
                            WHERE c.age_group_code = %s
                            GROUP BY c.brand, c.model_name, engine_name
                        ) AS model_engine_totals
                        ORDER BY overall_ranking
                        LIMIT 10;
                    """
                    cursor.execute(select_sql, (selected_age_code_for_query,))
                select_data = cursor.fetchall()

                if not select_data: 
                    st.write(f"선택하신 **{selected_age_text}**에 대한 모델 데이터가 없습니다.")
                else:                
                    st.write(f"차량 총 개수: {total_count_from_db:,}")

                    df_result = pd.DataFrame(select_data, columns=['순위', '브랜드', '모델명', '배기량', '총 구매량'])
                    df_result['순위'] = df_result['순위'].astype(str) + '위'

                    styled_df = df_result.style.format({
                        '총 구매량': '{:,.0f}'.format
                    })

                    st.dataframe(
                        styled_df,
                        hide_index=True,
                    )

    except pymysql.Error as e:
        st.error(f"데이터베이스 연결 또는 쿼리 실행 중 오류 발생: {e}")
    except Exception as e:
        st.error(f"예상치 못한 오류 발생: {e}")
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.open:
            conn.close()
