import streamlit as st
import pandas as pd
import datetime
import time

# ページ設定
st.set_page_config(page_title="チーム野球ノート", layout="wide")

# --- ログイン機能 ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("⚾️ チーム野球ノート ログイン")
    user = st.text_input("選手名を入力してください")
    if st.button("ログイン"):
        if user:
            st.session_state.logged_in = True
            st.session_state.user = user
            st.rerun()
        else:
            st.error("名前を入力してください")
else:
    # --- メイン画面 ---
    st.sidebar.title(f"👤 {st.session_state.user} 選手")
    if st.sidebar.button("ログアウト"):
        st.session_state.logged_in = False
        st.rerun()

    menu = st.sidebar.radio("メニュー", ["練習記録", "ストップウォッチ", "データ分析"])

    if menu == "練習記録":
        st.header("📝 今日の練習を記録しよう")
        date = st.date_input("日付", datetime.date.today())
        menu_type = st.selectbox("練習メニュー", ["打撃練習", "守備練習", "投球練習", "走塁", "ウェイト"])
        duration = st.number_input("時間（分）", min_value=0, step=5)
        note = st.text_area("振り返り・気づいたこと")
        
        if st.button("記録を保存"):
            st.success(f"{date} の {menu_type} を保存しました！")
            st.balloons()

    elif menu == "ストップウォッチ":
        st.header("⏱️ ストップウォッチ")
        if 'start_time' not in st.session_state:
            st.session_state.start_time = None

        col1, col2 = st.columns(2)
        if col1.button("スタート"):
            st.session_state.start_time = time.time()
        if col2.button("リセット"):
            st.session_state.start_time = None

        if st.session_state.start_time:
            placeholder = st.empty()
            elapsed = time.time() - st.session_state.start_time
            placeholder.metric("経過時間", f"{elapsed:.2f} 秒")

    elif menu == "データ分析":
        st.header("📊 練習の傾向")
        chart_data = pd.DataFrame({
            'メニュー': ["打撃", "守備", "投球", "ウェイト"],
            '合計時間(分)': [120, 80, 60, 45]
        })
        st.bar_chart(chart_data.set_index('メニュー'))
