import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv

# 페이지 설정
st.set_page_config(page_title="NewsBot", layout="wide")

# 환경 변수 로드
load_dotenv()

# 뉴스 데이터 로드
@st.cache_data
def load_data():
    return pd.read_csv("./Data/news.csv")

news_df = load_data()

# 세션 상태 초기화
if "selected_news" not in st.session_state:
    st.session_state["selected_news"] = None  # 선택된 뉴스 저장

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []  # 대화 기록 저장

if "show_recommendations" not in st.session_state:
    st.session_state["show_recommendations"] = False  # 추천 뉴스 표시 여부

# 뉴스 포털 홈
st.title("NewsBot - 개인화 뉴스 포털")

st.write("""
최신 뉴스를 확인하고 궁금한 내용을 챗봇에게 질문하세요.  
원하는 기사를 클릭하면 챗봇이 활성화됩니다.
""")

st.subheader("오늘의 주요 뉴스")

# 뉴스 리스트 UI (한 줄 1~2개 배치)
for _, news in news_df.head(6).iterrows():
    with st.container():
        st.markdown(f"""
        <div style="padding:15px; border-radius:10px; background-color:#FFFFFF; box-shadow: 3px 3px 15px rgba(0,0,0,0.1); margin-bottom:10px;">
            <h4 style="color:#333; margin-bottom:5px;">{news['title']}</h4>
            <p style="font-size:13px; color:#666;">{news['category']}</p>
        </div>
        """, unsafe_allow_html=True)

        # 뉴스 클릭 시 챗봇 활성화
        if st.button(f"🔍 {news['title']}", key=f"news_{news['news_id']}"):
            st.session_state["selected_news"] = news.to_dict()
            st.session_state["show_recommendations"] = False  # 추천 뉴스 숨김



# 우측 사이드바 챗봇 인터페이스
with st.sidebar:
    if st.session_state["selected_news"]:
        selected_news = st.session_state["selected_news"]

        st.subheader(f"{selected_news['title']}")
        st.caption(f"카테고리: {selected_news['category']}")
        st.write(selected_news["abstract"])

        st.markdown("---")
        st.subheader("추천 뉴스")

        # 협업 필터링 추천 버튼
        if st.button("이 뉴스를 본 사람들이 함께 본 뉴스"):
            st.session_state["show_recommendations"] = "cf"

        # 콘텐츠 기반 추천 버튼
        if st.button("이 뉴스와 유사한 뉴스 추천"):
            st.session_state["show_recommendations"] = "cbf"

        # 추천 뉴스 표시 (협업 필터링 & 콘텐츠 기반)
        if st.session_state["show_recommendations"]:
            st.markdown("---")

            if st.session_state["show_recommendations"] == "cf":
                st.subheader("협업 필터링 기반 추천 뉴스")
                recommended_news = news_df.sample(3)  # 현재는 랜덤 추천 (추후 ALS 모델 적용)

            elif st.session_state["show_recommendations"] == "cbf":
                st.subheader("콘텐츠 기반 추천 뉴스")
                recommended_news = news_df.sample(3)  # 현재는 랜덤 추천 (추후 TF-IDF + SVD 모델 적용)

            for _, row in recommended_news.iterrows():
                st.write(f"▶ {row['title']} ({row['category']})")

        st.markdown("---")
        st.subheader("뉴스 챗봇")

        # 챗봇 질문 입력창
        user_input = st.text_input("질문을 입력하세요", placeholder="예: 테슬라 주식 뉴스는?", key="chat_input")
        send_button = st.button("보내기")

        if send_button and user_input:
            st.session_state["chat_history"].append(
                {"user": user_input, "bot": "답변 생성 중..."}
            )

        # 대화 기록 표시
        st.markdown("---")
        st.subheader("대화 기록")
        chat_container = st.container()

        with chat_container:
            for msg in st.session_state["chat_history"]:
                with st.chat_message("user"):
                    st.markdown(f"""
                    <div style="padding:10px; background-color:#E3F2FD; border-radius:10px; width:fit-content; max-width:80%;">
                        {msg["user"]}
                    </div>
                    """, unsafe_allow_html=True)

                with st.chat_message("bot"):
                    st.markdown(f"""
                    <div style="padding:10px; background-color:#F1F8E9; border-radius:10px; width:fit-content; max-width:80%;">
                        {msg["bot"]}
                    </div>
                    """, unsafe_allow_html=True)

        # 홈으로 돌아가기 버튼
        if st.button("뉴스 목록으로 돌아가기"):
            st.session_state["selected_news"] = None
            st.session_state["chat_history"] = []
            st.session_state["show_recommendations"] = False
            st.experimental_rerun()
