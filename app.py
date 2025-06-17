import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

API_URL = "https://mostly-finance-population-lb.trycloudflare.com"

st.set_page_config(page_title="株価チェックアプリ", layout="centered")
st.title("📈 株価チェック（過去2週間＆チャート）")

code = st.text_input("銘柄コードを入力してください（例：7203）", value="7203")

show_chart = False  # チャート表示フラグ

if st.button("データ取得"):
    if not code.strip():
        st.warning("銘柄コードを入力してください。")
    else:
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

                # チャート表示ボタン
                if st.button("チャート表示"):
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
