import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium

# 1. Streamlit 클라우드 경로 설정
EXCEL_FILE = "출산율통계최종.xlsx"
SHP_FILE = "N3A_G0100000.shp"

# 2. 엑셀 데이터 로드 및 전처리
df_seoul_pop = pd.read_excel(EXCEL_FILE, engine='openpyxl', header=[0, 1])
df_seoul_pop.columns = ['_'.join(col).strip() for col in df_seoul_pop.columns.values]
df_seoul_pop = df_seoul_pop[['행정구역별_행정구역별', '2023_합계출산율 (가임여성 1명당 명)']]

# 시도 정보 채우기
df_seoul_pop['시도'] = df_seoul_pop['행정구역별_행정구역별'].where(
    df_seoul_pop['행정구역별_행정구역별'].str.contains('특별시|광역시|도$|특별자치시|특별자치도$'),
    None
).ffill()
df_seoul_pop['새_시도'] = df_seoul_pop['시도'] + ' ' + df_seoul_pop['행정구역별_행정구역별']
df_seoul_pop = df_seoul_pop[df_seoul_pop['행정구역별_행정구역별'] != df_seoul_pop['시도']]
df_seoul_pop = df_seoul_pop[df_seoul_pop['행정구역별_행정구역별'] != '전국']
df_seoul_pop = df_seoul_pop.reset_index(drop=True)
df_seoul_pop['행정구역별_행정구역별'] = df_seoul_pop['행정구역별_행정구역별'].str.strip()

# 3. GeoJSON 데이터 로드 및 전처리
gdf = gpd.read_file(SHP_FILE)
gdf.rename(columns={'NAME': '행정구역별_행정구역별'}, inplace=True)

# 중복된 행정구역 처리 함수
def modify_district_name(row, duplicated_names):
    if row['행정구역별_행정구역별'] in duplicated_names:
        bjcd_prefix = str(row['BJCD'])[:2]
        if bjcd_prefix == "26": return f"부산-{row['행정구역별_행정구역별']}"
        elif bjcd_prefix == "27": return f"대구-{row['행정구역별_행정구역별']}"
        elif bjcd_prefix == "29": return f"광주-{row['행정구역별_행정구역별']}"
        elif bjcd_prefix == "30": return f"대전-{row['행정구역별_행정구역별']}"
        elif bjcd_prefix == "31": return f"울산-{row['행정구역별_행정구역별']}"
        elif bjcd_prefix == "47": return f"포항-{row['행정구역별_행정구역별']}"
        elif bjcd_prefix == "48": return f"경상남도-{row['행정구역별_행정구역별']}"
        elif bjcd_prefix == "42": return f"강원-{row['행정구역별_행정구역별']}"
        else: return row['행정구역별_행정구역별']
    else:
        return row['행정구역별_행정구역별']

# 중복된 이름 처리
duplicated_names = gdf['행정구역별_행정구역별'][gdf['행정구역별_행정구역별'].duplicated(keep=False)].unique()
gdf['변환된_행정구역'] = gdf.apply(modify_district_name, axis=1, duplicated_names=duplicated_names)

# 추가 변환 및 정리
replace_dict = {'경상남도-고성군': '고성군', '창원시': '통합창원시', '세종특별자치시': '세종시'}
gdf['변환된_행정구역'] = gdf['변환된_행정구역'].replace(replace_dict)
gdf['변환된_행정구역'] = gdf['변환된_행정구역'].str.strip()

# 4. Folium 지도 생성
title_html = f'<h3 align="center" style="font-size:20px"><b>시군구별 출산율</b></h3>'
nation_map = folium.Map(location=[36.5, 127.8], zoom_start=7, tiles='cartodbpositron')
nation_map.get_root().html.add_child(folium.Element(title_html))

folium.Choropleth(
    geo_data=gdf,
    data=df_seoul_pop,
    columns=('행정구역별_행정구역별', '2023_합계출산율 (가임여성 1명당 명)'),
    key_on='feature.properties.변환된_행정구역',
    fill_color='BuPu',
    fill_opacity=0.7,
    line_opacity=0.5,
    legend_name='출산율'
).add_to(nation_map)

# 5. Streamlit에서 Folium 지도 렌더링
st_folium(nation_map, width=800, height=600)