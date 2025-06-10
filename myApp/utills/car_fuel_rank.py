import streamlit as st
import pandas as pd
import pymysql

# 연령대별 선호 연료 순위
def fuel_ranking():

    db_config = {
        'host': '',
        'user': '',
        'passwd': '',
        'database': '',
        'port': ''
    }

    conn = None
    cursor = None

    try:
        conn = pymysql.connect(**db_config)
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
                            RANK() OVER (ORDER BY total_purchase_count DESC) as ranking
                        , fuel_name
                        , total_purchase_count AS total
                        FROM (
                            SELECT
                                ft.name AS fuel_name
                                , SUM(c.purchase_count) AS total_purchase_count
                            FROM car_365 c
                            INNER JOIN fuel_type ft
                                ON c.fuel_type_code = ft.codes
                            GROUP BY 1
                        ) AS ranked_data
                        ORDER BY ranking
                        LIMIT 10;
                    """
                    cursor.execute(select_sql)
                else:
                    select_sql = """
                        SELECT
                            RANK() OVER (ORDER BY total_purchase_count DESC) as ranking
                        , fuel_name
                        , total_purchase_count AS total
                        FROM (
                            SELECT
                                ft.name AS fuel_name
                                , SUM(c.purchase_count) AS total_purchase_count
                            FROM car_365 c
                            INNER JOIN fuel_type ft
                                ON c.fuel_type_code = ft.codes
                            WHERE c.age_group_code = %s
                            GROUP BY 1
                        ) AS ranked_data
                        ORDER BY ranking
                        LIMIT 10;

                    """
                    cursor.execute(select_sql, (selected_age_code_for_query,))
                select_data = cursor.fetchall()

                if not select_data: 
                    st.write(f"선택하신 **{selected_age_text}**에 대한 엔진 데이터가 없습니다.")
                else:                
                    st.write(f"차량 총 개수: {total_count_from_db:,}")

                    df_result = pd.DataFrame(select_data, columns=['순위', '엔진', '총 구매량'])
                    df_result['순위'] = df_result['순위'].astype(str) + '위'

                    styled_df = df_result.style.format({
                        '총 구매량': '{:,.0f}'.format
                    }).set_properties(subset=['순위', '엔진'], **{'text-align': 'center'})

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