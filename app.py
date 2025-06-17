import mplfinance as mpf
import matplotlib.pyplot as plt
import pandas as pd
import requests
import streamlit as st
from io import BytesIO


# 外部APIのURL（Cloudflare Tunnel 経由）
API_URL = "https://mostly-finance-population-lb.trycloudflare.com"

# ページ設定
st.set_page_config(page_title="ルール1 株価チェック", layout="centered")

# CSS（入力欄の文字拡大）
st.markdown("""
    <style>
    input[type="number"], input[type="text"] {
        font-size: 22px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# タイトル
st.markdown("""
    <h1 style='text-align:left; color:#2E86C1; font-size:26px; line-height:1.4em;'>
        『ルール1』<br>株価チェックアプリ
    </h1>
""", unsafe_allow_html=True)
st.markdown("---")

st.caption("ルール１に該当する企業コードをこちらにご入力ください。")
code = st.text_input("企業コード（半角英数字のみ、例: 7203）", "7203")

recent_high = None
recent_low = None

def green_box(label, value, unit):
    st.markdown(f"""
        <div style="
            background-color: #f0fdf4;
            border-left: 4px solid #4CAF50;
            padding: 10px 15px;
            border-radius: 5px;
            margin-bottom: 10px;">
            ✅ <strong>{label}：</strong><br>
            <span style="font-size:24px; font-weight:bold;">{value} {unit}</span>
        </div>
    """, unsafe_allow_html=True)

if code:
    try:
        response = requests.get(API_URL, params={"code": code})
        if response.status_code == 200:
            data = response.json()
            company_name = data.get("name", "企業名不明")
            recent_high = data["high"]
            high_date = data["high_date"]
            recent_low = data["low"]
            low_date = data["low_date"]

            st.subheader(f"{company_name}（{code}）の株価情報")
            st.markdown(f"✅ **直近5営業日の高値**:<br><span style='font-size:24px'>{recent_high:.2f} 円（{high_date}）</span>", unsafe_allow_html=True)
            st.markdown(f"✅ **高値日から過去2週間以内の安値**:<br><span style='font-size:24px'>{recent_low:.2f} 円（{low_date}）</span>", unsafe_allow_html=True)

        else:
            st.error(f"APIエラー: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"データ取得中にエラーが発生しました: {e}")

st.markdown("---")

# 計算ツール
if recent_high and recent_low:
    st.markdown("""
        <h2 style='text-align:left; color:#2E86C1; font-size:26px; line-height:1.4em;'>
            上げ幅の半値押し<br>計算ツール
        </h2>
    """, unsafe_allow_html=True)

    high_input = st.number_input("高値（円）", min_value=0.0, value=recent_high, format="%.2f")
    low_input = st.number_input("2週間以内の最安値（円）", min_value=0.0, value=recent_low, format="%.2f")
    st.caption("必要であれば高値・安値を修正して「計算する」をタップしてください。")

    if st.button("計算する"):
        if high_input > low_input > 0:
            rise_rate = high_input / low_input
            width = high_input - low_input
            half = math.floor(width / 2)
            retrace = math.floor(high_input - half)

            green_box("上昇率", f"{rise_rate:.2f}", "倍")
            green_box("上げ幅", f"{width:.2f}", "円")
            green_box("上げ幅の半値", f"{half}", "円")
            green_box("上げ幅の半値押し", f"{retrace}", "円")
        else:
            st.warning("高値＞安値 の数値を正しく入力してください。")

st.markdown("---")