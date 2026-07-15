import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Set page configuration
st.set_page_config(
    page_title="Personal Finance Dashboard",
    page_icon="🌿",
    layout="wide"
)

# Custom styling optimized for a premium, low-friction Dark Mode
st.markdown("""
    <style>
    div[data-testid="stMetric"] {
        background-color: #1a1a1e;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #2d2824;
    }
    div[data-testid="stMetric"] label {
        color: #b5a89e !important;
        font-size: 0.9em !important;
        letter-spacing: 0.5px;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #f4edd2 !important;
        font-family: 'Georgia', serif;
    }
    h1, h2, h3, h4 {
        color: #f4edd2;
        font-family: 'Georgia', serif;
        font-weight: 400;
    }
    </style>
""", unsafe_allow_html=True)

# Warm, sophisticated design palette
PRIMARY_WARM = '#e07a5f'    # Terracotta
TREND_LINE = '#81b29a'      # Sage Green
ACCENT_AMBER = '#f2cc8f'    # Soft Gold
BG_TRANSPARENT = 'rgba(0,0,0,0)'

# Title of the dashboard
st.title("☕ My Capital Journal")
st.markdown("<p style='color: #b5a89e; font-style: italic; margin-bottom: 2rem;'>An intelligently designed space tracking outflow composition and behavioral spending trends.</p>", unsafe_allow_html=True)

@st.cache_data
def load_and_clean_data():
    try:
        csv_path = os.path.join("data", "register.csv")
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip()
        
        df['transaction_amount'] = pd.to_numeric(df['transaction_amount'], errors='coerce').fillna(0)
        
        # Parse Dates safely
        df['parsed_date'] = pd.to_datetime(df['date'].str.split('|').str[0].str.strip(), errors='coerce', utc=True)
        df['parsed_date'] = df['parsed_date'].fillna(pd.to_datetime(df['date'], errors='coerce', utc=True))
        
        df['current account balance'] = pd.to_numeric(df['current account balance'], errors='coerce').ffill()
        df['category'] = df['category'].fillna('Other').str.strip()
        
        df = df.sort_values(by='parsed_date').reset_index(drop=True)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()    

df = load_and_clean_data()

