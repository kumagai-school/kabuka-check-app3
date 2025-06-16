
import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import math

# APIのURL（Quick Tunnelなどで外部公開されているFlaskアプリのURL）
API_BASE_URL = "https://demonstrated-differ-adams-foster.trycloudflare.com"  # ←ここを実際のURLに書き換えてください

st.set_page_config(page_title="ルール1 株価チェック", layout="centered")

# 入力
code = st.text_input("企業コード（半角英数字のみ、例: 7203）", "7203")

recent_high = None
recent_low = None

if code:
    try:
        # 直近5営業日の高値取得
        response = requests.get(f"{API_BASE_URL}/api/highlow?code={code}")
        data = response.json()

        if "error" in data:
            st.error(data["error"])
        else:
            company_name = data["name"]
            high_date_str = data["high_date"]
            recent_high = float(data["high_value"])
            low_date_str = data["low_date"]
            recent_low = float(data["low_value"])

            st.subheader(f"{company_name}（{code}）の株価情報")

            st.markdown(f"✅ **直近5営業日の高値**:<br><span style='font-size:24px'>{recent_high:.2f} 円（{high_date_str}）</span>", unsafe_allow_html=True)
            st.markdown(f"✅ **高値日から過去2週間以内の安値**:<br><span style='font-size:24px'>{recent_low:.2f} 円（{low_date_str}）</span>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"エラーが発生しました：{e}")

st.markdown("---")
st.markdown("<h4>📌 <strong>注意事項</strong></h4>", unsafe_allow_html=True)

st.markdown("""
<div style='color:red; font-size:14px;'>
<ul>
  <li>Yahoo!financeのチャート更新タイミング（日足チャート：当日の20時30分ごろ）に連動いたします。</li>
  <li>ゴールデンウィークなどの連休・イレギュラーな日程には正確に対応できない場合があります。</li>
</ul>
</div>
""", unsafe_allow_html=True)


# 計算ツール
if recent_high is not None and recent_low is not None:
    st.markdown("---")
    st.markdown(
    """
    <h2 style='text-align:left; color:#2E86C1; font-size:26px; line-height:1.4em;'>
        上げ幅の半値押し<br>計算ツール
    </h2>
    """,
    unsafe_allow_html=True
    )
    high_input = st.number_input("高値（円）", min_value=0.0, value=recent_high, format="%.2f")
    low_input  = st.number_input("2週間以内の最安値（円）", min_value=0.0, value=recent_low, format="%.2f")
    st.caption("必要であれば高値・安値を修正して「計算する」をタップしてください。")

    if st.button("計算する"):
        if high_input > low_input and low_input > 0:
            rise_rate = high_input / low_input
            width     = high_input - low_input
            half      = math.floor(width / 2)
            retrace   = math.floor(high_input - half)

            green_box("上昇率", f"{rise_rate:.2f}", "倍")
            green_box("上げ幅", f"{width:.2f}", "円")
            green_box("上げ幅の半値", f"{half}", "円")
            green_box("上げ幅の半値押し", f"{retrace}", "円")


        else:
            st.warning("高値＞安値 の数値を正しく入力してください。")

st.markdown("---")
st.markdown("<h4>📌 <strong>注意事項</strong></h4>", unsafe_allow_html=True)

st.markdown("""
<div style='color:red; font-size:14px;'>
<ul>
  <li>Yahoo!financeのチャート更新タイミング（日足チャート：当日の20時30分ごろ）に連動いたします。</li>
  <li>ゴールデンウィークなどの連休・イレギュラーな日程には正確に対応できない場合があります。</li>
</ul>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

