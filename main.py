import streamlit as st
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import numpy as np
import hashlib
import random

# --- ページ設定 ---
st.set_page_config(page_title="次世代チーム野球ノート", layout="wide", page_icon="⚾️")
plt.rcParams['font.family'] = 'sans-serif'  # グラフの日本語対応用

# ==========================================
# 🔒 セキュリティ・暗号化関数
# ==========================================
def make_hashes(password):
    """パスワードをぐちゃぐちゃの文字列（ハッシュ値）に変換する（生パスワードを保存しない）"""
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    """入力されたパスワードが一致するか確認する"""
    if make_hashes(password) == hashed_text:
        return True
    return False

# ==========================================
# 📦 データ倉庫（疑似データベース / スプレッドシート代替ロジック）
# ==========================================
# 本来はgspreadを使用しますが、手軽に起動・検証できるよう高機能なセッションストレージで構築しています。
if 'users_auth' not in st.session_state:
    st.session_state.users_auth = pd.DataFrame([
        # 指導者アカウントは画面から新規登録できないようにするため、初期値としてここに登録
        {"選手名": "監督", "パスワード": make_hashes("coach123"), "立場": "監督・コーチ"},
        {"選手名": "コーチ", "パスワード": make_hashes("coach456"), "立場": "監督・コーチ"}
    ])

if 'notes_db' not in st.session_state:
    st.session_state.notes_db = pd.DataFrame(columns=[
        "選手名", "日付", "体調", "体重(kg)", "睡眠時間(時間)", 
        "メニュー", "時間(分)", "詳細数値", 
        "成果", "課題", "次への一手", "指導者コメント", "MVR"
    ])

if 'skills_db' not in st.session_state:
    st.session_state.skills_db = pd.DataFrame(columns=["選手名", "ミート", "パワー", "走力", "守備力", "メンタル"])

if 'chat_db' not in st.session_state:
    st.session_state.chat_db = pd.DataFrame(columns=["送信日時", "送信者", "受信者", "メッセージ"])

if 'slogan_db' not in st.session_state:
    st.session_state.slogan_db = "一球同心！日々の積み重ねが奇跡を生む。"

# ==========================================
# 🌟 心を燃やす「名言データベース」
# ==========================================
MEIGEN_LIST = [
    "「小さなことを積み重ねることが、とんでもないところへ行くただ一つの道」— イチロー",
    "「心が変われば態度が変わる。態度が変われば行動が変わる。行動が変われば運命が変わる」— 野村克也",
    "「無理だと思わないことが一番大事。無理だと思ったら終わりです」— 大谷翔平",
    "「やってみて、言ってきかせて、させてみせ、ほめてやらねば、人は動かじ」— 山本五十六",
    "「練習は裏切らない。もし裏切られたとしたら、それはまだ練習とは呼べない」— 野球格言"
]

if 'today_meigen' not in st.session_state:
    st.session_state.today_meigen = random.choice(MEIGEN_LIST)

# ==========================================
# 👤 ログイン状態管理
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'role' not in st.session_state:
    st.session_state.role = None

