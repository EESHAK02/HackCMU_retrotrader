import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import yfinance as yf

def apply_retro_style():
    st.markdown("""
        <style>
            body {
                background-color: black;
                color: #00FF00;
                font-family: 'Courier New', monospace;
            }
            .stButton>button {
                background-color: black;
                color: #00FF00;
                border: 2px solid #00FF00;
                font-family: 'Courier New', monospace;
            }
            .stTextInput>div>input {
                background-color: black;
                color: #00FF00;
                border: 2px solid #00FF00;
                font-family: 'Courier New', monospace;
            }
            .stTextArea>div>textarea {
                background-color: black;
                color: #00FF00;
                border: 2px solid #00FF00;
                font-family: 'Courier New', monospace;
            }
        </style>
    """, unsafe_allow_html=True)

def render_summary_box(summary_text: str):
    html_text = summary_text.replace("\n", "<br>")
    st.markdown(
        f"""
        <div style="
            background-color: #111;
            color: #0f0;
            padding: 15px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            max-height: 220px;
            overflow-y: auto;
        ">
        {html_text}
        </div>
        """,
        unsafe_allow_html=True
    )

def plot_stock_chart(info: dict, period="1y"):
    """
    Plot stock price trend over time.
    Red line = decreasing days, green line = increasing days (optional color shading)
    period: default '1y' for 1 year, can be '6mo', '3mo', etc.
    """
    try:
        data = yf.Ticker(info['ticker']).history(period=period)
        if data.empty:
            return None
        
        # Create a line chart of closing prices
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['Close'],
                mode='lines+markers',
                line=dict(color='lime', width=2),
                marker=dict(
                    color=['lime' if c >= o else 'red' for c, o in zip(data['Close'], data['Open'])],
                    size=6
                ),
                name='Close Price'
            )
        )

        fig.update_layout(
            title=f"{info['ticker']} Price Trend ({period})",
            xaxis_title="Date",
            yaxis_title="Price ($)",
            template="plotly_dark",
            height=400,
            plot_bgcolor='black',
            paper_bgcolor='black',
            font=dict(color='lime', family='Courier New')
        )

        return fig
    except Exception as e:
        print(f"Error plotting stock chart: {e}")
        return None

def render_competitors_table(competitors: list):
    if not competitors:
        st.write("No competitors found.")
        return
    df = pd.DataFrame(competitors)
    df['Trend'] = df['trend'].apply(lambda t: f"🟢 {t}" if t=="BULLISH" else f"🔴 {t}" if t=="BEARISH" else t)
    st.markdown(
        df[['name','ticker','price','Trend','sector','industry']].to_html(index=False),
        unsafe_allow_html=True
    )




