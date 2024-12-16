import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import folium_static

def app():
    st.title("시군구별 평균 소득 시각화 페이지")
    st.sidebar.title("시군구별 평균 소득 - 사이드바")

    # CSV & SHP 파일 경로
    csv_file_path = "C:/Users/Administrator/Downloads/KCB_SIGNGU_DATA5_23_202410.csv"
    shp_file_path = "C:/Users/Administrator/Downloads/LX법정구역경계_시군구_전국 (1)/SGG.shp"

    # CSV 불러오기
    st.subheader("1) CSV 데이터 불러오기")
    try:
        df2 = pd.read_csv(csv_file_path, encoding='utf-8')
        st.write("불러온 데이터 (CSV):")
        st.dataframe(df2.head())
    except Exception as e:
        st.error(f"CSV 파일 로드 에러: {e}")
        return  # 파일 로드 실패 시 이후 실행 중단

    # SHP 불러오기
    st.subheader("2) SHP(시군구 경계) 데이터 불러오기")
    try:
        gdf = gpd.read_file(shp_file_path)
        st.write("불러온 경계 데이터 (SHP):")
        st.dataframe(gdf.head())
    except Exception as e:
        st.error(f"SHP 파일 로드 에러: {e}")
        return

    # 데이터 타입 통일
    df2['SIGNGU_CD'] = df2['SIGNGU_CD'].astype(str)
    gdf['signgu_cd'] = gdf['signgu_cd'].astype(str)

    # (선택) signgu_nm이 비었거나 매칭이 필요한 경우 df2에 update 예시
    # df2['SIGNGU_NM'] = df2['SIGNGU_CD'].map(gdf.set_index('signgu_cd')['signgu_nm']).fillna(df2['SIGNGU_NM'])

    st.subheader("3) 시군구별 평균 소득 Choropleth 시각화")
    title2 = '시군구별 평균 소득 시각화'
    title_html2 = f'<h3 align="center" style="font-size:20px"><b>{title2}</b></h3>'

    nation_map2 = folium.Map(
        location=[36.5, 127.8],  # 대한민국 중앙 좌표
        zoom_start=7,
        tiles='cartodbpositron'
    )
    nation_map2.get_root().html.add_child(folium.Element(title_html2))

    folium.Choropleth(
        geo_data=gdf,                
        data=df2,                    
        columns=['SIGNGU_CD', 'AVRG_INCOME_PRICE'],  
        key_on='feature.properties.signgu_cd',      
        fill_color='YlOrRd',         
        fill_opacity=0.7,
        line_opacity=0.5,
        legend_name='평균 소득 (만원)'  
    ).add_to(nation_map2)

    folium_static(nation_map2)

    # 사이드바 추가 기능 예시
    st.sidebar.subheader("추가 기능/옵션")
    show_csv = st.sidebar.checkbox("원본 CSV 전체보기", value=False)
    if show_csv:
        st.write("**CSV 전체 데이터**")
        st.dataframe(df2)

def main():
    app()

if __name__ == "__main__":
    main()
