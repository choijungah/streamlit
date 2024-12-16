import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def app():
    st.title("네 번째 페이지: 고령비율 vs. 평균소득 (Scatter + Top/Bottom 5 이중축)")

    # -- 1) 두 번째 페이지 결과: 시군구 평균 소득 CSV --
    income_csv_path = "C:/Users/Administrator/Downloads/KCB_SIGNGU_DATA5_23_202410.csv"
    df_income = pd.read_csv(income_csv_path, encoding='utf-8')
    
    # -- 2) 세 번째 페이지 결과: 고령인구 비율 CSV --
    senior_csv_path = "C:/Users/Administrator/Downloads/merged_senior.csv"
    df_senior = pd.read_csv(senior_csv_path, encoding='utf-8')
    
    st.subheader("1) 시군구 평균 소득 데이터 미리보기")
    st.dataframe(df_income.head())
    st.write("---")
    
    st.subheader("2) 시군구 고령인구 비율 데이터 미리보기")
    st.dataframe(df_senior.head())
    st.write("---")
    
    # -- 3) 병합: 시군구 코드를 기준으로 합치기 --
    df_income['SIGNGU_CD'] = df_income['SIGNGU_CD'].astype(str)
    df_senior['행정기관코드_앞5자리'] = df_senior['행정기관코드_앞5자리'].astype(str)
    
    merged_all = pd.merge(
        df_income,
        df_senior,
        left_on='SIGNGU_CD',
        right_on='행정기관코드_앞5자리',
        how='inner'
    )
    
    st.subheader("3) 병합된 데이터 (소득 + 고령인구비율)")
    st.dataframe(merged_all.head())
    st.write("---")
    
    # -- 숫자형 변환 --
    merged_all['AVRG_INCOME_PRICE'] = pd.to_numeric(merged_all['AVRG_INCOME_PRICE'], errors='coerce')
    merged_all['고령인구 비율'] = pd.to_numeric(merged_all['고령인구 비율'], errors='coerce')
    
    # ------------------------------------------------------------------------------
    # (A) 전체 산점도(Scatter Plot): 고령비율 vs. 평균소득
    # ------------------------------------------------------------------------------
    st.subheader("A. 전체 산점도: 고령비율 vs. 평균소득")

    # 4분면 분류 위한 임계값 슬라이더
    st.sidebar.subheader("4분면 분류 기준 설정")
    senior_threshold = st.sidebar.slider("고령인구 비율 임계값(%)", 0, 100, 20, step=1)
    income_threshold = st.sidebar.slider("평균소득 임계값(만원)", 0, 100, 35, step=1)
    
    def categorize(row):
        if row['고령인구 비율'] >= senior_threshold and row['AVRG_INCOME_PRICE'] >= income_threshold:
            return "고령높음/소득높음"
        elif row['고령인구 비율'] >= senior_threshold and row['AVRG_INCOME_PRICE'] < income_threshold:
            return "고령높음/소득낮음"
        elif row['고령인구 비율'] < senior_threshold and row['AVRG_INCOME_PRICE'] >= income_threshold:
            return "고령낮음/소득높음"
        else:
            return "고령낮음/소득낮음"
    
    merged_all['분류'] = merged_all.apply(categorize, axis=1)
    
    color_map = {
        '고령높음/소득낮음': '#FF6347',  # 빨간
        '고령낮음/소득높음': '#1E90FF',  # 파랑
        '고령높음/소득높음': '#FFB347',  # 오렌지
        '고령낮음/소득낮음': '#9ACD32'   # 연두색
    }
    
    fig_scatter = px.scatter(
        merged_all,
        x="AVRG_INCOME_PRICE",
        y="고령인구 비율",
        hover_name="시군구명",
        color="분류",
        color_discrete_map=color_map,
        labels={
            "AVRG_INCOME_PRICE": "평균소득(만원)",
            "고령인구 비율": "고령인구 비율(%)",
            "분류": "4분면"
        },
        title="(산점도) 전체 시군구 고령인구 비율 vs. 평균소득"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.write("---")
    
    # ------------------------------------------------------------------------------
    # (B) 이중축 라인차트: 소득 Top5/Bottom5 + 고령비율 Top5/Bottom5
    # ------------------------------------------------------------------------------
    st.subheader("B. 이중축 라인차트: Top5/Bottom5 (소득 & 고령)")

    # 소득 상위 5, 하위 5 / 고령비율 상위 5, 하위 5
    df_top5_income = merged_all.nlargest(5, 'AVRG_INCOME_PRICE')
    df_bottom5_income = merged_all.nsmallest(5, 'AVRG_INCOME_PRICE')
    df_top5_senior = merged_all.nlargest(5, '고령인구 비율')
    df_bottom5_senior = merged_all.nsmallest(5, '고령인구 비율')
    
    # concat하여 중복제거
    df_filtered = pd.concat([df_top5_income, df_bottom5_income, df_top5_senior, df_bottom5_senior])
    df_filtered.drop_duplicates(subset=['SIGNGU_CD'], inplace=True)
    
    # 시군구명 기준 정렬
    df_filtered.sort_values(by="시군구명", inplace=True)
    
    st.subheader("선택된 지역 (소득Top5/하위5 + 고령비율Top5/하위5)")
    st.dataframe(df_filtered[['시군구명','AVRG_INCOME_PRICE','고령인구 비율']])
    st.write("---")
    
    st.subheader("이중축 라인차트 (Top5/Bottom5)")
    
    fig_line = go.Figure()
    
    # 왼쪽 Y축: 고령인구 비율
    fig_line.add_trace(go.Scatter(
        x=df_filtered['시군구명'],
        y=df_filtered['고령인구 비율'],
        mode='lines+markers',
        name='고령인구 비율(%)',
        line=dict(color='#FF6347')
    ))
    
    # 오른쪽 Y축: 평균소득(만원)
    fig_line.add_trace(go.Scatter(
        x=df_filtered['시군구명'],
        y=df_filtered['AVRG_INCOME_PRICE'],
        mode='lines+markers',
        name='평균소득(만원)',
        line=dict(color='#1E90FF'),
        yaxis='y2'
    ))
    
    fig_line.update_layout(
        title="[Top5/Bottom5] 고령인구 비율 & 평균소득 (이중축 라인차트)",
        xaxis=dict(title='시군구명'),
        yaxis=dict(
            title='고령인구 비율(%)',
            titlefont=dict(color='#FF6347'),
            tickfont=dict(color='#FF6347'),
            anchor='x',
        ),
        yaxis2=dict(
            title='평균소득(만원)',
            titlefont=dict(color='#1E90FF'),
            tickfont=dict(color='#1E90FF'),
            overlaying='y',
            side='right'
        ),
        legend=dict(x=0.05, y=0.95)
    )
    
    st.plotly_chart(fig_line, use_container_width=True)
    
    st.write("""
    **그래프 해석**:
    - (A) 전체 산점도에서 고령비율과 소득 사이의 전반적 분포(4분면)를 확인함.
    - (B) 소득Top5/Bottom5, 고령비율Top5/Bottom5에 해당하는 지역만 골라서 이중축 라인차트로 비교.
    - 왼쪽 축: 고령인구 비율(%), 오른쪽 축: 평균소득(만원).
    - Top/Bottom 샘플만 보기 때문에, 극단값을 중심으로 '고령높음↔소득낮음' 패턴을 간략히 파악 가능.
    """)

def main():
    app()

if __name__ == "__main__":
    main()