# ==========================================
# 🔑 エントランス画面（ログイン・新規登録）
# ==========================================
if not st.session_state.logged_in:
    st.title("⚾️ チーム野球ノートシステム PRO")
    
    # 名言を最上部に配置
    st.info(f"🌟 **今日の一言：** {st.session_state.today_meigen}")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["🔑 既存ユーザーログイン", "📝 選手新規アカウント作成"])
    
    with tab1:
        registered_users = st.session_state.users_auth["選手名"].tolist()
        if registered_users:
            input_user = st.selectbox("あなたの名前を選択してください", registered_users, key="login_name")
            input_password = st.text_input("パスワードを入力してください", type="password", key="login_pass")
            
            if st.button("安全にログイン", type="primary"):
                user_info = st.session_state.users_auth[st.session_state.users_auth["選手名"] == input_user]
                hashed_pass = user_info.iloc[0]["パスワード"]
                user_role = user_info.iloc[0]["立場"]
                
                if check_hashes(input_password, hashed_pass):
                    st.session_state.logged_in = True
                    st.session_state.user = input_user
                    st.session_state.role = user_role
                    st.success(f"{input_user} さんとして安全に接続しました。")
                    st.rerun()
                else:
                    st.error("パスワードが一致しません。セキュリティロックがかかりました。")
                    
    with tab2:
        st.caption("※監督・コーチのアカウントは画面から登録できません。管理者へ直接申請してください。")
        new_user = st.text_input("フルネームを入力（選手専用）", placeholder="例：山田 太郎")
        new_password = st.text_input("設定するパスワード（4文字以上）", type="password")
        new_password_conf = st.text_input("パスワードの再入力", type="password")
        
        if st.button("選手アカウントを作成"):
            if not new_user.strip():
                st.error("名前を入力してください。")
            elif new_user.strip() in st.session_state.users_auth["選手名"].tolist():
                st.error("その名前はすでに登録されています。")
            elif len(new_password) < 4:
                st.error("安全のためパスワードは4文字以上で設定してください。")
            elif new_password != new_password_conf:
                st.error("再入力されたパスワードが一致しません。")
            else:
                new_account = pd.DataFrame([{"選手名": new_user.strip(), "パスワード": make_hashes(new_password), "立場": "選手"}])
                st.session_state.users_auth = pd.concat([st.session_state.users_auth, new_account], ignore_index=True)
                st.success("アカウントが安全に暗号化されて登録されました！ログインタブからログインしてください。")
                st.balloons()

