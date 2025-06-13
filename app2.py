import streamlit as st
import pandas as pd
import os

# CSVファイルのパス（ローカル or 外部URLに変更可能）
CSV_FILE = "RealData.csv"  # または "https://example.com/RealData.csv"

st.set_page_config(page_title="Tower株価チェックAPP", layout="centered")
st.title("📈 Tower株価チェック（仮設置）")

# 銘柄コード入力
code = st.text_input("銘柄コードを入力してください（例：7203）", max_chars=8)

if code:
    try:
        # CSV読み込み（Shift-JISを明示）
        df = pd.read_csv(CSV_FILE, encoding="shift_jis")

        # 文字列形式で左ゼロ埋め
        padded_code = code.zfill(4)

        # 銘柄抽出
        target = df[df.iloc[:, 0].astype(str).str.zfill(4) == padded_code]

        if not target.empty:
            row = target.iloc[0]
            st.subheader(f"✅ {row[2]} ({row[0]})")
            st.write(f"🕒 時刻：{row[8]} / 日付：{row[7]}")
            st.metric("現在値", row[6])
            st.metric("高値", row[4])
            st.metric("安値", row[5])
            st.metric("前日比", row[9])
            st.metric("出来高", row[10])
        else:
            st.error("該当する銘柄が見つかりませんでした。")

    except FileNotFoundError:
        st.error(f"CSVファイルが見つかりません：{CSV_FILE}")
    except Exception as e:
        st.error(f"エラーが発生しました：{str(e)}")
else:
    st.info("銘柄コードを入力してください。")