if not df.empty:
    # --- Sidebar Filters ---
    st.sidebar.header("Filter Options")
    all_categories = sorted(df['category'].unique().tolist())
    selected_categories = st.sidebar.multiselect("Select Categories to View", options=all_categories, default=all_categories)
    
    filtered_df = df[df['category'].isin(selected_categories)]
    expenses_df = filtered_df[filtered_df['alert_type'] == 'Debit']

    # --- KPI Metrics ---
    total_credit = df[df['alert_type'] == 'Credit']['transaction_amount'].sum()
    total_debit = df[df['alert_type'] == 'Debit']['transaction_amount'].sum()
    latest_balance = df['current account balance'].iloc[-1] if not df['current account balance'].dropna().empty else 0

    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        st.metric(label="TOTAL INFLOW", value=f"${total_credit:,.2f}")
    with kpi2:
        st.metric(label="TOTAL OUTFLOW", value=f"${total_debit:,.2f}")
    with kpi3:
        st.metric(label="RESTING BALANCE", value=f"${latest_balance:,.2f}")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- SECTION 1: WHERE IS THE MONEY GOING? (Pareto-style Priority) ---
    st.subheader("🔍 Outflow Composition")
    
    if not expenses_df.empty:
        category_summary = expenses_df.groupby('category')['transaction_amount'].sum().reset_index()
        category_summary = category_summary.sort_values(by='transaction_amount', ascending=True) # Ascending for clean horizontal bottom-up growth
        
        cat_col1, cat_col2 = st.columns([3, 2])
        
        with cat_col1:
            fig_category = px.bar(
                category_summary,
                x='transaction_amount',
                y='category',
                orientation='h',
                template="plotly_dark",
                labels={'transaction_amount': 'Total Value Spent', 'category': ''}
            )
            
            # Intelligently clean up bar aesthetics
            fig_category.update_traces(
                marker_color=PRIMARY_WARM,
                marker_line_color=PRIMARY_WARM,
                opacity=0.85,
                hovertemplate="<b>%{y}</b><br>Total Spent: $% {x:,.2f}<extra></extra>"
            )
            fig_category.update_layout(
                paper_bgcolor=BG_TRANSPARENT,
                plot_bgcolor=BG_TRANSPARENT,
                font=dict(color="#b5a89e", family="sans-serif"),
                xaxis=dict(showgrid=True, gridcolor="#2a2a30", zeroline=False, tickprefix="$"),
                yaxis=dict(showgrid=False),
                margin=dict(l=20, r=20, t=10, b=10),
                height=320
            )
            st.plotly_chart(fig_category, use_container_width=True, config={'displayModeBar': False})
            
        with cat_col2:
            st.markdown("<p style='color:#b5a89e; font-size:0.9em; font-weight:bold; letter-spacing:1px;'>VOLUME RANKING</p>", unsafe_allow_html=True)
            # Display sorted descending for the text list
            for index, row in category_summary.iloc[::-1].iterrows():
                percentage = (row['transaction_amount'] / total_debit) * 100 if total_debit > 0 else 0
                st.markdown(f"""
                <div style='display: flex; justify-content: space-between; border-bottom: 1px solid #222226; padding: 6px 0;'>
                    <span style='color:#dfb295;'>{row['category']}</span>
                    <span style='color:#f4edd2; font-family:monospace;'>${row['transaction_amount']:,.2f} <span style='color:#81b29a; font-size:0.85em;'>({percentage:.1f}%)</span></span>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No expense data matching filters.")

    st.markdown("<br><hr style='border-top: 1px solid #222226;'><br>", unsafe_allow_html=True)

    # --- SECTION 2: SPENDING TRENDS OVER TIME (Macro vs Micro) ---
    st.subheader("📈 Behavioral Macro Trends")
    
    if not expenses_df.empty:
        # Build chronological daily timeline
        expenses_df['Date'] = expenses_df['parsed_date'].dt.date
        timeline_df = expenses_df.groupby('Date')['transaction_amount'].sum().reset_index()
        timeline_df = timeline_df.sort_values(by='Date')
        
        # Supercharge information efficiency: Compute a rolling 7-day baseline
        # This isolates noisy one-off transactions from baseline habits
        timeline_df['7_day_rolling'] = timeline_df['transaction_amount'].rolling(window=7, min_periods=1).mean()
        
        time_col1, time_col2 = st.columns([3, 1])
        
        with time_col1:
            fig_time = go.Figure()
            
            # Subtle raw daily data bars (Micro View)
            fig_time.add_trace(go.Bar(
                x=timeline_df['Date'],
                y=timeline_df['transaction_amount'],
                name='Daily Total Outflow',
                marker_color='#3d342e',
                opacity=0.6,
                hovertemplate="Daily Total: $% {y:,.2f}<extra></extra>"
            ))
            
            # Bright, smooth rolling baseline line chart (Macro View)
            fig_time.add_trace(go.Scatter(
                x=timeline_df['Date'],
                y=timeline_df['7_day_rolling'],
                mode='lines',
                name='7-Day Smooth Trend',
                line=dict(color=TREND_LINE, width=3.5, shape='spline'),
                hovertemplate="7-Day Avg Baseline: $% {y:,.2f}<extra></extra>"
            ))
            
            fig_time.update_layout(
                template="plotly_dark",
                paper_bgcolor=BG_TRANSPARENT,
                plot_bgcolor=BG_TRANSPARENT,
                font=dict(color="#b5a89e"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                xaxis=dict(showgrid=False, zeroline=False),
                yaxis=dict(showgrid=True, gridcolor="#2a2a30", zeroline=False, tickprefix="$"),
                margin=dict(l=20, r=20, t=10, b=10),
                height=350
            )
            st.plotly_chart(fig_time, use_container_width=True, config={'displayModeBar': False})
            
        with time_col2:
            st.markdown("<p style='color:#b5a89e; font-size:0.9em; font-weight:bold; letter-spacing:1px;'>BEHAVIOR INSIGHTS</p>", unsafe_allow_html=True)
            if not timeline_df.empty:
                max_spend_row = timeline_df.loc[timeline_df['transaction_amount'].idxmax()]
                avg_spend = timeline_df['transaction_amount'].mean()
                
                st.markdown(f"""
                <div style='background-color: #141417; padding: 15px; border-radius: 8px; border-left: 3px solid {TREND_LINE}; margin-bottom: 12px;'>
                    <p style='color:#b5a89e; margin:0; font-size:0.85em;'>DAILY OUTFLOW BASELINE</p>
                    <h3 style='margin:4px 0 0 0; color:#f4edd2;'>${avg_spend:,.2f}</h3>
                </div>
                <div style='background-color: #141417; padding: 15px; border-radius: 8px; border-left: 3px solid {PRIMARY_WARM};'>
                    <p style='color:#b5a89e; margin:0; font-size:0.85em;'>MAX OUTFLOW ANOMALY</p>
                    <h3 style='margin:4px 0 0 0; color:#e07a5f;'>${max_spend_row['transaction_amount']:,.2f}</h3>
                    <span style='color:#b5a89e; font-size:0.8em;'>Occurred on {max_spend_row['Date']}</span>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No historical expense trends available.")

    st.markdown("<br><hr style='border-top: 1px solid #222226;'><br>", unsafe_allow_html=True)

    # --- Detailed Data Table ---
    st.subheader("📋 Ledger")
    display_cols = ['parsed_date', 'report', 'alert_type', 'category', 'transaction_amount', 'description']
    st.dataframe(
        filtered_df[display_cols].rename(columns={'parsed_date': 'Timestamp'}),
        use_container_width=True,
        hide_index=True
    )