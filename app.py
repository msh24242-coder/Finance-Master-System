import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Page configuration
st.set_page_config(page_title="SPAR Budget Tracker", layout="wide")

# Dark Green Theme CSS
st.markdown("""
    <style>
    .stApp { background-color: #004d26; }
    h1, h2, h3, p, span, label { color: #ffffff !important; font-family: 'Segoe UI'; }
    [data-testid="stMetricValue"] { color: #00ff00 !important; }
    .stDataFrame { background-color: #ffffff; border-radius: 10px; }
    /* Sidebar styling */
    section[data-testid="stSidebar"] { background-color: #003d1e; border-right: 1px solid #00ff00; }
    </style>
    """, unsafe_allow_html=True)

st.title("🟢 SPAR Monthly Budget & LPO Tracker")

# Sidebar for Budget Management
st.sidebar.header("💰 Budget Management")
monthly_limit = st.sidebar.number_input("Set Monthly Budget (QR):", min_value=0, value=70000)

# File path
file_path = 'Data/LPO DATA 2023 jan Jihad.csv'

if not os.path.exists(file_path):
    st.error(f"File not found: {file_path}")
else:
    try:
        # Load Data
        df = pd.read_csv(file_path, skiprows=1)
        df.columns = [str(c).strip() for c in df.columns]
        df = df[df['LPO Number'].notna()]
        
        # Date Processing
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['Month'] = df['date'].dt.strftime('%B %Y') # Extract Month & Year
        
        # Financial Processing
        mall_cols = ['Tawar', '03 mall', 'Bsquare mall', 'Almana', 'Porto', 'QQ', 'aljazzera', 'head Office']
        for col in mall_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        df['Total_Amount'] = df[[c for c in mall_cols if c in df.columns]].sum(axis=1)

        # Monthly Selection
        available_months = df['Month'].dropna().unique().tolist()
        selected_month = st.sidebar.selectbox("Select Month to Track:", available_months if available_months else ["No Data"])

        # Filter data for selected month
        month_df = df[df['Month'] == selected_month]
        total_spent = month_df['Total_Amount'].sum()
        remaining = monthly_limit - total_spent
        utilization = (total_spent / monthly_limit) * 100 if monthly_limit > 0 else 0

        # --- Dashboard UI ---
        
        # Top Metrics
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Monthly Budget", f"{monthly_limit:,.2f} QR")
        with c2:
            st.metric("Total Spent", f"{total_spent:,.2f} QR")
        with c3:
            st.metric("Remaining", f"{remaining:,.2f} QR", delta_color="inverse")

        # Progress Bar for Budget
        st.subheader(f"Budget Utilization for {selected_month}")
        bar_color = "green" if utilization < 90 else "red"
        st.progress(min(utilization/100, 1.0))
        st.write(f"You have used **{utilization:.1f}%** of your monthly budget.")

        st.divider()

        # Charts
        left, right = st.columns(2)
        with left:
            st.subheader("Spending by Branch (This Month)")
            branch_sums = month_df[mall_cols].sum().reset_index()
            branch_sums.columns = ['Branch', 'Amount']
            fig = px.pie(branch_sums[branch_sums['Amount']>0], values='Amount', names='Branch', hole=0.5,
                         color_discrete_sequence=px.colors.sequential.Greens_r)
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig, use_container_width=True)

        with right:
            st.subheader("Daily Spending Trend")
            daily_trend = month_df.groupby('date')['Total_Amount'].sum().reset_index()
            fig_line = px.line(daily_trend, x='date', y='Total_Amount', markers=True)
            fig_line.update_traces(line_color='#00ff00')
            fig_line.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig_line, use_container_width=True)

        # Table
        st.subheader(f"LPO Details for {selected_month}")
        st.dataframe(month_df[['LPO Number', 'company name', 'date', 'Items', 'Total_Amount']], use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}")
