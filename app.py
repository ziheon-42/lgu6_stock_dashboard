import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from datetime import datetime, timedelta
import matplotlib.font_manager as fm
import platform
import os

# 폰트 파일 경로 설정
font_path = os.path.join('nanum-gothic', 'NanumGothic.ttf')
font_prop = fm.FontProperties(fname=font_path)

# 운영체제에 따른 한글 폰트 설정
if platform.system() == 'Windows':
    plt.rcParams['font.family'] = 'Malgun Gothic'
else:  # Linux or other systems
    # 폰트 매니저에 폰트 추가
    fm.fontManager.addfont(font_path)
    plt.rcParams['font.family'] = font_prop.get_name()
    
plt.rcParams['axes.unicode_minus'] = False
sns.set(font=plt.rcParams['font.family'], 
        rc={'axes.unicode_minus':False}, 
        style='darkgrid')

# 페이지 설정
st.set_page_config(page_title="주식 차트 대시보드", layout="wide")

# 대시보드 제목
st.title("주식 차트 대시보드")

# 티커 파일에서 데이터 로드
@st.cache_data
def load_tickers():
    tickers = {}
    try:
        with open('stock_tickers.txt', 'r') as file:
            for line in file:
                if ':' in line:
                    name, ticker = line.strip().split(':')
                    tickers[name.strip()] = ticker.strip()
    except Exception as e:
        st.error(f"티커 로딩 오류: {str(e)}")
        tickers = {"Apple": "AAPL"}  # 기본값
    return tickers

# 사이드바 - 사용자 입력
st.sidebar.header("주식 정보")
tickers = load_tickers()
selected_company = st.sidebar.selectbox(
    "기업 선택",
    options=list(tickers.keys()),
    index=0
)
ticker = tickers[selected_company]

# 날짜 선택
start_date = st.sidebar.date_input("시작 날짜", datetime.now() - timedelta(days=365))
end_date = st.sidebar.date_input("종료 날짜", datetime.now())

# 주식 데이터 가져오기
@st.cache_data
def load_data(ticker, start_date, end_date):
    stock = yf.Ticker(ticker)
    df = stock.history(start=start_date, end=end_date)
    return df

try:
    df = load_data(ticker, start_date, end_date)
    
    # 기본 주식 정보 표시
    st.subheader(f"{selected_company} ({ticker}) 주식 정보")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("현재 가격", f"${df['Close'][-1]:.2f}")
    with col2:
        st.metric("52주 최고가", f"${df['High'].max():.2f}")
    with col3:
        st.metric("52주 최저가", f"${df['Low'].min():.2f}")

    # 다양한 시각화를 위한 탭 생성
    tab1, tab2, tab3 = st.tabs(["Matplotlib", "Seaborn", "Plotly"])

    # Matplotlib 차트
    with tab1:
        st.subheader("Matplotlib 차트")
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(df.index, df['Close'], label='종가')
        ax.set_title(f"{selected_company} ({ticker}) 주가")
        ax.set_xlabel("날짜")
        ax.set_ylabel("가격 ($)")
        ax.grid(True)
        ax.legend()
        st.pyplot(fig)

    # Seaborn 차트
    with tab2:
        st.subheader("Seaborn 차트")
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.lineplot(data=df, x=df.index, y='Close', ax=ax)
        ax.set_title(f"{selected_company} ({ticker}) 주가")
        ax.set_xlabel("날짜")
        ax.set_ylabel("가격 ($)")
        ax.grid(True)
        st.pyplot(fig)

    # Plotly 차트
    with tab3:
        st.subheader("Plotly 차트")
        fig = px.line(df, x=df.index, y='Close', 
                     title=f"{selected_company} ({ticker}) 주가",
                     labels={'Close': '가격 ($)', 'index': '날짜'})
        fig.update_layout(
            xaxis_title="날짜",
            yaxis_title="가격 ($)",
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)

    # 기술적 분석
    st.subheader("기술적 분석")
    col1, col2 = st.columns(2)
    
    with col1:
        # 이동평균선
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['MA50'] = df['Close'].rolling(window=50).mean()
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(df.index, df['Close'], label='종가')
        ax.plot(df.index, df['MA20'], label='20일 이동평균')
        ax.plot(df.index, df['MA50'], label='50일 이동평균')
        ax.set_title(f"{selected_company} ({ticker}) 이동평균선")
        ax.set_xlabel("날짜")
        ax.set_ylabel("가격 ($)")
        ax.grid(True)
        ax.legend()
        st.pyplot(fig)

    with col2:
        # 거래량 분석
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar(df.index, df['Volume'], alpha=0.5)
        ax.set_title(f"{selected_company} ({ticker}) 거래량")
        ax.set_xlabel("날짜")
        ax.set_ylabel("거래량")
        ax.grid(True)
        st.pyplot(fig)

except Exception as e:
    st.error(f"데이터 로딩 오류: {str(e)}") 