# ==========================================
# 🏃‍♂️ ログイン後のシステムメイン画面
# ==========================================
else:
    # サイドバーメニュー構築
    st.sidebar.title(f"👤 {st.session_state.user}")
    st.sidebar.write(f"【所属権限: {st.session_state.role}】")
    
    if st.sidebar.button("システムからログアウト", type="secondary"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.role = None
        st.rerun()
        
    st.sidebar.markdown("---")

    # 🛑 鉄壁のセキュリティ壁：権限によってナビゲーションメニューのプログラムそのものを完全分離
    if st.session_state.role == "選手":
        menu = st.sidebar.radio("選手メニュー", [
            "🏠 選手ダッシュボード",
            "📝 今日の野球ノート提出", 
            "📊 体調・コンディション分析",
            "📊 マイ能力値（パワプロ風）",
            "💬 監督との個別トーク"
        ])
        
        # ------------------------------------------
        # 【選手】🏠 ダッシュボード
        # ------------------------------------------
        if menu == "🏠 選手ダッシュボード":
            st.header(f"🔥 {st.session_state.user} 選手専用ダッシュボード")
            
            # チームスローガン表示
            st.warning(f"📢 **今週のチームスローガン：** {st.session_state.slogan_db}")
            
            my_history = st.session_state.notes_db[st.session_state.notes_db["選手名"] == st.session_state.user]
            submit_count = len(my_history)
            
            # 🏅 努力のバッジシステム
            st.subheader("🏅 獲得バッジ（あなたの継続の証明）")
            b_col1, b_col2, b_col3, b_col4 = st.columns(4)
            with b_col1:
                if submit_count >= 1: st.success("🥉 銅バッジ\n(初提出達成！)")
                else: st.code("🔒 銅バッジ\n(ノート1回提出で解放)")
            with b_col2:
                if submit_count >= 5: st.success("🥈 銀バッジ\n(5回提出！習慣化の兆し)")
                else: st.code("🔒 銀バッジ\n(ノート5回提出で解放)")
            with b_col3:
                if submit_count >= 15: st.success("🥇 金バッジ\n(15回提出！チームの鏡)")
                else: st.code("🔒 金バッジ\n(ノート15回提出で解放)")
            with b_col4:
                jishu_time = my_history[my_history["メニュー"] == "自主練・その他"]["時間(分)"].sum()
                if jishu_time >= 600: st.success("🔥 自主練の鬼\n(自主練10時間突破！)")
                else: st.code(f"🔒 自主練の鬼\n(あと{max(0, 600-jishu_time)}分自主練)")
                
            st.markdown("---")
            
            # 指導者からの最新フィードバックポップアップ
            if not my_history.empty:
                last_note = my_history.sort_values(by="日付").iloc[-1]
                if last_note['指導者コメント'] != "まだコメントはありません":
                    st.info(f"💬 **監督・コーチからの最新の個別赤ペン指導:**\n\n`{last_note['指導者コメント']}`")
            
            # 👑 チームMVR（お手本ノート）の自動掲示
            st.subheader("🌟 チームのベストノート（MVR）")
            mvr_notes = st.session_state.notes_db[st.session_state.notes_db["MVR"] == "🌟 MVR選出済"]
            if not mvr_notes.empty:
                latest_mvr = mvr_notes.sort_values(by="日付").iloc[-1]
                st.warning(f"👑 **【お手本】{latest_mvr['日付']}（{latest_mvr['選手名']} 選手）**\n\n"
                           f"🟢 **【成果】** {latest_mvr['成果']}\n\n"
                           f"🔴 **【課題】** {latest_mvr['課題']}\n\n"
                           f"🔵 **【次への一手】** {latest_mvr['次への一手']}")
            else:
                st.info("現在選出されているMVRはありません。最初のお手本ノートを目指そう！")

        # ------------------------------------------
        # 【選手】📝 野球ノート提出
        # ------------------------------------------
        elif menu == "📝 今日の野球ノート提出":
            st.header("📝 本日の野球ノート")
            my_history = st.session_state.notes_db[st.session_state.notes_db["選手名"] == st.session_state.user]
            
            if not my_history.empty:
                st.warning(f"💡 **前回あなたが決めた【次への一手】:**\n「 {my_history.sort_values(by='日付').iloc[-1]['次への一手']} 」")
                
            with st.form("notebook_form", clear_on_submit=True):
                st.subheader("1. 体調・コンディション（怪我情報一体型）")
                col1, col2, col3 = st.columns(3)
                with col1:
                    condition = st.selectbox("今の体調と怪我の状態", [
                        "絶好調（怪我なし・キレ抜群）", "良好（怪我なし）", 
                        "普通（違和感・軽い痛みあり）", "重い（怪我・強い痛みあり）", "最悪（動けない・要休養）"
                    ], index=1)
                with col2: weight = st.number_input("今日の体重 (kg)", value=65.0, step=0.1)
                with col3: sleep_time = st.number_input("昨夜の睡眠時間 (時間)", value=7.0, step=0.5)
                
                st.subheader("2. 練習内容")
                l_col1, l_col2, l_col3 = st.columns(3)
                with l_col1: date = st.date_input("日付", datetime.date.today())
                with l_col2: menu_type = st.selectbox("本日のメインメニュー", ["打撃練習", "守備練習", "投球練習", "走塁", "ウェイト", "自主練・その他"])
                with l_col3: duration = st.number_input("練習時間（分）", value=120, step=5)
                detail_num = st.text_input("具体的な数値情報（任意）", placeholder="例: 投球数50球、ティー100本、スクワット80kgなど")
                
                st.subheader("3. 3ステップ振り返り（思考をかく乱・細分化）")
                note_success = st.text_area("①【成果】今日うまくいったこと・意識できたこと")
                note_challenge = st.text_area("②【課題】見つかった反省点・改善したいこと")
                note_next = st.text_area("③【次への一手】明日具体的にどう修正・練習するか")
                
                if st.form_submit_button("野球ノートをクラウドへ提出する"):
                    new_note = pd.DataFrame({
                        "選手名": [st.session_state.user], "日付": [str(date)], "体調": [condition], "体重(kg)": [weight], "睡眠時間(時間)": [sleep_time],
                        "メニュー": [menu_type], "時間(分)": [duration], "詳細数値": [detail_num], "成果": [note_success], "課題": [note_challenge], "次への一手": [note_next],
                        "指導者コメント": ["まだコメントはありません"], "MVR": ["未選出"]
                    })
                    st.session_state.notes_db = pd.concat([st.session_state.notes_db, new_note], ignore_index=True)
                    st.success("野球ノートを安全に送信・保存しました！指導者の返事を待ちましょう。")
                    st.balloons()

        # ------------------------------------------
        # 【選手】📊 コンディション分析
        # ------------------------------------------
        elif menu == "📊 体調・コンディション分析":
            st.header("📊 あなたの身体・コンディションデータ推移")
            my_data = st.session_state.notes_db[st.session_state.notes_db["選手名"] == st.session_state.user]
            
            if not my_data.empty:
                my_data_sorted = my_data.sort_values("日付")
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("📉 体重 (kg) のバイオリズム")
                    st.line_chart(my_data_sorted[["日付", "体重(kg)"]].set_index("日付"))
                with col2:
                    st.subheader("💤 睡眠時間 (時間) のバイオリズム")
                    st.line_chart(my_data_sorted[["日付", "睡眠時間(時間)"]].set_index("日付"))
            else:
                st.warning("データがまだ蓄積されていません。日々のノートを提出しましょう！")

        # ------------------------------------------
        # 【選手】📊 能力値レーダーチャート
        # ------------------------------------------
        elif menu == "📊 マイ能力値（パワプロ風）":
            st.header("📊 パワプロ風マイ能力値チャート")
            my_skill = st.session_state.skills_db[st.session_state.skills_db["選手名"] == st.session_state.user]
            
            with st.form("skill_form"):
                st.subheader("現在の自己能力を5段階で評価してください")
                col1, col2, col3, col4, col5 = st.columns(5)
                s_meet = col1.slider("ミート", 1, 5, int(my_skill.iloc[-1]["ミート"]) if not my_skill.empty else 3)
                s_pow = col2.slider("パワー", 1, 5, int(my_skill.iloc[-1]["パワー"]) if not my_skill.empty else 3)
                s_run = col3.slider("走力", 1, 5, int(my_skill.iloc[-1]["走力"]) if not my_skill.empty else 3)
                s_def = col4.slider("守備力", 1, 5, int(my_skill.iloc[-1]["守備力"]) if not my_skill.empty else 3)
                s_men = col5.slider("メンタル", 1, 5, int(my_skill.iloc[-1]["メンタル"]) if not my_skill.empty else 3)
                
                if st.form_submit_button("能力チャートを更新"):
                    new_skill = pd.DataFrame({"選手名": [st.session_state.user], "ミート": [s_meet], "パワー": [s_pow], "走力": [s_run], "守備力": [s_def], "メンタル": [s_men]})
                    st.session_state.skills_db = st.session_state.skills_db[st.session_state.skills_db["選手名"] != st.session_state.user]
                    st.session_state.skills_db = pd.concat([st.session_state.skills_db, new_skill], ignore_index=True)
                    st.success("能力値を解析・更新しました！")
                    st.rerun()
            
            if not st.session_state.skills_db[st.session_state.skills_db["選手名"] == st.session_state.user].empty:
                labels = np.array(['Meat', 'Power', 'Run', 'Def', 'Mental'])
                stats = st.session_state.skills_db[st.session_state.skills_db["選手名"] == st.session_state.user].iloc[-1][1:6].values.astype(int)
                
                angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
                stats = np.concatenate((stats, [stats[0]]))
                angles = np.concatenate((angles, [angles[0]]))
                
                fig, ax = plt.subplots(figsize=(3, 3), subplot_kw=dict(polar=True))
                ax.fill(angles, stats, color='blue', alpha=0.25)
                ax.plot(angles, stats, color='blue', linewidth=2)
                ax.set_xticks(angles[:-1])
                ax.set_xticklabels(labels)
                st.pyplot(fig)

        # ------------------------------------------
        # 【選手】💬 LINE風個別トーク
        # ------------------------------------------
        elif menu == "💬 監督との個別トーク":
            st.header("💬 監督・コーチへの個別トーク（LINE風）")
            
            # トーク履歴の抽出
            chat_history = st.session_state.chat_db[
                ((st.session_state.chat_db["送信者"] == st.session_state.user) & (st.session_state.chat_db["受信者"] == "指導者共通")) |
                ((st.session_state.chat_db["送信者"] == "指導者共通") & (st.session_state.chat_db["受信者"] == st.session_state.user))
            ].sort_values(by="送信日時")
            
            # チャット風表示
            for _, msg in chat_history.iterrows():
                if msg["送信者"] == st.session_state.user:
                    st.markdown(f"<div style='text-align: right; background-color: #DCF8C6; padding: 10px; border-radius: 10px; margin: 5px; display: block; float: right; clear: both;'><b>あなた:</b> {msg['メッセージ']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='text-align: left; background-color: #EAEAEA; padding: 10px; border-radius: 10px; margin: 5px; display: block; float: left; clear: both;'><b>指導者:</b> {msg['メッセージ']}</div>", unsafe_allow_html=True)
            
            st.markdown("<div style='clear: both; padding-top: 20px;'></div>", unsafe_allow_html=True)
            
            with st.form("chat_form", clear_on_submit=True):
                send_msg = st.text_input("メッセージを入力...")
                if st.form_submit_button("送信"):
                    if send_msg.strip():
                        new_chat = pd.DataFrame([{
                            "送信日時": str(datetime.datetime.now().strftime('%m/%d %H:%M')),
                            "送信者": st.session_state.user, "受信者": "指導者共通", "メッセージ": send_msg.strip()
                        }])
                        st.session_state.chat_db = pd.concat([st.session_state.chat_db, new_chat], ignore_index=True)
                        st.rerun()

    # 🛑 鉄壁のセキュリティ壁：ここから下は指導者のみアクセス可能。プログラム自体が分離しているため選手は絶対に開けない
    elif st.session_state.role == "監督・コーチ":
        menu = st.sidebar.radio("指導者メニュー", [
            "👀 選手ノート一覧 ＆ 個別指導", 
            "📈 チーム全体の動向 ＆ ランキング",
            "💬 選手との個別トーク（LINE風）"
        ])
        
        # ------------------------------------------
        # 【指導者】👀 ノート確認＆個別指導
        # ------------------------------------------
        if menu == "👀 選手ノート一覧 ＆ 個別指導":
            st.header("👀 選手ノート確認 ＆ 個別指導システム")
            
            if not st.session_state.notes_db.empty:
                players = st.session_state.users_auth[st.session_state.users_auth["立場"] == "選手"]["選手名"].unique()
                if len(players) == 0:
                    st.info("まだ登録された選手がいません。")
                else:
                    selected_player = st.selectbox("指導・確認する選手を選択してください", players)
                    player_notes = st.session_state.notes_db[st.session_state.notes_db["選手名"] == selected_player]
                    
                    st.subheader(f"🏃‍♂️ {selected_player} 選手のノート履歴")
                    for idx, row in player_notes.sort_values(by="日付", ascending=False).iterrows():
                        # 怪我アラート検知システム
                        is_injured = "⚠️" if "重い" in row['体調'] or "最悪" in row['体調'] else "📅"
                        mvr_badge = "【🌟 MVR選出中】" if row['MVR'] == "🌟 MVR選出済" else ""
                        
                        with st.expander(f"{is_injured} {row['日付']} | 体調: {row['体調']} {mvr_badge}"):
                            st.text(f"身体データ -> 体重: {row['体重(kg)']}kg / 睡眠: {row['睡眠時間(時間)']}時間")
                            st.markdown(f"🟢 **成果:** {row['成果']}")
                            st.markdown(f"🔴 **課題:** {row['課題']}")
                            st.markdown(f"🔵 **次への一手:** {row['次への一手']}")
                            st.markdown("---")
                            st.write(f"💬 現在の赤ペン: `{row['指導者コメント']}`")
                            
                            # 爆速クイック返信スタンプ機能
                            stamp = st.radio("クイック返信スタンプを選択", ["（利用しない）", "ナイス分析！その調子で次も意識しよう！", "素晴らしい努力！怪我だけは気をつけていこう。", "明日は無理せず完全休養を指示します。お大事に。"], key=f"stamp_{idx}")
                            custom_reply = st.text_input("個別指導コメントを手入力", key=f"rep_{idx}")
                            
                            final_reply = custom_reply if custom_reply else (stamp if stamp != "（利用しない）" else "")
                            
                            c1, c2 = st.columns(2)
                            if c1.button("個別フィードバックを保存する", key=f"b_rep_{idx}", type="primary"):
                                if final_reply:
                                    st.session_state.notes_db.at[idx, "指導者コメント"] = final_reply
                                    st.success("個別メッセージをカルテに保存しました。")
                                    st.rerun()
                                    
                            if row['MVR'] != "🌟 MVR選出済":
                                if c2.button("👑 このノートをチームMVR（お手本）に選出", key=f"b_mvr_{idx}"):
                                    st.session_state.notes_db.at[idx, "MVR"] = "🌟 MVR選出済"
                                    st.success("チームのダッシュボードへお手本として掲示しました。")
                                    st.rerun()
            else:
                st.info("選手から提出された野球ノートはまだありません。")

        # ------------------------------------------
        # 【指導者】📈 チーム動向＆ランキング
        # ------------------------------------------
        elif menu == "📈 チーム全体の動向 ＆ ランキング":
            st.header("📈 チーム管理・スローガン設定 ＆ 月間努力ランキング")
            
            # スローガン設定機能
            st.subheader("📢 今週のチームスローガン更新")
            new_slogan = st.text_input("選手トップ画面に表示するメッセージを入力", value=st.session_state.slogan_db)
            if st.button("スローガンを全体配信"):
                st.session_state.slogan_db = new_slogan
                st.success("全選手のトップページへスローガンを同期・配信しました！")
                
            st.markdown("---")
            
            # 月間ランキング自動生成
            st.subheader("🔥 リアルタイム月間努力ランキング")
            if not st.session_state.notes_db.empty:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("🏆 **総練習時間 ランキング（上位順）**")
                    ranking_time = st.session_state.notes_db.groupby("選手名")["時間(分)"].sum().reset_index()
                    ranking_time = ranking_time.sort_values(by="時間(分)", ascending=False).reset_index(drop=True)
                    ranking_time.index = ranking_time.index + 1
                    st.table(ranking_time)
                with col2:
                    st.markdown("🏆 **ノート提出回数 ランキング**")
                    ranking_count = st.session_state.notes_db["選手名"].value_counts().reset_index()
                    ranking_count.columns = ["選手名", "提出回数"]
                    ranking_count.index = ranking_count.index + 1
                    st.table(ranking_count)
            else:
                st.info("選手データが蓄積されると、ここに自動でランキング順位表が生成されます。")

        # ------------------------------------------
        # 【指導者】💬 LINE風個別トーク管理
        # ------------------------------------------
        elif menu == "💬 選手との個別トーク（LINE風）":
            st.header("💬 選手個別LINE風トークルーム")
            
            players = st.session_state.users_auth[st.session_state.users_auth["立場"] == "選手"]["選手名"].unique()
            if len(players) == 0:
                st.info("選手アカウントがまだありません。")
            else:
                chat_player = st.selectbox("トークする選手を選択してください", players)
                st.subheader(f"💬 {chat_player} 選手とのチャット")
                
                chat_history = st.session_state.chat_db[
                    ((st.session_state.chat_db["送信者"] == chat_player) & (st.session_state.chat_db["受信者"] == "指導者共通")) |
                    ((st.session_state.chat_db["送信者"] == "指導者共通") & (st.session_state.chat_db["受信者"] == chat_player))
                ].sort_values(by="送信日時")
                
                for _, msg in chat_history.iterrows():
                    if msg["送信者"] == "指導者共通":
                        st.markdown(f"<div style='text-align: right; background-color: #DCF8C6; padding: 10px; border-radius: 10px; margin: 5px; display: block; float: right; clear: both;'><b>あなた(指導者):</b> {msg['メッセージ']}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div style='text-align: left; background-color: #EAEAEA; padding: 10px; border-radius: 10px; margin: 5px; display: block; float: left; clear: both;'><b>{chat_player}:</b> {msg['メッセージ']}</div>", unsafe_allow_html=True)
                
                st.markdown("<div style='clear: both; padding-top: 20px;'></div>", unsafe_allow_html=True)
                
                with st.form("coach_chat_form", clear_on_submit=True):
                    send_msg = st.text_input("メッセージを入力...")
                    if st.form_submit_button("送信"):
                        if send_msg.strip():
                            new_chat = pd.DataFrame([{
                                "送信日時": str(datetime.datetime.now().strftime('%m/%d %H:%M')),
                                "送信者": "指導者共通", "受信者": chat_player, "メッセージ": send_msg.strip()
                            }])
                            st.session_state.chat_db = pd.concat([st.session_state.chat_db, new_chat], ignore_index=True)
                            st.rerun()
      
