import streamlit as st
import requests
import math
import mplfinance as mpf
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import pandas as pd
import requests
import streamlit as st
from io import BytesIO

# --------------------------
# 設定
# --------------------------
API_URL = "https://mostly-finance-population-lb.trycloudflare.com"

# --------------------------
# ヘッダー
# --------------------------
st.set_page_config(page_title="株価チェックアプリ", layout="centered")
st.title("📈 株価チェック（過去2週間＆チャート）")

# --------------------------
# ユーザー入力
# --------------------------
code = st.text_input("銘柄コードを入力してください（例：7203）", value="7203")

if st.button("データ取得"):
    if not code.strip():
        st.warning("銘柄コードを入力してください。")
    else:
        with st.spinner("データを取得中..."):
            # 高値・安値 API 呼び出し
            try:
                resp = requests.get(f"{API_URL}/api/highlow", params={"code": code})
                data = resp.json()

                if "error" in data:
                    st.error(data["error"])
                else:
                    st.success("✅ 高値・安値を取得しました")
                    st.write(f"**銘柄コード：** {data['code']}")
                    st.write(f"**高値：** {data['high']}（{data['high_date']}）")
                    st.write(f"**安値：** {data['low']}（{data['low_date']}）")
            except Exception as e:
                st.error(f"高値・安値データ取得に失敗しました: {e}")

            # チャート API 呼び出し
           try:
                # ✅ 1回だけ呼び出す
                resp = requests.get(f"{API_URL}/api/highlow", params={"code": code})
                data = resp.json()

                if "error" in data:
                    st.error(data["error"])
                else:
                    st.success("✅ 高値・安値を取得しました")
                    st.write(f"**銘柄コード：** {data['code']}")
                    st.write(f"**高値：** {data['high']}（{data['high_date']}）")
                    st.write(f"**安値：** {data['low']}（{data['low_date']}）")

                    # チャートもここで取得（if の中に含める）
                    chart_resp = requests.get(f"{API_URL}/api/candle", params={"code": code})
                    chart_data = chart_resp.json().get("data", [])

                    if not chart_data:
                        st.warning("ローソク足チャートの取得に失敗しました。")
                    else:
                        df = pd.DataFrame(chart_data)
                        df["date"] = pd.to_datetime(df["date"])
                        fig = go.Figure(data=[
                            go.Candlestick(
                                x=df['date'],
                                open=df['open'],
                                high=df['high'],
                                low=df['low'],
                                close=df['close'],
                                increasing_line_color="red",
                                decreasing_line_color="blue"
                            )
                        ])
                        fig.update_layout(
                            title=f"{data.get('name', '')} の2週間ローソク足チャート",
                            xaxis_title="日付",
                            yaxis_title="株価",
                            xaxis_rangeslider_visible=False
                        )
                        st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"データ取得中にエラーが発生しました: {e}")

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
st.markdown("<h4>📌 <strong>注意事項</strong></h4>", unsafe_allow_html=True)

st.markdown("""
<div style='color:red; font-size:14px;'>
<ul>
  <li>このアプリは東京証券取引所（.T）上場企業のみに対応しています。</li>
  <li>平日朝8時45分～9時頃にメンテナンスが入ることがございます。</li>
  <li>ゴールデンウィークなどの連休・イレギュラーな日程には正確に対応できない場合があります。</li>
</ul>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
