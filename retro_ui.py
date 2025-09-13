# import streamlit as st
# import plotly.graph_objects as go
# import pandas as pd
# import yfinance as yf

# def apply_retro_style():
#     st.markdown("""
#         <style>
#             body {
#                 background-color: black;
#                 color: #00FF00;
#                 font-family: 'Courier New', monospace;
#             }
#             .stButton>button {
#                 background-color: black;
#                 color: #00FF00;
#                 border: 2px solid #00FF00;
#                 font-family: 'Courier New', monospace;
#             }
#             .stTextInput>div>input {
#                 background-color: black;
#                 color: #00FF00;
#                 border: 2px solid #00FF00;
#                 font-family: 'Courier New', monospace;
#             }
#             .stTextArea>div>textarea {
#                 background-color: black;
#                 color: #00FF00;
#                 border: 2px solid #00FF00;
#                 font-family: 'Courier New', monospace;
#             }
#         </style>
#     """, unsafe_allow_html=True)

# def render_summary_box(summary_text: str):
#     html_text = summary_text.replace("\n", "<br>")
#     st.markdown(
#         f"""
#         <div style="
#             background-color: #111;
#             color: #0f0;
#             padding: 15px;
#             border-radius: 5px;
#             font-family: 'Courier New', monospace;
#             font-size: 14px;
#             max-height: 220px;
#             overflow-y: auto;
#         ">
#         {html_text}
#         </div>
#         """,
#         unsafe_allow_html=True
#     )
# retro_ui.py — UI-only helpers for RetroTrader (retro CRT style)
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import yfinance as yf

# ---------- Global style ----------
def apply_retro_style():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=VT323&family=Press+Start+2P&display=swap');

    html, body, [data-testid="stAppViewContainer"]{
        background: radial-gradient(circle at 50% -20%, #18201a 0%, #0b0f0c 40%, #080b08 100%) !important;
        color:#e4ffe8 !important;
        font-family:"VT323", monospace !important;
        letter-spacing:.2px;
    }

    /* CRT scanlines + vignette (doesn't block clicks) */
    .crt-overlay::before{
        content:""; position:fixed; inset:0; pointer-events:none; z-index:9999;
        background: repeating-linear-gradient(
            0deg, rgba(0,0,0,.22), rgba(0,0,0,.22) 2px,
                  rgba(255,255,255,.03) 2px, rgba(255,255,255,.03) 4px);
        mix-blend-mode:multiply;
    }
    .crt-overlay::after{
        content:""; position:fixed; inset:0; pointer-events:none; z-index:9998;
        background: radial-gradient(circle at 50% 50%, transparent 0%, rgba(0,0,0,.15) 70%, rgba(0,0,0,.55) 100%);
    }

    h1,h2,h3,h4{
        font-family:"Press Start 2P", monospace !important;
        color:#39ff14 !important;
        text-shadow:0 0 6px rgba(57,255,20,.45);
        line-height:1.25;
    }

    /* Panels */
    .retro-panel{
        border:2px solid #39ff14; border-radius:12px;
        padding:16px; margin:8px 0 16px 0;
        background:rgba(10,14,11,.60);
        box-shadow:0 0 18px rgba(57,255,20,.12), inset 0 0 12px rgba(57,255,20,.08);
    }

    /* Inputs */
    .stTextInput > div > div > input{
        background:#0e140f; color:#e4ffe8; border:1.5px solid #2adf0e;
        border-radius:10px; box-shadow:inset 0 0 8px rgba(57,255,20,.10);
    }

    /* Buttons */
    .stButton > button{
        font-family:"Press Start 2P", monospace !important;
        background:#0b0f0c;
        color:#39ff14;
        border:2px solid #39ff14;
        border-radius:12px;
        padding:12px 18px;
        letter-spacing:1px;
        font-size:14px;
        box-shadow:0 0 14px rgba(57,255,20,.35), inset 0 0 8px rgba(57,255,20,.20);
        transition:all .12s ease-in-out;
        text-transform:uppercase;
        animation: glow-pulse 1.6s infinite alternate;
    }
    .stButton > button:hover{
        transform:translateY(-2px) scale(1.02);
        box-shadow:0 0 20px rgba(57,255,20,.65), inset 0 0 12px rgba(57,255,20,.30);
        background:#111a12;
    }

    /* Glowing pulse animation */
    @keyframes glow-pulse {
        from { box-shadow:0 0 8px rgba(57,255,20,.35); }
        to   { box-shadow:0 0 20px rgba(57,255,20,.75); }
    }

    /* Tables */
    .stDataFrame, .dataframe { filter: drop-shadow(0 0 6px rgba(57,255,20,.15)); }

    /* Code blocks */
    .stMarkdown code, .stCode{
        background:#081008 !important; border:1px solid #2adf0e !important;
        color:#caffc7 !important;
    }

    #MainMenu, footer {visibility:hidden;}
    </style>
    <div class="crt-overlay"></div>
    """, unsafe_allow_html=True)

# ---------- Components ----------
def render_summary_box(items):
    """Render bullet summary in retro panel."""
    st.markdown('<div class="retro-panel">', unsafe_allow_html=True)
    if isinstance(items, (list, tuple)):
        for it in items:
            st.markdown(f"<div>► {str(it)}</div>", unsafe_allow_html=True)
    elif isinstance(items, str):
        for line in items.splitlines():
            if line.strip():
                st.markdown(f"<div>► {line.strip()}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

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






