import streamlit as st

def main():
    # 페이지 타이틀 / 헤더
    st.title(" Streamlit 멀티 페이지 개요")

    # 간단한 설명
    st.write("""
    이 앱은 **시군구별 평균 소득**과 **65세 이상 인구** 통계를 
    **Folium 지도**에 시각화한 멀티 페이지 예시입니다.
    
    왼쪽 사이드바 혹은 아래 버튼을 통해 다른 페이지로 이동할 수 있습니다.
    """)

    # 사이드바 구성
    st.sidebar.title("메인 페이지 사이드바")
    st.sidebar.write("이곳에서 다양한 기능/옵션을 추가할 수 있습니다.")

    # 화면을 2개의 컬럼으로 분할하여 소개를 배치
    col1, col2 = st.columns([2,1])

    with col1:
        st.subheader("앱 개요")
        st.markdown("""
        - **시군구별 평균 소득**: CSV 파일과 시군구 경계(SHP)를 기반으로 Folium Choropleth 시각화
        - **시군구별 65세 이상 인구**: 연령별 데이터 전처리 후 지도 시각화
        - **추가 분석**: 필요 시 다른 통계나 머신러닝 분석 결과를 표시
        - **멀티 페이지 구조**: Streamlit `pages/` 폴더 구조 활용
        """)

        # 버튼을 통해 다른 페이지로 이동하는 방법 (Streamlit의 멀티페이지 표준 방식은 사이드바 메뉴 사용)
        # 여기서는 간단히 링크 안내
        if st.button("평균소득 시각화 페이지로 이동"):
            st.write("왼쪽 사이드바에서 page 2를 클릭하세요.")
        if st.button("65세 이상 인구 시각화 페이지로 이동"):
            st.write("왼쪽 사이드바에서 page 3를 클릭하세요.")

    with col2:
        st.subheader("개발 환경")
        st.write("""
        - **Python**: 3.x
        - **라이브러리**:
          - Streamlit
          - Pandas, GeoPandas
          - Folium
        """)

   
if __name__ == "__main__":
    main()
