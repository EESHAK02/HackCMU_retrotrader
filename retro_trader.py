import streamlit as st
from nlp_utils import load_models, summarize_text, analyze_sentiment, detect_main_company
from data_utils import extract_article_text, COMPANY_TICKER_MAP, get_stock_info, get_competitors, get_ticker
from retro_ui import apply_retro_style, render_summary_box, plot_stock_chart, render_competitors_table

st.title("📟 RetroTrader: Retro Terminal Market Summarizer")
st.caption("Paste a financial article text below and get headlines, sentiment, and stock insights.")

apply_retro_style()

article_url = st.text_input("Enter News Article URL:")

if st.button("🔎 Analyze Article"):
    if not article_url:
        st.warning("Please enter a URL first!")
        st.stop()

    # Load models
    summarizer, finbert = load_models()

    # Fetch article
    try:
        article_text = extract_article_text(article_url)
    except Exception as e:
        st.error(f"Could not fetch article: {e}")
        st.stop()
    
    # Detect main company
    company_list = list(COMPANY_TICKER_MAP.keys())
    main_company_name = detect_main_company(article_text)
    
    if not main_company_name:
        st.warning("No company detected in article.")
        st.stop()

    #main_company_ticker = COMPANY_TICKER_MAP[main_company_name]
    #main_company_ticker = get_ticker(main_company_name)
    # Resolve to ticker
    main_company_ticker = get_ticker(main_company_name)
    if not main_company_ticker:
        st.warning(f"Could not resolve ticker for {main_company_name}")
        st.stop()

    # Summarize & Sentiment
    summary = summarize_text(article_text, summarizer)
    sentiment = analyze_sentiment(article_text, finbert)

    st.subheader("Summary")
    render_summary_box(summary)

    st.subheader("Sentiment")
    st.write(f"{sentiment['label']} | Confidence: {sentiment['score']:.2f}")

    # Stock info
    st.subheader(f"Stock Insight: {main_company_name.title()} ({main_company_ticker})")
    info = get_stock_info(main_company_ticker)
    st.write(f"Price: ${info['price']:.2f} | Trend: {info['trend']} | Δ: {info['pct']:.2f}% | Sector: {info['sector']} | Industry: {info['industry']}")
    fig = plot_stock_chart(info, period="1y")
    if fig:
        st.plotly_chart(fig, use_container_width=True)

    # Competitors
    st.subheader("Competitors")
    competitors = get_competitors(main_company_ticker)
    render_competitors_table(competitors)
