import streamlit as st
import pandas as pd
import datetime
import time
import os

# --- 1. 保存用ファイル（CSV）の設定 ---
CSV_FILE = "practice_log.csv"

def load_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    else:
        return pd.DataFrame(columns=["日付", "名前", "メニュー", "時間(分)", "評価", "メモ"])

def save_data(new_row):
    df = load_data()
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")

# --- 2. アプリの基本設定 ---
st.set_page_config(page_title="チーム野球ノート", layout="wide")

if "elapsed_time" not in st.session_state: st.session_state.elapsed_time = 0
if "is_running" not in st.session_state: st.session_state.is_running = False
if "last_start_time" not in st.session_state: st.session_state.last_start_time = None

# --- 3. ログイン画面 ---
if "user_name" not in st.session_state:
    st.title("⚾️ チーム野球ノート ログイン")
    name = st.selectbox("あなたの名前を選択してください", ["監督", "田中選手", "佐藤選手", "鈴木選手"])
    if st.button("ログイン"):
        st.session_state["user_name"] = name
        st.rerun()
else:
    user = st.session_state["user_name"]
    st.sidebar.header(f"👤 {user}")
    if st.sidebar.button("ログアウト"):
        del st.session_state["user_name"]
        st.rerun()

    # --- 4. メイン画面 ---
    st.title(f"🚀 {user} の練習管理")

    if user != "監督":
        st.subheader("⏱️ 練習時間を測る")
        if st.session_state.is_running:
            now = time.time()
            st.session_state.elapsed_time += now - st.session_state.last_start_time
            st.session_state.last_start_time = now

        mins, secs = divmod(int(st.session_state.elapsed_time), 60)
        st.metric("現在の練習時間", f"{mins:02d}:{secs:02d}")

        col1, col2, col3 = st.columns(3)
        with col1:
            if not st.session_state.is_running:
                if st.button("▶️ 開始 / 再開"):
                    st.session_state.is_running = True
                    st.session_state.last_start_time = time.time()
                    st.rerun()
            else:
                if st.button("⏸️ 一時停止"):
                    st.session_state.is_running = False
                    st.rerun()
        with col2:
            if st.button("🔄 リセット"):
                st.session_state.elapsed_time = 0
                st.session_state.is_running = False
                st.rerun()
        
        if st.session_state.is_running:
            time.sleep(1)
            st.rerun()

    st.divider()

    # --- 5. データ表示と保存 ---
    df_history = load_data()
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("📈 チーム全体の練習量推移")
        if not df_history.empty:
            chart_df = df_history.pivot_table(index="日付", columns="名前", values="時間(分)", aggfunc="sum").fillna(0)
            st.line_chart(chart_df)
        else:
            st.info("まだ練習記録がありません。")

        if user != "監督":
            st.subheader("📝 今日の内容を記録")
            with st.form("save_form"):
                date_val = st.date_input("日付", datetime.date.today())
                menu_val = st.selectbox("練習メニュー", ["打撃練習", "守備練習", "ピッチング", "走り込み", "筋トレ"])
                measured_min = int(st.session_state.elapsed_time // 60)
                time_val = st.number_input("練習時間（分）
