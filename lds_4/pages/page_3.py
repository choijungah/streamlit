import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import folium_static
import re  # 정규표현식 사용을 위해 필요

def main():
    st.title("시군구별 고령인구 비율 시각화")
    
    # ------ 로컬 경로 직접 지정 ------
    csv_path = "지역별(행정동) 성별 연령별 주민등록 인구수_20241031.csv"
    shp_path = "LX법정구역경계_시군구_전국 (1)/SGG.shp"
    
    # ---- CSV 파일 읽기 (euc-kr 인코딩) ----
    df = pd.read_csv(csv_path, encoding='euc-kr')
    st.subheader("원본 데이터 미리보기 (상위 5행)")
    st.dataframe(df.head())

    # 행정기관코드 앞 5자리 추출
    df['행정기관코드_앞5자리'] = df['행정기관코드'].astype(str).str[:5]

    # 그룹화하여 필요한 열만 선택 및 집계
    grouped_df = df.groupby('행정기관코드_앞5자리').agg({
        '행정기관코드': 'first',  # 그룹의 첫 번째 값을 유지
        '시도명': 'first',         # 시도명은 동일하므로 첫 번째 값 사용
        '시군구명': 'first',       # 시군구명은 동일하므로 첫 번째 값 사용
        '계': 'sum'               # 그룹 내 계 열을 합산
    }).reset_index(drop=True)

    st.subheader("그룹화된 (행정기관코드_앞5자리 기준) 데이터 미리보기")
    st.dataframe(grouped_df.head())

    # ---- SHP 파일(GeoDataFrame) 읽기 ----
    gdf = gpd.read_file(shp_path)
    st.subheader("SHP(GeoDataFrame) 미리보기 (상위 5행)")
    st.write(gdf.head())  # geometry 컬럼이 포함된 GeoDataFrame

    # SHP의 signgu_cd 앞 5자리 추출
    gdf['signgu_cd'] = gdf['signgu_cd'].astype(str).str[:5]

    # grouped_df와 지오데이터프레임을 매핑하기 위해,
    # grouped_df에도 동일한 5자리 코드가 있는지 확인
    grouped_df['행정기관코드_앞5자리'] = grouped_df['행정기관코드'].astype(str).str[:5]

    # gdf를 통해 시군구명을 다시 매핑: signgu_cd <-> signgu_nm
    grouped_df['시군구명'] = grouped_df['행정기관코드_앞5자리'].map(
        gdf.set_index('signgu_cd')['signgu_nm']
    )

    # --- 65세 이상 인구 계산을 위해 CSV를 다시 읽어오기 ---
    df3 = pd.read_csv(csv_path, encoding='euc-kr')
    df3['행정기관코드_앞5자리'] = df3['행정기관코드'].astype(str).str[:5]

    # 정규표현식으로 65세 이상 남자/여자 컬럼명을 식별
    male_cols = [
        col for col in df3.columns
        if '남자' in col and re.search(r'\d+', col) and int(re.search(r'\d+', col).group()) >= 65
    ]
    female_cols = [
        col for col in df3.columns
        if '여자' in col and re.search(r'\d+', col) and int(re.search(r'\d+', col).group()) >= 65
    ]

    # 65세 이상 남녀 합계 계산
    df3['65세이상남자합'] = df3[male_cols].sum(axis=1)
    df3['65세이상여자합'] = df3[female_cols].sum(axis=1)

    grouped_df3 = df3.groupby('행정기관코드_앞5자리')[['65세이상남자합', '65세이상여자합']].sum().reset_index()
    grouped_df3['65세이상총합'] = grouped_df3['65세이상남자합'] + grouped_df3['65세이상여자합']

    st.subheader("65세 이상 인구 집계 데이터 (grouped_df3) 미리보기")
    st.dataframe(grouped_df3.head())

    # ----- 병합 merged_df 생성 -----
    merged_df = pd.merge(
        grouped_df,
        grouped_df3,
        on='행정기관코드_앞5자리',
        how='inner'
    )

    # 불필요한 컬럼 삭제
    merged_df = merged_df.drop(['65세이상남자합', '65세이상여자합'], axis=1)

    # 고령인구 비율 계산 (65세 이상 총합 / 전체 인구 * 100)
    merged_df['고령인구 비율'] = (merged_df['65세이상총합'] / merged_df['계']) * 100

    st.subheader("병합 결과 merged_df 미리보기")
    st.dataframe(merged_df.head())

    # ------ Folium Choropleth 시각화 ------
    title4 = '시군구별 고령인구 비율 시각화'
    title_html4 = f'<h3 align="center" style="font-size:20px"><b>{title4}</b></h3>'

    # gdf와 merged_df 키 일치(문자열)
    gdf['signgu_cd'] = gdf['signgu_cd'].astype(str)
    merged_df['행정기관코드_앞5자리'] = merged_df['행정기관코드_앞5자리'].astype(str)

    # 대한민국 중심 좌표를 기준으로 지도 생성
    nation_map4 = folium.Map(
        location=[36.5, 127.8],  # 대한민국 중심 좌표
        zoom_start=7,            # 적절한 줌 레벨
        tiles='cartodbpositron'  # 심플한 배경 타일
    )

    # 타이틀 추가
    nation_map4.get_root().html.add_child(folium.Element(title_html4))

    # Choropleth는 전체 데이터(merged_df) 기준으로 그립니다.
    folium.Choropleth(
        geo_data=gdf,
        data=merged_df,
        columns=['행정기관코드_앞5자리', '고령인구 비율'],
        key_on='feature.properties.signgu_cd', 
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.5,
        legend_name='고령인구 비율 (%)'
    ).add_to(nation_map4)

    # Streamlit 앱에 지도 표시
    folium_static(nation_map4)

    # --- 사이드바에서 고령인구 비율 최소 기준 설정 ---
    st.sidebar.subheader("필터 기준 설정")
    min_ratio = st.sidebar.slider(
        "최소 고령인구 비율(%)", 
        min_value=0.0, 
        max_value=50.0,
        value=20.0,
        step=0.5
    )
    
    # 체크박스: 필터 적용 여부
    apply_filter = st.sidebar.checkbox("고령인구 비율 필터 적용하기", value=True)
    
    if apply_filter:
        filtered_df = merged_df[merged_df['고령인구 비율'] >= min_ratio]
        st.subheader(f"**고령인구 비율 {min_ratio}% 이상인 지역**")
        st.dataframe(filtered_df.reset_index(drop=True))
    else:
        st.subheader("필터를 사용하지 않습니다. (전체 지역)")
        filtered_df = merged_df

    # 병합된 데이터 저장
    merged_df.to_csv("C:/Users/Administrator/Downloads/merged_senior.csv", index=False, encoding='utf-8-sig')
    st.success("고령인구 비율 데이터가 'merged_senior.csv'로 저장되었습니다.")

if __name__ == "__main__":
    main()

